# Skinwise — Own-kit Look Lab

**Tagline:** Use what you own. Decide what to try.

**Primary entry:** `/planner` · **Platform:** browser application, desktop Chromium verified; mobile layout exercised at390px.

## Inspiration

A virtual makeup gallery can show many attractive results without answering the practical question before an occasion: “What can I plan with the products I already have and the time I have left?” We put that decision before rendering. The person supplies their kit and limits; our software determines feasible combinations; YouCam supplies illustrative previews; the person chooses what to try or opts for no added makeup.

## What it does

Enter up to nine owned products across matte lip color, blush and single-color eye shadow. Set a time estimate, a maximum product count, and required or excluded steps. The solver enumerates the bounded combination space, enforces those constraints and explains when nothing fits. Three starting alternatives favor speed and structural variety; an expandable catalog exposes every feasible combination. Any can be chosen and exported for free without a photo or API call. The starters are a variety heuristic, not an attractiveness score.

Optional YouCam previews use the same prepared original for every option. The user can compare available images, prefer either, record a tie or reject both. A preference graph preserves conflicts rather than forcing a winner. The user explicitly selects a plan and exports the kit, constraints, digital recipe, decision trail and selection basis: entered constraints, a loaded illustrative preview, or no added makeup. Any feasible recipe can open one focused optional preview without changing the kit or losing earlier decisions. Choosing no added makeup is an explicit opt-out, not a claim that an unmet required step was satisfied.

## How we built it

React and TypeScript run on Vinext and Cloudflare Workers. The server recomputes recipe feasibility before calling YouCam Makeup VTO. It uploads the image through the File API, starts the asynchronous makeup task and provides a signed receipt for GET-only recovery. Effects explicitly set skin smoothing and lip morphology to zero. Results come from the provider; no generated success is substituted after an error.

Our contribution is the constraint solver, infeasibility explanations, bounded comparison design, preference graph, original-photo ownership checks, exact-effect task reuse across changed planning limits, and decision export. Browser storage failures are visible; unreadable sessions are preserved; separate private backup/restore files retain task access. Ordinary plan exports exclude photos, result URLs and access receipts. API credentials remain on the server.

A separate skin evidence workspace at `/` can inspect real YouCam skin detection images and returned regional scores. It does not determine makeup suitability, health or treatment. It is a supporting capability, not a prerequisite for the planner.

## What we verified

Four real YouCam jobs completed on a labelled AI-generated adult portrait: two skin-analysis jobs and two makeup configurations, including the complete three-effect recipe. The most recent render-reuse release passed24planner/recovery/decision/reuse browser cases; earlier unchanged core flows have31additional browser cases and19Node contract/context/solver tests. TypeScript, scoped changed-component lint and production builds passed. Deployed checks verified real existing-task retrieval and preserved invalid browser data. An independent subset oracle matched69,120constraint cases across six fixed kits. Tests distinguish mocked responses, fictional kits and actual provider output.

## What remains uncertain

The prototype uses approximate user-entered RGB colors, fixed digital effect settings and additive user-entered time estimates. It does not recognize SKUs or guarantee physical shade, application time, wear, comfort or outcome. No intended user has yet tested it; no benefit or savings claim has been established. A prepared pilot compares it with an ordinary swatch/product board and observes physical follow-through. Physical-phone camera coverage and exact-engine skin validity remain unverified.

## Links and submission status

- Working private entry: https://skinwise-journal.bonnypuppy8192.chatgpt.site/planner
- Source: complete MIT-licensed source archive prepared; **judge-accessible repository URL not yet supplied**.
- Primary recorded demo: `outputs/skinwise-planner-demo.mp4`,106.28seconds, actual UI with synthetic portrait / fictional kit / actual completed YouCam output replay labels. **Public video URL not yet supplied**.
- Screenshots, captions and final access checklist: `outputs/submission/`.

This is prepared submission text, not a claim that a Devpost entry, public upload, judge access, eligibility or final submission has been completed. The current [official rules](https://youcam-api-skin-ai-ecommerce.devpost.com/rules) must govern final entry.
