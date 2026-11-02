'use client';
import {useEffect,useRef,useState} from 'react';
import {RotateCw,Crop,Undo2,ScanFace} from 'lucide-react';
import {DEFAULT_FRAME,drawFramedImage,frameGeometry,type FrameSettings} from '@/lib/portrait-framing';
import './portrait-framing.css';

type Props={file:File;disabled:boolean;onApply:(file:File,frame:FrameSettings,lossless:boolean)=>Promise<void>};
/** Explicit local crop. Each edit starts from the original, never a prior JPEG. */
export default function PortraitFraming({file,disabled,onApply}:Props){
 const [open,setOpen]=useState(false),[settings,setSettings]=useState<FrameSettings>(DEFAULT_FRAME);
 const [source,setSource]=useState<HTMLImageElement|null>(null),[error,setError]=useState(''),[working,setWorking]=useState(false);
 const [lossless,setLossless]=useState(false);
 const [checking,setChecking]=useState(false),[advice,setAdvice]=useState<string[]>([]),[suggestion,setSuggestion]=useState<FrameSettings|null>(null);
 const canvasRef=useRef<HTMLCanvasElement>(null),ticketRef=useRef(0),busyRef=useRef(false),checkWorker=useRef<Worker|null>(null),checkTimer=useRef<ReturnType<typeof setTimeout>|null>(null);
 useEffect(()=>{if(!open)return;let cancelled=false;const url=URL.createObjectURL(file);const image=new Image();image.src=url;
  image.decode().then(()=>{if(cancelled)return;if(image.naturalWidth*image.naturalHeight>32_000_000)throw Error('This original is too large for local framing. Use a smaller original photo.');setSource(image);}).catch(()=>{if(!cancelled)setError('This original could not be opened for framing. Keep the current portrait or choose another image.');});
  return()=>{cancelled=true;ticketRef.current++;checkWorker.current?.terminate();checkWorker.current=null;if(checkTimer.current)clearTimeout(checkTimer.current);URL.revokeObjectURL(url);};
 },[file,open]);
 const geometry=source?frameGeometry(source.naturalWidth,source.naturalHeight,settings):null;

 useEffect(()=>{if(!source||!canvasRef.current)return;try{drawFramedImage(canvasRef.current,source,settings,640);}catch{/* Apply reports a browser allocation failure without changing the portrait. */}},[source,settings]);
 async function checkPhoto(){
  if(!source||disabled||working||checking)return;
  if(typeof Worker==='undefined'||typeof OffscreenCanvas==='undefined'||typeof createImageBitmap==='undefined'){setAdvice(['Local face guidance is unavailable here. Inspect framing manually.']);return;}
  setChecking(true);setSuggestion(null);setAdvice(['Loading the local face check. Your photo stays on this device.']);
  let model:Worker;
  try{model=new Worker('/camera/face-worker.js');checkWorker.current=model;}catch{setChecking(false);setAdvice(['Local face guidance could not start. Inspect framing manually.']);return;}
  const done=(messages:string[],suggested:FrameSettings|null=null)=>{if(checkWorker.current!==model)return;model.terminate();checkWorker.current=null;if(checkTimer.current)clearTimeout(checkTimer.current);setChecking(false);setAdvice(messages);setSuggestion(suggested);};
  model.onerror=e=>{e.preventDefault();done(['Local face guidance is unavailable. Inspect framing manually.']);};
  model.onmessage=event=>{const data=event.data;if(data.error){done(['Local face guidance is unavailable. Inspect framing manually.']);return;}if(data.ready)return;
   const warnings=Array.isArray(data.warnings)?data.warnings.filter((v:unknown):v is string=>typeof v==='string'):[];
   const box=data.bounds;let suggested:FrameSettings|null=null;
   if(data.faceCount===1&&box&&[box.x,box.y,box.width,box.height].every(Number.isFinite)&&box.width>0&&box.height>0){
    const zoom=Math.max(1,Math.min(3,Math.min(source.naturalWidth,source.naturalHeight)/480,.48/Math.max(box.width,box.height)));
    if(zoom>1.05)suggested={zoom,x:box.x+box.width/2,y:box.y+box.height/2,turns:0};
   }
   done(warnings.length?warnings:['No warning from this local check. Inspect the whole face, focus and lighting yourself.'],suggested);
  };
  checkTimer.current=setTimeout(()=>done(['The local face check took too long. Inspect framing manually.']),20000);
  try{const ratio=Math.min(1,640/Math.max(source.naturalWidth,source.naturalHeight));const bitmap=await createImageBitmap(source,{resizeWidth:Math.max(1,Math.round(source.naturalWidth*ratio)),resizeHeight:Math.max(1,Math.round(source.naturalHeight*ratio)),resizeQuality:'high'});if(checkWorker.current!==model){bitmap.close();return;}model.postMessage({id:1,bitmap},[bitmap]);}catch{done(['Local face guidance could not inspect this photo. You can adjust framing manually.']);}
 }
 async function apply(reset=false){
  if(disabled||busyRef.current||!source)return;const frame=reset?DEFAULT_FRAME:settings;const g=frameGeometry(source.naturalWidth,source.naturalHeight,frame);
  if(!g.usable){setError('This crop leaves too few original pixels. Zoom out or take a closer photo; the app will not enlarge it.');return;}
  busyRef.current=true;setWorking(true);setError('');const ticket=++ticketRef.current;
  try{
   // The shared preparation step draws this crop directly from the original into the final JPEG.
   await onApply(file,frame,!reset&&lossless);
   if(reset&&ticket===ticketRef.current)setSettings(DEFAULT_FRAME);
  }catch(e){if(ticket===ticketRef.current)setError(e instanceof Error?e.message:'Framing failed. Your current portrait is unchanged.');}
  finally{busyRef.current=false;if(ticket===ticketRef.current)setWorking(false);}
 }
 return <section className="portrait-framing" aria-label="Portrait framing">
  <button type="button" aria-expanded={open} disabled={disabled||working} onClick={()=>{if(open){checkWorker.current?.terminate();checkWorker.current=null;if(checkTimer.current)clearTimeout(checkTimer.current);setChecking(false);setAdvice([]);setSuggestion(null);}setOpen(v=>!v);setError('');}}><Crop size={16}/>{open?'Close framing':'Adjust framing before preview'}</button>
  {open&&<div className="framing-workspace"><div><h3>Keep the face detail. Leave the extra background.</h3><p>Crop before resizing so more original face pixels fit in the preview. Keep your forehead, chin, eyes and lips fully inside the frame. This changes framing only, not skin detail or color.</p><canvas ref={canvasRef} aria-label="Local framing preview"/><p className="planner-small">This preview is not mirrored. Check that left and right look correct.</p></div>
   <div className="framing-controls"><button type="button" disabled={disabled||working||checking||!source} onClick={()=>void checkPhoto()}><ScanFace size={16}/>{checking?'Checking photo locally…':'Check photo locally'}</button>
    {advice.length>0&&<div className="framing-advice" role="status"><ul>{advice.map(text=><li key={text}>{text}</li>)}</ul><p>Uncalibrated hints can miss problems; they do not establish image or cosmetic accuracy.</p></div>}
    {suggestion&&<button type="button" disabled={disabled||working} onClick={()=>setSettings(suggestion)}>Preview suggested framing</button>}
    <label>Framing zoom<input type="range" min="1" max="3" step="0.05" value={settings.zoom} disabled={disabled||working} onChange={e=>setSettings(s=>({...s,zoom:Number(e.target.value)}))}/></label>
    <label>Horizontal position<input type="range" min="0" max="1" step="0.01" value={settings.x} disabled={disabled||working||settings.zoom===1} onChange={e=>setSettings(s=>({...s,x:Number(e.target.value)}))}/></label>
    <label>Vertical position<input type="range" min="0" max="1" step="0.01" value={settings.y} disabled={disabled||working||settings.zoom===1} onChange={e=>setSettings(s=>({...s,y:Number(e.target.value)}))}/></label>
    <button type="button" disabled={disabled||working} onClick={()=>setSettings(s=>({...s,turns:(s.turns+1)%4}))}><RotateCw size={16}/>Rotate 90°</button>
    {geometry&&<p className="framing-dimensions">{geometry.cropWidth} × {geometry.cropHeight} original pixels retained<br/>{geometry.preparedWidth} × {geometry.preparedHeight} after preparation. No enlargement.</p>}
    {geometry&&!geometry.usable&&<p role="status">Too few original pixels remain. Zoom out or retake closer.</p>}
    <label className="framing-lossless"><input type="checkbox" checked={lossless} disabled={disabled||working} onChange={e=>setLossless(e.target.checked)}/>Use lossless PNG for this framing</label><p className="planner-small">PNG avoids another lossy compression step but can upload more slowly. It cannot restore detail already lost in the source.</p>
    <div className="planner-actions"><button type="button" disabled={disabled||working||!geometry?.usable} onClick={()=>void apply()}>{working?'Preparing framing…':'Use this framing'}</button><button type="button" disabled={disabled||working||!source} onClick={()=>void apply(true)}><Undo2 size={16}/>Use full original</button></div>
    <p className="planner-small">Applying a different portrait resets consent and may replace its preview receipts after confirmation. No YouCam request is made here.</p>
   </div>{error&&<p role="alert">{error}</p>}
  </div>}
 </section>;
}
