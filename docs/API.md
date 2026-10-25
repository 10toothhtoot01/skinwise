# YouCam integration research — 2026-10-24

This file contains protocol notes and dated integration history. Historical credit balances and test counts below are observations from those stages, not current account checks or the complete current suite. The primary product is the [own-kit planner](OWN-KIT-PLANNER.md); its API contract is in “Owned-kit makeup previews”. The current skin profile contract is in “Implemented contract for frontend”.

## Skills selected and inspected

1. Vendor skill `skin-analysis-expert`, pinned revision `1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4`, saved under `work/skills/api-youcam/`. Source: https://github.com/YouCam-API/skills/tree/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/skin-analysis-expert . The official documentation directly links this repository: https://docs.perfectcorp.com/develop/agent_skills . GitHub API reports zero stars, so popularity is not evidence here; selected as authoritative protocol reference with independent official OpenAPI cross-check. Read SKILL.md and references/interpretation.md. Adopted its score direction, SD/HD separation, real-result-only policy, JSON format, and polling instead of duplicate paid task creation. Its interactive pre-run questions concern running an analysis, not building software; the initial integration exposed six SD concerns; the current visible profile exposes four concerns and its dimension-dependent tier/cost before invocation.
2. Anthropic `webapp-testing`, pinned revision `dbd4588f9e1033efb41dad4bef2f7947c8993d44`, saved under `work/skills/api-testing/`. Source: https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/webapp-testing . GitHub API reported 183,269 stars. Read SKILL.md; relevant for parent browser verification. Leaderboard checked first at https://skills.sh/ . No unsupported install-count claim is made; no observed count for vendor skill.
3. Read installed Vercel `next-best-practices` upstream skill for server route conventions, then used native Request/Response handlers and kept credentials in server modules. Its linked route-handler resource was unavailable in the installed package; did not invent missing guidance.

## Official API and interpretation

Latest v2.1 endpoints: POST `/s2s/v2.1/task/skin-analysis` and GET `/s2s/v2.1/task/skin-analysis/{task_id}`. Choose `format:json`; the default ZIP has a different schema. Poll every ten seconds; asynchronous completion has no documented maximum that guarantees a single 60-second request. Schema is in downloaded `work/research/youcam-openapi.json` from https://docs.perfectcorp.com/_bundle/reference/ai_skin_analysis.json?download= and human reference https://docs.perfectcorp.com/reference/ai_skin_analysis/v2.1 . Body uses `src_file_id`, `dst_actions`, `format`, optional `miniserver_args`; do not claim Camera Kit capture if ordinary upload was used.

Host and bearer setup: https://docs.perfectcorp.com/develop/api_server and https://docs.perfectcorp.com/develop/quick_start_guide . Fixed host is https://yce-api-01.makeupar.com; header `Authorization: Bearer <key>`. Server key was later supplied by the project owner and placed in ignored `.dev.vars`; it was read only into process memory for a zero-cost balance lookup. No secret was printed.

Upload workflow and score background: https://docs.perfectcorp.com/reference/ai_skin_analysis . POST `/s2s/v2.0/file` with `{files:[{content_type,file_name,file_size}]}`; response `data.files[0]` has `file_id`, `requests:[{url,method,headers}]`. PUT actual bytes to the presigned storage URL before creating the task. Never forward bearer credentials to storage. Task create returns `data.task_id`; poll returns `data.task_status` (`running`, `success`, `error`). JSON results `data.results.output` contains `type`, optional `region`, `ui_score`, `raw_score`, `mask_urls`. Expose only returned `ui_score`; higher means better condition. Raw-score direction can vary by concern; never invert UI scores. Missing fields must remain missing.

The same overview lists tier costs: 1–4 concerns 9 SD/12 HD units; 5–8 concerns 12 SD/16 HD; 9–12 concerns 14 SD/20 HD; 13–16 concerns 16 SD/22 HD. Six SD concerns therefore cost 12 units. Successful tasks consume units. Do not mix SD and HD actions. Vendor overview states SD short side >=480; v2.1 resizes automatically; app caps accepted long side at4096 and should resize to2560 before sending when possible.

## Rate and retention caveats

https://docs.perfectcorp.com/develop/rate_limit says both IP and token limits are 250 requests per 300 seconds and returns429. Its 5QPS recommendation is inconsistent with that rolling total; honor the stricter total and use10-second polling.

