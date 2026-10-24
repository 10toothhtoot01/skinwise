import test from 'node:test';
import assert from 'node:assert/strict';
import { ACTIONS, AnalysisError, normalizeResult, normalizeVisuals, pollAnalysis, startAnalysis, validateImage } from '../lib/youcam.ts';
function png(width=1080,height=1440) {const bytes=new Uint8Array(32);bytes.set([137,80,78,71,13,10,26,10]);const view=new DataView(bytes.buffer);view.setUint32(16,width);view.setUint32(20,height);return bytes;}
test('rejects spoofed MIME types and invalid dimensions',()=>{
 assert.throws(()=>validateImage(new Uint8Array(100),'image/jpeg'),AnalysisError);
 assert.throws(()=>validateImage(png(),'image/jpeg'),AnalysisError);
 assert.throws(()=>validateImage(png(100,100),'image/png'),AnalysisError);
 assert.throws(()=>validateImage(png(4097,1080),'image/png'),AnalysisError);
 assert.doesNotThrow(()=>validateImage(png(),'image/png'));
});
test('normalizes only real supported scores; higher is better',()=>{
 const result=normalizeResult('task',{output:[{type:'moisture',ui_score:90},{type:'pore',ui_score:35},{type:'acne',ui_score:70},{type:'texture',raw_score:80},{type:'redness',ui_score:300}]});
 assert.deepEqual(result.metrics.map(m=>m.score),[90,35,70]);assert.deepEqual(result.concerns,[],'unrelated metric scales must not create priorities');assert.deepEqual(result.method,{provider:'youcam',endpointVersion:'2.1',tier:'SD',scoreKind:'ui_score',modelVersion:null});assert.equal(result.metrics[0].label,'Moisture estimate');assert.equal(result.source,'youcam');
 assert.throws(()=>normalizeResult('bad',{output:[{type:'pore',raw_score:20}]}),AnalysisError);
});
test('upload, task creation and signed polling follow official protocol',async()=>{
 const original=globalThis.fetch,oldKey=process.env.YOUCAM_API_KEY;process.env.YOUCAM_API_KEY='test-only';const calls=[];
 globalThis.fetch=async(url,init)=>{calls.push({url:String(url),init});const data=String(url).endsWith('/file')?{files:[{file_id:'file-test',requests:[{url:'https://test.s3.amazonaws.com/selfie',method:'PUT',headers:{'Content-Type':'image/png'}}]}]}:String(url).endsWith('/task/skin-analysis')?{task_id:'task-123'}:{task_status:'success',results:{output:ACTIONS.map(type=>({type,ui_score:75}))}};return Response.json({status:200,data});};
 try {const task=await startAnalysis(png(),'image/png');assert.equal(task.units,12);assert.equal(calls.length,3);assert.equal(calls[1].init.headers.Authorization,undefined);assert.ok(calls.every(call=>call.init.redirect==='manual'),'Workers-compatible redirect handling must never forward credentials to a redirect');assert.deepEqual(JSON.parse(calls[2].init.body).dst_actions,ACTIONS);const result=await pollAnalysis(task.taskId,task.token);assert.equal(result.result.metrics.length,6);const count=calls.length;await assert.rejects(pollAnalysis(task.taskId,task.token.slice(0,-1)+'x'),{code:'INVALID_TASK'});assert.equal(calls.length,count);}
 finally {globalThis.fetch=original;if(oldKey===undefined)delete process.env.YOUCAM_API_KEY;else process.env.YOUCAM_API_KEY=oldKey;}
});
test('no credential means no synthetic result or upstream request',async()=>{const oldKey=process.env.YOUCAM_API_KEY;delete process.env.YOUCAM_API_KEY;try{await assert.rejects(startAnalysis(png(),'image/png'),{code:'NOT_CONFIGURED',status:503});}finally{if(oldKey!==undefined)process.env.YOUCAM_API_KEY=oldKey;}});
test('rejects unexpected storage destination before upload',async()=>{const original=globalThis.fetch,oldKey=process.env.YOUCAM_API_KEY;process.env.YOUCAM_API_KEY='test-only';let count=0;globalThis.fetch=async()=>{count++;return Response.json({status:200,data:{files:[{file_id:'x',requests:[{url:'https://example.com/upload',method:'PUT'}]}]}});};try{await assert.rejects(startAnalysis(png(),'image/png'),{code:'PROVIDER_RESPONSE'});assert.equal(count,1);globalThis.fetch=async()=>Response.json({error:'private details'},{status:401});await assert.rejects(startAnalysis(png(),'image/png'),{code:'PROVIDER_AUTH'});}finally{globalThis.fetch=original;if(oldKey===undefined)delete process.env.YOUCAM_API_KEY;else process.env.YOUCAM_API_KEY=oldKey;}});

