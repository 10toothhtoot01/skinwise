import {z} from 'zod';
import {categoryLabels,productSchema,rulesSchema,solvePlan} from './look-planner.ts';

export const SAVED_LOOKS_KEY='skinwise-private-saved-looks-v1';
export const SAVED_LOOKS_LIMIT=30;
export const savedLookNameSchema=z.string().trim().min(1).max(80);
const choiceFields={products:z.array(productSchema.strict()).max(3),rules:rulesSchema.strict(),event:z.string().max(120),sample:z.boolean(),original:z.boolean(),basis:z.enum(['constraints-only','loaded-preview','original','not-recorded'])};
function validChoice(choice:z.infer<z.ZodObject<typeof choiceFields>>,ctx:z.RefinementCtx){
 if(choice.original){if(choice.products.length||choice.basis!=='original')ctx.addIssue({code:'custom',message:'No-added-makeup snapshots must have no selected products and an original selection basis.'});return;}
 if(choice.basis==='original'||!choice.products.length){ctx.addIssue({code:'custom',message:'A product look needs explicitly selected products.'});return;}
 if(new Set(choice.products.map(p=>p.id)).size!==choice.products.length||new Set(choice.products.map(p=>p.category)).size!==choice.products.length){ctx.addIssue({code:'custom',message:'A selected look needs unique products and categories.'});return;}
 if(!solvePlan(choice).recipes.some(r=>r.products.length===choice.products.length))ctx.addIssue({code:'custom',message:'Selected products must satisfy the saved limits.'});
}
export const savedLookChoiceSchema=z.object(choiceFields).strict().superRefine(validChoice);
export const savedLookSchema=z.object({...choiceFields,id:z.string().uuid(),name:savedLookNameSchema,savedAt:z.string().datetime()}).strict().superRefine(validChoice);
export const savedLooksSchema=z.object({version:z.literal(1),looks:z.array(savedLookSchema).max(SAVED_LOOKS_LIMIT)}).strict().superRefine(({looks},ctx)=>{if(new Set(looks.map(l=>l.id)).size!==looks.length)ctx.addIssue({code:'custom',message:'Saved looks need unique identities.'});});
export type SavedLookChoice=z.infer<typeof savedLookChoiceSchema>;
export type SavedLook=z.infer<typeof savedLookSchema>;
export type SavedLooksStorage=Pick<Storage,'getItem'|'setItem'|'removeItem'>;
export type SavedLooksRead={looks:SavedLook[];raw:string|null;blocked:boolean;error:string};
export function newestSavedLooks(looks:SavedLook[]){return [...looks].sort((a,b)=>b.savedAt.localeCompare(a.savedAt)||a.id.localeCompare(b.id));}
export function createSavedLook(choice:SavedLookChoice,name:string,id:string,savedAt:string):SavedLook{
 // Project only the public snapshot fields; parent planner models can contain private receipts.
 return savedLookSchema.parse({products:choice.products.map(p=>({id:p.id,name:p.name,category:p.category,color:p.color,minutes:p.minutes})),rules:{maxMinutes:choice.rules.maxMinutes,maxProducts:choice.rules.maxProducts,required:[...choice.rules.required],excluded:[...choice.rules.excluded]},event:choice.event,sample:choice.sample,original:choice.original,basis:choice.basis,id,name,savedAt});
}
export function readSavedLooks(storage:SavedLooksStorage):SavedLooksRead{
 let raw:string|null=null;
 try{raw=storage.getItem(SAVED_LOOKS_KEY);}catch{return {looks:[],raw,blocked:true,error:'This browser could not read saved looks. Enable browser storage, then reload the library.'};}
 if(raw===null)return {looks:[],raw,blocked:false,error:''};
 try{return {looks:newestSavedLooks(savedLooksSchema.parse(JSON.parse(raw)).looks),raw,blocked:false,error:''};}
 catch{return {looks:[],raw,blocked:true,error:'Saved looks could not be read. Original bytes are preserved. Export them before deliberately clearing this library.'};}
}
export function writeSavedLooks(storage:SavedLooksStorage,looks:SavedLook[],expectedRaw:string|null):string{
 const data=JSON.stringify(savedLooksSchema.parse({version:1,looks:newestSavedLooks(looks)}));
 if(storage.getItem(SAVED_LOOKS_KEY)!==expectedRaw)throw new Error('Saved looks changed in another tab. Export the displayed library, then reload it before editing.');
 storage.setItem(SAVED_LOOKS_KEY,data);
 if(storage.getItem(SAVED_LOOKS_KEY)!==data)throw new Error('The saved change could not be verified. Browser storage may differ from this list. Export the displayed library, then reload it.');
 return data;
}
export function clearUnreadableSavedLooks(storage:SavedLooksStorage,expectedRaw:string|null){
 if(storage.getItem(SAVED_LOOKS_KEY)!==expectedRaw)throw new Error('Saved looks changed. Reload the library before clearing unreadable data.');
 storage.removeItem(SAVED_LOOKS_KEY);
 if(storage.getItem(SAVED_LOOKS_KEY)!==null)throw new Error('Clearing saved looks could not be verified. Reload the library to inspect browser storage.');
}
export function savedLookReuse(look:SavedLook){
 const snapshot=savedLookSchema.parse(look);
 if(snapshot.original)return {products:snapshot.products,rules:snapshot.rules,event:snapshot.event,sample:snapshot.sample,selected:'original',selectionBasis:'original' as const};
 const recipe=solvePlan(snapshot).recipes.find(r=>r.products.length===snapshot.products.length);
 if(!recipe)throw new Error('This saved look no longer satisfies the planner constraints.');
 return {products:snapshot.products,rules:snapshot.rules,event:snapshot.event,sample:snapshot.sample,selected:recipe.key,selectionBasis:'constraints-only' as const};
}
export function savedLookBasis(look:SavedLookChoice){return look.original?'No added makeup chosen; required product steps do not apply.':look.basis==='loaded-preview'?'Historically chosen from a loaded illustrative preview; the preview is not stored.':look.basis==='constraints-only'?'Chosen from entered products and limits, without requiring a preview.':'Historical selection basis was not recorded.';}
export function savedLookText(look:SavedLook){
 return ['Skinwise · '+look.name,look.sample?'FICTIONAL KIT · demonstration only':'User-entered owned products',`Saved: ${look.savedAt}`,`Occasion: ${look.event||'Not stated'}`,savedLookBasis(look),look.original?'No added makeup':look.products.map(p=>`${p.name} — ${categoryLabels[p.category]} — ${p.color} (approximate) — ${p.minutes} estimated min`).join('\n'),`Total: ${look.products.reduce((n,p)=>n+p.minutes,0)} estimated min; ${look.rules.maxMinutes} min available; maximum ${look.rules.maxProducts} products.`,`Required: ${look.rules.required.map(c=>categoryLabels[c]).join(', ')||'None'}`,`Excluded: ${look.rules.excluded.map(c=>categoryLabels[c]).join(', ')||'None'}`,'User-entered estimates and approximate colors. No application order, exact product match, physical shade, comfort, wear or outcome is established. No portrait or preview is stored.'].join('\n\n')+'\n';
}
