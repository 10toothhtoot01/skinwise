'use client';

import { useEffect, useRef, useState } from 'react';

export type CaptureChecks = { hasFace: boolean; position: string; frontal: string; lighting: string };
export type CaptureEvidence = { source: 'youcam-camera-kit'; sdkVersion: '2.5'; preset: 'moderate'; checks: CaptureChecks };
type CaptureProps = { onCapture: (file: File, evidence: CaptureEvidence) => void; disabled?: boolean };
type CameraKit = {
  init: (config: Record<string, unknown>) => void;
  openCameraKit: () => void;
  close: () => void;
  addEventListener: (event: string, handler: (payload?: unknown) => void) => unknown;
  removeEventListener: (id: unknown) => void;
};
type CameraWindow = Window & { YMK?: CameraKit; YMKAsyncInit?: () => void; ymkAsyncInit?: () => void };
const SDK_URL = 'https://plugins-media.makeupar.com/v2.5-camera-kit/sdk.js';
const INITIAL_CHECKS: CaptureChecks = { hasFace: false, position: 'unknown', frontal: 'unknown', lighting: 'unknown' };
function checksFrom(value: unknown): CaptureChecks {
  const q = value && typeof value === 'object' ? value as Record<string, unknown> : {};
  return { hasFace: q.hasFace === true, position: typeof q.position === 'string' ? q.position : 'unknown', frontal: typeof q.frontal === 'string' ? q.frontal : 'unknown', lighting: typeof q.lighting === 'string' ? q.lighting : 'unknown' };
}
function checksPass(q: CaptureChecks) { return q.hasFace && q.position === 'good' && q.frontal === 'good' && (q.lighting === 'good' || q.lighting === 'ok'); }
function cameraFailure(payload: unknown) {
  const object = payload && typeof payload === 'object' ? payload as Record<string, unknown> : {};
  const code = typeof payload === 'string' ? payload : String(object.code || object.error || object.errorCode || '');
  if (code.includes('domain') || code.includes('license') || code.includes('permission_invalid')) return 'Guided capture is not available on this site. Use photo upload instead.';
  if (code.includes('permission')) return 'Camera access was denied. Allow access in your browser settings, or upload a photo instead.';
  if (code.includes('resolution')) return 'This camera does not meet the capture resolution requirement. Use another camera or upload a photo.';
  return 'The camera could not be opened. Check that another app is not using it, or upload a photo instead.';
}

