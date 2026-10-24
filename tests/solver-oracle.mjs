// Independent bit-mask subset oracle, not the production category-product expansion.
// No provider calls. Run: node --experimental-strip-types tests/solver-oracle.mjs
import assert from 'node:assert/strict';
import {solvePlan} from '../lib/look-planner.ts';
const categories=['lip_color','blush','eye_shadow'];
const kit=(counts,extreme=false)=>counts.flatMap((count,c)=>Array.from({length:count},(_,i)=>({id:`p-${c}-${i}`,name:`Owned ${c}/${i}`,category:categories[c],color:'#a44357',minutes:extreme?30:1+((c*7+i*11)%30)})));
const kits=[[],kit([9,0,0]),kit([3,3,3]),kit([7,1,1]),kit([1,1,0]),kit([3,3,3],true)];
const subsets=products=>Array.from({length:2**products.length-1},(_,i)=>{
 const chosen=products.filter((_,j)=>(i+1)&(1<<j));
 return {ids:chosen.map(p=>p.id).sort().join('|'),count:chosen.length,categoryMask:chosen.reduce((n,p)=>n|(1<<categories.indexOf(p.category)),0),minutes:chosen.reduce((n,p)=>n+p.minutes,0)};
}).filter(s=>categories.filter((_,c)=>s.categoryMask&(1<<c)).length===s.count);
const start=performance.now();let cases=0,totalFeasible=0;
for(let k=0;k<kits.length;k++){
 const products=kits[k],all=subsets(products);
 for(let req=0;req<8;req++)for(let exc=0;exc<8;exc++)for(let cap=1;cap<=3;cap++)for(let minutes=1;minutes<=60;minutes++){
  const rules={required:categories.filter((_,c)=>req&(1<<c)),excluded:categories.filter((_,c)=>exc&(1<<c)),maxProducts:cap,maxMinutes:minutes};
  const expected=all.filter(s=>s.count<=cap&&s.minutes<=minutes&&(s.categoryMask&req)===req&&(s.categoryMask&exc)===0).map(s=>s.ids).sort();
  const result=solvePlan({products,rules});
  const actual=result.recipes.map(r=>r.products.map(p=>p.id).sort().join('|')).sort();
  const context=JSON.stringify({kit:k,rules});
  assert.deepEqual(actual,expected,context);assert.equal(result.considered,all.length,context);assert(all.length<=63);
  assert.equal(result.shortlist.length,Math.min(3,expected.length),context);
  assert.equal(new Set(result.shortlist.map(r=>r.id)).size,result.shortlist.length,context);
  assert(result.shortlist.every(r=>expected.includes(r.products.map(p=>p.id).sort().join('|'))),context);
  for(const recipe of result.recipes)assert.equal(recipe.minutes,recipe.products.reduce((n,p)=>n+p.minutes,0),context);
  if(expected.length){assert.deepEqual(result.reasons,[],context);assert.equal(result.shortlist[0].minutes,Math.min(...result.recipes.map(r=>r.minutes)),context);}
  else assert(result.reasons.length>0,context);
  cases++;totalFeasible+=expected.length;
 }
}
const result={method:'Independent exhaustive bit-mask subsets vs production category expansion',kits:kits.map(products=>products.map(p=>({category:p.category,minutes:p.minutes}))),ruleCoverage:'All 8 required subsets × 8 excluded subsets × 3 product caps × 60 integer minute limits per kit',cases,totalFeasibleCombinationsCompared:totalFeasible,passed:true,elapsedSeconds:Number(((performance.now()-start)/1000).toFixed(3)),scope:'Six fixed kits, not all possible product inputs or real physical times; no provider or consumer accuracy claim',paidJobs:0};
console.log(JSON.stringify({...result,kits:result.kits.map(kit=>kit.length)},null,2));
