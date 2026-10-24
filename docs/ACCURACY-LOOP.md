# Accuracy improvement ledger

The loop is: define a user-visible claim, find a falsifying input, reproduce the failure, change its owning layer, rerun the regression and obtain independent review. A passing software test does not establish the provider's scientific accuracy. Skills are selected for relevant expertise, maintained provenance and inspectable methods; repository popularity alone is not an accuracy criterion.

## October 24: incomplete regional evidence

Claim: every returned detection region is inspectable, even when its numeric score is unavailable.

Counterexample: a cheek overlay without a valid UI score was retained by the adapter, but region navigation used score records only. A valid image was inaccessible. A whole-face image accompanying regional-only scores also lacked a return control.

Fix: navigation uses the union of returned image regions and score regions. Image-only regions explicitly say “No score returned”; the reading never substitutes another region's score. The browser regression reproduced the inaccessible cheek before the fix and now verifies cheek, score-only nose and image-only whole face. It uses intercepted responses, not a new paid analysis.

## October 24: unknown historical method

Claim: numerical differences are withheld when compared live observations have incompatible or unknown method metadata.

Counterexample: an older live score of 50 without method metadata and a current HD score of 75 produced +25. The compatibility check only ran when both method objects existed.

Fix: missing metadata on either live observation withholds the delta while retaining both recorded scores. Regression covers first, latest and both metadata objects missing. Fictional walkthrough comparisons remain available. Matching known fields still does not identify the provider model build or establish biological change.

## Sources and independent review

- [Official YouCam skill, pinned revision](https://github.com/YouCam-API/skills/tree/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/skin-analysis-expert): preserve actual UI scores and returned evidence; do not invent missing conditions. Its suggested cross-concern rankings are not adopted because their interpretation is unsupported for this intended use.
- [Anthropic webapp-testing skill, pinned revision](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/webapp-testing): test rendered browser behavior, inspect errors, and distinguish controlled fixtures from live responses.
- Latest vendor overview and v2.1 index fetched October 24 from the [official reference](https://docs.perfectcorp.com/reference/ai_skin_analysis). Local research snapshots preserve consulted text. No paid task was needed to reproduce either defect.
- An independent subagent reproduced the metadata defect, implemented its narrow patch, and separately reviewed the regional navigation fix and ran its browser regression.

## Next evidence gates

Investigate observed failures before adding heuristics. Real-person usefulness requires a consenting user to inspect their own concern and explain whether the evidence answered the question. Provider accuracy requires an applicable reference study, known model build and representative evaluation data. Neither can be replaced by repeated synthetic scans or generated confidence scores. See ACCURACY-EVIDENCE.md for the proposed validation protocol and its uncompleted gates.
