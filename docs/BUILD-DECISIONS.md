# Skill-guided decisions

The project uses skills as reviewable methods, with official protocol documentation as the authority for API facts. No skill is asserted to be objectively “the best.” Selection considers provenance, scope match, maintenance, adoption and executable guidance.

| Decision | Skill source | Application and tradeoff |
|---|---|---|
| Product scope | lean-build (local); Anthropic frontend-design | One-change skincare observation loop, complete capture-to-journal flow; avoid ungrounded product prescriptions and unnecessary LLM dependency. |
| UI | [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Subject-specific field journal, deliberate typography/colors, two-pass plan then critique. Actual pinned provenance in research files. |
| Runtime/stack | Sites supplied runtime; [Vercel React best practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) | React/TypeScript Vinext for interactive forms and Workers server routes; preserve platform build adapter. Beta runtime portability is a material limitation; source includes exact lockfile. |
| Data | Vercel React best practices | Version browser storage; no stored photos. Keep live and demo records explicitly sourced. Browser-scoped persistence avoids adding accounts and a server database before lifecycle needs them. |
| API | [YouCam-API skills](https://github.com/YouCam-API/skills) plus official docs | Server-side upload, asynchronous tasks, bounded polling and normalized score semantics. Vendor expertise matters more than popularity for protocol correctness. |
| QA | [Anthropic webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Inspect actual rendered app before acting, meaningful end-to-end tests and screenshots. |
| UI review | [Vercel web interface guidelines](https://github.com/vercel-labs/web-interface-guidelines) | Keyboard/focus, semantic controls, labelled forms, status announcements, responsive overflow, reduced motion. |

## Improvement policy

Choose one observed defect or unmet acceptance condition per loop. State expected behavior, make a bounded change, verify, record outcome. Do not add features or repeatedly rewrite passing areas merely to consume time. Independent reviews cover functional correctness and visual usability.
