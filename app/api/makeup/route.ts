import { startMakeup,pollMakeup } from '@/lib/makeup';
import { AnalysisError } from '@/lib/youcam';
import { boundedForm } from '@/lib/upload';
const headers={'Cache-Control':'no-store'};
function failure(error:unknown){if(error instanceof AnalysisError)return Response.json({error:error.message,code:error.code},{status:error.status,headers});return Response.json({error:'The preview request is invalid or could not be completed.',code:'REQUEST_FAILED'},{status:400,headers});}
export async function POST(request:Request){try{
 const origin=request.headers.get('origin');if(origin&&origin!==new URL(request.url).origin)throw new AnalysisError('INVALID_ORIGIN','Start previews from this app.',403);
 if(!request.headers.get('content-type')?.startsWith('multipart/form-data'))throw new AnalysisError('INVALID_UPLOAD','Use the preview form.');
 const form=await boundedForm(request),file=form.get('file'),plan=form.get('plan'),recipeId=form.get('recipeId');
 if(!file||typeof file==='string'||!('arrayBuffer'in file)||typeof plan!=='string'||plan.length>12000||typeof recipeId!=='string')throw new AnalysisError('INVALID_UPLOAD','Choose a portrait and a feasible combination.');
 return Response.json(await startMakeup(new Uint8Array(await file.arrayBuffer()),file.type,JSON.parse(plan),recipeId),{status:202,headers});
 }catch(error){return failure(error);}}
export async function GET(request:Request){try{const p=new URL(request.url).searchParams;return Response.json(await pollMakeup(p.get('taskId')||'',p.get('token')||''),{headers});}catch(error){return failure(error);}}
