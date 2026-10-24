import { AnalysisError, pollAnalysis, startAnalysis } from '@/lib/youcam';
const responseHeaders = { 'Cache-Control':'no-store' };
function failure(error: unknown) {
  if (error instanceof AnalysisError) return Response.json({error:error.message,code:error.code},{status:error.status,headers:responseHeaders});
  return Response.json({error:'The request could not be processed. Please try again.',code:'REQUEST_FAILED'},{status:500,headers:responseHeaders});
}
async function boundedForm(request: Request) {
  const reader = request.body?.getReader();
  if (!reader) throw new AnalysisError('INVALID_UPLOAD','Choose a photo to upload.');
  const chunks: Uint8Array[] = []; let size = 0;
  for (;;) {
    const {done,value} = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 9 * 1024 * 1024) { await reader.cancel(); throw new AnalysisError('INVALID_UPLOAD','Choose a photo smaller than 8 MB.',413); }
    chunks.push(value);
  }
  try {
    return await new Response(new Blob(chunks as BlobPart[]),{headers:{'Content-Type':request.headers.get('content-type') || ''}}).formData();
  } catch { throw new AnalysisError('INVALID_UPLOAD','The photo upload was incomplete. Please try again.'); }
}
export async function POST(request: Request) {
  try {
    const origin = request.headers.get('origin');
    if (origin && origin !== new URL(request.url).origin) throw new AnalysisError('INVALID_ORIGIN','Please start analysis from this app.',403);
    if (!request.headers.get('content-type')?.startsWith('multipart/form-data')) throw new AnalysisError('INVALID_UPLOAD','Upload a photo using the analysis form.');
    const length = Number(request.headers.get('content-length'));
    if (Number.isFinite(length) && length > 9 * 1024 * 1024) throw new AnalysisError('INVALID_UPLOAD','Choose a photo smaller than 8 MB.',413);
    const form = await boundedForm(request); const file = form.get('file');
    if (!file || typeof file === 'string' || !('arrayBuffer' in file)) throw new AnalysisError('INVALID_UPLOAD','Choose a JPEG or PNG photo.');
    if (file.size > 8 * 1024 * 1024) throw new AnalysisError('INVALID_UPLOAD','Choose a photo smaller than 8 MB.',413);
    return Response.json(await startAnalysis(new Uint8Array(await file.arrayBuffer()),file.type),{status:202,headers:responseHeaders});
  } catch(error) { return failure(error); }
}
export async function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    return Response.json(await pollAnalysis(params.get('taskId') || '',params.get('token') || ''),{headers:responseHeaders});
  } catch(error) { return failure(error); }
}
