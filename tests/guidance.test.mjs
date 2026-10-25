import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolveGuidance,techniqueGuides,guidanceSources,reviewEvidence} from '../lib/cosmetic-guidance.ts';
const cases=JSON.parse(await readFile(new URL('./fixtures/guidance-evaluation.json',import.meta.url),'utf8'));
for(const item of cases)test(`prewritten guidance evaluation: ${item.id}`,()=>{
 const result=resolveGuidance(item.request);assert.equal(result.status,item.status);
 if(result.status==='supported'){assert(result.guide.sources.length);for(const id of result.guide.sources)assert.match(guidanceSources[id].url,/^https:\/\//);assert.equal(result.message,result.guide.action);}
 else assert(result.message.length>20);
});
test('finite corpus has traceable source metadata and no seeded social evidence',()=>{
 assert.equal(cases.length,18);assert.equal(techniqueGuides.length,3);assert.equal(reviewEvidence.count,0);assert.equal(reviewEvidence.status,'unavailable');
 for(const source of Object.values(guidanceSources)){assert(source.kind);assert(source.sourceDate);assert.equal(source.checkedOn,'2026-10-25');}
});
