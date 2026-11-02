import test from 'node:test';
import assert from 'node:assert/strict';
import { comparisonLimit } from '../lib/capture-context.ts';
const setup = (changes={}) => ({workflow:'upload',width:960,height:960,setupLabel:'Phone by window',lighting:'daylight',camera:'front',unfiltered:'yes',guided:null,...changes});

test('missing context remains unknown, not comparable by assumption',()=>{
  assert.match(comparisonLimit(undefined,setup()),/missing/);
  assert.match(comparisonLimit(setup(),undefined),/missing/);
  assert.match(comparisonLimit(),/missing/);
});
test('unconfirmed or processed photos preserve filter warning',()=>{
  for(const value of ['no','unknown']) {
    assert.match(comparisonLimit(setup({unfiltered:value}),setup()),/Filter-free capture was not confirmed/);
    assert.match(comparisonLimit(setup(),setup({unfiltered:value})),/Filter-free capture was not confirmed/);
  }
});
test('unknown self reported camera/light/label prevents matching assertion',()=>{
  for(const value of [{camera:'unknown'},{lighting:'unknown'},{setupLabel:'  '}])
    assert.match(comparisonLimit(setup(value),setup()),/incomplete/);
});
test('changed device label, camera or lighting explicitly warns',()=>{
  for(const value of [{camera:'rear'},{lighting:'indoor'},{setupLabel:'Different tablet'}])
    assert.match(comparisonLimit(setup(value),setup()),/setup changed/);
});
test('matching self reported setup returns no setup mismatch; dimensions not invented quality thresholds',()=>{
  assert.equal(comparisonLimit(setup(),setup()),null);
  assert.equal(comparisonLimit(setup({setupLabel:'  PHONE BY WINDOW '}),setup()),null);
  assert.equal(comparisonLimit(setup(),setup({width:480,height:640})),null);
});

const preparation = {originalWidth:6000,originalHeight:4000,inputBytes:123456,outputBytes:45678,inputType:'image/jpeg',outputType:'image/png',resized:true,orientationNormalized:false,crop:null,encoding:'lossless-png'};
test('changed or missing preparation warns before interpreting a score difference',()=>{
  const first=setup({width:4096,height:2731,preparation});
  assert.match(comparisonLimit(first,setup()),/Photo preparation or framing differs/);
  assert.match(comparisonLimit(first,setup({width:4096,height:2731,preparation:{...preparation,crop:{left:0,top:0,width:4000,height:4000}}})),/Photo preparation or framing differs/);
  assert.match(comparisonLimit(first,setup({width:4096,height:2731,preparation:{...preparation,encoding:'jpeg-0.95'}})),/Photo preparation or framing differs/);
});
test('encoding byte count alone does not invent a changed capture setup',()=>{
 const first=setup({width:4096,height:2731,preparation});
 assert.equal(comparisonLimit(first,setup({width:4096,height:2731,preparation:{...preparation,inputBytes:222222,outputBytes:777777}})),null);
});
