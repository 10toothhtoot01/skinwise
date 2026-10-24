# Capture reliability implementation and tests

Reviewed October 24, 2026. Recommendations below concern photo acquisition. They do not establish the accuracy of scores derived from the photo.

## Verified vendor interface

The [current JS Camera Kit reference](https://docs.perfectcorp.com/reference/ai_face_analyzer/section/overview/js-camera-kit) documents SDK 2.5, HTTPS/getUserMedia, and mount `YMK-module`. Relevant initialization:

```js
YMK.init({
  faceDetectionMode: 'skincare',
  imageFormat: 'blob',
  qualityLevel: 'moderate',
  disableCameraResolutionCheck: false,
  videoQuality: '1080p',
  language: 'enu'
});
YMK.openCameraKit();
```

`faceQualityChanged` provides `hasFace`, `position`, `frontal`, `lighting`; example values are true/good/good/ok. `faceDetectionCaptured` provides `images[]` with image, width, height, phase. `cameraFailed` and `unsupportedResolution` report acquisition failures. Close with `YMK.close()` and remove listeners by their returned identifiers. Quality presets are relaxed/moderate/strict; defaults must not be confused with our explicitly selected moderate setting. Documentation exposes position, pose, and lighting checks, not blur scores or score-accuracy confidence.

The documented prerequisites and init parameters do not specify a license key, REST API key, application ID, or domain-registration step. This omission does not establish unrestricted licensing. No separate license was purchased or confirmed in this audit. The owner must verify applicable usage terms and deployment compatibility.

## Actual SDK discrepancy and feasibility

The public [SDK script](https://plugins-media.makeupar.com/v2.5-camera-kit/sdk.js) was fetched without credentials for read-only interface inspection. Its actual loader invokes `window.ymkAsyncInit` with lowercase y, while current prose uses `window.YMKAsyncInit`. The downloaded script also contains invalid-domain and invalid-license error messages. These strings demonstrate possible failure states, not whether this account or domain requires additional registration. There are no observed `apiKey`/`appKey` parameters in the inspected loader. Runtime activation remains the final compatibility test.

`components/guided-capture.tsx` registers both init spellings to the same idempotent callback and restores prior globals on cleanup. It loads the SDK only after the explicit Open guided camera button, registers documented events, waits for actual capture plus the latest passing checks, and returns a File with provenance. SDK load and camera startup have bounded failure messages. It does not send a secret to the browser or start an analysis. The caller reviews the image before any paid task.

## Choosing the approach

Use the vendor's guided mode as an optional acquisition path because its documented checks target the provider's face-position/pose/light requirements. Keep upload usable when the SDK fails or a user declines camera access. Do not write an unvalidated homegrown blur/lighting classifier and label its output “quality approved.” Heuristics can give retake hints only after they are separately tested and named honestly.

Vendor capture passing means the SDK accepted that capture session. It does not mean the photo is clinically valid, repeatable across devices, blur-free, or comparable with a previous session. The API still validates bytes and dimensions independently. A physical camera capture has not yet been tested by this implementation audit.

## Evidence to preserve

Camera provenance: source `youcam-camera-kit`, SDK version `2.5`, preset `moderate`, and the actual latest checks. Keep endpoint protocol and model identity separate: endpoint version `2.1`, SD, UI score, model build unknown. Record capture time and final pixel dimensions as observations. Browser-reported camera dimensions do not prove device-model identity.

Upload provenance: source `upload`, quality assessment `not-assessed`, decoded pixel dimensions, and voluntary capture notes. Ask for same camera, lighting, position, and recent skincare conditions when comparing sessions; do not mark those facts verified because a user checked a box. Do not infer camera model, no makeup, lighting consistency, identity, age, skin tone, or consent from EXIF or image appearance. Strip unnecessary EXIF and retain no raw image merely to support a score label.

## Actionable verification matrix

These tests are proposed acceptance checks; distinguish mocked results from real-device evidence when recording them.

| Test | Expected proof |
|---|---|
| Initial page render | No SDK request, getUserMedia request, or analysis request |
| Explicit camera click | SDK requested once; init uses skincare/moderate/blob; camera opens only afterward |
| SDK loader uses lowercase callback | Initialization succeeds; duplicate uppercase callback cannot open twice |
| CDN denied or timeout | Bounded error, upload remains available, no quality approval |
| Permission denied | Specific guidance; no File/evidence callback; no paid request |
| Resolution unsupported | Specific guidance; no forced resolution-check bypass |
| No face / bad position / nonfrontal / bad lighting | Individual observable checks; capture never emits approved evidence |
| Capture event without prior quality event | Reject missing evidence; never assume SDK passed everything |
| Passing checks without capture event | No File callback; a quality update is not an image capture |
| Passing checks then invalid image payload | Reject unsupported MIME or missing Blob; no fabricated image |
| Valid capture event and checks | Exact File plus exact recorded provenance, once only |
| Unmount/cancel/reopen | Close camera, remove listeners, restore prior callbacks; no stale event writes |
| Stored upload fallback | Label unassessed; numeric score availability never implies capture approval |
| No physical camera available | Fake camera/UI tests clearly labeled; no hardware-compatibility claim |

Mock SDK tests can intercept the CDN with a minimal YMK implementation exposing listener registration, trigger controlled events, and spy on open/close calls. Use a real Blob payload. Assert callback count and provenance, not just green status text. Fake Chromium camera tests additionally exercise browser permission/stream flows, but cannot validate the vendor's real face checker.

Real hardware testing requires a consenting adult at the device. Test intended phone/browser combinations (including iOS Safari and Android Chrome), front-camera orientation, permission revocation, network failure, and at least repeated captures with matched conditions. Observe SDK startup/domain failures before buying or configuring another license. Keep all device/skin-tone performance conclusions open until these tests and the broader measurement protocol in ACCURACY-EVIDENCE.md are completed.

## Actual CDN test finding

A controlled Chromium run used a fake video device and fake permission UI, never a person's webcam. The actual SDK, UI bundles, and WASM/data resources loaded with HTTP 200; YMK existed and mounted the camera interface. No analysis requests were sent. Camera startup failed with SDK `error.no.camera`, and the app displayed its upload fallback. The SDK also emitted an uncaught promise rejection. This is a failed camera startup test, not successful guided capture.

Read-only inspection of the downloaded public SDK found its camera-label predicate deliberately rejects labels matching `cyberlink|videomeeting|youcam|virtual|fake|manycam|perfectcam|droidcam` (case insensitive). Chrome's fake device matches that rejection. Its camera lookup therefore has no accepted device. The SDK's `openCameraKit()` wrapper invokes its internal open operation without returning that operation's promise, so the application cannot attach a rejection handler through this documented method. No global rejection handler or SDK patch was added.

This explains the fake-device failure without establishing real-device support or a domain-license failure. Keep mocked event-contract tests separate, retain upload, and mark physical guided capture unverified until a consenting user tests accepted hardware. Do not hide or rename fake camera labels to present a hardware pass.
