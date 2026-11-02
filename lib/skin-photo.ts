/** Faithful skin-photo preparation: geometry/encoding only, never reconstructed skin detail. */
export type SkinCrop={left:number;top:number;width:number;height:number};
export type SkinPreparation={originalWidth:number;originalHeight:number;inputBytes:number;outputBytes:number;inputType:string;outputType:string;resized:boolean;orientationNormalized:boolean;crop:SkinCrop|null;encoding:'original'|'lossless-png'|'jpeg-0.95'};
export type PreparedSkinPhoto={file:File;width:number;height:number;preparation:SkinPreparation};
const MAX_FILE=8*1024*1024;
const MIME=['image/jpeg','image/png','image/webp','image/avif','image/heic','image/heif'];
export function skinPhotoGeometry(width:number,height:number,crop?:SkinCrop){
 if(!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1)throw Error('This image has no readable dimensions.');
 const area=crop??{left:0,top:0,width,height};
 if(!Object.values(area).every(Number.isInteger)||area.left<0||area.top<0||area.width<1||area.height<1||area.left+area.width>width||area.top+area.height>height)throw Error('The selected crop is outside the original photo.');
 const scale=Math.min(1,4096/Math.max(area.width,area.height));
 const preparedWidth=Math.round(area.width*scale),preparedHeight=Math.round(area.height*scale);
 return {crop:area,width:preparedWidth,height:preparedHeight,resized:scale<1,usable:Math.min(preparedWidth,preparedHeight)>=480};
}
function jpegOrientation(bytes:Uint8Array){
 try{const data=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);let p=2;
  while(p+4<bytes.length&&bytes[p]===255){const marker=bytes[p+1],length=data.getUint16(p+2);if(length<2||p+2+length>bytes.length)break;
   if(marker===225&&data.getUint32(p+4)===0x45786966){const t=p+10,little=data.getUint16(t)===0x4949;if(data.getUint16(t+2,little)!==42)break;const ifd=t+data.getUint32(t+4,little),count=data.getUint16(ifd,little);for(let i=0;i<count;i++){const at=ifd+2+12*i;if(data.getUint16(at,little)===274){const orientation=data.getUint16(at+8,little);return orientation>=1&&orientation<=8?orientation:1;}}}
   p+=2+length;
  }
 }catch{/* Invalid metadata never prevents decoding the actual image. */}return 1;
}
export async function decodeSkinPhoto(file:File):Promise<{image:HTMLImageElement;release:()=>void;orientation:number;signature:'image/jpeg'|'image/png'|'other'}>{
 const extension=/\.(jpe?g|png|webp|avif|hei[cf])$/i.test(file.name);
 if(!MIME.includes(file.type)&&!(file.type===''&&extension))throw Error('Choose a still JPEG, PNG, WebP, AVIF or HEIC/HEIF photo.');
 if(file.size>25*1024*1024)throw Error('This original is over 25 MB. Export a smaller original photo without beauty filters.');
 const bytes=new Uint8Array(await file.slice(0,128*1024).arrayBuffer());
 const signature=bytes[0]===255&&bytes[1]===216?'image/jpeg':bytes[0]===137&&bytes[1]===80&&bytes[2]===78&&bytes[3]===71?'image/png':'other';
 const orientation=signature==='image/jpeg'?jpegOrientation(bytes):1;
 const url=URL.createObjectURL(file),image=new Image();image.src=url;
 try{await image.decode();if(image.naturalWidth*image.naturalHeight>64_000_000)throw Error('This original exceeds 64 megapixels. Export a smaller original to fit this device’s memory.');return{image,release:()=>URL.revokeObjectURL(url),orientation,signature};}
 catch(error){URL.revokeObjectURL(url);if(error instanceof Error&&error.message.startsWith('This original'))throw error;throw Error(/hei[cf]/i.test(file.type+file.name)?'This browser cannot decode this HEIC/HEIF photo. In Photos, save or export it as JPEG (Most Compatible), then choose that copy.':'This image could not be decoded. Export the original as JPEG or PNG without beauty filters.');}
}
export async function prepareSkinPhoto(file:File,crop?:SkinCrop):Promise<PreparedSkinPhoto>{
 const decoded=await decodeSkinPhoto(file);
 try{
  const image=decoded.image,width=image.naturalWidth,height=image.naturalHeight;
  const g=skinPhotoGeometry(width,height,crop);
  if(!g.usable)throw Error(Math.min(width,height)<480?'This image does not meet the 480-pixel minimum on its short side. Choose the larger original; enlarging or adding borders would not restore face detail.':'This wide photo needs framing before it fits the analysis limits. Use “Frame original photo” below to keep your whole face and remove extra background.');
  const preparation:SkinPreparation={originalWidth:width,originalHeight:height,inputBytes:file.size,outputBytes:file.size,inputType:file.type||'not-reported',outputType:file.type,resized:g.resized,orientationNormalized:decoded.orientation!==1,crop:crop??null,encoding:'original'};
  if(!crop&&!g.resized&&file.size<=MAX_FILE&&decoded.orientation===1&&decoded.signature!=='other'){
   const original=file.type===decoded.signature?file:new File([file],decoded.signature==='image/png'?'skin-original.png':'skin-original.jpg',{type:decoded.signature});
   return{file:original,width,height,preparation:{...preparation,outputType:original.type}};
  }
  const canvas=document.createElement('canvas');canvas.width=g.width;canvas.height=g.height;
  const ctx=canvas.getContext('2d');if(!ctx)throw Error('This browser could not prepare this photo. Try a smaller original or another browser.');
  ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(image,g.crop.left,g.crop.top,g.crop.width,g.crop.height,0,0,g.width,g.height);
  const blobFor=(type:string,quality?:number)=>new Promise<Blob>((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(Error('The photo could not be encoded. Try a smaller original.')),type,quality));
  let blob=await blobFor('image/png');let encoding:SkinPreparation['encoding']='lossless-png';
  if(blob.size>MAX_FILE){ctx.globalCompositeOperation='destination-over';ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);blob=await blobFor('image/jpeg',.95);encoding='jpeg-0.95';}
  canvas.width=0;canvas.height=0;
  if(blob.size>MAX_FILE)throw Error('This detailed image remains larger than 8 MB after preparation. Frame the original more closely around your whole face.');
  const prepared=new File([blob],encoding==='lossless-png'?'skin-prepared.png':'skin-prepared.jpg',{type:blob.type});
  return{file:prepared,width:g.width,height:g.height,preparation:{...preparation,outputBytes:blob.size,outputType:blob.type,encoding}};
 }finally{decoded.release();}
}
