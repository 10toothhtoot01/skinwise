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

Prerequisite: Python Playwright, Pillow and Chromium (`python -m pip install -r tests/requirements.txt`, then `python -m playwright install chromium`). Tests use Chromium headless; rendered DOM was inspected before controls were selected. Screenshots and per-case request/error logs are written to `../../work/qa-acceptance` by default; override `SKINWISE_EVIDENCE_DIR` to keep them elsewhere. Responsive inspection uses `test-results/browser` by default.

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

## Evidence workspace release gate

The evidence-workspace focus suite passed **6/6 cases in 37.415 seconds** after the selected-region reading was corrected. API responses and AWS-shaped image URLs in this suite were intercepted locally; the rendered images were valid PNG fixtures. This proves frontend handling of returned evidence, not a new real-provider or accuracy claim, and spent no analysis units.

```sh
PYTHONPATH=tests SKINWISE_BASE_URL=http://127.0.0.1:5173 python -m unittest -v browser_evidence
```

Verified behavior:

- A new request explicitly submits the `visible` profile. The UI renders the returned original, pore overlay, cheek overlay and redness mask, with their actual returned URLs and decoded image dimensions.
- Selecting the left cheek displays its returned 58 score; selecting the nose displays its 53 score; returning to whole face restores the 64 score and whole-face overlay. A missing concern/region image or score has an explicit empty state. Whole-face scores are not substituted into the selected-region reading.
- A three-part signed task receipt is saved separately and survives reload. Images do not survive as journal data. Explicit image refresh uses GET on the completed task; neither reload nor refresh starts another POST.
- Expired image bytes and expired task access produce visible fallback/error states. They do not invent detection images, remove the saved numeric record or start a replacement analysis.
- An older scan can be inspected and reviewed independently of the latest scan. Match/mismatch choices and a note persist after reload and appear in journal export; another scan's review remains untouched.
- Journal storage and exported JSON contain neither temporary image URLs nor access tokens. Private completed-task receipts remain outside the export. Deletion clears those receipts, and a delayed refresh response cannot restore deleted evidence or observations.
- Before submission, a 1079-pixel short side is labelled SD / 9 units and a 1080-pixel short side HD / 12 units. This UI boundary test starts no API job; backend contract tests and separately recorded real-provider evidence cover provider execution.

One meaningful interpretation defect was corrected during this gate: the selected regional image initially left the reading heading on the whole-face score. The focused test now checks selected-region and whole-face readings explicitly. An intermediate development-server module reload interrupted one run; its uncaught error remained a failure, followed by a fresh run against frozen source.

Evidence logs: workspace `work/qa-acceptance/evidence-suite.log` and `evidence-base-regression.log`. The earlier 23-case core/capture suite was rerun after the focused evidence tests; its final result follows below.

Evidence-workspace regression result: **23/23 existing core/capture cases passed in 128.787 seconds**, following the focused **6/6 evidence cases**. Both gates asserted no uncaught browser exceptions and made no paid API requests. The evidence workspace therefore has 29 passing focused/regression cases across these two runs; actual provider usefulness and returned visual capability are recorded separately by the integration owner.


## Accuracy loop: incomplete evidence and unknown method metadata

October 24: seven evidence-workspace cases passed in 40.219 seconds; 24 core/capture cases passed in 132.050 seconds (31 browser cases total). The new missing-score regional-image test additionally runs at a 390-pixel mobile viewport. Thirteen Node contract/context tests, TypeScript, scoped evidence-component lint, and production build pass. All browser analysis responses in these regression gates are mocked; no additional provider units were consumed.

The new tests first reproduced two defects: image-only returned regions were inaccessible, and unknown historical analysis metadata permitted numerical comparisons. Both are fixed, with independent review. Scores and images are preserved independently; missing scores remain absent; missing-method comparisons retain observations and withhold deltas. See ACCURACY-LOOP.md for counterexamples, methods, provenance and next validation gates. These checks establish software behavior, not clinical accuracy or real-person usefulness.

## Own-kit planner release gate — October 24 evening

The new `/planner` route implements the product hypothesis and concrete software contribution documented in OWN-KIT-PLANNER.md. Current proof: **7 focused planner browser cases passed in 45.638 seconds**, **31 existing core/capture/evidence regressions passed in 174.073 seconds** (38 Chromium cases total), **19 Node contract/context/planner tests passed**, TypeScript, scoped new planner/API lint and the official production build passed. The final metadata-only layout addition is included in the publication build.

Independent review found and verified fixes for fractional-time rendering failure, stale selection after rejection, changed-occasion decision reuse, unavailable-image selection, the recoverable session task limit, and rejection loss after reload. The latter was reproduced by a failing browser regression before the semantic graph was separated from currently loaded image IDs. Source replacement and same-source recovery are tested separately. All browser regression API/image responses were mocked; the sample kit starts no paid request.

Two justified live makeup jobs used the same generated adult portrait: one lip-only configuration and one complete lip/blush/eye-shadow combination. Each returned a real provider image, at the documented 1 unit per job. Later UI replay retrieved the existing task with GET, loaded the real image, selected a plan and preserved the exclusion of image URLs from session metadata. Paid receipts/results are private workspace evidence, not deliverable source. These tests establish protocol handling and workflow, not physical shade fidelity, clinical accuracy or a real consumer outcome. No real-person makeup test was conducted.

## Planner storage recovery follow-up

The storage audit reproduced unreadable-session overwrite and quota/write-failure receipt loss using synthetic data and mocked API calls. The subsequent patch preserves invalid raw bytes, checks durable session read/write before a new paid POST, reports later write failures, and adds an explicit private metadata/receipt backup and restore path. Ordinary decision exports remain free of task-access data.

