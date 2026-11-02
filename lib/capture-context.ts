import { z } from 'zod';

export const guidedEvidenceSchema = z.object({
  source:z.literal('youcam-camera-kit'), sdkVersion:z.literal('2.5'), preset:z.literal('moderate'),
  checks:z.object({hasFace:z.boolean(),position:z.string(),frontal:z.string(),lighting:z.string()}),
});
export const captureContextSchema = z.object({
  workflow:z.enum(['upload','guided']), width:z.number().int().positive(), height:z.number().int().positive(),
  setupLabel:z.string().max(80), lighting:z.enum(['daylight','indoor','mixed','unknown']),
  camera:z.enum(['front','rear','unknown']), unfiltered:z.enum(['yes','no','unknown']),
  guided:guidedEvidenceSchema.nullable(),
  preparation:z.object({originalWidth:z.number().int().positive(),originalHeight:z.number().int().positive(),inputBytes:z.number().int().nonnegative(),outputBytes:z.number().int().nonnegative(),inputType:z.string(),outputType:z.string(),resized:z.boolean(),orientationNormalized:z.boolean(),crop:z.object({left:z.number().int().nonnegative(),top:z.number().int().nonnegative(),width:z.number().int().positive(),height:z.number().int().positive()}).nullable(),encoding:z.enum(['original','lossless-png','jpeg-0.95'])}).optional(),
});
export type CaptureContext = z.infer<typeof captureContextSchema>;
export type GuidedEvidence = z.infer<typeof guidedEvidenceSchema>;
/** File constraints are vendor requirements, not a claim of visual or clinical quality. */
export async function inspectPhoto(file:File):Promise<{width:number;height:number}> {
  if (!['image/jpeg','image/png'].includes(file.type)) throw new Error('Choose a JPEG or PNG photo.');
  if (file.size > 8*1024*1024) throw new Error('Choose a photo smaller than 8 MB.');
  const url=URL.createObjectURL(file);
  try {
    const img=new Image(); img.src=url; await img.decode();
    const width=img.naturalWidth,height=img.naturalHeight;
    if (Math.min(width,height)<480) throw new Error('This image does not meet the 480-pixel minimum on its short side. Try the original photo or another camera. Enlarging it will not restore detail.');
    if (Math.max(width,height)>4096) throw new Error('This image is larger than 4096 pixels on its long side. Export a smaller copy; do not apply filters or sharpening.');
    return {width,height};
  } catch(error) {
    if(error instanceof Error && (error.message.startsWith('This image'))) throw error;
    throw new Error('This image could not be decoded. Try the original JPEG or PNG photo.');
  } finally {URL.revokeObjectURL(url);}
}
/** These are capture comparability checks only, never proof of biological change. */
export function comparisonLimit(first?:CaptureContext,last?:CaptureContext):string|null {
  if(!first || !last) return 'Capture context is missing for one or both photos. Lighting, camera and filters may differ.';
  if(first.unfiltered!=='yes' || last.unfiltered!=='yes') return 'Filter-free capture was not confirmed for both photos. Smoothing or other processing may change the estimates.';
  if(!first.setupLabel.trim() || !last.setupLabel.trim() || first.lighting==='unknown' || last.lighting==='unknown' || first.camera==='unknown' || last.camera==='unknown') return 'The capture setup is incomplete. Matching photo conditions have not been established.';
  if(first.setupLabel.trim().toLowerCase()!==last.setupLabel.trim().toLowerCase() || first.lighting!==last.lighting || first.camera!==last.camera) return 'The recorded camera or lighting setup changed. Do not interpret the score difference as skin improvement.';
  const signature=(value:CaptureContext)=>JSON.stringify(value.preparation?{width:value.width,height:value.height,source:[value.preparation.originalWidth,value.preparation.originalHeight],crop:value.preparation.crop,resized:value.preparation.resized,orientation:value.preparation.orientationNormalized,encoding:value.preparation.encoding}:null);
  if(signature(first)!==signature(last)) return 'Photo preparation or framing differs, or was not recorded for both photos. This can change the appearance estimates.';
  return null;
}
