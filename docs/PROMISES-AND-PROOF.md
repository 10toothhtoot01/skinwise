# What Skinwise can promise

The product is an observation journal with optional model estimates. It is not yet a validated way to identify effective skincare products. The interface must make this distinction where scores appear, rather than rely on a footer.

| Promise | Delivered behavior | Evidence / limit |
|---|---|---|
| Keep a faithful record | Save the person's chosen intention, dated comfort score and exact note; retain the intention context on later check-ins | Browser persistence/export tests. User reports are subjective; not objective symptoms. |
| Show actual provider output | Display supported YouCam UI scores and source; no synthetic fallback | One real provider job on a synthetic portrait; six metrics returned. Workflow proof only. |
| Explain what numbers mean | Appearance estimates, not percentages, diagnostic measures or confidence | Visible result explanation; vendor UI-scale documentation. No clinical calibration is claimed. |
| Show history without inventing improvement | Match source and metric; label differences as descriptive and uncertain | Matching-source test. Capture conditions/model build are not verified; meaningful-change threshold unknown. |
| Give control over local journal data | Export exact saved metadata and confirm local deletion | Browser equality/deletion tests. Vendor retention is separate. |

## Claims withheld

- “Very accurate”, a percentage accuracy guarantee, dermatologist-equivalent performance, or validity on every skin tone/device.
- Measuring physical hydration or sebum from these scores.
- Determining which product works, diagnosing a condition, prescribing care, or attributing a change to a product.
- Treating a +1, +5, or any arbitrary score change as meaningful improvement.
- Assuming endpoint version 2.1 identifies the exact algorithm model build evaluated in a paper.
- Ranking different metric scores as clinical priorities.

## Concrete use case

A person chooses to keep one part of their existing routine consistent. They record that intention and add dated comfort notes. When reviewing later, the app shows what they actually recorded alongside optional photo estimates. That preserves context they would otherwise need to remember. It does not conclude the routine helped, recommend a purchase, or claim savings. Whether this journal measurably improves decisions remains a user-study question.

## Validation before stronger claims

1. Define the exact claim and intended population before collecting results. Distinguish image appearance agreement, same-session repeatability, longitudinal sensitivity, and useful decisions.
2. Obtain provider model-build/score-transform details and evidence that applies to the exact SD API configuration. Endpoint version alone is insufficient.
3. With consent, collect repeat captures across representative devices, tones and conditions. Separate recapture noise from reprocessing the identical image. Include unsuitable images and measure appropriate rejection.
4. Use multiple blinded qualified raters for visible signs; use an appropriate physical reference instrument if claiming hydration or sebum measurement. Predefine reference labels and account for rater disagreement.
5. Estimate agreement/errors and confidence intervals by metric and subgroup on a held-out set. Evaluate repeatability and limits of agreement. Determine a meaningful-change threshold with suitable expertise; do not invent one from a few synthetic scores.
6. Test whether users can correctly interpret uncertain results and avoid causal conclusions. A future usefulness study must measure the promised decision outcome, not just clicks.
7. Keep unsupported claims withheld if any relevant gate fails. Document limitations and recalibrate after model changes.

This protocol is planned, not completed. A meaningful accuracy study cannot be manufactured by tomorrow's software deadline or established with one generated portrait.

## Capture practicality decision

Prefer the provider's guided camera checks over a homegrown “accuracy score.” Detect unsupported resolution and permission errors with specific recovery steps; keep upload available as explicitly unassessed visual quality. Validate file decoding and documented dimensions before paid analysis. Do not reject people based on phone price, inferred skin tone, or a whole-image brightness threshold. Capture-context fields are voluntary and self-reported, not automated verification.

A controlled Chromium fake-camera test loaded the actual SDK, which rejected its virtual camera label. This is evidence of a supported failure path, not real-hardware readiness. A real phone must still be exercised by its user. Document expected vendor errors rather than hide them globally. Known method mismatches (SD/HD, endpoint, score kind) withhold numerical deltas. Matching self-reported setup is helpful context but does not prove measurement accuracy.
