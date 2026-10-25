# Bounded technique guidance and review evidence

Checked 25 October 2026 using direct primary sources. This is an edited, finite browsing path, not an LLM, product recommender, personalized assessment or community. No new dependencies, API calls, remote fetching or product identity inference. General technique help is free and independent of portrait access.

## Method and acceptance, before content

Hypothesis: after selecting a plan, the user lacks even a relevant application starting point and source. A three-question help panel should let them find a supported technique, check its applicability, and inspect its original source without paying for a preview. Falsifier: irrelevant technique shown as applicable, unsupported product/physical claims, inaccessible source/context, or invented social evidence.

The 18 requests in `tests/fixtures/guidance-evaluation.json` were written before the guidance corpus. Cases cover three supported techniques, five missing/wrong tool or formula contexts, unknown question, unconfirmed and confirmed-but-unsupported product requests, shade/wear/allergy/reviews, and missing/stale/conflicting evidence. These are scripted contract evaluations, not a natural-language benchmark or human usefulness research. Resolver inputs are structured; there is no natural-language question box. Evidence-state test flags model abstention behavior only: the app does not automatically detect page changes or conflicting evidence on the internet.

Applied pinned Anthropic frontend-design and Vercel React guidance from `docs/skills`: question-led wording, deliberate category context, semantic label/select/checkbox/details, explicit empty state, no network waterfall or new service. Scope follows lean-build: exactly three questions, no speculative catalog. Existing planner appearance is reused.

## Claim → source → applicability → withheld claim

| Question / edited claim | Direct source and location | Applicability | Withheld / source limits |
|---|---|---|---|
| Lip line: use the opposite index finger outside the natural outline as a guide; glide corner toward center, upper then lower lip | [Shiseido Guide Makeup](https://corp.shiseido.com/en/sustainability/power-of-beauty/pdf/guide2.pdf), printed pp.4–9 | Guide designed for blind/low-vision users, slanted lipstick bullet; context disclosed | No liquid-lipstick advice, color/texture recommendation, guaranteed application result or applicability to every user. Publication date not stated in PDF. |
| Blush placement: high apple, blend toward ear, amount according to desired color | [Bobbi Brown Cheeks FAQ](https://www.bobbibrowncosmetics.ca/products/23824/makeup/face/cheeks), “Where do I apply blush?” | Cream/powder blush used on cheeks | One manufacturer's general starting suggestion, not ideal face-shape placement or matched shade. Commercial page; publication date not stated. |
| Eyeshadow: fluffy blending brush softens edge; back-and-forth socket blending | [M·A·C Ask an Artist](https://www.maccosmetics.co.uk/pages/how-to-apply-eyeshadow), application/blending paragraphs | Eye-labelled shadow and blending brush | Not finger technique, every eye-shape instruction, brush endorsement or validated physical outcome. By a pro M·A·C artist in Liverpool; publication date not stated. |
| Eyeshadow applicability boundary: use cosmetics intended for eye area; names/colors do not establish this | [FDA Eye Cosmetic Safety](https://www.fda.gov/cosmetics/cosmetic-products/eye-cosmetic-safety), safety checklist | Eye area | Regulator guidance, not a test of a user's product. Page lists updated 18 December 2006; checked again 25 October 2026. |

Short paraphrases only. Source pages contain broader marketing/health/skin-type claims not adopted. A source being a manufacturer establishes its provenance, not that every statement is universally true. No source is a verified review of a user's item. Source date and retrieval/check date remain separate. No automatic freshness assertion; recheck when content or formulation changes.

## Review scope

There are **zero genuine external review records** in this release. No ratings, people, usage conditions, “verified purchase,” consensus, duplicate counts or variant matching is fabricated. Product names/categories/hex colors do not confirm brand, exact formula or variant. Even a confirmed identity would not conjure review evidence; the resolver abstains. Private observations are a separate feature and cannot be counted as external reviews. Public posting, crawling/aggregation and a hosted community are outside this slice.

## Validation

`node --experimental-strip-types --test tests/guidance.test.mjs`: 18 prewritten cases plus source-metadata/zero-social-evidence invariant passed (19 tests). This proves deterministic branch behavior and traceability, not automatic source entailment or real application success. A reviewer must inspect paraphrases against the precise source locations above; root owns integrated desktop/mobile browser verification and overall build.
