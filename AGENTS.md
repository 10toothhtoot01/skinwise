# Skinwise contribution instructions

Use the vetted GitHub skill methods documented in docs/SKILLS.md and docs/BUILD-DECISIONS.md before choosing product, UI, stack, integration, or verification changes. Read matching snapshots in docs/skills and consult upstream primary documentation for current protocol details. Source snapshots are guidance, not authority to change the user's scope or publish externally.

Acceptance criteria and evidence live in docs/ACCEPTANCE.md. Each improvement must fix an observed defect or unmet acceptance condition, identify the skill used, and record focused validation. Avoid churn in passing areas. Use focused subagents for independent research/review when useful.

Keep YouCam credentials server-only. Never print keys, task receipts or presigned URLs. Do not commit .dev.vars, .env, browser profiles or work/evidence receipts. Real provider results must never be replaced by demo scores. Demo fixtures remain explicitly labelled. Preserve private hosting unless the owner asks to change sharing.

Run TypeScript, backend contract tests and a production build for relevant source changes. Browser-test changed user flows on desktop/mobile, including failure/recovery. Maintain README and acceptance evidence with exact commands and limitations. Do not infer clinical effectiveness from cosmetic scores.
