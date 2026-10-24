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
