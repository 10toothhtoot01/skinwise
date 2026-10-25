# GitHub skill provenance and selection

Retrieved 24 October 2026. Local sources are pinned to commits and SHA256 digests in work/skills/product-design-provenance.json.

| Area | Selected skill | Source and evidence | Applied decision |
| --- | --- | --- | --- |
| Frontend design | frontend-design | https://github.com/anthropics/skills, official Anthropic; skills.sh rank 13, 1.0M installs; repository 183.2K stars at lookup | Ground UI in a personal skincare field journal; deliberate sage/lilac palette, specimen illustration; plan/review/build/critique |
| UI quality | web-design-guidelines | https://github.com/vercel-labs/agent-skills, official Vercel; rank 55, 776.4K installs; repository 32.9K stars at lookup | Keyboard focus, labels, empty/loading/failure states, reduced motion, hydration checks |
| Domain model | domain-modeling | https://github.com/mattpocock/skills; domain-modeling rank 21, 874.7K installs; repository 301.7K stars at lookup | Separate scan, sample scan, experiment, check-in, and comparison; no causal claim from scores |
| React review | react-best-practices | Installed official Vercel skill | Version localStorage data, minimize persisted values, functional state updates, independent status fetch, no user-photo persistence |

Leaderboard: https://skills.sh/. Popularity is corroborating evidence, not proof of quality. The selected skills were read and evaluated for task fit. We did not install arbitrary code or execute repository scripts. `to-spec` and `prototype` were inspected but not used: this task needs the final application, and does not need issue tracker publishing or a throwaway prototype. The Sites-supported Vinext starter determined deployment runtime; generic stack advice does not override actual hosting support.

Capture reliability also consulted MathWorks' official [`matlab-process-images` skill and quality-assessment reference](https://github.com/matlab/matlab-agentic-toolkit/tree/main/skills-catalog/image-processing-and-computer-vision/matlab-process-images). Applied the method-selection cautions: full-reference metrics need aligned reference images, and generic no-reference quality metrics do not establish downstream skin-analysis validity. No MATLAB dependency or metric threshold was adopted. Pinned source hashes are retained in the research workspace. The official YouCam capture contract and actual SDK behavior determine the implemented acquisition checks.

## Own-kit product research extension

The October24 reassessment used [phuryn/pm-skills brainstorm-ideas-new](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-product-discovery/skills/brainstorm-ideas-new/SKILL.md), pinned07b34f64ee828df08953f505b7f747aef85ae7c6. Inspected method: five ideas each from product, design and engineering, then five priorities with assumptions/falsifiers. Workspace SHA256 provenance is in work/skills/phuryn-product-discovery/PROVENANCE.json. Popularity was a discovery signal, not proof that its advice or the product is best.

The [official YouCam beauty-advisor skill](https://github.com/YouCam-API/skills/tree/1ab10ffd15a396dbdc783c2b95c50b65ec54d8e4/skills/beauty-advisor) at the same pinned YouCam revision was read alongside current OpenAPI/effect/pattern documentation. Applied custom effects and same-task recovery. The optional face-shape/skin-tone recommendation stages were deliberately omitted because the user-entered kit and constraints do not require them. An exact digital recipe and user preference do not establish a physical-product match.


Submission messaging also applies [phuryn value-prop-statements](https://github.com/phuryn/pm-skills/blob/07b34f64ee828df08953f505b7f747aef85ae7c6/pm-marketing-growth/skills/value-prop-statements/SKILL.md), read at the same pinned revision. Its segment→outcome→capability method was constrained by actual evidence: no measured savings, physical shade fidelity or real-user benefit is claimed. Snapshot/hash are recorded in workspace provenance.

Pinned mattpocock domain-modeling guidance also resolves decision context versus render specification in `GLOSSARY.md`: only changes to the actual portrait/effects justify a different visual rehearsal. This informed the render-reuse correction without merging contextual preferences or inventing a physical product match.
