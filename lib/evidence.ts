import { z } from 'zod';
export const focusOptions = [
  {key:'pore',label:'Pore appearance',question:'Where is pore visibility being marked?'},
  {key:'redness',label:'Redness appearance',question:'Which areas are marked for redness?'},
  {key:'texture',label:'Texture appearance',question:'Where is uneven texture being marked?'},
  {key:'acne',label:'Blemish appearance',question:'Where are blemish-like areas being marked?'},
] as const;
export type Focus = typeof focusOptions[number]['key'];
export const focusSchema = z.enum(['pore','redness','texture','acne']);
export const regionSchema=z.object({key:z.string(),label:z.string(),region:z.string(),score:z.number().finite().min(0).max(100)});
const vendorUrl=z.string().url().refine(value=>{try{const u=new URL(value);return u.protocol==='https:' && u.hostname.endsWith('.amazonaws.com');}catch{return false;}},'Unsupported image destination');
export const visualsSchema=z.object({originalUrl:vendorUrl.optional(),items:z.array(z.object({key:z.string(),region:z.string(),url:vendorUrl,kind:z.enum(['overlay','mask'])})).max(100)});
export type Visuals=z.infer<typeof visualsSchema>;
export const reviewSchema=z.object({focus:focusSchema,region:z.string().max(100).optional(),match:z.enum(['yes','no','unsure']),note:z.string().max(600)});
export type EvidenceReview=z.infer<typeof reviewSchema>;