const visibleHD={profile:'visible',tier:'HD'};
test('preserves actual HD regions without inventing scores or mixing tiers',()=>{
 const result=normalizeResult('hd',{output:[
  {type:'hd_pore',region:'whole',ui_score:80},{type:'hd_pore',region:'nose',ui_score:60},
  {type:'hd_pore',region:'forehead',ui_score:70},{type:'hd_pore',region:'cheek',raw_score:30},
  {type:'hd_texture',region:'whole',ui_score:0},{type:'hd_redness',ui_score:NaN},
  {type:'hd_acne',ui_score:Infinity},{type:'pore',region:'nose',ui_score:99},
  {type:'resize_image',mask_urls:['https://test.s3.amazonaws.com/original.jpg']}
 ]},visibleHD);
 assert.deepEqual(result.metrics.map(m=>[m.key,m.score]),[['pore',80],['texture',0]]);
 assert.deepEqual(result.regions.map(r=>[r.key,r.region,r.score]),[['pore','nose',60],['pore','forehead',70]]);
 assert.equal(result.method.tier,'HD'); assert.equal(JSON.stringify(result).includes('amazonaws'),false);
 const regionalOnly=normalizeResult('regional',{output:[{type:'hd_pore',region:'nose',ui_score:50}]},visibleHD);
 assert.equal(regionalOnly.metrics.length,0);assert.equal(regionalOnly.regions.length,1);
});
test('visuals contain only actual HTTPS AWS image URLs and distinguish overlays from legacy masks',()=>{
 const good='https://test.s3.amazonaws.com/pore.jpg';
 const results={output:[{type:'hd_pore',region:'nose',mask_urls:[good,'https://example.com/no.jpg','http://test.s3.amazonaws.com/no.jpg','https://test.s3.amazonaws.com.evil.test/no.jpg','https://user:password@test.s3.amazonaws.com/no.jpg','https://test.s3.amazonaws.com:444/no.jpg',null]},
 {type:'resize_image',mask_urls:['https://test.s3.amazonaws.com/original.jpg']},{type:'unknown',mask_urls:[good]},
 {type:'hd_texture',mask_urls:[]},{type:'hd_acne',mask_urls:null}]};
 const visual=normalizeVisuals(results,visibleHD);
 assert.equal(visual.items.length,1);assert.deepEqual(visual.items[0],{key:'pore',region:'nose',url:good,kind:'overlay'});
 assert.equal(visual.originalUrl,'https://test.s3.amazonaws.com/original.jpg');assert.equal(visual.availability,'temporary');
 assert.equal(normalizeVisuals({output:[{type:'pore',mask_urls:[good]}]}).items[0].kind,'mask');
 assert.deepEqual(normalizeVisuals({output:[]},visibleHD).items,[]);
});
test('visible profile selects dimension-specific actions/cost and signs tier against tampering',async()=>{
 const original=globalThis.fetch,oldKey=process.env.YOUCAM_API_KEY;process.env.YOUCAM_API_KEY='test-only';const calls=[];
 let currentTier='HD';
 globalThis.fetch=async(url,init)=>{calls.push({url:String(url),init});const data=String(url).endsWith('/file')?{files:[{file_id:'file-test',requests:[{url:'https://test.s3.amazonaws.com/selfie',method:'PUT'}]}]}:String(url).endsWith('/task/skin-analysis')?{task_id:'task-visible'}:{task_status:'success',results:{output:[{type:currentTier==='HD'?'hd_pore':'pore',region:'nose',ui_score:65,mask_urls:['https://test.s3.amazonaws.com/mask.jpg']}]}};return Response.json({status:200,data});};
 try {
  const hd=await startAnalysis(png(1080,1920),'image/png',{profile:'visible'});
  assert.equal(hd.units,12);assert.equal(hd.method.tier,'HD');assert.equal(hd.token.split('.').length,3);
  const body=JSON.parse(calls[2].init.body);assert.deepEqual(body.dst_actions,['hd_pore','hd_redness','hd_texture','hd_acne']);assert.deepEqual(body.miniserver_args,{enable_mask_overlay:true});assert.equal(body.pf_camera_kit,undefined);
  const result=await pollAnalysis(hd.taskId,hd.token);assert.equal(result.result.method.tier,'HD');assert.equal(result.result.regions[0].region,'nose');assert.equal(result.visuals.items[0].kind,'overlay');
  const parts=hd.token.split('.');parts[1]=Buffer.from(JSON.stringify({profile:'visible',tier:'SD'})).toString('base64url');
  const before=calls.length;await assert.rejects(pollAnalysis(hd.taskId,parts.join('.')),{code:'INVALID_TASK'});assert.equal(calls.length,before);
  currentTier='SD';const sd=await startAnalysis(png(1079,1920),'image/png',{profile:'visible'});
  assert.equal(sd.units,9);assert.equal(sd.method.tier,'SD');assert.deepEqual(sd.actions,['pore','redness','texture','acne']);
  assert.equal((await pollAnalysis(sd.taskId,sd.token)).result.method.tier,'SD');
  await assert.rejects(pollAnalysis(sd.taskId,sd.token+'.extra'),{code:'INVALID_TASK'});
 } finally {globalThis.fetch=original;if(oldKey===undefined)delete process.env.YOUCAM_API_KEY;else process.env.YOUCAM_API_KEY=oldKey;}
});
