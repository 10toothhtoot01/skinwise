import { apiKey, AnalysisError, validateImage } from './youcam.ts';
import { solvePlan, makeupEffects } from './look-planner.ts';
const BASE='https://yce-api-01.makeupar.com';
type ProviderData={files?:{file_id?:string;requests?:{url?:string;method?:string;headers?:Record<string,string>}[]}[];task_id?:string;task_status?:string;results?:unknown};
async function key(){const value=await apiKey();if(!value)throw new AnalysisError('NOT_CONFIGURED','YouCam is not configured on the server.',503);return value;}
async function request(path:string,credential:string,body?:unknown){
 let response:Response;try{response=await fetch(BASE+path,{method:body?'POST':'GET',headers:{Authorization:`Bearer ${credential}`,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{}),redirect:'manual',signal:AbortSignal.timeout(25000),cache:'no-store'});}catch{throw new AnalysisError('PROVIDER_UNAVAILABLE','YouCam did not respond. A start request may have reached it; do not automatically resubmit.',502);}
 const data=await response.json().catch(()=>null) as {status?:number;data?:ProviderData}|null;
 if(!response.ok||data?.status!==200||!data.data)throw new AnalysisError('PROVIDER_ERROR',response.status===429?'YouCam is busy. Wait before trying again.':'YouCam could not complete this request. Check the photo and available units.',response.status===429?429:502);
 return data.data;
}
export function makeupUrl(value:unknown):string|null{if(typeof value!=='string'||value.length>16000)return null;try{const u=new URL(value);return u.protocol==='https:'&&u.hostname.endsWith('.amazonaws.com')&&!u.username&&!u.password&&(!u.port||u.port==='443')?u.href:null;}catch{return null;}}
async function sign(credential:string,value:string){const k=await crypto.subtle.importKey('raw',new TextEncoder().encode(credential),{name:'HMAC',hash:'SHA-256'},false,['sign']);return [...new Uint8Array(await crypto.subtle.sign('HMAC',k,new TextEncoder().encode('makeup-v1.'+value)))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export async function startMakeup(bytes:Uint8Array,type:string,plan:unknown,recipeId:string){
 const solved=solvePlan(plan),recipe=solved.recipes.find(r=>r.id===recipeId);
 if(!recipe)throw new AnalysisError('INFEASIBLE_RECIPE','This combination does not meet the supplied kit and constraints.');
 const dimensions=validateImage(bytes,type);
 if(Math.max(dimensions.width,dimensions.height)>1024)throw new AnalysisError('IMAGE_DIMENSIONS','Use the app-prepared photo with a long side no larger than 1024 pixels.');
 const credential=await key();
 const upload=await request('/s2s/v2.0/file',credential,{files:[{content_type:type,file_name:type==='image/png'?'look.png':'look.jpg',file_size:bytes.length}]});
 const file=upload.files?.[0],destination=file?.requests?.[0];
 const url=makeupUrl(destination?.url);
 if(!url||!destination||!file||destination.method!=='PUT'||typeof file.file_id!=='string')throw new AnalysisError('PROVIDER_RESPONSE','YouCam returned an unsupported upload destination.',502);
 let sent:Response;try{sent=await fetch(url,{method:'PUT',headers:{'Content-Type':destination.headers?.['Content-Type']||type},body:new Blob([bytes as BlobPart],{type}),redirect:'manual',signal:AbortSignal.timeout(25000)});}catch{throw new AnalysisError('UPLOAD_FAILED','The photo upload did not complete.',502);}
 if(!sent.ok)throw new AnalysisError('UPLOAD_FAILED','The photo upload did not complete.',502);
 const data=await request('/s2s/v2.0/task/makeup-vto',credential,{src_file_id:file.file_id,version:'1.0',effects:makeupEffects(recipe.products)});
 if(typeof data.task_id!=='string'||!data.task_id)throw new AnalysisError('PROVIDER_RESPONSE','No preview task receipt was returned. Do not automatically resubmit.',502);
 const expires=Date.now()+24*60*60*1000;
 return {status:'running',taskId:data.task_id,token:`${expires}.${await sign(credential,`${data.task_id}.${expires}`)}`,units:1,recipe};
}
export async function pollMakeup(taskId:string,token:string){
 const credential=await key();const [expires,mac,...extra]=token.split('.');
 if(!/^[\w+\/-]{1,256}$/.test(taskId)||!/^\d{13}$/.test(expires||'')||Number(expires)<Date.now()||extra.length||!/^[a-f0-9]{64}$/.test(mac||''))throw new AnalysisError('INVALID_TASK','This preview receipt is invalid or expired.',403);
 const expected=await sign(credential,`${taskId}.${expires}`);let mismatch=0;for(let i=0;i<64;i++)mismatch|=expected.charCodeAt(i)^mac.charCodeAt(i);
 if(mismatch)throw new AnalysisError('INVALID_TASK','This preview receipt is invalid.',403);
 const task=await request(`/s2s/v2.0/task/makeup-vto/${encodeURIComponent(taskId)}`,credential);
 if(['running','queued','processing'].includes(task.task_status||''))return {status:'running'};
 if(task.task_status==='error')throw new AnalysisError('PREVIEW_FAILED','YouCam could not render this photo. Try a clear single-person portrait; no replacement is started automatically.',422);
 if(task.task_status!=='success')throw new AnalysisError('PROVIDER_RESPONSE','YouCam returned an unknown preview status.',502);
 const raw=task.results;
 const url=makeupUrl((raw as {url?:unknown})?.url)||(Array.isArray(raw)?makeupUrl(raw[0]?.download_url):null);
 if(!url)throw new AnalysisError('PROVIDER_RESPONSE','No supported provider preview image was returned.',502);
 return {status:'success',url};
}
