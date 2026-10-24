# Skinwise acceptance evidence

This is a functional release gate, based on the GitHub-sourced Anthropic `webapp-testing` skill, Vercel `react-best-practices` (`client-localstorage-schema`) and Vercel Web Interface Guidelines (semantic controls, keyboard focus, live status, responsive layout, destructive-action confirmation). Skill snapshots are in the workspace `work/skills` directory; provenance is recorded separately.

## Acceptance matrix

| Flow | Required observation | Evidence status |
| --- | --- | --- |
| Entry | Product purpose and non-diagnostic limits are clear; primary action works | Pass: rendered desktop/mobile and sample entry |
| Sample | Explicit sample labels; deterministic results; no provider request; never becomes live data | Pass: sample and follow-up assertions; zero analysis requests |
| Live readiness | Configuration state explained; no silent sample fallback | Pass: mocked failure keeps analyses empty; genuine provider verification separate |
| Upload | Image validation; clear external processing consent; analysis requires consent | Partial: browser consent gating and privacy copy; API image validation covered separately |
| Provider failure | Rejected and failed analysis leave a recoverable error, not a fabricated result | Pass: mocked 429, terminal 422; no fabricated analysis |
| Results | Actual metric names and direction retained; unavailable metrics stay unavailable | Pass: mocked async result exact storage equality and matching-metric comparison |
| Plan | One user-selected change persists through reload | Pass: intention text retained after reload |
| Journal | Check-in persists through reload; comparison has same source and metric | Pass: observation and comfort retained; comparison assertions |
| Comparison | Source mismatch and missing metrics cannot create unsupported numeric deltas | Pass: demo99 excluded; live40→45 gives +5; unmatched metrics omitted |
| Export | Downloaded JSON matches visible saved records and explicitly records source | Pass: JSON equality with saved journal; demo source retained, no photo data |
| Delete | Confirmation or undo; cleared state stays cleared through reload | Pass: bulk cancel/confirm/reload and single-note cancel/confirm |
| Corrupt storage | Invalid JSON, wrong schema, and invalid records fail safely without breaking entry | Pass: four corrupt inputs; original bytes preserved; Export original available |
| Mobile | 390px and narrow 320px viewport have no unintended horizontal overflow | Pass: Overview, Skin check, My journal, Progress; screenshot inspection |
| Keyboard | Skip link and dialog keyboard behavior | Pass: skip link initial focus; modal default focus, Shift+Tab containment, Escape dismissal |
| Runtime | No uncaught browser exceptions across primary flows | Pass: each automated flow asserts empty pageerror collection |

## Test boundary

Mocked browser provider responses exercise frontend handling only; they do not verify credentials, provider availability, billing, or real YouCam analysis. A genuine live check requires a configured account and an authorized user's image. A passing sample walkthrough cannot satisfy this live gate.

## Reproduction

With the app already running on port 5173, from the project directory:

```sh
SKINWISE_BASE_URL=http://127.0.0.1:5173 python tests/browser_acceptance.py
SKINWISE_BASE_URL=http://127.0.0.1:5173 python tests/browser_inspect.py
```

Prerequisite: Python Playwright and its Chromium browser (`python -m pip install playwright`, then `python -m playwright install chromium`). Tests use Chromium headless; rendered DOM was inspected before controls were selected. Screenshots and per-case request/error logs are written to `../../work/qa-acceptance` by default; override `SKINWISE_EVIDENCE_DIR` to keep them elsewhere. Responsive inspection uses `test-results/browser` by default.

The automated suite includes a pending-analysis refresh test: it records exactly one POST, reloads before polling, resumes the preserved receipt with one GET, and asserts the resulting live record. Consent is unchecked after reload and no second upload occurs.

## Defects found and corrected during acceptance

- Server/client date mismatch caused a hydration exception and error overlay. Date rendering now waits for client readiness; subsequent three-viewport inspection had no exceptions.
- Nested invalid local data could crash result rendering. The app now validates nested records and preserves unreadable original bytes for export.
- Bulk-delete modal allowed keyboard focus to escape and lacked Escape dismissal. Focus is now contained and background panels are inert.
- Individual check-in deletion lacked confirmation. Browser tests exercise both cancelling and confirming.
- Terminal failed/expired provider tasks could keep the app stuck resuming the same task. These failures now clear the receipt and allow a fresh image.

A server restart interrupted one intermediate run with connection-refused errors; these were infrastructure interruptions, and the suite was rerun against the restarted server. Tests never upload a synthetic fixture to the actual provider.

## Accuracy and promise checks

A focused 5-case run passed after the interpretation copy and note-context changes:

