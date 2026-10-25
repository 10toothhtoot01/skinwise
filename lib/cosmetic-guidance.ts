// Small editorial corpus; no generated answers or inferred product identity.
export const guidanceCheckedOn = '2026-10-25';
export const guidanceSources = {
 shiseido:{title:'Shiseido Guide Makeup, pages 4–9',publisher:'Shiseido',kind:'Manufacturer technique',url:'https://corp.shiseido.com/en/sustainability/power-of-beauty/pdf/guide2.pdf',sourceDate:'Not stated in guide',checkedOn:guidanceCheckedOn},
 bobbi:{title:'Cheek questions: Where do I apply blush?',publisher:'Bobbi Brown',kind:'Manufacturer technique',url:'https://www.bobbibrowncosmetics.ca/products/23824/makeup/face/cheeks',sourceDate:'Not stated on page',checkedOn:guidanceCheckedOn},
 mac:{title:'Ask an Artist: How to Apply Eyeshadow?',publisher:'M·A·C',kind:'Manufacturer artist technique',url:'https://www.maccosmetics.co.uk/pages/how-to-apply-eyeshadow',sourceDate:'Not stated on page',checkedOn:guidanceCheckedOn},
 fda:{title:'Eye Cosmetic Safety: safety checklist',publisher:'US FDA',kind:'Regulator safety guidance',url:'https://www.fda.gov/cosmetics/cosmetic-products/eye-cosmetic-safety',sourceDate:'Page lists update: 2006-12-18',checkedOn:guidanceCheckedOn}
} as const;
export const techniqueGuides = [
 {id:'lip-edge',question:'How can I keep lipstick within my lip line?',context:'slanted-bullet',contextLabel:'I use a slanted lipstick bullet',category:'lip_color',action:'Use the index finger of your other hand just outside the natural lip line as a guide. Work from the lip corner toward the center, finishing the upper lip before the lower lip.',limit:'This is a tactile technique from a guide for blind or low-vision users using a slanted lipstick bullet. It is an option to try, not a liquid-lipstick instruction or a guarantee of an even result.',sources:['shiseido']},
 {id:'blush-placement',question:'Where can I start placing cheek blush?',context:'cheek-blush',contextLabel:'My product is labelled for cheek blush',category:'blush',action:'One starting placement is high on the apple of the cheek, blending outward toward the ear. Blend the edges; choose the amount according to the color you want.',limit:'This is Bobbi Brown’s general placement suggestion for cream or powder blush. It does not select your shade, amount or formula and does not establish one ideal placement for every face.',sources:['bobbi']},
 {id:'shadow-edge',question:'How can I soften an eyeshadow edge with a brush?',context:'brush-eyeshadow',contextLabel:'I use eye-labelled shadow and a blending brush',category:'eye_shadow',action:'A fluffy blending brush gives a softer application than a dense applicator brush. Move the blending brush back and forth through the socket to soften the color edge.',limit:'This is a brush technique from a M·A·C artist, not a finger-application or every-eye-shape tutorial. Use cosmetics intended for the eye area; a lip or cheek color entry does not establish eye suitability.',sources:['mac','fda']}
] as const;
export type GuidanceQuestion = typeof techniqueGuides[number]['id'];
export type GuidanceRequest = {question:string;context:string;claim?:string;evidence?:'current'|'missing'|'stale'|'conflicting';identity?:string};
export function resolveGuidance(request:GuidanceRequest){
 if(request.claim && request.claim!=='technique')return {status:'unavailable' as const,message:'This collection has no product-specific, shade-match, wear-time, allergy or review evidence. A name or approximate color is not a confirmed product and variant.'};
 if(request.evidence && request.evidence!=='current')return {status:'unavailable' as const,message:request.evidence==='conflicting'?'Conflicting evidence needs review; no combined instruction is supplied.':'The supporting evidence is unavailable or needs rechecking. Open the original source and product label.'};
 const guide=techniqueGuides.find(g=>g.id===request.question);
 if(!guide)return {status:'unavailable' as const,message:'This question is outside the three checked techniques. Check your product’s instructions; no answer is inferred.'};
 if(guide.context!==request.context)return {status:'needs-context' as const,message:`Check applicability first: ${guide.contextLabel.toLowerCase()}.`,guide};
 return {status:'supported' as const,message:guide.action,guide};
}
export const reviewEvidence = {count:0,status:'unavailable',message:'No verified external reviews or community tips are in this collection. There is no rating, consensus or product recommendation to show. Product identity and variant remain unconfirmed; check the package and manufacturer instructions.'} as const;
