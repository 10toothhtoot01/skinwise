import test from 'node:test';
import assert from 'node:assert/strict';
import {SAVED_LOOKS_KEY,SAVED_LOOKS_LIMIT,clearUnreadableSavedLooks,createSavedLook,newestSavedLooks,readSavedLooks,savedLookChoiceSchema,savedLookReuse,savedLookSchema,savedLooksSchema,savedLookText,writeSavedLooks} from '../lib/saved-looks.ts';

const product={id:'rose',name:'Entered rose',category:'lip_color',color:'#a44357',minutes:3};
const rules={maxMinutes:10,maxProducts:2,required:['lip_color'],excluded:['eye_shadow']};
const choice={products:[product],rules,event:'Friday dinner',sample:false,original:false,basis:'loaded-preview'};
const id=n=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const look=(n=1,patch={})=>createSavedLook({...choice,...patch},`Look ${n}`,id(n),`2026-11-${String(n%28+1).padStart(2,'0')}T10:20:30.000Z`);
function memory(raw=null){let value=raw;return {getItem(key){assert.equal(key,SAVED_LOOKS_KEY);return value;},setItem(key,next){assert.equal(key,SAVED_LOOKS_KEY);value=next;},removeItem(key){assert.equal(key,SAVED_LOOKS_KEY);value=null;}};}

test('snapshot retains exact selected fields and deep-copies products and rules',()=>{
 const input=structuredClone(choice);
 const snapshot=createSavedLook(input,'  Dinner look  ',id(1),'2026-11-02T10:20:30.000Z');
 assert.equal(snapshot.name,'Dinner look');assert.deepEqual(snapshot.products,input.products);assert.deepEqual(snapshot.rules,input.rules);assert.equal(snapshot.event,input.event);assert.equal(snapshot.basis,'loaded-preview');assert.equal(snapshot.savedAt,'2026-11-02T10:20:30.000Z');
 input.products[0].name='Changed active kit';input.products[0].color='#000000';input.rules.required.length=0;
 assert.equal(snapshot.products[0].name,'Entered rose');assert.equal(snapshot.products[0].color,'#a44357');assert.deepEqual(snapshot.rules.required,['lip_color']);
});

test('snapshot projects only safe fields even when passed a larger planner object',()=>{
 const unsafe={...choice,portrait:'data:image/png;base64,private',url:'https://private.invalid',token:'private-receipt',tasks:[{token:'receipt'}],key:'server-key',sourceHash:'portrait-fingerprint',products:[{...product,receipt:'product-secret'}],rules:{...rules,key:'private-rule'}};
 const snapshot=createSavedLook(unsafe,'Safe look',id(1),'2026-11-02T10:20:30.000Z');
 assert.deepEqual(Object.keys(snapshot).sort(),['basis','event','id','name','original','products','rules','sample','savedAt']);
 for(const secret of ['private','receipt','portrait','fingerprint','server-key'])assert(!JSON.stringify(snapshot).includes(secret));
 assert.equal(savedLookSchema.safeParse({...snapshot,token:'private'}).success,false);
});

test('versioned persistence is exact and newest-first without removing entries',()=>{
 const store=memory();const a=look(1),b=look(2);const raw=writeSavedLooks(store,[a,b],null);
 assert.deepEqual(JSON.parse(raw),{version:1,looks:[b,a]});
 assert.deepEqual(readSavedLooks(store),{looks:[b,a],raw,blocked:false,error:''});
 assert.deepEqual(readSavedLooks(memory()).looks,[]);
 assert.deepEqual(newestSavedLooks([a,b]),[b,a]);
});

test('30-entry capacity accepts the last slot and rejects the next without writing',()=>{
 const store=memory();const entries=Array.from({length:SAVED_LOOKS_LIMIT},(_,i)=>look(i+1));
 const raw=writeSavedLooks(store,entries,null);assert.equal(readSavedLooks(store).looks.length,30);
 assert.throws(()=>writeSavedLooks(store,[...entries,look(31)],raw));assert.equal(store.getItem(SAVED_LOOKS_KEY),raw);
});

test('unreadable JSON, versions, nested products and duplicate IDs preserve original bytes',()=>{
 const valid=look();for(const raw of [' { not json \n',JSON.stringify({version:2,looks:[]}),JSON.stringify({version:1,looks:[{...valid,products:[{...product,color:'bad'}]}]}),JSON.stringify({version:1,looks:[valid,valid]}),JSON.stringify({version:1,looks:[{...valid,taskId:'private'}]})]){
  const store=memory(raw);const loaded=readSavedLooks(store);assert.equal(loaded.blocked,true);assert.equal(loaded.raw,raw);assert.deepEqual(loaded.looks,[]);assert.equal(store.getItem(SAVED_LOOKS_KEY),raw);
 }
});

