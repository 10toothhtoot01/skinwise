import test from 'node:test';
import assert from 'node:assert/strict';
import {frameGeometry,DEFAULT_FRAME} from '../lib/portrait-framing.ts';
test('crop retains original pixels before the single provider resize',()=>{
 const full=frameGeometry(3000,4000,DEFAULT_FRAME);
 const crop=frameGeometry(3000,4000,{...DEFAULT_FRAME,zoom:2});
 assert.deepEqual([full.preparedWidth,full.preparedHeight],[768,1024]);
 assert.deepEqual([crop.left,crop.top,crop.cropWidth,crop.cropHeight],[750,1000,1500,2000]);
 // A feature of100originalpixels occupies25.6px with full frame and51.2px with crop.
 assert.equal(crop.preparedWidth/crop.cropWidth,2*full.preparedWidth/full.cropWidth);
});
test('bounds never exceed the original at any control extreme',()=>{
 for(const w of [480,768,1200,3000])for(const h of [480,1024,1600,4000])for(const turns of [0,1,2,3])for(const zoom of [1,1.05,2,3])for(const x of [0,.5,1])for(const y of [0,.5,1]){
  const g=frameGeometry(w,h,{turns,zoom,x,y});assert.ok(g.left>=0&&g.top>=0);assert.ok(g.left+g.cropWidth<=g.rotatedWidth);assert.ok(g.top+g.cropHeight<=g.rotatedHeight);assert.ok(g.preparedWidth<=g.cropWidth&&g.preparedHeight<=g.cropHeight);assert.ok(Math.max(g.preparedWidth,g.preparedHeight)<=1024);
 }
});
test('rotation swaps dimensions; full original and small crops stay explicit',()=>{
 assert.deepEqual(frameGeometry(768,1024,{...DEFAULT_FRAME,turns:4}),frameGeometry(768,1024,DEFAULT_FRAME));
 const rotated=frameGeometry(768,1024,{...DEFAULT_FRAME,turns:1});assert.equal(rotated.preparedWidth,1024);assert.equal(rotated.preparedHeight,768);
 assert.equal(frameGeometry(768,1024,{...DEFAULT_FRAME,zoom:3}).usable,false);
});
test('rejects nonfinite settings and invalid source dimensions',()=>{
 assert.throws(()=>frameGeometry(0,100,DEFAULT_FRAME));assert.throws(()=>frameGeometry(100,100,{...DEFAULT_FRAME,zoom:NaN}));
});
