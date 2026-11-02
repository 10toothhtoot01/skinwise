# Portrait preparation and camera evidence

The makeup planner accepts an original JPEG or PNG, decodes it in the browser, preserves its displayed orientation, and prepares a compact JPEG, or an explicitly selected lossless PNG, with a maximum long side of 1024 pixels. It never enlarges the source. The prepared image is available for inspection before the user explicitly consents to YouCam processing. The photo is not saved in planner session storage. The private fingerprint identifies the exact prepared bytes; task reuse is limited to that portrait and compatible effects.

## Framing before resize

An optional local framing control lets a person crop and rotate the original, inspect the proposed frame, then explicitly apply it. Edits always start from the original image. Cropping removes outside pixels; it does not synthesize or sharpen facial detail. It must retain a 480-pixel prepared short side and the whole face should remain visible. The original can be restored. Applying a different image clears consent and asks before discarding receipts associated with the earlier portrait. Cancel keeps the current image and receipts. Applying framing does not create a provider task.

Why crop before resize? On a 3000 × 4000 source, the existing full-image limit yields 768 × 1024 pixels. A centered 1500 × 2000 crop also yields 768 × 1024 pixels; a 100-pixel feature in the original occupies approximately 51 pixels instead of 26 in the prepared image. This is a geometric calculation, not proof of better makeup rendering or shade accuracy. A crop that cuts off facial features can harm the result; use retake if the source is blurry or poorly exposed.

The framing step draws directly from the decoded original into the resized output canvas, followed by one encoding step. JPEG is the compact default; an explicit lossless PNG option avoids additional lossy encoding at the cost of a larger upload. Neither restores detail already lost in the source. This avoids a full-resolution intermediate PNG on phones. It does not intentionally smooth skin, change white balance, recolor, infer missing detail, or apply generative enhancement. Canvas color handling and JPEG compression can still change numeric pixel values. Alpha is composited on white by the existing pipeline; this may not represent a real camera capture.

## Provider boundary

[Perfect Corp's Makeup Virtual Try-On documentation](https://docs.perfectcorp.com/reference/makeup_vto) lists JPEG/PNG, long side <1920, face width >=100 and file size <10 MB, but an error-description row also states width <1920 and height <1080. These published descriptions are not identical. The app keeps its conservative 1024 limit pending a controlled vendor-confirmed test; 1024 is the app limit, not a claim that the provider requires it. The vendor describes light balancing within its own engine; its performance has not been independently established here. Color correction and generative restoration can change the evidence and must not be presented as accuracy improvements without a relevant controlled comparison.

## Validation and remaining evidence

Geometry tests check crop boundaries, rotation, no enlargement, and the 2× feature-scale example. Browser tests use a synthetic red/blue chart to check a quarter-turn, restoration of the same prepared fingerprint, insufficient pixels, cancellation of receipt replacement, and an EXIF orientation case. These tests are software/geometry evidence; they do not validate physical camera color, skin appearance, model accuracy, or utility for people. Model/camera results and their exact source state should be recorded separately before release.

A controlled encode of the synthetic 1024 × 1024 adult fixture produced a 985,456-byte PNG with zero decoded pixel change, and a 235,023-byte JPEG at quality 95 with mean absolute channel errors below 0.1 on a 0–255 scale. This one fixture demonstrates the size/fidelity tradeoff, not a measured difference in YouCam results or physical color.