The focused recovery suite covers original-byte export, preflight failure with zero POSTs, after-start write failure with in-memory private recovery and GET checks, valid private-file restore with no new generation, and invalid import preserving current data. A malformed-JSON private-prefix regression was first observed failing, then corrected with a generic format error. Exact final release results are recorded in the workspace progress ledger and delivery document. No real participant or paid API job was used for this follow-up.

## Portrait preparation race and solver oracle

Independent controlled-delay reproduction found that a replacement portrait could finish after a paid task had started on the previous portrait, deleting its new receipt and stranding the busy state. The regression failed before a preparation gate was added. The UI now pauses preview starts/checks and consent during preparation; synchronous refs guard handlers, latest-ticket ownership controls cleanup, and clear/restore cancels pending preparation. Regression cases cover release/reconsent/one mocked POST+GET and clearing while preparation is pending; an additional390px check and overlapping selections verify latest-photo ownership. No paid calls or physical-device claim.

The independent solver oracle enumerates all binary product subsets rather than using the production category expansion. For six fixed representative kits (empty,9same-category,balanced9,7/1/1,2sparse,all30minute), it compares all8required×8excluded subsets×3product caps×60minute limits:69,120cases. It checks exact feasible-set equality, considered count, summed estimates, unique feasible shortlist of up to3, quickest-first and explanation presence/absence. All passed. This is bounded algorithm evidence, not proof for every possible kit, entered-time accuracy or consumer benefit.

```sh
node --experimental-strip-types tests/solver-oracle.mjs
PYTHONPATH=tests python -m unittest -v browser_planner browser_planner_recovery
```

This release passed7planner cases in47.635seconds and7recovery cases in44.191seconds; the two focused390px cases passed12.857seconds.19Node tests, TypeScript, scoped planner lint and the official production build passed. Earlier31unchanged core/capture/evidence cases are reused:45browser cases across suites, not a claim that all45ran together. Source identity is recorded in the delivery package and workspace progress ledger.


## Free all-feasible decision loop — October25

Independent review found a four-product kit had11feasible recipes but only3accessible, and every product choice required a paid loaded image. The original missing-catalog regression failed. The correction exposes every feasible recipe in a free text catalog, allows explicit constraints-only selection/export and free no-added-makeup, and opens one focused optional card alongside the3starters. No API request occurs until a separate explicit start/check. Selection basis distinguishes `constraints-only`, `loaded-preview`, `original`, and legacy `not-recorded`.

Four new mocked-browser cases passed38.854seconds: omitted three-step recipe selection/export/reload with zero requests; exact focused recipe submission and GET-only return; expired image retaining a text-based choice; and100comparison append guard with export/reset. Independent edge checks verified first/replacement portraits retain constraints-only choice, old sessions default newfieldsnull, and rejected catalog choices stay guarded. At390px, all63balanced-kit recipes were individually selectable with zeroAPIcalls, no overflow and at most4recipe cards. This is emulation, not physical-phone proof.

The14nearest planner/recovery regression cases passed84.920seconds after source was frozen. A prior invocation overlapped hot-module replacement and lost a mocked in-flight request; the stable rerun resolved that infrastructure ambiguity.19Node tests,tsc,scopedplannerlint,gitdiffcheck and officialproductionbuild passed.49browser cases across suites (18current planner/recovery/decision and31earlier unchanged core/capture/evidence), not a claim of one49case run. No real-person or new paidprovider test was used.

```sh
PYTHONPATH=tests python -m unittest -v browser_planner browser_planner_recovery browser_planner_decision
```


## Clean-source handoff verification — October25

The exact676e3889source ZIP was extracted into a new directory with no dependencies, key file, Git metadata, `.sites-runtime` or `.wrangler` state. OnLinux/Node22.23.1/npm10.9.8, documented `npm ci` installed687packages; TypeScript,19Node tests and `npm run build` passed. A fresh devserver on5181 returned HTTP200 with keyconfiguredfalse; a fictional full-catalog choice exported exact products/seven estimated minutes with zero paid-API attempts and no browser exceptions. The owned fresh devserver was stopped afterward.

An independent prerequisite review found the browser instructions omitted Pillow. A new Python3.14venv with only documented Playwright reproduced `ModuleNotFoundError: No module named PIL`. Added `tests/requirements.txt` for verifiedPlaywright1.59.0/Pillow12.3.0, explicit virtual-environment setup and `.venv` ignore. Installing that file in the fresh venv made all4decision cases pass41.250seconds against the fresh server. These dependencies requirePython3.10+; only3.14was executed here. The host's existing Chromium binary/native libraries were reused; this is not a cleanOS or all-platform claim.

Free setup now needs only `npm ci`/`npm run dev`; the server key file is an explicit optional step for actual provider work. No new paid call, app/runtime change or new browser case was introduced by this handoff correction. Later source revisions contain documentation/test-requirements only, so matching runtime evidence is reused.


## Promise-scope audit — October25

An independent review found that the global promise matrix still described only the old journal/firstSDjob, and ordinary planner exports said “No face analysis” even though MakeupVTO processes a portrait. The matrix now covers the primary free planner and supporting skin workflow separately; dated API balances/testcounts/initialSDmethod examples are explicitly historical. Skin-only accuracy/value reports are scoped accordingly. Export limits now state the exact boundary: preview settings request zero skin smoothing, and the planner does not call the skin-analysis endpoint. No claim that portraits avoid processing is made.

Runtime diff is only that explanatory export string. Four existing decision cases passed38.784seconds;19Node tests,TypeScript,gitdiffcheck and productionbuild passed. No new case or paidjob was added; prior unchanged functional evidence is reused. Focused independent review found no further unsupported generalization within the checked surfaces. Real-user benefit, physical shade accuracy, clinical validity and hardware coverage remain unvalidated.
