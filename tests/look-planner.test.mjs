import test from 'node:test';
import assert from 'node:assert/strict';
import {solvePlan,makeupEffects,preferenceState} from '../lib/look-planner.ts';
import {startMakeup,pollMakeup} from '../lib/makeup.ts';
const p=(id,category,minutes=3)=>({id,name:id,category,color:'#a44357',minutes});
const products=[p('rose','lip_color',3),p('coral','lip_color',2),p('cheek','blush',4),p('eye','eye_shadow',5)];
const rules={maxMinutes:7,maxProducts:2,required:['lip_color'],excluded:['eye_shadow']};
test('solver enforces owned kit, one product per step, hard constraints, exact estimates',()=>{
 const {recipes,shortlist}=solvePlan({products,rules});assert.equal(recipes.length,4);
 for(const r of recipes){assert(r.products.length<=2);assert(r.minutes<=7);assert(r.products.some(p=>p.category==='lip_color'));assert(!r.products.some(p=>p.category==='eye_shadow'));assert.equal(new Set(r.products.map(p=>p.category)).size,r.products.length);assert(r.products.every(p=>products.some(owned=>owned.id===p.id)));}
 assert.equal(shortlist.length,3);assert.equal(new Set(shortlist.map(r=>r.id)).size,3);assert.equal(shortlist[0].id,'coral');
 assert.deepEqual(solvePlan({products:products.toReversed(),rules}).shortlist.map(r=>r.id),shortlist.map(r=>r.id));
});
test('infeasibility explains conflicts, missing kit, count and time without invented products',()=>{
 assert.match(solvePlan({products,rules:{...rules,excluded:['lip_color']}}).reasons.join(' '),/both required and excluded/);
 assert.match(solvePlan({products:[],rules}).reasons.join(' '),/No owned lip color/);
 assert.match(solvePlan({products,rules:{...rules,maxMinutes:1}}).reasons.join(' '),/needs 2 minutes/);
 assert.match(solvePlan({products,rules:{...rules,required:['lip_color','blush'],maxProducts:1}}).reasons.join(' '),/at least 2 products/);
 assert.equal(solvePlan({products:[],rules:{...rules,required:[]}}).recipes.length,0);
 assert.throws(()=>solvePlan({products:[products[0],products[0]],rules}));
});
test('effects use only selected products and explicitly disable smoothing/morphology',()=>{
 const effects=makeupEffects([products[0],products[2]]);assert.deepEqual(effects[0],{category:'skin_smooth',skinSmoothStrength:0,skinSmoothColorIntensity:0});assert.equal(effects.length,3);assert.equal(effects[1].palettes[0].color,products[0].color);assert.deepEqual(effects[1].morphology,{fullness:0,wrinkless:0});assert.equal(effects[2].pattern.name,'1color1');
});
test('preference graph preserves ties, reject-both, unobserved pairs and cycles',()=>{
 const ids=['a','b','c'];let state=preferenceState(ids,[{a:'a',b:'b',choice:'a'},{a:'b',b:'c',choice:'a'}]);assert.deepEqual(state.next,['a','c']);assert.equal(state.cycle,false);
 state=preferenceState(ids,[{a:'a',b:'b',choice:'a'},{a:'b',b:'c',choice:'a'},{a:'c',b:'a',choice:'a'}]);assert.equal(state.cycle,true);assert.deepEqual(state.leaders,[]);assert.equal(state.complete,true);
 state=preferenceState(['a','b'],[{a:'a',b:'b',choice:'tie'}]);assert.deepEqual(state.leaders,['a','b']);assert.equal(state.complete,true);
 state=preferenceState(ids,[{a:'a',b:'b',choice:'neither'}]);assert.deepEqual(state.active,['c']);assert.deepEqual(state.rejected,['a','b']);assert.equal(state.next,null);
});
function png(){const bytes=new Uint8Array(32);bytes.set([137,80,78,71,13,10,26,10]);const v=new DataView(bytes.buffer);v.setUint32(16,768);v.setUint32(20,1024);return bytes;}
test('server recomputes feasible recipe before network or key use',async()=>{let called=false;const original=globalThis.fetch;globalThis.fetch=async()=>{called=true;throw new Error('must not call');};try{await assert.rejects(startMakeup(png(),'image/png',{products,rules},'eye'),{code:'INFEASIBLE_RECIPE'});assert.equal(called,false);}finally{globalThis.fetch=original;}});
test('protocol, no key on byte PUT, signed receipt, GET-only recovery',async()=>{
 const original=globalThis.fetch,old=process.env.YOUCAM_API_KEY;process.env.YOUCAM_API_KEY='test-only';const calls=[];
 globalThis.fetch=async(url,init)=>{calls.push({url:String(url),init});if(String(url).includes('amazonaws'))return new Response('',{status:200});return Response.json({status:200,data:String(url).endsWith('/file')?{files:[{file_id:'photo',requests:[{url:'https://test.s3.amazonaws.com/input',method:'PUT'}]}]}:String(url).endsWith('/makeup-vto')?{task_id:'look-task'}:{task_status:'success',results:{url:'https://test.s3.amazonaws.com/result.jpg'}}});};
 try{const task=await startMakeup(png(),'image/png',{products,rules},'rose');assert.equal(task.units,1);const body=JSON.parse(calls[2].init.body);assert.equal(body.src_file_id,'photo');assert.equal(body.effects[0].skinSmoothStrength,0);assert.equal(calls[1].init.headers.Authorization,undefined);const result=await pollMakeup(task.taskId,task.token);assert.equal(result.status,'success');assert.equal(calls.at(-1).init.method,'GET');const before=calls.length;await assert.rejects(pollMakeup(task.taskId,task.token.slice(0,-1)+'x'),{code:'INVALID_TASK'});assert.equal(calls.length,before);}
 finally{globalThis.fetch=original;if(old===undefined)delete process.env.YOUCAM_API_KEY;else process.env.YOUCAM_API_KEY=old;}
});
