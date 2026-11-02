# Browser camera and local acquisition assistance

Added November 2, 2026. This is an optional acquisition aid for the makeup planner. It does not certify cosmetic accuracy, photo quality, identity or medical suitability. Native capture and file upload remain available.

## Implemented flow

`BrowserCamera` opens only after an explicit button action. It asks for video permission, displays a preview, can switch cameras when multiple video inputs are reported, captures a full-resolution lossless PNG, stops the stream, and offers review, retake or use. The selfie video is mirrored only in CSS; captured pixels and review are unmirrored. Rear preview is unmirrored. `onCapture(File)` enters the existing shared validation/framing/preparation flow. The camera component never uploads a photo or creates a provider task.

Close, unmount, navigation and capture stop every stream track and terminate the worker. Generation tickets reject late permission results and captures. Pending permission can be cancelled in the app; if the browser later grants it, the stale stream is immediately stopped. Permission denial, no camera, busy device, unsupported constraints and insecure context have actionable fallback messages. An open preview does not imply the browser granted a particular resolution or physical lens.

The root planner owns the active original and endpoint preparation. Browser camera itself adds no JPEG compression, crop, color change, smoothing or enhancement. Model checks use a separate at-most640px bitmap; that analysis bitmap never replaces the captured original.

## Chosen local model and runtime

Pinned `@mediapipe/tasks-vision`0.10.32 and official BlazeFace short-range float16 model version1. The model is229,746bytes and supplies face bounds plus six approximate keypoints, sufficient for optional acquisition hints without downloading a full facial-mesh model. Runtime and model are self-hosted; the app makes no request to a remote image-inference service.

The actual selected SIMD download is approximately12MB uncompressed:11,453,626-byte WASM,204,816-byte loader,137,315-byte JS wrapper and229,746-byte model. The alternative non-SIMD WASM is10,647,962bytes; both fallbacks are in source, but FilesetResolver chooses a runtime. No model assets are requested until explicit camera opening or a separate explicit image check. This is a small model, **not** a tiny total runtime.

Package and model are Apache2.0. Original license and exact file hashes are in `public/camera/vendor/LICENSE` and `PROVENANCE.json`. The CommonJS package bundle is copied as `vision_bundle.js`, with a worker-local `exports` object; the classic worker supports the pinned loader's `importScripts` requirement. No upstream executable installer was run (`npm install --ignore-scripts`).

Primary references: [Google Web face detector guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector/web_js), [model overview](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector), [official model card and license](https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf). These sources describe intended inputs; they do not validate this application's thresholds or users.

## Work scheduling and hints

Inference runs in a dedicated worker, one frame in flight, normally at least650ms apart. Results over350ms slow the next interval to2seconds. Hidden tabs pause new frames. Loading times out at20seconds and individual checks at8seconds; failure terminates inference and leaves manual capture usable. No burst capture is implemented: there is no measured evidence it improves on the simpler review/retake flow here.

Warnings cover absent/multiple faces, low detector confidence, small/cut-off/off-center bounds, approximate eye-line/head orientation and changing position. Face-region luminance and Laplacian edge variance run on a64×64 crop of the detected face. Small size, edges, mean differences and clipping cutoffs are explicitly **uncalibrated advisory heuristics**. They can miss blur or lighting issues and give false warnings; noise can raise edge variance. Pose estimates use a few keypoints, not calibrated 3D angles. A rotated synthetic fixture also raised a sideways warning; this is an observed limitation. No quality percentage or all-clear certification is shown, and warnings never block capture. On a no-warning result, the UI still asks users to inspect focus, lighting and their whole face.

## Verification and evidence level

`tests/browser_camera_local.py` uses real browser canvas-backed MediaStreams with a deterministic model adapter to isolate lifecycle behavior. Six cases passed together in13.596s: permission/device/busy/constraint/insecure fallbacks; exact red/blue PNG left-right pixels; full landscape capture; mirrored live preview; retake and shared preparation; consent not auto-granted; portrait dimensions; model failure/timeout with manual capture; stale permission and repeated stop; camera switching; hidden-tab suspension; worker termination. A seventh focused case passed in2.477s, verifying actual cross-workspace navigation stops tracks before pagehide completes. No physical device or provider request is implied.

`tests/browser_camera_model.py` runs the **real pinned model** through the actual component's camera path, supplying an explicitly synthetic adult via a canvas MediaStream. One case passed in3.544s: no model asset request before open, one face detected, full1024×1024 lossless review, stopped tracks, then shared prepared portrait. Zero provider attempts and page errors. This is real model execution with a simulated camera, not physical camera validation.

Controlled actual-model probes under `work/qa-camera-local` measured baseline/repeats, blur, dark/bright/uneven light, rotation, small face, two faces and blank input. Representative640px inference was7–12ms after initialization on this Linux headless Chromium host; one earlier1024px call measured52.6ms,166.5ms including initialization. These are observations, not phone benchmarks or service-level guarantees. Synthetic blur reduced face-region edge variance from1459.47 to15.24 and raised the soft-detail warning. Bright and side-light controls raised relevant warnings. A dark control remained detected without a dark warning; sensitivity is incomplete. Multiple and blank inputs returned2 and0faces.

Initial direct-ImageBitmap inference caused a MediaPipe texture abort; passing decoded ImageData to the detector in the worker corrected that path. A diagnostic which created bitmaps directly from OffscreenCanvas intermittently returned0faces; a subsequent run passed. Explicit pixel snapshots (`getImageData`→ImageBitmap) made the controlled probe stable in the recorded run. This issue was observed in the diagnostic canvas snapshot path, not claimed fixed universally. Five fresh workers using the application-style direct decoded-image resize each returned1face on both tested frames. Actual component model execution also passed. The original failing diagnostic output remains in `model-evaluation.log`; it is not counted as a successful accuracy test.

Four Node heuristic tests verify warning branches and limits. Two additional worker-source regression cases reproduced a negative-origin face crop including extra background and sampling a fully offscreen box. The crop now uses the true intersection of the detected bounds and image bounds; both cases pass after the focused correction. Six Node cases pass together. TypeScript passed; scoped ESLint has0errors and the expected native-image warning for the local object-URL review image. Root's final production build and broader release checks are recorded separately.

```sh
PYTHONPATH=tests python -m unittest -v browser_camera_local browser_camera_model
node --test tests/camera-guidance.test.mjs
```

The actual-model test requires the existing synthetic fixture at `../../work/fixtures/synthetic-adult-makeup-qa.jpg`, or `SKINWISE_SYNTHETIC_PORTRAIT` pointing to an authorized synthetic test image. It skips explicitly if unavailable. `SKINWISE_BASE_URL` selects a running dev or compiled server. Model evidence and browser screenshots are local safe reports; none contain task receipts or keys.

## Remaining material limits

Physical iOS/Android cameras, diverse real people, calibration across lighting/skin appearance, Safari worker/WebGL behavior and physical cosmetic shade/texture/wear remain unverified. Unsupported worker/runtime paths show manual fallback. The provider's separate vendor Camera Kit previously rejected a synthetic camera and remains unchanged; this new browser path does not erase that result. No claim of universal device support, calibrated capture confidence, diagnosis or physical product fidelity follows from these tests.
