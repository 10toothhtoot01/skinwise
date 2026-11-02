/** Geometry only: preserve observed pixels; never reconstruct or recolor a face. */
export type FrameSettings = {zoom:number; x:number; y:number; turns:number};
export const DEFAULT_FRAME: FrameSettings = {zoom:1,x:0.5,y:0.5,turns:0};
export function frameGeometry(width:number,height:number,settings:FrameSettings){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1)throw Error('Invalid source dimensions.');
 if(![settings.zoom,settings.x,settings.y,settings.turns].every(Number.isFinite))throw Error('Invalid framing settings.');
 const turns=((Math.round(settings.turns)%4)+4)%4;
 const rotatedWidth=turns%2?height:width,rotatedHeight=turns%2?width:height;
 const zoom=Math.max(1,Math.min(3,settings.zoom));
 const cropWidth=Math.max(1,Math.round(rotatedWidth/zoom));
 const cropHeight=Math.max(1,Math.round(rotatedHeight/zoom));
 const left=Math.max(0,Math.min(rotatedWidth-cropWidth,Math.round(settings.x*rotatedWidth-cropWidth/2)));
 const top=Math.max(0,Math.min(rotatedHeight-cropHeight,Math.round(settings.y*rotatedHeight-cropHeight/2)));
 const scale=Math.min(1,1024/Math.max(cropWidth,cropHeight));
 const preparedWidth=Math.round(cropWidth*scale),preparedHeight=Math.round(cropHeight*scale);
 return {turns,rotatedWidth,rotatedHeight,left,top,cropWidth,cropHeight,preparedWidth,preparedHeight,usable:Math.min(preparedWidth,preparedHeight)>=480};
}

/** Draw directly from decoded source into the output. Orientation is applied once by image decoding. */
export function drawFramedImage(canvas:HTMLCanvasElement,image:HTMLImageElement,frame:FrameSettings,maxSide:number){
 const g=frameGeometry(image.naturalWidth,image.naturalHeight,frame);
 const scale=Math.min(1,maxSide/Math.max(g.cropWidth,g.cropHeight));
 canvas.width=Math.round(g.cropWidth*scale);canvas.height=Math.round(g.cropHeight*scale);
 const ctx=canvas.getContext('2d');if(!ctx)throw Error('This browser cannot prepare the photo.');
 ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);
 ctx.scale(scale,scale);ctx.translate(-g.left,-g.top);
 if(g.turns===1){ctx.translate(g.rotatedWidth,0);ctx.rotate(Math.PI/2);}
 if(g.turns===2){ctx.translate(g.rotatedWidth,g.rotatedHeight);ctx.rotate(Math.PI);}
 if(g.turns===3){ctx.translate(0,g.rotatedHeight);ctx.rotate(-Math.PI/2);}
 ctx.drawImage(image,0,0);return canvas;
}
