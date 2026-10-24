/** Protocol: Perfect Corp Skin Analysis v2.1; see docs/API.md. Server imports only. */
const BASE = 'https://yce-api-01.makeupar.com';
export const ACTIONS = ['moisture', 'texture', 'pore', 'redness', 'acne', 'oiliness'] as const;
const LABELS: Record<string, string> = { moisture: 'Moisture estimate', texture: 'Texture appearance', pore: 'Pore appearance', redness: 'Redness appearance', acne: 'Blemish appearance', oiliness: 'Oiliness estimate' };
export type AnalysisResult = { id: string; date: string; source: 'youcam'; metrics: { key: string; label: string; score: number }[]; concerns: string[]; method: {provider:'youcam';endpointVersion:'2.1';tier:'SD';scoreKind:'ui_score';modelVersion:null} };
export class AnalysisError extends Error {
  public code: string;
  public status: number;
  constructor(code: string, message: string, status = 400) {
    super(message); this.code = code; this.status = status;
  }
}
export async function apiKey() {
  try {
    const { env } = await import('cloudflare:workers');
    const value = (env as unknown as Record<string, unknown>).YOUCAM_API_KEY;
    if (typeof value === 'string' && value.trim()) return value.trim();
  } catch { /* Standard Node runtime uses process.env below. */ }
  return process.env.YOUCAM_API_KEY?.trim() || '';
}
async function configuredKey() {
  const key = await apiKey();
  if (!key) throw new AnalysisError('NOT_CONFIGURED', 'Live analysis needs a YouCam API key on the server. You can explore the sample report meanwhile.', 503);
  return key;
}
export function validateImage(bytes: Uint8Array, type: string) {
  if (bytes.length < 24 || bytes.length > 8 * 1024 * 1024) throw new AnalysisError('INVALID_IMAGE', 'Choose a JPEG or PNG image smaller than 8 MB.');
  const png = [137,80,78,71,13,10,26,10].every((v,i) => bytes[i] === v);
  const jpg = bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255;
  if (!((png && type === 'image/png') || (jpg && type === 'image/jpeg'))) throw new AnalysisError('INVALID_IMAGE', 'Choose a valid JPEG or PNG photo.');
  let width = 0, height = 0;
  if (png) {
    const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    width = view.getUint32(16); height = view.getUint32(20);
  } else {
    for (let i = 2; i + 8 < bytes.length;) {
      if (bytes[i] !== 255) break;
      const marker = bytes[i+1];
      if (marker === 0xd9 || marker === 0xda) break;
      const length = (bytes[i+2] << 8) + bytes[i+3];
      if (length < 2 || i + 2 + length > bytes.length) break;
      if ([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker)) {
        height = (bytes[i+5] << 8) + bytes[i+6]; width = (bytes[i+7] << 8) + bytes[i+8]; break;
      }
      i += 2 + length;
    }
  }
  if (!width || !height) throw new AnalysisError('INVALID_IMAGE', 'The photo could not be read. Export it as a fresh JPEG or PNG.');
  if (Math.min(width,height) < 480 || Math.max(width,height) > 4096) throw new AnalysisError('IMAGE_DIMENSIONS', 'Use a photo with a short side of at least 480 pixels and a long side no larger than 4096 pixels.');
}
type ProviderData = { files?: {file_id?: string; requests?: {url?:string; method?:string; headers?:Record<string,string>}[]}[]; task_id?:string; task_status?:string; results?:unknown };
async function request(path: string, key: string, body?: object): Promise<ProviderData> {
  let response: Response;
  try {
    response = await fetch(BASE + path, { method: body ? 'POST' : 'GET', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, ...(body ? { body: JSON.stringify(body) } : {}), signal: AbortSignal.timeout(20_000), redirect: 'manual', cache: 'no-store' });
  } catch { throw new AnalysisError('PROVIDER_UNAVAILABLE', 'The analysis service did not respond. Please try again later.', 502); }
  const data = await response.json().catch(() => null) as {status?:number;data?:ProviderData} | null;
  if (!response.ok || !data || data.status !== 200) {
    if (response.status === 401 || response.status === 403) throw new AnalysisError('PROVIDER_AUTH', 'The server API key was rejected. The project owner needs to check its YouCam configuration.', 503);
    if (response.status === 429) throw new AnalysisError('PROVIDER_BUSY', 'The analysis service is busy. Wait a minute before trying again.', 429);
    throw new AnalysisError('PROVIDER_ERROR', 'YouCam could not process this request. Check the photo quality and available API units.', 502);
  }
  if (!data.data) throw new AnalysisError('PROVIDER_RESPONSE', 'The analysis service returned incomplete data.',502);
  return data.data;
}
async function signature(key: string, value: string) {
  const signingKey = await crypto.subtle.importKey('raw', new TextEncoder().encode(key), {name:'HMAC',hash:'SHA-256'}, false, ['sign']);
  const signed = new Uint8Array(await crypto.subtle.sign('HMAC', signingKey, new TextEncoder().encode(value)));
  return Array.from(signed, b => b.toString(16).padStart(2,'0')).join('');
}
async function issueReceipt(key: string, taskId: string) {
  const expires = Date.now() + 24*60*60*1000;
  return `${expires}.${await signature(key, `${taskId}.${expires}`)}`;
}
async function checkReceipt(key: string, taskId: string, token: string) {
  const [expires,mac] = token.split('.');
  if (!/^\d{13}$/.test(expires || '') || Number(expires) < Date.now() || !/^[a-f0-9]{64}$/.test(mac || '')) throw new AnalysisError('INVALID_TASK', 'This analysis session has expired. Start a new analysis.', 403);
  const expected = await signature(key, `${taskId}.${expires}`);
  let mismatch = 0; for (let i = 0; i < expected.length; i++) mismatch |= expected.charCodeAt(i) ^ mac.charCodeAt(i);
  if (mismatch) throw new AnalysisError('INVALID_TASK', 'This analysis session is invalid.', 403);
}
export async function startAnalysis(bytes: Uint8Array, type: string) {
  const key = await configuredKey(); validateImage(bytes,type);
  const metadata = await request('/s2s/v2.0/file', key, { files: [{ content_type: type, file_name: type === 'image/png' ? 'selfie.png' : 'selfie.jpg', file_size: bytes.length }] });
  const file = metadata?.files?.[0]; const upload = file?.requests?.[0];
  let url: URL; try { url = new URL(upload?.url || ''); } catch { throw new AnalysisError('PROVIDER_RESPONSE', 'The upload service returned an invalid response.',502); }
  if (url.protocol !== 'https:' || !url.hostname.endsWith('.amazonaws.com') || upload?.method !== 'PUT' || typeof file?.file_id !== 'string') throw new AnalysisError('PROVIDER_RESPONSE', 'The upload service returned an unsupported destination.',502);
  let uploaded: Response;
  try { uploaded = await fetch(url, { method: 'PUT', headers: { 'Content-Type': upload.headers?.['Content-Type'] || type }, body: new Blob([bytes as BlobPart],{type}), signal: AbortSignal.timeout(25_000), redirect:'manual' }); }
  catch { throw new AnalysisError('UPLOAD_FAILED','The photo upload failed. Please try again.',502); }
  if (!uploaded.ok) throw new AnalysisError('UPLOAD_FAILED','The photo upload failed. Please try again.',502);
  const task = await request('/s2s/v2.1/task/skin-analysis',key,{ src_file_id:file.file_id, dst_actions:ACTIONS, format:'json', miniserver_args:{enable_mask_overlay:false} });
  if (typeof task?.task_id !== 'string' || !task.task_id) throw new AnalysisError('PROVIDER_RESPONSE','The analysis service returned no task identifier.',502);
  return { status:'running' as const, taskId:task.task_id, token:await issueReceipt(key,task.task_id), pollingInterval:10_000, units:12 };
}
export function normalizeResult(taskId: string, results: unknown): AnalysisResult {
  const output = (results as {output?:unknown})?.output;
  if (!Array.isArray(output)) throw new AnalysisError('PROVIDER_RESPONSE','YouCam returned an unreadable result. Please contact the project owner.',502);
  const metrics: AnalysisResult['metrics'] = [];
  for (const action of ACTIONS) {
    const item = output.find(x => x && x.type === action && (!x.region || x.region === 'whole'));
    if (!item || typeof item.ui_score !== 'number' || !Number.isFinite(item.ui_score) || item.ui_score < 0 || item.ui_score > 100) continue;
    metrics.push({ key:action, label:LABELS[action], score:item.ui_score });
  }
  if (!metrics.length) throw new AnalysisError('PROVIDER_RESPONSE','No supported skin scores were returned. Please try a clearer, front-facing photo.',502);
  return { id:taskId,date:new Date().toISOString(),source:'youcam',metrics,concerns:[],method:{provider:'youcam',endpointVersion:'2.1',tier:'SD',scoreKind:'ui_score',modelVersion:null} };
}
export async function pollAnalysis(taskId: string, token: string) {
  const key = await configuredKey();
  if (!taskId || taskId.length > 256 || !/^[\w+\/-]+$/.test(taskId)) throw new AnalysisError('INVALID_TASK','Invalid analysis session.',400);
  await checkReceipt(key,taskId,token);
  const task = await request(`/s2s/v2.1/task/skin-analysis/${encodeURIComponent(taskId)}`,key);
  if (task?.task_status === 'running') return {status:'running' as const};
  if (task?.task_status === 'error') throw new AnalysisError('ANALYSIS_FAILED','The photo could not be analyzed. Retake a single-person, front-facing photo in even lighting.',422);
  if (task?.task_status !== 'success') throw new AnalysisError('PROVIDER_RESPONSE','The analysis service returned an unknown task status.',502);
  return {status:'success' as const,result:normalizeResult(taskId,task.results)};
}
