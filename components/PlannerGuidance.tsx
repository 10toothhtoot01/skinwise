'use client';
import { useState } from 'react';
import './planner-guidance.css';
import { guidanceSources, resolveGuidance, reviewEvidence, techniqueGuides, type GuidanceQuestion } from '@/lib/cosmetic-guidance';

export function PlannerGuidance(){
 const [question,setQuestion]=useState<GuidanceQuestion>('lip-edge');
 const [confirmed,setConfirmed]=useState(false);
 const guide=techniqueGuides.find(g=>g.id===question)!;
 const answer=resolveGuidance({question,context:confirmed?guide.context:'unknown'});
 return <section className="planner-guidance" aria-labelledby="guidance-title">
  <h2 id="guidance-title">Help with applying your plan</h2>
  <p>Three checked techniques. Pick a question, then check whether the technique fits your product and tools.</p>
  <label htmlFor="technique-question">Technique question</label>
  <select id="technique-question" value={question} onChange={event=>{setQuestion(event.target.value as GuidanceQuestion);setConfirmed(false);}}>
   {techniqueGuides.map(item=><option key={item.id} value={item.id}>{item.question}</option>)}
  </select>
  <label style={{display:'flex',alignItems:'start',gap:'.65rem',marginTop:'1rem'}}><input type="checkbox" checked={confirmed} onChange={event=>setConfirmed(event.target.checked)} style={{width:'auto',marginTop:'.3rem'}} />{guide.contextLabel}</label>
  <div aria-live="polite"><p>{answer.message}</p></div>
  {answer.status==='supported'&&<><p><strong>When this helps:</strong> {guide.contextLabel}. The kit’s name and color alone cannot confirm this.</p><p><strong>Limits:</strong> {guide.limit}</p></>}
  <details><summary>Read the source and its limits</summary>
   <p>Edited category guidance from commercial manufacturer education; these sources do not validate your physical product or the digital preview. Checked 25 October 2026. No automatic refresh.</p>
   <ul>{guide.sources.map(id=>{const source=guidanceSources[id];return <li key={id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><br />{source.kind} · {source.publisher}<br />{source.sourceDate}; checked {source.checkedOn}.</li>;})}</ul>
  </details>
  <details style={{marginTop:'1rem'}}><summary>Reviews and tips: evidence available</summary><p>{reviewEvidence.message}</p><p>General technique guidance above is separate from customer experience. None of these sources is a review of an item in your kit.</p></details>
 </section>;
}
