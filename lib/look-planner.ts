import { z } from 'zod';
export const categories = ['lip_color','blush','eye_shadow'] as const;
export type Category = typeof categories[number];
export const categoryLabels:Record<Category,string> = {lip_color:'Lip color',blush:'Blush',eye_shadow:'Eye shadow'};
export const productSchema = z.object({id:z.string().regex(/^[a-zA-Z0-9-]{1,40}$/),name:z.string().trim().min(1).max(80),category:z.enum(categories),color:z.string().regex(/^#[0-9a-fA-F]{6}$/),minutes:z.number().int().min(1).max(30)});
export const rulesSchema = z.object({maxMinutes:z.number().int().min(1).max(60),maxProducts:z.number().int().min(1).max(3),required:z.array(z.enum(categories)).max(3),excluded:z.array(z.enum(categories)).max(3)});
export const planSchema = z.object({products:z.array(productSchema).max(9),rules:rulesSchema}).superRefine((p,ctx)=>{if(new Set(p.products.map(p=>p.id)).size!==p.products.length)ctx.addIssue({code:'custom',message:'Each owned product needs a unique identity.'});});
export type Product=z.infer<typeof productSchema>;
export type Rules=z.infer<typeof rulesSchema>;
export type Recipe={id:string;products:Product[];minutes:number;key:string};
export function solvePlan(input:unknown){
 const {products,rules}=planSchema.parse(input);
 let choices:Product[][]=[[]];
 for(const category of categories)choices=choices.flatMap(choice=>[choice,...products.filter(p=>p.category===category).map(p=>[...choice,p])]);
 const nonempty=choices.filter(choice=>choice.length);
 const recipes:Recipe[]=nonempty.filter(choice=>choice.length<=rules.maxProducts&&choice.reduce((n,p)=>n+p.minutes,0)<=rules.maxMinutes&&rules.required.every(c=>choice.some(p=>p.category===c))&&!choice.some(p=>rules.excluded.includes(p.category))).map(choice=>({id:choice.map(p=>p.id).join('+'),products:choice,minutes:choice.reduce((n,p)=>n+p.minutes,0),key:JSON.stringify({products:choice,rules})})).sort((a,b)=>a.minutes-b.minutes||a.id.localeCompare(b.id));
 const reasons:string[]=[];
 for(const c of rules.required){if(rules.excluded.includes(c))reasons.push(`${categoryLabels[c]} is both required and excluded.`);else if(!products.some(p=>p.category===c))reasons.push(`No owned ${categoryLabels[c].toLowerCase()} is recorded.`);}
 if(!recipes.length&&!reasons.length){const eligible=nonempty.filter(choice=>rules.required.every(c=>choice.some(p=>p.category===c))&&!choice.some(p=>rules.excluded.includes(p.category)));
  const minCount=Math.min(...eligible.map(c=>c.length));
  const withinCount=eligible.filter(c=>c.length<=rules.maxProducts);
  if(minCount>rules.maxProducts&&Number.isFinite(minCount))reasons.push(`The required categories need at least ${minCount} products; your limit is ${rules.maxProducts}.`);
  else if(withinCount.length)reasons.push(`The quickest eligible combination needs ${Math.min(...withinCount.map(c=>c.reduce((n,p)=>n+p.minutes,0)))} minutes by your estimates; your limit is ${rules.maxMinutes}.`);
  else reasons.push('No permitted owned products remain. Add an owned item or change an exclusion.');
 }
 // Farthest-first selection is structural variety, not an inferred beauty or suitability score.
 const shortlist:Recipe[]=[];const remaining=[...recipes];
 while(shortlist.length<3&&remaining.length){let best=0;if(shortlist.length){let distance=-1;for(let i=0;i<remaining.length;i++){const d=Math.min(...shortlist.map(s=>categories.reduce((n,c)=>n+Number(s.products.find(p=>p.category===c)?.id!==remaining[i].products.find(p=>p.category===c)?.id),0)));if(d>distance){distance=d;best=i;}}}shortlist.push(remaining.splice(best,1)[0]);}
 return {recipes,shortlist,reasons,considered:nonempty.length};
}
export function makeupEffects(products:Product[]){return [{category:'skin_smooth',skinSmoothStrength:0,skinSmoothColorIntensity:0},...products.map(p=>p.category==='lip_color'?{category:p.category,shape:{name:'original'},morphology:{fullness:0,wrinkless:0},palettes:[{color:p.color,texture:'matte',colorIntensity:50}],style:{type:'full'}}:{category:p.category,pattern:{name:'1color1'},palettes:[{color:p.color,texture:'matte',colorIntensity:50}]})];}
export type Comparison={a:string;b:string;choice:'a'|'b'|'tie'|'neither'};
export function preferenceState(ids:string[],comparisons:Comparison[]){
 const valid=comparisons.filter(c=>ids.includes(c.a)&&ids.includes(c.b)&&c.a!==c.b);
 const rejected=new Set(valid.filter(c=>c.choice==='neither').flatMap(c=>[c.a,c.b]));
 const active=ids.filter(id=>!rejected.has(id));
 const edges=valid.filter(c=>c.choice==='a'||c.choice==='b').map(c=>c.choice==='a'?[c.a,c.b]:[c.b,c.a]).filter(e=>active.includes(e[0])&&active.includes(e[1]));
 const reaches=(from:string,to:string,seen=new Set<string>()):boolean=>{if(seen.has(from))return false;seen.add(from);return edges.some(([a,b])=>a===from&&(b===to||reaches(b,to,seen)));};
 const cycle=active.some(id=>reaches(id,id));
 // Do not infer unasked comparisons from transitivity: preferences may be contextual.
 const remaining: [string,string][]=[];for(let i=0;i<active.length;i++)for(let j=i+1;j<active.length;j++)if(!valid.some(c=>(c.a===active[i]&&c.b===active[j])||(c.b===active[i]&&c.a===active[j])))remaining.push([active[i],active[j]]);
 const participation=(id:string)=>valid.filter(c=>c.a===id||c.b===id).length;
 remaining.sort((a,b)=>participation(a[0])+participation(a[1])-participation(b[0])-participation(b[1]));
 const leaders=cycle?[]:active.filter(id=>!edges.some(([,loser])=>loser===id));
 return {cycle,active,rejected:[...rejected],next:remaining[0]||null,leaders,complete:!remaining.length};
}
