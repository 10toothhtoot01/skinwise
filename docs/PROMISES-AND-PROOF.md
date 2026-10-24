# What Skinwise can promise

The primary product is the experimental **Own-kit Look Lab** at `/planner`. It helps enumerate and keep a plan from entered products and constraints. The supporting skin evidence workspace at `/` preserves observations and displays optional model output. Neither workflow has established real-user benefit or physical/clinical accuracy.

## Primary planner promises and limits

| Promise | Delivered behavior | Evidence and boundary |
|---|---|---|
|Use only my entered kit and limits|Enumerate zero/one item per supported step; enforce required/excluded steps, product cap and sum of entered minutes; explain infeasibility|Solver contract cases, independent69,120case subset audit on six fixed kits; this checks arithmetic, not actual duration or physical feasibility. Max9items/3supported categories.|
|Let me reach every feasible choice|Full text catalog, three starter suggestions and one focused optional preview card|11recipe regression plus all63maximum balanced-kit recipes individually selected at390px with no API calls; starters are variety, not a suitability rank.|
|Keep a plan without buying a render|Free constraints-only recipe choice, no-makeup opt-out and exact export need no portrait, provider key or provider request|Four decision browser cases and clean-source no-key smoke; the deployed site still requires owner access. No-makeup is an opt-out, not satisfaction of required product steps.|
|Show a real optional preview|Explicit budgeted Makeup VTO from the same prepared original; server computes effects and sets smoothing/morphology to zero|Two actual makeup tasks on a generated adult portrait: lip-only and three effects. Protocol proof, not physical shade/identity/fidelity proof. No skin-analysis endpoint called by the planner; the makeup service still processes the portrait.|
|Preserve what I actually chose|Explicit choice basis, ties, rejected options and cycles; no forced inferred winner|Contract/browser tests, independent preference oracles; this verifies graph semantics, not the stability or quality of human preferences.100record comparison limit is explicit.|
|Recover existing tasks without another paid start|Signed24hour receipts, GET-only checks, visible storage failures and separate private recovery files|Recovery browser cases and deployed checks. Storage can fail after preflight; vendor/receipt expiry remains. No guaranteed recovery of a start that returns no receipt.50task cap is not a global spending control.|
|Give an honest handoff|Exact chosen products, estimates, constraints, digital settings, selection basis and decision trail; ordinary export excludes photos/resultURLs/task access|Export/reload and recovery-boundary tests. Digital settings are not physical application instructions; no allergy, exactSKU, shade, wear or outcome prediction.|

Exact commands, run scopes and known environments are in [ACCEPTANCE.md](ACCEPTANCE.md). Source decisions and scope are in [OWN-KIT-PLANNER.md](OWN-KIT-PLANNER.md). These are bounded software promises. No intended participant or physical makeup application has been observed; the prepared user study is unexecuted because no tester is available.

## Supporting skin-workspace promises

| Promise | Delivered behavior | Evidence and boundary |
|---|---|---|
|Keep a faithful personal record|Retain chosen intention, dated comfort/note and historical context; exact export and confirmed deletion|Browser persistence/export/deletion tests. User reports are subjective. Vendor retention is separate.|
|Show actual supported provider evidence|Retain exact returned scores/regions/images when available; missing information stays missing; no synthetic success fallback|Two real synthetic-portrait skin jobs: initial SDsix-metric integration and later HDfour-concern visible workflow. These are historical integration observations, not model validity or current balance checks.|
|Explain and compare without inventing improvement|Appearance estimates are not percentages/diagnosis/confidence; match source/metric/method, flag uncertain capture context and withhold unsupported deltas|Interpretation, missing-evidence and method-compatibility regressions; no calibrated meaningful-change threshold.|

The four total real provider jobs comprise two skin and two makeup tests on generated adult imagery. Existing-task demo replays create no new task. No real-person or clinical result is implied by a successful response.

## Claims withheld

- “Very accurate”, a percentage accuracy guarantee, dermatologist-equivalent performance, or validity on every skin tone/device.
- Measuring physical hydration or sebum from these scores.
- Determining which product works, diagnosing a condition, prescribing care, or attributing a change to a product.
- Treating a +1, +5, or any arbitrary score change as meaningful improvement.
- Assuming endpoint version 2.1 identifies the exact algorithm model build evaluated in a paper.
- Ranking different metric scores as clinical priorities.

## Supporting skin-workspace use case

A person chooses to keep one part of their existing routine consistent. They record that intention and add dated comfort notes. When reviewing later, the app shows what they actually recorded alongside optional photo estimates. That preserves context they would otherwise need to remember. It does not conclude the routine helped, recommend a purchase, or claim savings. Whether this journal measurably improves decisions remains a user-study question.

## Validation before stronger skin-analysis claims

1. Define the exact claim and intended population before collecting results. Distinguish image appearance agreement, same-session repeatability, longitudinal sensitivity, and useful decisions.
2. Obtain provider model-build/score-transform details and evidence that applies to the exact SD API configuration. Endpoint version alone is insufficient.
3. With consent, collect repeat captures across representative devices, tones and conditions. Separate recapture noise from reprocessing the identical image. Include unsuitable images and measure appropriate rejection.
4. Use multiple blinded qualified raters for visible signs; use an appropriate physical reference instrument if claiming hydration or sebum measurement. Predefine reference labels and account for rater disagreement.
5. Estimate agreement/errors and confidence intervals by metric and subgroup on a held-out set. Evaluate repeatability and limits of agreement. Determine a meaningful-change threshold with suitable expertise; do not invent one from a few synthetic scores.
6. Test whether users can correctly interpret uncertain results and avoid causal conclusions. A future usefulness study must measure the promised decision outcome, not just clicks.
7. Keep unsupported claims withheld if any relevant gate fails. Document limitations and recalibrate after model changes.

This protocol is planned, not completed. A software deadline and generated-portrait tests cannot establish real-person accuracy.

## Capture practicality decision

Prefer the provider's guided camera checks over a homegrown “accuracy score.” Detect unsupported resolution and permission errors with specific recovery steps; keep upload available as explicitly unassessed visual quality. Validate file decoding and documented dimensions before paid analysis. Do not reject people based on phone price, inferred skin tone, or a whole-image brightness threshold. Capture-context fields are voluntary and self-reported, not automated verification.

A controlled Chromium fake-camera test loaded the actual SDK, which rejected its virtual camera label. This is evidence of a supported failure path, not real-hardware readiness. A real phone must still be exercised by its user. Document expected vendor errors rather than hide them globally. Known method mismatches (SD/HD, endpoint, score kind) withhold numerical deltas. Matching self-reported setup is helpful context but does not prove measurement accuracy.
