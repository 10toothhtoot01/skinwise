# YouCam integration research — 2026-10-24

## Skills selected and inspected

1. Vendor skill `skin-analysis-expert`, pinned revision `1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4`, saved under `work/skills/api-youcam/`. Source: https://github.com/YouCam-API/skills/tree/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/skin-analysis-expert . The official documentation directly links this repository: https://docs.perfectcorp.com/develop/agent_skills . GitHub API reports zero stars, so popularity is not evidence here; selected as authoritative protocol reference with independent official OpenAPI cross-check. Read SKILL.md and references/interpretation.md. Adopted its score direction, SD/HD separation, real-result-only policy, JSON format, and polling instead of duplicate paid task creation. Its interactive pre-run questions concern running an analysis, not building software; the application exposes the chosen six-concern tier and cost before invocation.
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

POST `/api/analyze`, multipart field `file`, JPEG/PNG <=8MB, short side>=480, long<=4096 ->202 `{status:'running',taskId,token,pollingInterval:10000,units:12}`. GET same route with query `taskId` and `token` -> `{status:'running'}` or `{status:'success',result:{id,date,source:'youcam',metrics:[{key,label,score}],concerns:[],method:{provider:'youcam',endpointVersion:'2.1',tier:'SD',scoreKind:'ui_score',modelVersion:null}}}`. Six SD actions: moisture,texture,pore,redness,acne,oiliness. GET `/api/status` reveals configured boolean only. All errors `{error,code}` with relevant HTTP status; never synthetic live scores. Signed expiring task receipts gate polling; fixed upstream host and presigned AWS destination check constrain networking. API key reads Cloudflare binding first, Node environment second. Timeout per provider call; no paid-task retries. Preserve pending task receipts in UI to avoid duplicate charges.

## Remaining external requirements

Credential configuration is present. The initial zero-cost official GET `/s2s/v1.0/client/credit` returned an empty package list. After the user confirmed redemption, a fresh lookup returned HTTP200/provider status200 with two active API packages of1000 and40units, totaling1040spendable units. A later live workflow test used an AI-generated adult portrait (no real person) and completed successfully; see `docs/LIVE-VERIFICATION.md`. Real-person accuracy remains unverified. No image is uploaded during mocked tests. Public hosting, real API verification, Devpost submission, and public demo-video publishing are separate external actions. These are not claimed completed by backend implementation.


## Verification and deployment boundary

Five mocked backend tests pass: byte/MIME/dimension validation, genuine-score normalization, exact upload/task/poll flow and signed receipts, missing configuration, and unexpected storage-host/provider-auth errors. TypeScript and scoped ESLint pass. Chunked multipart reads stop at9MB before parsing. Current hosting is owner-private; preserve platform access control. Publishing to arbitrary users requires deliberate budget/access controls first; provider limits do not replace app spending limits. The balance was rechecked after redemption and now reports1040spendable units; a synthetic-adult live test subsequently completed through the local API. Balance afterward was1028units, matching one12unit job. This proves integration, not real-skin validity.


Native Node verification command: `node --experimental-strip-types --test tests/api.test.mjs` passes all5tests. AnalysisError uses plain property declarations, so no transformation flag or additional dependency is required.


Live workflow proof: `docs/LIVE-VERIFICATION.md`. Runtime corrections: Workers-compatible `redirect:manual` (3xx rejected), and multipart framework limit9MB matching bounded parser overhead. Private task receipt and provider storage URLs are excluded from public evidence.


Truthfulness revision: numeric scores do not establish a comparable scale across different concerns. The API now returns `concerns:[]` rather than ranking action priorities. Labels use appearance/estimate terminology. Each result includes method metadata `{provider:"youcam",endpointVersion:"2.1",tier:"SD",scoreKind:"ui_score",modelVersion:null}`. Endpoint version is not a known model-engine version.
