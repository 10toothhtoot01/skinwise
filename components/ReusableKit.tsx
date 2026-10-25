'use client';
import {useEffect,useRef,useState} from 'react';
import {z} from 'zod';
import {productSchema,type Product} from '@/lib/look-planner';
const schema=z.object({version:z.literal(1),sample:z.boolean(),products:z.array(productSchema).max(9)}).superRefine((v,ctx)=>{if(new Set(v.products.map(p=>p.id)).size!==v.products.length)ctx.addIssue({code:'custom',message:'Duplicate items'});});
export default function ReusableKit({products,sample,onRestore}:{products:Product[];sample:boolean;onRestore:(products:Product[],sample:boolean)=>void}){
 const [message,setMessage]=useState('');const readTicket=useRef(0);
 useEffect(()=>()=>{readTicket.current++;},[]);
 function save(){const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,sample,products},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='my-owned-kit.json';a.click();URL.revokeObjectURL(url);}
 async function restore(file?:File){if(!file)return;const ticket=++readTicket.current;try{if(file.size>50000)throw Error();const data=schema.safeParse(JSON.parse(await file.text()));if(ticket!==readTicket.current)return;if(!data.success)throw Error();if(!window.confirm('Replace the kit with this file? Current choices and comparisons will reset; existing portrait task receipts stay available for compatible effects.'))return;onRestore(data.data.products,data.data.sample);setMessage('Kit restored. No portrait, preview or private task receipt was imported.');}catch{if(ticket===readTicket.current)setMessage('This is not a valid kit file. Your current kit was kept.');}}
 return <details className="planner-kit-file"><summary>Keep your kit for another visit</summary><p>Save just your product names, approximate colors, estimates and fictional-data label. This separate file has no portrait, task receipt or chosen plan. Keep it somewhere you trust; restore it in a later session.</p><button disabled={!products.length} onClick={save}>Save kit file</button><label>Restore kit file<input type="file" accept="application/json,.json" onChange={e=>{void restore(e.target.files?.[0]);e.target.value='';}}/></label>{message&&<p role="status">{message}</p>}</details>;
}
