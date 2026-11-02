# Journal photo preparation

The journal now prepares common large phone images locally before applying the existing analysis upload contract. This corrects the observed rejection of otherwise usable portraits above the app's 4096-pixel long-side cap. The original stays in memory for explicit reframing; selecting a photo never submits an analysis.

## Current provider contract and application policy

Reviewed 2 November 2026 against official [File Specs & Errors](https://docs.perfectcorp.com/reference/ai_skin_analysis/section/overview/file-specs-and-errors) and [Skin Analysis v2.1](https://docs.perfectcorp.com/reference/ai_skin_analysis/v2.1). Current specs require JPEG/PNG below 10 MB, short side at least 480 for SD or 1080 for HD. They state that longer inputs are accepted and automatically reduced to 2560 pixels. The integration instructions recommend preparing at 2560. Thus 4096 is **Skinwise's existing application/backend cap**, not a current claimed provider limit. We preserve already-valid images within that cap to avoid needless local recompression and leave the documented provider resizing to YouCam. Preparation does not promise that the provider uses every submitted pixel.

## Exact behavior

- Decode the original in the browser with its camera orientation. Accept JPEG, PNG, WebP, AVIF and browser-decodable HEIC/HEIF; recognize allowed extensions when MIME is empty. HEIC without a decoder gives specific JPEG export guidance. No third-party codec or upload is used.
- Retain exact file bytes for valid JPEG/PNG originals at most 4096 pixels on the long side and 8 MB with normal orientation. Correct a missing MIME label without recompressing.
- Resize larger originals proportionally to a maximum 4096 pixels. Never enlarge. Keep the original for later cropping.
- Encode changed images as PNG first. Only if that exceeds 8 MB, encode once at JPEG quality 0.95; transparent areas are flattened white for that JPEG fallback. The UI reports output encoding, orientation normalization, crop and original/prepared dimensions.
- If a panorama would become shorter than 480 pixels on its short side, offer explicit original-photo framing instead of stretching or padding. Crops are clamped to original bounds, previewed and applied only by the user. A genuinely undersized source remains blocked.
- No sharpening, denoising, lighting/color correction, generative reconstruction, beauty filtering or fabricated texture. A valid dimension check is not proof that a face is sufficiently large, unobstructed or evenly lit.
- Original inputs above 25 MB or decoded 64 megapixels are rejected with specific guidance to reduce memory pressure. This bound is not a guarantee against low-memory failures on every device.
- New selections reset consent. Generation guards discard stale encoding results after another selection, remove or unmount. The selected prepared pixels can be inspected before consent.
- Changed preparations are recorded with capture context. Differences in crop, dimensions, resizing, orientation or encoding warn when comparing scans. File byte count alone does not create a comparison warning. Photos are not stored in the journal.

## Verification and limits

Focused real Chromium decoding tests cover large portrait/landscape, exact original preservation, panorama cropping and restore, EXIF rotation, WebP conversion, empty MIME, unsupported HEIC, undersized/oversized rejection, consent reset, stale preparation and removal, crop rounding, and a 390-pixel mobile viewport. Provider calls are mocked or blocked in those tests. A separate root-agent live test submitted one synthetic adult image through this path; it is provider integration evidence, not cosmetic validity evidence.

Physical iPhone/Android HEIC support, low-memory devices, camera color/texture fidelity, actual-user utility and repeatability remain unverified. Canvas output may use browser color-management behavior. Lossless PNG encoding avoids additional codec loss but does not reverse resampling or preexisting compression. Reframe close around the entire face rather than relying on resizing to repair a distant subject.
