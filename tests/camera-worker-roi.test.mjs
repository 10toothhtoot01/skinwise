import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../public/camera/face-worker.js',import.meta.url),'utf8');
async function cropFor(box){
  const draws=[];let closed=false;
  const scope={console,performance,OffscreenCanvas:class{constructor(w,h){this.width=w;this.height=h;}getContext(){return{drawImage:(...args)=>draws.push(args.slice(1)),getImageData:()=>({data:new Uint8ClampedArray(64*64*4)})};}}};
  scope.self=scope;scope.importScripts=()=>{scope.exports.FilesetResolver={forVisionTasks:async()=>({})};scope.exports.FaceDetector={createFromOptions:async()=>({detect:()=>({detections:[{boundingBox:box}]})})};scope.SkinwiseFaceGuidance={assess:()=>({bounds:null,warnings:[]})};};scope.postMessage=()=>{};
  vm.runInNewContext(source,scope);
  await scope.onmessage({data:{id:1,bitmap:{width:640,height:480,close:()=>{closed=true;}}}});
  assert.equal(closed,true);return draws.filter(args=>args.length===8);
}
test('face pixel crop intersects negative-origin bounds instead of including extra background',async()=>{assert.deepEqual(await cropFor({originX:-10,originY:-20,width:100,height:120}),[[0,0,90,100,0,0,64,64]]);});
test('face pixel crop intersects right/bottom edges and excludes fully outside regions',async()=>{assert.deepEqual(await cropFor({originX:600,originY:450,width:100,height:100}),[[600,450,40,30,0,0,64,64]]);assert.deepEqual(await cropFor({originX:-100,originY:-100,width:50,height:50}),[]);});