test('failed reads, writes and readback are reported without a false success',()=>{
 const original=JSON.stringify({version:1,looks:[look()]});
 const readBlocked={getItem(){throw Error('storage disabled');}};assert.equal(readSavedLooks(readBlocked).blocked,true);assert.equal(readSavedLooks(readBlocked).raw,null);
 const writeBlocked={getItem(){return original;},setItem(){throw Error('quota');}};assert.throws(()=>writeSavedLooks(writeBlocked,[look(2)],original),/quota/);assert.equal(writeBlocked.getItem(),original);
 const ignored=memory(original);ignored.setItem=()=>{};assert.throws(()=>writeSavedLooks(ignored,[look(2)],original),/could not be verified/);
 let applied=original;let written=false;const failedReadback={getItem(){if(written)throw Error('readback blocked');return applied;},setItem(key,value){applied=value;written=true;}};assert.throws(()=>writeSavedLooks(failedReadback,[look(2)],original),/readback blocked/);assert.deepEqual(JSON.parse(applied).looks,[look(2)]);
});

test('stale displayed libraries cannot overwrite a change from another tab',()=>{
 const current=JSON.stringify({version:1,looks:[look(2)]});const store=memory(current);
 assert.throws(()=>writeSavedLooks(store,[look(1)],null),/changed in another tab/);assert.equal(store.getItem(SAVED_LOOKS_KEY),current);
 assert.throws(()=>clearUnreadableSavedLooks(store,'older unreadable bytes'),/changed/);assert.equal(store.getItem(SAVED_LOOKS_KEY),current);
});

test('deliberate unreadable-library clearing checks removal and leaves other storage keys untouched',()=>{
 const store=memory('corrupt');clearUnreadableSavedLooks(store,'corrupt');assert.equal(store.getItem(SAVED_LOOKS_KEY),null);
 const ignored=memory('corrupt');ignored.removeItem=()=>{};assert.throws(()=>clearUnreadableSavedLooks(ignored,'corrupt'),/could not be verified/);
});

test('rename changes only name; deletion preserves every other immutable entry',()=>{
 const a=look(),b=look(2);const store=memory();let raw=writeSavedLooks(store,[a,b],null);
 raw=writeSavedLooks(store,[{...a,name:'Renamed'},b],raw);const renamed=readSavedLooks(store).looks.find(l=>l.id===a.id);assert.deepEqual(renamed,{...a,name:'Renamed'});assert.deepEqual(readSavedLooks(store).looks.find(l=>l.id===b.id),b);
 writeSavedLooks(store,[b],raw);assert.deepEqual(readSavedLooks(store).looks,[b]);
});

test('names, IDs, dates and chosen feasibility are validated at every storage boundary',()=>{
 assert.equal(createSavedLook(choice,'x'.repeat(80),id(1),'2026-11-02T10:20:30.000Z').name.length,80);
 for(const name of ['','   ','x'.repeat(81)])assert.throws(()=>createSavedLook(choice,name,id(1),'2026-11-02T10:20:30.000Z'));
 assert.equal(savedLookSchema.safeParse({...look(),id:'not-unique-id'}).success,false);assert.equal(savedLookSchema.safeParse({...look(),savedAt:'yesterday'}).success,false);
 for(const bad of [{products:[]},{products:[product,product]},{products:[product,{...product,id:'second'}]},{rules:{...rules,maxMinutes:2}},{rules:{...rules,excluded:['lip_color']}},{basis:'original'}])assert.equal(savedLookChoiceSchema.safeParse({...choice,...bad}).success,false);
 assert.equal(savedLooksSchema.safeParse({version:1,looks:[],token:'private'}).success,false);
});

test('loaded-preview reuse re-solves exact snapshots as a fresh free choice with zero network',()=>{
 const historical=look();const original=globalThis.fetch;let calls=0;globalThis.fetch=()=>{calls++;throw Error('must not fetch');};
 try{const fresh=savedLookReuse(historical);assert.equal(fresh.selectionBasis,'constraints-only');assert.equal(JSON.parse(fresh.selected).products[0].color,product.color);assert.deepEqual(fresh.products,historical.products);assert.deepEqual(fresh.rules,historical.rules);assert.equal(fresh.event,historical.event);assert.equal(historical.basis,'loaded-preview');assert(!('tasks' in fresh));assert(!('sourceHash' in fresh));fresh.products[0].name='Active edit';assert.equal(historical.products[0].name,product.name);assert.equal(calls,0);}finally{globalThis.fetch=original;}
});

test('fictional snapshots keep sample status and original choices retain the explicit opt-out',()=>{
 const fictional=look(1,{sample:true});assert.equal(savedLookReuse(fictional).sample,true);assert.match(savedLookText(fictional),/FICTIONAL KIT/);
 const original=look(2,{original:true,products:[],basis:'original'});const fresh=savedLookReuse(original);assert.deepEqual(fresh,{products:[],rules,event:'Friday dinner',sample:false,selected:'original',selectionBasis:'original'});assert.match(savedLookText(original),/required product steps do not apply/);
 assert.equal(savedLookSchema.safeParse({...original,products:[product]}).success,false);
});

test('download text includes exact color, context, historical basis and constraints without image metadata',()=>{
 const text=savedLookText(look());for(const expected of ['Entered rose','#a44357','Friday dinner','loaded illustrative preview','3 estimated min','10 min available','maximum 2 products','Required: Lip color','Excluded: Eye shadow','2026-11-02T10:20:30.000Z'])assert(text.includes(expected),expected);
 for(const field of ['data:image','https://','taskId','token','sourceHash'])assert(!text.includes(field));
});
