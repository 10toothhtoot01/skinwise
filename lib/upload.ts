import { AnalysisError } from './youcam.ts';
export async function boundedForm(request: Request) {
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
