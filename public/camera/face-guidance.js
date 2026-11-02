/* Local, uncalibrated acquisition heuristics. These never certify image accuracy. */
/* eslint-env worker */
(function (scope) {
  function assess(detections, width, height, pixels, previous) {
    const warnings = [];
    const first = detections[0];
    if (!first) return {faceCount: 0, warnings: ['No face detected. Face the camera in even light, or inspect the photo yourself.'], bounds: null, metrics: null};
    if (detections.length > 1) warnings.push('More than one face detected. Keep only your face in the portrait.');
    const b = first.boundingBox;
    if (!b || !width || !height) return {faceCount: detections.length, warnings: ['Face framing could not be estimated. Inspect the full portrait yourself.'], bounds: null, metrics: null};
    const bounds = {x: b.originX / width, y: b.originY / height, width: b.width / width, height: b.height / height};
    const score = first.categories?.[0]?.score;
    if (!Number.isFinite(score) || score < 0.7) warnings.push('Face detection is uncertain. These positioning hints may be wrong.');
    if (bounds.width < 0.22 || bounds.height < 0.22) warnings.push('Your face may be too small. Move closer while keeping your whole face visible.');
    if (bounds.x < 0.02 || bounds.y < 0.02 || bounds.x + bounds.width > 0.98 || bounds.y + bounds.height > 0.98) warnings.push('Your face may be cut off. Leave space around your face.');
    if (Math.abs(bounds.x + bounds.width / 2 - 0.5) > 0.16 || Math.abs(bounds.y + bounds.height / 2 - 0.5) > 0.2) warnings.push('Move your face nearer the center of the frame.');
    const points = first.keypoints || [];
    if (points.length >= 3) {
      const [left, right, nose] = points;
      const dx = Math.abs(right.x-left.x), dy = Math.abs(right.y-left.y);
      if (dx > 0 && dy / dx > 0.22) warnings.push('Your head may be tilted. Try keeping your eyes level.');
      if (dx > 0 && Math.abs(nose.x-(left.x+right.x)/2)/dx > 0.23) warnings.push('You may be turned sideways. Face the camera directly.');
    }
    if (previous && Math.hypot(bounds.x-previous.x,bounds.y-previous.y) > 0.055) warnings.push('Framing changed between checks. Hold still before capturing.');
    let metrics = null;
    if (pixels && pixels.length === 64*64*4) {
      const gray = new Float32Array(64*64); let dark=0,bright=0,left=0,right=0;
      for(let i=0;i<gray.length;i++){const v=.2126*pixels[i*4]+.7152*pixels[i*4+1]+.0722*pixels[i*4+2];gray[i]=v;dark+=v<20?1:0;bright+=v>245?1:0;if(i%64<32)left+=v;else right+=v;}
      let sum=0,sq=0,n=0;
      for(let y=1;y<63;y++)for(let x=1;x<63;x++){const i=y*64+x;const lap=gray[i-1]+gray[i+1]+gray[i-64]+gray[i+64]-4*gray[i];sum+=lap;sq+=lap*lap;n++;}
      metrics={edgeVariance:sq/n-(sum/n)**2,darkFraction:dark/4096,brightFraction:bright/4096,sideDifference:Math.abs(left-right)/2048};
      if(metrics.edgeVariance<25)warnings.push('Face detail may be soft. Hold still and inspect eyes and lips for blur.');
      if(metrics.darkFraction>.4)warnings.push('Much of the detected face region is very dark. Try more even light.');
      if(metrics.brightFraction>.25)warnings.push('Highlights may be clipped on the face. Move away from harsh direct light.');
      if(metrics.sideDifference>45)warnings.push('Lighting across the detected face may be uneven. Try facing a soft light source.');
    }
    return {faceCount: detections.length, bounds, warnings, metrics};
  }
  scope.SkinwiseFaceGuidance = {assess};
})(globalThis);
