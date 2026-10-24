# Skinwise product and design decision record

Historical initial journal design. The current primary submission entry is the owned-kit planner; see OWN-KIT-PLANNER.md for its current product model and acceptance. The journal criteria below apply to the supporting skin workspace.

Skills applied: Anthropic frontend-design (intentional tokens, grounded subject matter, plan/review/build/critique); Matt Pocock domain-modeling (precise domain boundaries and edge scenarios); Vercel web-design-guidelines (interaction/accessibility review). Fetched SKILL.md documents and hashes are recorded in product-design-provenance.json. to-spec was researched but not invoked because its issue-tracker publishing workflow is outside this delegated task.

## Product model
A scan is a dated cosmetic observation, never a diagnosis. A sample scan is a disclosed fictional walkthrough and never mixed into live comparison. An experiment records one chosen routine change, start date, and personal notes. A check-in is a dated subjective observation. A comparison describes change in a shared metric from same-source scans and never attributes causation.

## Product acceptance
- A first-time visitor understands the loop: observe, change one thing, check in, compare.
- First view is a useful product overview, with one obvious primary action and a secondary sample walkthrough.
- Photo analysis requires explicit consent, valid image, bounded file size, and configured backend; sample mode remains useful without credentials and is always labeled.
- Photos are never persisted in browser storage. Journal data persists across reload, can export to JSON, and can be deleted after confirmation.
- Result provenance is visible; scores are cosmetic observations; no fabricated real scans or diagnoses.
- User can create one experiment, log a check-in, inspect recent history, and compare two same-source scans.
- Loading, empty, unavailable API, invalid upload, persistence failures, and small mobile layouts are deliberate states.
- Keyboard focus is visible; labels accessible; controls comfortably tappable; status changes announced.

## Visual plan
Palette: mist #F5F7F4; forest #254F42; sage #DDE8DB; lilac #E7E2F2; ink #243B34; muted #61716A. Body uses a legible geometric system sans; display uses Georgia with intentional open spacing. Layout is an airy field journal: narrow fixed desktop sidebar, broad left-aligned page, split hero with a botanical observation plate, horizontal next-step journal entry, and quiet evidence strips. Mobile condenses navigation into a horizontal row and stacks the hero. The memorable element is an illustrated specimen-like face with concentric observation contours. Borders encode section boundaries; rounded pale surfaces are reserved for the hero and meaningful actions rather than every line of content.

Critique before build: a generic skincare marketing hero would obscure the product; replace it with working journal actions and explicit baseline state. Avoid numerical improvement promises and dashboard scores on an empty journal. Navigation keeps the same nouns throughout.

## Stack recommendation
Use supplied Vinext + React + TypeScript scaffold because Sites explicitly supports this runtime. Keep credentials and provider requests server-only; render interactive state on client; persist bounded journal metadata in browser. Use existing lucide-react icons and CSS tokens, not a new UI kit. Review React implementation with official Vercel performance skill. No new paid service or infrastructure required.

## Independent visual review and readability refinement
Desktop and 390px mobile screenshots were inspected. The specimen illustration, spacious hierarchy, and journal grouping were retained. The first visual pass overused 8–11px supporting text and pale muted greens/lilacs. A bounded CSS pass increases important explanatory text to 13–14px, buttons to 13px, secondary metadata to 11–12px, and forms to 14px (16px on mobile to avoid native zoom). Muted text now uses darker forest, olive, and plum colors selected for normal-text contrast; no global numeric replacement or layout reset was used. Mobile navigation now stacks icon and label within four equal columns, preserving legible labels at 320px. Comparison numbers use tabular figures and journal history uses content visibility for long local journals. Focus, reduced motion, native controls, and the existing mobile hierarchy remain intact.
