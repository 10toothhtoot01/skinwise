# API-centered user value

## The problem this version addresses

An isolated appearance score does not show what an image model detected. A person may not know whether it refers to the area they care about, whether an image artifact is involved, or what to record. The product now starts with that uncertainty, rather than treating a score as an actionable answer.

## Shipped interaction

1. Choose a visible-appearance question: pores, redness, texture or blemish appearance.
2. Prepare a photo and consent to analysis. Four visible concerns use HD when the actual image short side is at least1080pixels (12units), otherwise SD when at least480pixels (9units). The interface discloses the tier/cost before submission; the server selects it independently.
3. Inspect the actual returned reference image and provider overlay. Switch concern without another analysis. For pores, inspect only the regional scores/images actually returned (the live test returned forehead, nose and cheek).
4. Zoom and scroll images, then record whether the selected concern/area matches the user's question, does not match, or remains uncertain. Save a note with its concern and region. Personal agreement is not clinical validation.
5. Return to an observation from its timeline. Refresh temporary images through its signed existing-task receipt. That GET does not create a charged task. Numeric observations and personal interpretations remain available when images cannot be recovered.

The journal supports this evidence workflow; it is no longer the main reason to call the API. No LLM fills missing regions, fabricates a mask, ranks unrelated metrics into clinical priorities, or recommends a product from a low score. Skin simulation was considered and deferred: a hypothetical edited image cannot establish a product's likely outcome. VTO would support a different shopping decision, but adds a different product workflow rather than fixing the missing evidence here.

## Real verification

A new live HD job used the same AI-generated adult QA portrait. It returned:

- Four HD whole-face concern scores (pores, redness, texture, blemish appearance).
- Three additional pore regions:forehead68,nose79,cheek69.
- Seven actual provider detection images and a reference image.

A Chromium browser retrieved that existing job, loaded the real whole-face and nose images, saved a review, and retained the three regional values. There were no new paid POSTs during the browser replay, no uncaught page errors, and no image URLs or task tokens in the journal record. These are workflow/capability checks on a synthetic portrait, not real-skin validity findings. The job itself cost12units; this was a justified extension test, separate from the earlier12unit SD integration test.

## Lifecycle and remaining limits

Signed task receipts are stored separately in this browser to enable explicit image refresh. They are excluded from journal exports and removed by Delete all data. Signed image URLs remain in session memory, not journal storage/export. The provider retains its own files under its policy. The app's receipt expires after24hours; images are not promised as permanent report attachments. Expiry/failure must show unavailable information without manufacturing another result or starting an analysis automatically.

The product can expose and organize model output. It cannot establish that a detection is correct, diagnose a condition, infer which product will work, or guarantee that a changed score is a biological change. Those require the separate validation evidence described in ACCURACY-EVIDENCE.md.

The free credit endpoint confirmed1,016units remain after the HD test (1,028before it). Across the original SD integration test and this HD capability test,24units were consumed. Existing-task browser replays and image refreshes made no new analysis POSTs.

A specific UI regression was found and corrected during this upgrade: choosing the nose overlay originally left the whole-face value in the reading heading. The heading now resolves the selected concern+region only. Tests assert regional values and restoration of the whole-face view, with missing scores staying unavailable. This is a software correctness fix; it does not establish the biological accuracy of either score.
