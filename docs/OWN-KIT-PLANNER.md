# Own-kit look lab: software contribution and proof

Research and implementation, October 24, 2026. Experimental route: `/planner`. The existing skin evidence workflow remains available. This is a product hypothesis with a working implementation, not a validated claim of consumer benefit or algorithmic novelty.

## Consumer job

“I have an occasion, a few products, and a time limit. Which combinations can I actually plan to use, and which one do I prefer?” The user's entered kit, exclusions, required steps and time estimates define feasibility. The renderer supplies illustrative images; it does not infer suitability, product identity, physical shade or real-world performance.

## Work performed by our software

1. **Finite constraint solver.** Enumerate zero or one product for each supported step, remove the empty recipe, enforce required/excluded categories, maximum product count and the exact sum of user-entered minutes. With at most nine products across three categories, the largest search is 63 nonempty combinations. No unavailable product or prohibited step is invented. Infeasible requests receive a specific missing-item, conflicting-rule, product-count or minimum-time explanation.
2. **Bounded comparison design.** Show at most three feasible options: the quickest first, then farthest-first structural variety using differing product/step identities. This is a deterministic diversity heuristic, not a beauty ranking or claim of statistical optimality. It limits what the user needs to inspect without hiding the total feasible count.
3. **Controlled rendering.** Recompute feasibility on the server before spending a unit. Build effects from the selected owned items, never accept arbitrary client-supplied effects. Every render starts from the same prepared original. Explicitly disable default skin smoothing and lip morphology. No generated result is fed back as the next input.
4. **Preference graph.** Record explicit left/right preferences, ties and rejection of both. Ask an unobserved pair with low previous participation; do not infer unasked comparisons from transitivity. Surface cycles without a forced winner or confidence percentage. The user explicitly chooses the final plan. A comparison clears the previous choice; rejected options cannot be chosen until comparisons are reset. Changing occasion or constraints clears contextual choices.
5. **Provenance and recovery.** SHA-256 of the prepared portrait distinguishes the same original from a replacement. Reselecting the same prepared bytes preserves paid-task receipts; replacing a portrait asks before dropping them. HMAC receipts have a makeup-specific signing domain, preventing reuse as skin-analysis receipts. GET retrieves the same task; refresh never starts another paid render. A deliberate 50-task session limit prevents a new paid request from exceeding the recoverable storage schema.
6. **Actionable handoff.** Export the entered kit, occasion, constraints, user estimates, chosen recipe, exact digital settings and labelled comparison trail. Exclude photos, temporary image URLs, fingerprints and access receipts. Choosing no added makeup and exporting unresolved choices are valid outcomes.

## Scope and precise promises

The first slice supports matte lip color, blush and one-color eye shadow. The fixed preview intensity is 50; blush/eye shadow use the vendor's documented `1color1` pattern. RGB colors are approximate user inputs, not recognized SKUs. A digital effect configuration is not a calibrated physical application tutorial. Time estimates are user-entered and additive, not an observed completion-time promise. No allergy, wear-time, exact-shade, attractiveness or product-effectiveness inference is made.

The client decodes the image, resizes without enlargement to a maximum long side of 1024, exports JPEG at quality .95 and requires the short side to remain at least 480. This deliberately conservative application envelope fits the conflicting overview/error dimension guidance. It does not validate face width, blur or pose. The server checks signatures/header dimensions, not a complete image decode. Temporary images must actually load before they enter comparisons or become selectable. Recorded rejection decisions survive image expiry/reload.

Session metadata, product names, a portrait fingerprint and private recovery receipts persist in this browser tab when session storage is available. Photos and result URLs remain in memory only. A tab/session close may lose recovery access. Provider retention is disclosed separately. The site remains private; the session cap is a user-experience safeguard, not a global API budget control.

## Skills and primary protocol sources

- Product hypothesis and 15 perspective seeds: [phuryn brainstorm-ideas-new](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-product-discovery/skills/brainstorm-ideas-new/SKILL.md). Pinned snapshot and SHA256 in the workspace provenance record. The alternative/assumption matrix is in `outputs/RESEARCH-USER-VALUE.md`.
- API: [official YouCam beauty-advisor skill](https://github.com/YouCam-API/skills/tree/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/beauty-advisor), current [Makeup VTO protocol](https://docs.perfectcorp.com/reference/makeup_vto/section/overview) and downloaded OpenAPI. Use parameterized effects and same-task polling. Face-shape/skin-tone recommendation stages are intentionally omitted: they are unnecessary to the owned-kit job and would add unsupported suitability inference.
- UI and QA: pinned Anthropic frontend-design/webapp-testing and Vercel React skills already documented in SKILLS.md; bounded implementation and independent review under project contribution instructions.

## Acceptance and observed limits

Contract tests cover constraints, infeasibility explanations, deterministic shortlist, actual effect parameters, preference ties/cycles/rejections, server feasibility enforcement before upstream work, and signed GET recovery. Browser tests cover actual rendered behavior, mobile layout, fractional input, no paid sample workflow, expired images, source replacement, reload recovery, contextual decisions and private export boundaries. The release's exact results are appended to ACCEPTANCE.md.

The live integration uses only a clearly labelled generated adult portrait. A returned image and completed task prove protocol execution, not identity preservation, physical shade accuracy or real-user usefulness. The two planned integration hypotheses are single-lip execution and a full three-effect feasible combination. Paid jobs are not repeated for replay.

## Next validation gate

Observe an intended user with an actual occasion and their actual kit. Compare this workflow against a simple swatch/photo board, varying task order. Record input burden, constraints met, physical application time, rendering failures, rejected options and whether the final choice is used or regretted. If the solver and previews do not improve this concrete decision, simplify or reject the concept. Software test counts cannot substitute for this gate.

## Browser storage failure and private recovery

An October24 follow-up audit reproduced two receipt-loss paths: an invalid saved session was overwritten by the empty fallback, and a browser write exception left a completed paid task only in memory with no warning. A subsequent explicit user retry after reload could therefore start another task; no automatic duplicate POST was observed.

Unreadable saved bytes are now preserved until explicit clear or valid replacement, with byte-exact original export. New paid starts require a successful session write and readback before contacting the API. If storage fails after a task starts, the receipt remains in memory, the failure is visible, and existing-task GET checks remain available. Storage can still fail after preflight; no browser write check can guarantee the later write.

A separate **private recovery file** contains the session metadata, portrait fingerprint and signed task receipts, but no photos, returned image URLs or server API key. Keep it private: it grants access to those tasks until their receipts expire. Valid import replaces the session after confirmation, invalidates in-flight work and clears current photo/image state. It makes no API call; the user explicitly checks existing tasks afterward. Invalid imports preserve the current session, and malformed JSON errors do not echo the file's contents. This file is different from the ordinary shareable plan export, which still excludes receipts and fingerprints.

## Portrait preparation ownership

Decoding/resizing/hashing a newly selected portrait pauses preview checks and new paid starts. Consent is cleared and cannot be granted until the current preparation finishes. Synchronous handler guards complement disabled controls. Only the latest selection may finish preparation; clear/restore invalidates pending preparation. A preview request already in flight prevents starting a replacement selection. This prevents a task on the old portrait from losing its receipt when a slower replacement finishes.
