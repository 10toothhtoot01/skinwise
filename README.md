# Skinwise

A YouCam-powered skincare observation journal. Capture a consistent photo, review returned appearance estimates, choose one routine change to observe, and keep context alongside later check-ins. A separate sample walkthrough uses explicitly synthetic scores.

## Run locally

Requires Node.js 22.13+ and npm. From this directory:

```bash
npm ci
cp .dev.vars.example .dev.vars
# Edit .dev.vars with your YouCam key. Never commit it.
npm run dev
```

Open the Local URL printed by the server (normally http://127.0.0.1:5173). The account needs active API units; the six-concern standard analysis costs 12 units according to the consulted provider documentation. `GET /api/status` only checks whether a key is configured, not whether it has credits.

The supplied key was configured locally for this build in ignored `.dev.vars` and as a secret on the private Sites deployment. It is not included in source or a downloadable source archive. Other developers supply their own key.

## Accuracy and capture reliability

Skinwise has not established clinical accuracy, measurement repeatability on users’ devices, or a reliable-change threshold for this SD API configuration. Scores are provider UI estimates, not physical hydration measurements, confidence probabilities, or product-effectiveness findings. Published validation on other configurations does not transfer automatically. See [evidence audit](docs/ACCURACY-EVIDENCE.md) and [promises with proof](docs/PROMISES-AND-PROOF.md).

Optional YouCam guided capture checks face position, angle, lighting and resolution. It is loaded only after a user clicks to open the camera. Upload remains available with explicit unverified visual quality. Local image decode/dimension checks do not establish that a face is in focus. Hardware capture and SDK domain compatibility require real-device testing; SDK mocks cannot prove them. See [capture reliability](docs/CAPTURE-RELIABILITY.md).

## What to try

- Open the sample walkthrough to explore results and journal behavior without API use.
- For live analysis, use the guided camera or a consenting adult's clear, front-facing JPEG/PNG. Record the optional capture setup so later differences in conditions remain visible. The face should fill most of the image, with no filters and consistent lighting.
- Read the processing notice, consent, and submit once. The app polls the existing task; do not restart a pending paid job.
- Save one change and write a check-in. Reload to confirm browser persistence.
- Review matching metrics from the same source, with capture-context warnings and no improvement verdict. Export your journal or delete it with confirmation.

## Data and limits

Photos are sent to YouCam/Perfect Corp for analysis. The application does not save photo bytes in its journal or database. YouCam's own retention policy applies to uploaded files and task records; consulted documentation states 30 days. Local deletion clears this browser's journal and pending task receipt; it does not delete vendor-held files. Browser storage is device/profile-specific, can be cleared by the browser, and is not encrypted application storage. Export before relying on it.

Scores are appearance estimates. Lighting, camera, pose, and ordinary day-to-day variation affect comparisons. A change in score cannot establish that a product caused it. This app does not diagnose conditions or prescribe care. Demo scores are synthetic and are never substituted for provider failures.

## Implementation

React and TypeScript on the supplied Vinext/Cloudflare Workers runtime. API handlers perform upload validation, provider metadata upload, presigned byte upload, task creation and polling. The API key stays on the server. A signed expiring task receipt restricts task lookups. See [API details](docs/API.md).

The current hosting target is owner-private. Do not expose the paid analysis endpoint publicly without adding appropriate access and budget controls. There is no user-account or multi-device database layer in this prototype.

## Verification and delivery

```bash
npx tsc --noEmit
node --experimental-strip-types --test tests/api.test.mjs tests/capture-context.test.mjs
npm run build
```

Exact tested commands, browser checks and their limits are recorded in [acceptance evidence](docs/ACCEPTANCE.md). Development browser tests require Python Playwright and Chromium.

See [build decisions](docs/BUILD-DECISIONS.md), [submission draft](docs/SUBMISSION-DRAFT.md), and [demo recording script](docs/DEMO-SCRIPT.md). The repository is MIT licensed; included starter/vendor assets retain their license notices. Submission still requires a judge-accessible repository, screenshots and a publicly visible 1–3 minute video.

## Skill gate and improvement

The GitHub-sourced skills used for UI, React, API integration and testing are documented with provenance. We select skills for quality and fit; popularity does not establish correctness. Improvement loops select an observed defect or unmet acceptance condition, make one bounded change, run focused evidence, and request independent review at milestones. Passing areas are not repeatedly rewritten without a new reason.