/** Optional vendor capture. No REST credential or analysis request belongs in this component. */
export function GuidedCapture({ onCapture, disabled = false }: CaptureProps) {
  const [phase, setPhase] = useState<'idle' | 'loading' | 'open' | 'captured' | 'error'>('idle');
  const [message, setMessage] = useState('Guided capture checks face position, angle, and lighting. It does not establish score accuracy.');
  const [checks, setChecks] = useState<CaptureChecks>(INITIAL_CHECKS);
  const cleanupRef = useRef<() => void>(() => {});
  const callbackRef = useRef(onCapture);
  useEffect(() => { callbackRef.current = onCapture; }, [onCapture]);
  useEffect(() => () => cleanupRef.current(), []);

  function stop() { cleanupRef.current(); setPhase('idle'); setMessage('Camera closed. You can start again or upload a photo.'); }
  function start() {
    if (disabled) return;
    cleanupRef.current();
    const cameraWindow = window as CameraWindow;
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) { setPhase('error'); setMessage('Camera capture needs a supported browser on HTTPS or localhost. You can upload a photo instead.'); return; }
    let active = true, initialized = false, captured = false;
    let latest = { ...INITIAL_CHECKS };
    let kit: CameraKit | undefined;
    const listeners: unknown[] = [];
    const previousUpper = cameraWindow.YMKAsyncInit, previousLower = cameraWindow.ymkAsyncInit;
    let loadTimer: ReturnType<typeof setTimeout> | undefined;
    let cameraTimer: ReturnType<typeof setTimeout> | undefined;
    let script: HTMLScriptElement | undefined;
    function cleanup() {
      active = false;
      clearTimeout(loadTimer); clearTimeout(cameraTimer);
      if (kit) { for (const id of listeners) { try { kit.removeEventListener(id); } catch { /* SDK may already have disposed it. */ } } try { kit.close(); } catch { /* No camera may have opened. */ } }
      if (cameraWindow.YMKAsyncInit === initialize) cameraWindow.YMKAsyncInit = previousUpper;
      if (cameraWindow.ymkAsyncInit === initialize) cameraWindow.ymkAsyncInit = previousLower;
      if (script) { script.onerror = null; if (!kit) script.remove(); }
    }
    function fail(text: string) { if (!active) return; cleanup(); setPhase('error'); setMessage(text); }
    function listen(name: string, handler: (payload?: unknown) => void) { listeners.push(kit!.addEventListener(name, payload => { if (active) handler(payload); })); }
    function initialize() {
      if (!active || initialized) return;
      kit = cameraWindow.YMK;
      if (!kit) return;
      initialized = true; clearTimeout(loadTimer);
      try {
        listen('faceQualityChanged', value => { latest = checksFrom(value); setChecks(latest); });
        listen('cameraOpened', () => { clearTimeout(cameraTimer); setPhase('open'); setMessage('Follow the camera guidance. Capture completes when the vendor checks pass.'); });
        listen('cameraFailed', value => fail(cameraFailure(value)));
        listen('unsupportedResolution', () => fail('This camera does not meet the capture resolution requirement. Use another camera or upload a photo.'));
        listen('closed', () => { cleanup(); setPhase('idle'); setMessage('Camera closed. You can use photo upload instead.'); });
        listen('faceDetectionCaptured', async payload => {
          if (captured) return;
          if (!checksPass(latest)) { fail('The latest face-position, angle, and lighting checks were not all available. Please retake or upload a photo.'); return; }
          const result = payload && typeof payload === 'object' ? payload as { images?: { image?: unknown }[] } : {};
          const image = result.images?.[0]?.image;
          const evidence: CaptureEvidence = { source: 'youcam-camera-kit', sdkVersion: '2.5', preset: 'moderate', checks: { ...latest } };
          captured = true;
          try {
            let blob: Blob;
            if (image instanceof Blob) blob = image;
            else if (typeof image === 'string' && /^data:image\/(png|jpeg);base64,/.test(image)) blob = await (await fetch(image)).blob();
            else { fail('Guided capture returned no supported image. Please use photo upload.'); return; }
            if (!active) return;
            if (!['image/jpeg', 'image/png'].includes(blob.type)) { fail('Guided capture returned an unsupported image format. Please use photo upload.'); return; }
            cleanup(); setPhase('captured'); setMessage('Photo captured with vendor position, angle, and lighting checks. Review it before analysis.');
            callbackRef.current(new File([blob], blob.type === 'image/png' ? 'guided-selfie.png' : 'guided-selfie.jpg', { type: blob.type }), evidence);
          } catch { fail('The captured image could not be read. Please use photo upload.'); }
        });
        kit.init({ faceDetectionMode: 'skincare', imageFormat: 'blob', qualityLevel: 'moderate', disableCameraResolutionCheck: false, videoQuality: '1080p', language: 'enu' });
        cameraTimer = setTimeout(() => fail('Camera startup timed out. Check permissions and connection, or upload a photo.'), 45_000);
        kit.openCameraKit();
      } catch { fail('Guided capture could not initialize on this browser or site. Use photo upload instead.'); }
    }
    cleanupRef.current = cleanup;
    setChecks(INITIAL_CHECKS); setPhase('loading'); setMessage('Loading guided capture. Your browser will ask for camera permission.');
    // Current documentation uses uppercase Y; the actual v2.5 loader invokes lowercase y.
    cameraWindow.YMKAsyncInit = initialize; cameraWindow.ymkAsyncInit = initialize;
    if (cameraWindow.YMK) initialize();
    else {
      loadTimer = setTimeout(() => fail('Guided capture did not load. Check your connection or upload a photo instead.'), 25_000);
      script = document.querySelector<HTMLScriptElement>('script[data-youcam-camera-kit]') || undefined;
      if (!script) { script = document.createElement('script'); script.src = SDK_URL; script.async = true; script.dataset.youcamCameraKit = '2.5'; script.onerror = () => { script?.remove(); fail('Guided capture could not download. Check your connection or upload a photo instead.'); }; document.head.appendChild(script); }
    }
  }
  const active = phase === 'loading' || phase === 'open';
  return <section aria-label="Guided camera capture" className="rounded-xl border border-[#d8e3dc] bg-white p-4">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div><h3 className="font-semibold">Guided camera capture</h3><p className="mt-1 text-sm text-[#65736b]">Optional YouCam position and lighting guidance</p></div>
      <button type="button" onClick={active ? stop : start} disabled={disabled && !active} className="rounded-lg border border-[#375d48] px-4 py-2 text-sm font-medium text-[#375d48]">{active ? 'Close camera' : 'Open guided camera'}</button>
    </div>
    <p role={phase === 'error' ? 'alert' : 'status'} className="mt-3 text-sm text-[#52665a]">{message}</p>
    {phase === 'open' ? <ul aria-label="Current capture checks" className="mt-3 grid grid-cols-2 gap-2 text-xs text-[#65736b]"><li>Face: {checks.hasFace ? 'Detected' : 'Not detected'}</li><li>Position: {checks.position}</li><li>Angle: {checks.frontal}</li><li>Lighting: {checks.lighting}</li></ul> : null}
    <div id="YMK-module" className={active ? 'mt-4 min-h-80' : 'hidden'} />
  </section>;
}
