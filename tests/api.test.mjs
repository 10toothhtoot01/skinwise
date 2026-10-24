import test from 'node:test';
import assert from 'node:assert/strict';
import { ACTIONS, AnalysisError, normalizeResult, pollAnalysis, startAnalysis, validateImage } from '../lib/youcam.ts';
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