- Overview does not contain the previous “find what works for your skin” promise or claims of proven efficacy/accurate measurement.
- Results include keyboard-operable expanded guidance explicitly saying a score of 72 is not 72% hydration, health, or confidence; moisture is inferred from a photo; this configuration's real-world accuracy/repeatability is unvalidated; score differences do not establish product efficacy.
- Comparison deltas are labelled “score points”. These are arithmetic differences, without a reliability or causal claim.
- Check-ins snapshot the active intention. Closing the experiment does not remove historical note context; later notes without an active intention omit it. Context survives reload and export.
- Optional analysis-method metadata survives schema loading, reload, and export, including a null model version. The app does not invent a model version.
- The late-result test held an analysis response in flight, deleted all journal data, then released a successful response. Neither the deleted analysis nor the task receipt reappeared.

These assertions verify visible interpretation and data behavior; they cannot establish model validity or complete human comprehension. They do not validate the research papers or turn sample scores into measured evidence. The expanded 14-case release suite is recorded separately in the workspace `work/qa-acceptance/release-suite.log`.

Release gate result: **14/14 browser cases passed in 94.177 seconds**, against `http://127.0.0.1:5173`. Every case asserted no uncaught browser exceptions. Provider requests in this suite were intercepted by Playwright; it spent no analysis units.

## Photo preflight and guided capture gate

The new capture path was checked using real PNG files generated with Pillow and decoded by the browser, rather than PNG-like headers. Eight focused browser cases passed in 47.826 seconds:

- A 479-pixel short side is rejected; a 480 × 960 PNG is accepted; a 4097-pixel long side is rejected.
- Invalid image contents, an oversized file and unsupported MIME type fail without a selected photo, guided-evidence claim or analysis request.
- An accepted upload is described as resolution checked, with lighting/position/processing unverified.
- Mock Camera Kit script-download failure, permission denial and unsupported resolution all preserve the upload fallback and produce no guided photo.
- Missing face-quality evidence, absent face, poor angle or poor lighting cannot yield a claimed guided photo, even if a capture event arrives.
- A mock capture with passing vendor checks yields a valid decoded image and a limited guidance description. It does not automatically run paid analysis.
- Capture setup survives a pending-task reload, accompanies the resulting record, and remains in exported JSON; only one upload request is made.
- Missing context, unknown filters and changed/incomplete camera or lighting setup produce explicit comparison limitations. Matching self-reported setup removes the setup-mismatch warning while retaining the unvalidated meaningful-change warning.

Five direct `comparisonLimit` unit cases passed: missing context; unconfirmed/processed photos; unknown camera/light/label; changed setup; matching self-reported setup. These checks do not invent brightness, blur or confidence thresholds.

```sh
node --experimental-strip-types --test tests/capture-context.test.mjs
SKINWISE_BASE_URL=http://127.0.0.1:5173 python tests/browser_capture.py
PYTHONPATH=tests SKINWISE_BASE_URL=http://127.0.0.1:5173 python -m unittest -v browser_acceptance browser_capture
```

The extended capture tests require Pillow in addition to Playwright. The combined gate includes an SD-versus-HD method-change case: it retains returned raw scores but withholds the numerical delta with an em dash and “Not comparable”.

## Actual SDK measurement and remaining hardware limit

`tests/browser_actual_camera.py` separately loaded the actual Camera Kit v2.5 CDN in headless Chromium with its synthetic camera device. SDK, supporting model and WebAssembly resources returned HTTP 200, and the vendor UI mounted. The SDK then emitted `cameraFailed` with `error_access_failed`; its uncaught promise rejection was `error.no.camera`, originating in `webenvcheckercontrollerv2-a8d7166d45e1322cfd54.bundle.js:4082:8`. The app displayed its upload fallback. No `/api/analyze` request was made.

The API integration review traced this outcome to the vendor's deliberate exclusion of fake/virtual camera labels. The test did not disguise the synthetic device or bypass that exclusion. The vendor rejection is recorded, not suppressed. This measurement establishes SDK loading and fallback behavior in this environment; it does **not** establish successful capture on a physical phone or laptop camera. Physical device permissions, quality guidance and capture remain a separate manual verification requirement. No clinical accuracy or repeatability was established.

Workspace evidence: `work/qa-acceptance/capture-suite.log`, `capture-context-unit.log`, `combined-release-suite.log`, and `work/qa-actual-camera/actual-sdk-fake-camera.json`. Fresh deliverable screenshots are in `screenshots/` and show labelled sample results and the capture screen without credentials or task receipts.

Final combined capture release gate: **23/23 browser cases passed in 139.473 seconds**, with no uncaught exceptions in the mocked/functional suite. This result includes the known-method mismatch and capture regressions above. The separately measured actual vendor SDK rejection on Chromium's synthetic device remains a documented environment limitation and is not counted as a passing physical-camera test.
