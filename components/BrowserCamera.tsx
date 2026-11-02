'use client';
import {useCallback, useEffect, useRef, useState} from 'react';
import {Camera, RefreshCw, X} from 'lucide-react';
import './browser-camera.css';

type Guidance = {faceCount:number; warnings:string[]; bounds:{x:number;y:number;width:number;height:number}|null; elapsedMs:number};
type Phase = 'closed'|'opening'|'live'|'review';
const unavailable = 'Local face guidance is unavailable. You can still capture and inspect the photo yourself.';
function cameraError(error:unknown) {
  const name=error instanceof DOMException?error.name:'';
  if(name==='NotAllowedError'||name==='SecurityError')return 'Camera permission was not granted. Allow camera access in your browser, or use upload / native camera instead.';
  if(name==='NotFoundError')return 'No camera was found. Connect a camera or choose an existing portrait.';
  if(name==='NotReadableError'||name==='AbortError')return 'The camera could not start. Close other apps using it and try again, or upload a portrait.';
  if(name==='OverconstrainedError')return 'This camera cannot provide the requested view. Try the other camera or upload a portrait.';
  return 'The camera could not open. Try again or use upload / native camera instead.';
}

export default function BrowserCamera({onCapture,disabled=false}:{onCapture:(file:File)=>void;disabled?:boolean}) {
  const [phase,setPhase]=useState<Phase>('closed');
  const [message,setMessage]=useState('');
  const [guidance,setGuidance]=useState<Guidance|null>(null);
  const [modelMessage,setModelMessage]=useState('');
  const [ready,setReady]=useState(false);
  const [taking,setTaking]=useState(false);
  const [facing,setFacing]=useState<'user'|'environment'>('user');
  const [switchable,setSwitchable]=useState(false);
  const [review,setReview]=useState('');
  const video=useRef<HTMLVideoElement>(null),openButton=useRef<HTMLButtonElement>(null);
  const stream=useRef<MediaStream|null>(null),worker=useRef<Worker|null>(null);
  const generation=useRef(0), timer=useRef<ReturnType<typeof setTimeout>|null>(null), watchdog=useRef<ReturnType<typeof setTimeout>|null>(null);
  const reviewUrl=useRef(''), captured=useRef<File|null>(null), modelBusy=useRef(false);
  const stopResources=useCallback(()=>{
    if(timer.current)clearTimeout(timer.current);if(watchdog.current)clearTimeout(watchdog.current);
    timer.current=null;watchdog.current=null;modelBusy.current=false;
    worker.current?.terminate();worker.current=null;
    stream.current?.getTracks().forEach(track=>track.stop());stream.current=null;
    if(video.current)video.current.srcObject=null;
  },[]);
  const releaseReview=useCallback(()=>{if(reviewUrl.current)URL.revokeObjectURL(reviewUrl.current);reviewUrl.current='';captured.current=null;},[]);
  const close=useCallback(()=>{
    generation.current++;stopResources();releaseReview();setPhase('closed');setReview('');setGuidance(null);setReady(false);setTaking(false);setModelMessage('');
    openButton.current?.focus();
  },[stopResources,releaseReview]);
  useEffect(()=>()=>{generation.current++;stopResources();releaseReview();},[stopResources,releaseReview]);
  useEffect(()=>{const leave=()=>{generation.current++;stopResources();releaseReview();};window.addEventListener('pagehide',leave);return()=>window.removeEventListener('pagehide',leave);},[stopResources,releaseReview]);

  function beginGuidance(ticket:number) {
    if(typeof Worker==='undefined'||typeof OffscreenCanvas==='undefined'||typeof createImageBitmap==='undefined'){setModelMessage(unavailable);return;}
    let model:Worker;
    try{model=new Worker('/camera/face-worker.js');worker.current=model;}catch{setModelMessage(unavailable);return;}
    setModelMessage('Loading local face guidance… Camera frames stay on this device.');
    const fail=()=>{if(ticket!==generation.current)return;model.terminate();if(worker.current===model)worker.current=null;modelBusy.current=false;if(timer.current)clearTimeout(timer.current);if(watchdog.current)clearTimeout(watchdog.current);setGuidance(null);setModelMessage(unavailable);};
    const check=async()=>{
      if(ticket!==generation.current||worker.current!==model)return;
      if(document.hidden){setGuidance(null);setModelMessage('Local checks paused while this tab is hidden.');timer.current=setTimeout(()=>void check(),700);return;}
      const v=video.current;
      if(!v||v.readyState<2||!v.videoWidth||modelBusy.current){timer.current=setTimeout(()=>void check(),500);return;}
      modelBusy.current=true;
      try{
        const scale=Math.min(1,640/Math.max(v.videoWidth,v.videoHeight));
        const bitmap=await createImageBitmap(v,{resizeWidth:Math.max(1,Math.round(v.videoWidth*scale)),resizeHeight:Math.max(1,Math.round(v.videoHeight*scale)),resizeQuality:'high'});
        if(ticket!==generation.current||worker.current!==model){bitmap.close();return;}
        watchdog.current=setTimeout(fail,8000);
        model.postMessage({id:ticket,bitmap},[bitmap]);
      }catch{fail();}
    };
    model.onmessage=event=>{
      if(ticket!==generation.current||worker.current!==model)return;
      if(watchdog.current)clearTimeout(watchdog.current);modelBusy.current=false;
      const data=event.data;
      if(data.error){fail();return;}
      if(!data.ready){setGuidance(data as Guidance);setModelMessage(data.elapsedMs>350?'Local checks are running less often on this device.':'Local positioning hints · advisory only');}
      timer.current=setTimeout(()=>void check(),data.elapsedMs>350?2000:650);
    };
    model.onerror=event=>{event.preventDefault();fail();};
    watchdog.current=setTimeout(fail,20000);model.postMessage({id:ticket});
  }

  async function start(nextFacing:'user'|'environment'=facing) {
    const ticket=++generation.current;stopResources();releaseReview();setReview('');setGuidance(null);setMessage('');setReady(false);setTaking(false);setSwitchable(false);setModelMessage('');setFacing(nextFacing);setPhase('opening');
    if(!window.isSecureContext||!navigator.mediaDevices?.getUserMedia){setMessage('Browser camera needs HTTPS or localhost and camera support. Use upload / native camera instead.');setPhase('closed');return;}
    try{
      const media=await navigator.mediaDevices.getUserMedia({audio:false,video:{facingMode:{ideal:nextFacing},width:{ideal:1280},height:{ideal:960}}});
      if(ticket!==generation.current){media.getTracks().forEach(track=>track.stop());return;}
      stream.current=media;
      for(const track of media.getVideoTracks())track.addEventListener('ended',()=>{if(ticket===generation.current){generation.current++;stopResources();setReady(false);setPhase('closed');setMessage('Camera access ended. Open it again or use upload.');}});
      const v=video.current;if(!v)throw new Error('Camera preview unavailable');v.srcObject=media;await v.play();
      if(ticket!==generation.current)return;
      setReady(v.videoWidth>0);setPhase('live');beginGuidance(ticket);
      try{const devices=await navigator.mediaDevices.enumerateDevices();if(ticket===generation.current)setSwitchable(devices.filter(d=>d.kind==='videoinput').length>1);}catch{/* Switching is optional; the current camera remains usable. */}
    }catch(error){if(ticket!==generation.current)return;stopResources();setReady(false);setPhase('closed');setMessage(cameraError(error));}
  }

  async function takePhoto() {
    const v=video.current,ticket=generation.current;if(!v||!ready||taking)return;
    setTaking(true);setMessage('');
    try{
      const canvas=document.createElement('canvas');canvas.width=v.videoWidth;canvas.height=v.videoHeight;
      if(!canvas.width||!canvas.height)throw new Error('No camera frame');
      const ctx=canvas.getContext('2d');if(!ctx)throw new Error('No canvas');ctx.drawImage(v,0,0);
      const blob=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('Capture failed')),'image/png'));
      canvas.width=0;canvas.height=0;
      if(ticket!==generation.current)return;
      stopResources();setGuidance(null);captured.current=new File([blob],'camera-original.png',{type:'image/png'});reviewUrl.current=URL.createObjectURL(blob);setReview(reviewUrl.current);setPhase('review');setTaking(false);setReady(false);setModelMessage('Camera stopped. Review the original unmirrored capture before using it.');
    }catch{if(ticket===generation.current){setTaking(false);setMessage('The photo could not be captured. Try again or use upload.');}}
  }
  function accept(){const file=captured.current;if(!file||disabled)return;onCapture(file);close();setMessage('Capture selected. Inspect the prepared portrait before starting a preview.');}

  return <div className="browser-camera">
    <button ref={openButton} type="button" disabled={disabled||phase!=='closed'} onClick={()=>void start()}><Camera size={17}/> Open browser camera</button>
    <p className="camera-intro">Optional local face and framing hints. Opening asks for camera permission; it does not upload or start a paid preview.</p>
    {message&&<p role="status">{message}</p>}
    {phase!=='closed'&&<section className="camera-panel" aria-label="Browser portrait camera" onKeyDown={e=>{if(e.key==='Escape'){e.stopPropagation();close();}}}>
      <div className="camera-panel-head"><h3>{phase==='review'?'Review your capture':'Frame your portrait'}</h3><button type="button" onClick={close} aria-label="Close browser camera"><X size={18}/></button></div>
      {phase==='review'?<img className="camera-review" src={review} alt="Original unmirrored camera capture for review"/>:<div className="camera-view"><video ref={video} muted playsInline autoPlay className={facing==='user'?'camera-mirrored':''} aria-label="Live camera preview" onLoadedMetadata={()=>setReady(true)}/><div className="camera-frame" aria-hidden="true"/></div>}
      <p className="camera-mirror-note">{phase==='review'?'This is the original camera orientation.':facing==='user'?'Selfie preview is mirrored for positioning. The captured photo is not mirrored.':'Rear camera preview and captured photo are not mirrored.'}</p>
      {phase==='opening'&&<p role="status">Waiting for camera permission… You can close this panel to cancel.</p>}
      {modelMessage&&<p className="camera-model-state" role="status">{modelMessage}</p>}
      {guidance&&<div className="camera-advice"><strong>{guidance.faceCount===1?'One face detected':`${guidance.faceCount} faces detected`}</strong>{guidance.warnings.length?<ul>{guidance.warnings.map(w=><li key={w}>{w}</li>)}</ul>:<p>No framing warning from this check. Inspect focus, lighting and the full face yourself.</p>}</div>}
      <p className="camera-limit">These uncalibrated hints can miss problems or be wrong. They do not certify photo quality or cosmetic accuracy, and never block capture. Avoid beauty filters; keep eyes, lips and the whole face visible.</p>
      <div className="camera-actions">{phase==='review'?<><button type="button" disabled={disabled} onClick={accept}>Use this capture</button><button type="button" onClick={()=>void start()}><RefreshCw size={16}/> Retake photo</button></>:<><button type="button" disabled={phase!=='live'||!ready||taking} onClick={()=>void takePhoto()}>{taking?'Capturing…':'Capture photo'}</button>{switchable&&<button type="button" disabled={taking} onClick={()=>void start(facing==='user'?'environment':'user')}>Switch camera</button>}</>}<button type="button" onClick={close}>Cancel camera</button></div>
    </section>}
  </div>;
}
