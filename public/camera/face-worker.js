/* eslint-disable no-restricted-globals */
/* global importScripts, OffscreenCanvas */
// Classic worker is required by the pinned MediaPipe WASM loader's importScripts.
self.exports = {};
importScripts('/camera/vendor/vision_bundle.js', '/camera/face-guidance.js');
let detector;
let loading;
let previous;
async function initialize() {
  if (!loading) loading = (async () => {
    const {FilesetResolver, FaceDetector} = self.exports;
    const vision = await FilesetResolver.forVisionTasks('/camera/vendor');
    detector = await FaceDetector.createFromOptions(vision, {
      baseOptions: {modelAssetPath:'/camera/vendor/blaze_face_short_range.tflite', delegate:'CPU'},
      runningMode:'IMAGE', minDetectionConfidence:0.5,
      canvas:new OffscreenCanvas(1,1),
    });
  })();
  return loading;
}
self.onmessage = async ({data}) => {
  const {id, bitmap} = data;
  try {
    await initialize();
    if (!bitmap) {self.postMessage({id, ready:true});return;}
    const start=performance.now();
    const frame=new OffscreenCanvas(bitmap.width,bitmap.height);
    const frameContext=frame.getContext('2d', {willReadFrequently:true});
    frameContext.drawImage(bitmap,0,0);
    const result=detector.detect(frameContext.getImageData(0,0,bitmap.width,bitmap.height));
    const bounds=result.detections[0]?.boundingBox;
    let pixels;
    if(bounds){
      const x=Math.max(0,bounds.originX),y=Math.max(0,bounds.originY);
      const w=Math.min(bitmap.width,bounds.originX+bounds.width)-x,h=Math.min(bitmap.height,bounds.originY+bounds.height)-y;
      if(w>0&&h>0){const canvas=new OffscreenCanvas(64,64);const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.drawImage(bitmap,x,y,w,h,0,0,64,64);pixels=ctx.getImageData(0,0,64,64).data;}
    }
    const guidance=self.SkinwiseFaceGuidance.assess(result.detections,bitmap.width,bitmap.height,pixels,previous);
    previous=guidance.bounds;
    self.postMessage({id,...guidance,elapsedMs:performance.now()-start});
  } catch (error) {
    console.warn("Local face guidance failed:", error instanceof Error ? error.message : "Unknown model failure");
    self.postMessage({id,error:'Local face guidance is unavailable. You can still capture and inspect the photo yourself.'});
  } finally {bitmap?.close();}
};