https://docs.perfectcorp.com/develop/file_retention_period says uploaded/generated files and task IDs last30days; download URLs last2hours and may be refreshed by task lookup. Older task-specific material still says24hours. Do not promise immediate vendor deletion or long-term hosted mask availability. Application receipt expires after24hours; local saved reports retain numeric values only. A backend can be built without credentials; genuine provider execution requires a valid key and units; both were subsequently supplied and a synthetic-input workflow test succeeded.

## Hackathon and India

Rules: https://youcam-api-skin-ai-ecommerce.devpost.com/rules . At least one YouCam API must power a working prototype. Repository and runnable testing access, English materials, screenshots, and a public1–3minute demo are needed. Judges assess implementation, design, impact, and originality. Submission closes November2,2026 at11:45EST, which is22:15IST. Age-of-majority and other eligibility rules apply. India is absent from the listed excluded territories; this is a rules reading, not a personal eligibility determination.

Resources: https://youcam-api-skin-ai-ecommerce.devpost.com/resources . Registration yields an emailed redeem code for1000units. India-specific links point to https://yce.makeupar.com/ai-api and https://docs.makeupar.com/develop/introduction ; use India console https://yce.makeupar.com/api-console/ . India terms link https://www.makeupar.com/perfectbeauty/youcam/terms-of-service-api . No separate India endpoint host was specified in the consulted resources.

## Implemented contract for frontend

POST `/api/analyze`, multipart `file`, optional `profile=visible`, JPEG/PNG <=8MB, short side>=480, long<=4096. Missing profile preserves the legacy six SD concerns at12units. Visible profile selects four visible-concern actions pore/redness/texture/acne: HD when parsed image dimensions have short side>=1080 (12units), otherwise SD (9units). The visible profile requests provider overlays; legacy jobs retain raw masks. No `pf_camera_kit` flag is forwarded because its effect is undocumented.

HTTP202 response: `{status:'running',taskId,token,pollingInterval:10000,units,actions,method}`. `method` is `{provider:'youcam',endpointVersion:'2.1',tier:'SD'|'HD',scoreKind:'ui_score',modelVersion:null}`. For visible jobs, the token has three parts: expiry, base64url metadata, HMAC. The MAC binds task ID, expiry and exact metadata. Legacy two-part receipts remain valid and identify SD/raw-mask behavior. Receipt validity is conservatively24hours despite conflicting vendor24hour/30day documentation. No paid-task retries.

GET the same route with `taskId` and `token`: `{status:'running'}` or `{status:'success',result,visuals}`. `result` has `{id,date,source:'youcam',metrics:[{key,label,score}],concerns:[],method,regions?:[{key,label,region,score}]}`. Metric keys are canonical (e.g. `pore` for `hd_pore`); whole/absent-region values form `metrics`, and only actually returned non-whole region scores form `regions`. Missing/nonfinite/out-of-range scores stay absent. No score or detected-area priority is fabricated. A regional-only valid result can have an empty metrics array.

`visuals` is ephemeral and separate: `{availability:'temporary',originalUrl?:string,items:[{key,region,url,kind:'overlay'|'mask'}]}`. The reference image comes only from returned `resize_image`; each image item comes only from returned concern `mask_urls`. Missing region is represented as `whole` for display, with no inferred regional score. Only HTTPS AWS-hosted URLs without embedded credentials or nonstandard ports are admitted. No photos or signed URLs belong in persistent analysis/journal exports. GET refreshes the existing provider task and can return fresh links without creating a paid analysis. After receipt expiry, return unavailable rather than automatically create another job. Actual image download/retention windows are provider controlled; no exact per-image expiry is asserted.

GET `/api/status` reveals configured boolean only. Errors use `{error,code}` with relevant HTTP status. Header parsing validates MIME signatures and dimensions on the server; it is not full pixel decoding or a capture-quality assessment. Client decoded image validation complements this; real capture readiness remains separately tested. Signed expiring task receipts gate polling; fixed upstream host and presigned AWS destination checks constrain networking. API keys use Cloudflare bindings first, Node environment second. Provider calls are time bounded. Preserve pending receipts to prevent duplicate charges.

## Visible explorer validation

