# Accuracy and usefulness evidence audit

Reviewed October 24, 2026. No paid API calls were made for this audit. The previous synthetic-portrait run proves the network workflow only.

## Decision

The evidence supports investigating cosmetic image assessment, but does not validate Skinwise as a clinical instrument, treatment evaluator, or precise personal progress meter. No consulted publication identifies our exact SD REST API 2.1 engine build or establishes its smallest detectable longitudinal change. Product value currently comes from keeping observations and routines organized; whether its scores improve user decisions remains untested.

## Primary research

### Clinical case series, 2026

[Huang et al., Skin Parameter Scoring Using Artificial Intelligence](https://link.springer.com/article/10.1007/s13555-026-01966-w) tested investigator application v 1.67 against one blinded dermatologist:46 photos, 13 male/33 female; Fitzpatrick I–V counts 9/12/5/5/15, VI absent; estimated ages 10–79. Fluorescent lighting varied with flash. Overall 37% matched exactly and 46% differed by one five-point grade; 83% is their sum, not exact accuracy. Mean ICC was 0.41.

| Implemented metric | Within one grade | Human–AI ICC |
|---|---:|---:|
| Moisture |72%|0.05|
| Oiliness |80%|0.26|
| Texture |78%|0.41|
| Pores |80%|0.43|
| Redness |100%|0.68|
| Acne |80%|0.61|

The comparison transformed raw scores; patient-facing scores were inflated. Limitations include one rater, small sample, heterogeneous photos, and score binning. Funding text inconsistently states Perfect provided funding/model access and then says no funding/sponsorship; disclose this ambiguity. Feldman declares industry relationships and journal editorial membership. This is no validation of our current UI-score changes.

### Skin-type comparison, 2024 issue

[Kontzias et al., Validation across Fitzpatrick skin types](https://onlinelibrary.wiley.com/doi/10.1111/jocd.16024) studied 54 adults:mean age 50, 78% female, 63% White, 28% Black, 6% Asian, 4% Native American/Alaskan Native (rounded categories). Fitzpatrick I–II/III–IV/V–VI groups had 19/18/17 participants. An iOS tablet application and VISIA were compared using five metrics and one blinded dermatologist. Overall pairwise ranking agreement was 69% for the application versus 56% for VISIA. Application group totals were 71%, 75%, 61%; texture agreement in V–VI was 40%. Non-significant differences between correlation coefficients do not establish equivalence or fairness. Small groups and one rater limit inference. Perfect funded the study; Feldman disclosed industry relationships. These data do not demonstrate consistent performance for Indian smartphone users or our six-metric API configuration.

### Updated pore model, 2024

[Gantz et al., Validity of pore detection](https://onlinelibrary.wiley.com/doi/10.1111/jocd.16412) compared four updated models against the original model, VISIA, and one dermatologist using iPad Pro images under uniform lighting. There were 54 adults, 78% female, with Fitzpatrick groups 19/18/17. Best overall updated modelD reached 70.4% pairwise concordance; modelD's V–VI result was 66.7%. Different models performed best in different groups. Ties were removed. The endpoint 2.1 contract does not identify its engine as modelD. This is a small, controlled cross-sectional comparison, not evidence of precise longitudinal sensitivity. Funding/conflict details were not available in the retrieved publisher text; do not call this independently funded.

### Repeatability and device comparison, 2022

[Cook et al., Comparison of two devices](https://onlinelibrary.wiley.com/doi/full/10.1111/jocd.15434) enrolled 50 clinic patients:ages 15–83, 58% female, 76% Caucasian, 58% Fitzpatrick II. Actual acquisition used a 2021 iPad Pro 12.9-inch on a stand, frontal default camera without flash. Two consecutive captures occurred within one minute under constant room conditions. Tablet test–retest ICC was 0.990; Cronbach alpha 0.998. Pairwise ordering agreed with VISIA 67.7% overall; five metrics were spots, wrinkles, redness, texture, pores. Perfect funded the work and Feldman disclosed industry relationships. High repeatability under this setup does not quantify absolute error or smallest meaningful change in our UI scores, and does not validate arbitrary phones, lighting, or weeks-long tracking. Neither moisture nor oiliness was part of this five-metric device comparison.

[Cook et al., Initial validation](https://pubmed.ncbi.nlm.nih.gov/36126096/) reports 69% physician-ranking agreement on an iPad Pro, highest for erythema 83.7% and wrinkles 81.6%, lowest for oiliness 53.1%. The accessible abstract describes high retest reliability without enough details to reproduce an absolute error estimate. The [publisher funding disclosure](https://www.tandfonline.com/doi/abs/10.1080/09546634.2022.2127305) names Perfect Corporation. Full methods were inaccessible in this audit; no missing numbers are inferred.

## Exact applicability to Skinwise

[Current vendor reference](https://docs.perfectcorp.com/reference/ai_skin_analysis/v2.1) describes updated engines behind REST endpoint 2.1 and separate SD/HD actions, but does not map the deployed build to the studies above. API protocol numbering is not engine identity. The [official pinned GitHub interpretation skill](https://github.com/YouCam-API/skills/blob/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/skin-analysis-expert/references/interpretation.md) says UI scores are higher-is-better and raw-score direction may vary. It supplies integration guidance, not scientific validation. Publications and source methodology govern scientific claims.

No consulted source gives our SD 2.1 UI-score standard error of measurement, agreement limits, smallest detectable change, or patient-important change. Absence from this reviewed set is not proof no such study exists. Cross-sectional rankings, within-one-grade agreement, retest ICC, and percentage accuracy are different quantities and must not be substituted for one another. A stable wrong estimate can have excellent repeatability.

## Concrete claim limits

Use “photo-based appearance estimates” and identify YouCam, SD, endpoint 2.1, UI-score, and unknown model build. Describe moisture/oiliness as estimates rather than direct water/sebum measurements. Display a score as returned; do not present its fraction of 100 as percentage health or probability. Do not generate confidence percentages, healthy/unhealthy cutoffs, or automatic clinical priorities from unrelated metric scales.

A change can be described as a different returned score. It cannot yet be called improvement, deterioration, statistically significant change, or proof a product worked. Do not call a composite average “skin health” without validating the construct and weights. If photos are noncomparable or engine version is unknown, state that interpretation is limited. Symptoms and treatment decisions require appropriate professional evaluation; this app's cosmetic estimates should not determine them.

## Proposed validation protocol — recommendations, not completed work

1. Define intended use first: cosmetic journaling and reproducible photo estimates. Register which decisions the app should improve, each metric's intended interpretation, and known unsupported claims. Obtain the vendor's exact engine/build mapping, output transformations, training/validation overlap, subgroup evidence, and model-change policy. Save API method, capture device, image dimensions, and preprocessing with every consented test.
2. Separate software determinism from acquisition repeatability. With explicit participant consent and a budget, first resubmit the identical image to test inference stability. Then collect repeated new captures of the same person without a skin intervention, keeping camera, distance, angle, lighting, exposure, time, and recent skincare conditions fixed. Distinguish backend version changes from biological or photographic variation.
3. Deliberately vary capture conditions one at a time: phone family, camera, lighting direction/brightness, flash, pose, distance, compression, and cosmetic products. Randomize order. Include realistically diverse adult skin tones and intended user demographics; decide sample size using prespecified precision/power targets with statistical advice, rather than declaring a convenient number adequate. Report failures and exclusions by subgroup.
4. Estimate metric-specific within-person variation and paired difference distributions, bias, and agreement limits. Use an explicitly specified absolute-agreement ICC with confidence intervals, alongside absolute error. Derive a detectable-change rule only from the exact output scale and repeated-measures design; test assumptions before applying any formula. Avoid inventing a universal five- or ten-point threshold.
5. Assess validity against prespecified references: multiple blinded trained raters for visible appearance, plus appropriate calibrated physical measurements if claiming hydration or sebum. Harmonize definitions, independently score disagreements, and report per-metric and subgroup results. Do not treat another photograph algorithm as perfect ground truth.
6. For longitudinal utility, separately study unchanged controls and planned interventions with independently assessed outcomes. Evaluate responsiveness and meaningful change; use controls and prespecified analysis before attributing changes to a product. Test whether users understand uncertainty, avoid unnecessary purchases, and make better decisions. User liking and completed API calls are not outcome validity.
7. Before launch claims, publish the protocol, failures, uncertainty, subgroup gaps, version identifiers, and limitations. Gate progress labels and recommendations on evidence collected for the shipped version. Revalidate after engine or capture changes. This is future work requiring consent, funding, and potentially ethics review; none was performed in this audit.
