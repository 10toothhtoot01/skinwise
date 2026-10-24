'use client';
import {useState} from 'react';
import {focusOptions,type Focus,type Visuals,type EvidenceReview} from '@/lib/evidence';
type Region={key:string;label:string;region:string;score:number};
type Props={id:string;source:'demo'|'youcam';metrics:{key:string;label:string;score:number}[];regions?:Region[];visuals?:Visuals;focus:Focus;onFocus:(focus:Focus)=>void;review?:EvidenceReview;onReview:(review:EvidenceReview)=>void;canRefresh:boolean;refreshing:boolean;onRefresh:()=>void;error?:string};
const regionName=(value:string)=>value.replaceAll('_',' ').replace(/^./,s=>s.toUpperCase());
export function EvidenceInspector({source,metrics,regions=[],visuals,focus,onFocus,review,onReview,canRefresh,refreshing,onRefresh,error}:Props){
  const [zoom,setZoom]=useState(1);
  const [region,setRegion]=useState(review?.focus===focus?(review.region||'whole'):'whole');
  const [note,setNote]=useState(review?.focus===focus?review.note:'');
  function selectRegion(value:string){setRegion(value);setNote(review?.focus===focus&&(review.region||'whole')===value?review.note:'');}
  const entries=regions.filter(r=>r.key===focus);
  const image=visuals?.items.find(v=>v.key===focus&&v.region===region);
  const focused=metrics.find(m=>m.key===focus || focus==='pore'&&m.key==='pores');
  // Images and scores are independent provider outputs; either can make a region inspectable.
  const returnedRegions=[...new Set([
    ...(focused?['whole']:[]),
    ...entries.map(entry=>entry.region),
    ...(visuals?.items.filter(item=>item.key===focus).map(item=>item.region)||[]),
  ])];
  const selectedScore=region==='whole'?focused?.score:entries.find(entry=>entry.region===region)?.score;
  const question=focusOptions.find(f=>f.key===focus)!.question;
  return <section className="evidence-workspace" aria-label="YouCam visual evidence">
    <div className="section-heading"><div><h2>Inspect what YouCam marked.</h2><p>Start with your question. Inspect the returned image before interpreting a score.</p></div><span className="pill">{source==='demo'?'Fictional walkthrough':'Actual provider output'}</span></div>
    <div className="focus-options" role="group" aria-label="Question to inspect">{focusOptions.map(option=><button key={option.key} type="button" aria-pressed={focus===option.key} onClick={()=>onFocus(option.key)}>{option.label}</button>)}</div>
    <h3 className="evidence-question">{question}</h3>
    {returnedRegions.length>0&&<div className="region-options" role="group" aria-label="Returned facial regions">{returnedRegions.map(value=>{const score=value==='whole'?focused?.score:entries.find(entry=>entry.region===value)?.score;return <button key={value} aria-pressed={region===value} onClick={()=>selectRegion(value)}>{value==='whole'?'Whole face':regionName(value)} <span>{score!==undefined?`${score}/100`:'No score returned'}</span></button>;})}</div>}
    <div className="evidence-zoom"><label htmlFor="evidence-zoom">Inspect image detail</label><input id="evidence-zoom" type="range" min="1" max="3" step="0.25" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/><span>{zoom}× · scroll either image to inspect</span></div><div className="evidence-images">
      <figure><ImageTile key={visuals?.originalUrl||'no-original'} url={visuals?.originalUrl} zoom={zoom} alt="Provider-returned input image used for this scan" empty={source==='demo'?'Sample records contain no real portrait.':'The provider input image is not loaded.'}/><figcaption>Reference image returned by YouCam</figcaption></figure>
      <figure><ImageTile key={image?.url||'no-detection'} url={image?.url} zoom={zoom} alt={`YouCam ${image?.kind||'image'} for ${focusOptions.find(f=>f.key===focus)!.label}, ${regionName(region)}`} empty={source==='demo'?'No detection image is invented for sample data.':'No detection image is loaded for this concern and region.'}/><figcaption>{image?.kind==='overlay'?'Provider detection overlay':'Provider detection mask'} · {regionName(region)}</figcaption></figure>
    </div>
    {source==='youcam'&&<div className="evidence-reload"><p>Images are temporary and stay out of journal exports. Refresh retrieves the existing completed task; it does not start another analysis.</p><button className="button secondary" disabled={!canRefresh||refreshing} onClick={onRefresh}>{refreshing?'Refreshing images…':'Refresh detection images'}</button>{!canRefresh&&<span>No saved task receipt is available on this browser. A new analysis is not started automatically.</span>}</div>}
    {error&&<p role="status" className="inline-note">{error}</p>}
    <div className="evidence-reading"><div><h3>{selectedScore!==undefined?`${regionName(region)} ${focusOptions.find(option=>option.key===focus)!.label}: ${selectedScore}/100`:'No score was returned for this concern and region.'}</h3><p>The mark shows what the model detected, not a confirmed condition or a probability map. {entries.length>0?'Regional values are listed only where YouCam returned them.':'No regional score breakdown is available for this concern.'}</p></div><div><h3>Your decision</h3><p>Does the marked area match what you wanted to inspect? If it does not, record the mismatch and avoid basing a routine decision on this result.</p></div></div>
    <div className="evidence-review"><h3>Keep your interpretation with the scan.</h3><p>Saving replaces this scan’s current interpretation. Selected area: {regionName(region)}.</p><div role="group" aria-label="Does the model match your concern?">{([{value:'yes',label:'Matches my concern'},{value:'no',label:'Does not match'},{value:'unsure',label:'Not sure'}] as const).map(option=><button type="button" key={option.value} aria-pressed={review?.focus===focus&&(review.region||"whole")===region&&review.match===option.value} onClick={()=>onReview({focus,region,match:option.value,note})}>{option.label}</button>)}</div><label htmlFor="evidence-note">What did you notice in the marked area?</label><textarea id="evidence-note" name="evidence-note" autoComplete="off" maxLength={600} value={note} onChange={e=>setNote(e.target.value)} placeholder="For example, the model marked my nose, but my question was about my cheeks…"/><button className="button secondary" onClick={()=>onReview({focus,region,match:review?.focus===focus&&(review.region||"whole")===region?review.match:'unsure',note})}>Save scan interpretation</button><p>Your interpretation is a personal observation, not validation that the model is correct.</p></div>
  </section>;
}

function ImageTile({url,zoom,alt,empty}:{url?:string;zoom:number;alt:string;empty:string}){const[failed,setFailed]=useState(false);return <div className="evidence-image-window" tabIndex={0} role="region" aria-label={`Scrollable ${alt}`}>{url&&!failed?
// Provider images are temporary signed originals; avoid transforming or caching them through an optimizer.
// eslint-disable-next-line @next/next/no-img-element
<img width="600" height="600" src={url} style={{width:`${zoom*100}%`,maxWidth:"none",height:`${zoom*350}px`}} referrerPolicy="no-referrer" alt={alt} onError={()=>setFailed(true)}/>:<div className="image-empty">{failed?'This temporary image could not load. Refresh images from the existing task.':empty}</div>}</div>;}