Applied the pinned official YouCam skill protocol and local surgical-patch method to the observed loss of provider regions/images. Focused tests cover exact HD/SD actions and costs, signed metadata tampering, legacy receipt compatibility, real region preservation, absent/nonfinite scores, image URL filtering, overlay/mask identity, and no invented images. Research rationale and acceptance matrix: `outputs/API-VALUE-RESEARCH.md` in the outer workspace.

## Remaining external requirements

Credential configuration is present. The initial zero-cost official GET `/s2s/v1.0/client/credit` returned an empty package list. After the user confirmed redemption, a fresh lookup returned HTTP200/provider status200 with two active API packages of1000 and40units, totaling1040spendable units. A later live workflow test used an AI-generated adult portrait (no real person) and completed successfully; see `docs/LIVE-VERIFICATION.md`. Real-person accuracy remains unverified. No image is uploaded during mocked tests. Public hosting, real API verification, Devpost submission, and public demo-video publishing are separate external actions. These are not claimed completed by backend implementation.


## Historical initial verification and deployment boundary

Five mocked backend tests pass: byte/MIME/dimension validation, genuine-score normalization, exact upload/task/poll flow and signed receipts, missing configuration, and unexpected storage-host/provider-auth errors. TypeScript and scoped ESLint pass. Chunked multipart reads stop at9MB before parsing. Current hosting is owner-private; preserve platform access control. Publishing to arbitrary users requires deliberate budget/access controls first; provider limits do not replace app spending limits. The balance was rechecked after redemption and now reports1040spendable units; a synthetic-adult live test subsequently completed through the local API. Balance afterward was1028units, matching one12unit job. This proves integration, not real-skin validity.


Initial Node verification command: `node --experimental-strip-types --test tests/api.test.mjs` passes all5tests. AnalysisError uses plain property declarations, so no transformation flag or additional dependency is required.


Live workflow proof: `docs/LIVE-VERIFICATION.md`. Runtime corrections: Workers-compatible `redirect:manual` (3xx rejected), and multipart framework limit9MB matching bounded parser overhead. Private task receipt and provider storage URLs are excluded from public evidence.


Truthfulness revision: numeric scores do not establish a comparable scale across different concerns. The API now returns `concerns:[]` rather than ranking action priorities. Labels use appearance/estimate terminology. The initial SD result includes method metadata `{provider:"youcam",endpointVersion:"2.1",tier:"SD",scoreKind:"ui_score",modelVersion:null}`; the current visible profile may instead identify HD as described above. Endpoint version is not a known model-engine version.

## Owned-kit makeup previews

`POST /api/makeup` accepts bounded multipart fields `file`, `plan` (JSON `{products,rules}`) and `recipeId`. The server validates the kit/constraint schema, recomputes feasible recipes and refuses a nonmember before any upstream request. Valid prepared JPEG/PNG input has a short side at least480 and long side at most1024; the existing8MB application limit applies. This is a conservative app envelope, not a complete face-quality check.

The adapter uses the existing file-metadata→signed bytePUT flow, then `POST /s2s/v2.0/task/makeup-vto` with `src_file_id`, `version:'1.0'` and server-constructed effects. It explicitly zeroes both skin-smoothing fields and lip morphology. The response contains a24hour HMAC task receipt signed with a makeup-specific domain prefix. `GET /api/makeup?taskId=...&token=...` validates it before upstream GET; it accepts documented running states and the documented results URL shapes, retaining only a real HTTPS AWS destination. No API key is returned or sent to the upload host.

Each explicit start costs1unit according to the consulted provider documentation; no unit is spent by the local constraint solver. GET task checks and image refreshes create no replacement job. A failed/ambiguous start can have reached the provider: the UI never silently retries a POST. The owner-private hosting boundary is preserved. The50task session guard is not a server-wide budget or rate-limit policy.


The browser session stores a versioned rendering-settings snapshot on new makeup receipts. Contextual recipe keys remain separate. Compatible exact-effect tasks on the same prepared portrait are retrieved with GET across planning-limit/metadata changes; no duplicate receipt alias is added. Changing the portrait clears that session's tasks after confirmation. The snapshot is client bookkeeping rather than a provider-signed settings attestation; the server-side signed task token and upstream request protocol are unchanged.
