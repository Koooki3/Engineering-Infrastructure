# Skills reference

Generated from `skills-registry.json` and `skills-lock.json`.
CORE tree hashes pin bundled content. Public bundle pins include the source revision and every selected file.

## academic-research-plan

- **Category** AI/ML & Research
- **Tier** DOMAIN
- **Capabilities** research-planning
- **Triggers** Design source-grounded ML and robotics experiments.
- **Non goals** Presenting planned experiments as results.
- **Source** Local-only
- **Source path** academic-research-plan
- **License** CC-BY-NC-4.0 declared locally
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## jupyter-notebook

- **Category** AI/ML & Research
- **Tier** DOMAIN
- **Capabilities** notebook-engineering
- **Triggers** Create or maintain a runnable notebook with a reproducible structure.
- **Non goals** Ordinary edits already covered by native project tooling.
- **Source** https://github.com/openai/skills
- **Source path** skills/.curated/jupyter-notebook
- **License** Apache-2.0
- **Installation** stage-reference jupyter-notebook; isolated review, native adapter after authorization
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Publisher bundle files read and hash-pinned; functional runtime evaluation remains separate.
- **Dependencies** Python and the project notebook runtime
- **Conflicts** None recorded
- **Trust** Pinned upstream review lane with executable content.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `49f948faa9258a0c61caceaf225e179651397431`

## gh-fix-ci

- **Category** CI & Release
- **Tier** RECOMMENDED
- **Capabilities** ci-debugging
- **Triggers** An existing GitHub Actions PR check fails.
- **Non goals** Pipeline design and general debugging.
- **Source** https://github.com/openai/skills
- **Source path** skills/.curated/gh-fix-ci
- **License** Apache-2.0
- **Installation** stage-reference gh-fix-ci; isolated review, native adapter after authorization
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local provenance matches the pinned publisher and file inventory; the local variant carries adaptations. Runtime evaluation of the upstream bundle remains separate.
- **Dependencies** Authenticated GitHub CLI
- **Conflicts** None recorded
- **Trust** Pinned upstream review lane. Keep independently maintained variants under their existing ownership.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `49f948faa9258a0c61caceaf225e179651397431`

## constraint-ladder

- **Category** Core Engineering
- **Tier** RECOMMENDED
- **Capabilities** recurring-failures, mechanical-constraints
- **Triggers** A failure repeats and needs an enforceable constraint.
- **Non goals** One-off corrections and generic style guidance.
- **Source** Local-only
- **Source path** constraint-ladder
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** claude
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## engineering-workflow

- **Category** Core Engineering
- **Tier** CORE
- **Capabilities** engineering-workflow, implementation, debugging, verification, risk-routing, quality-gates, repository-synchronization, integration-deployment, worktree-governance, context-checkpoint, knowledge-distillation
- **Triggers** Substantive implementation, bug fixes, verification and delivery.
- **Non goals** Simple questions and domain-specific workflow rules.
- **Source** https://github.com/Koooki3/Engineering-Infrastructure
- **Source path** engineering-workflow-kit/engineering-workflow
- **License** Apache-2.0
- **Installation** Global bootstrap (bundled and hash-locked)
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Bundled source and offline regression suite
- **Dependencies** Python 3.9+, Git 2.31+ for the project lifecycle
- **Conflicts** None recorded
- **Trust** Bundled core
- **Status** BUNDLED
- **Verified** 2026-11-26
- **Version** `d59f2d40337cc0e469a8d26822a99ee61762650d4710a739564bce63b881b663`

## team-mode

- **Category** Core Engineering
- **Tier** RECOMMENDED
- **Capabilities** multi-agent
- **Triggers** Independent work with observable benefit and explicit delegation authority.
- **Non goals** Short or shared single-target changes.
- **Source** Local-only
- **Source path** team-mode
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## winui-app

- **Category** Desktop
- **Tier** DOMAIN
- **Capabilities** winui, desktop-development
- **Triggers** Implement or verify a Windows App SDK app.
- **Non goals** Non-Windows desktop and web development.
- **Source** Local-only
- **Source path** winui-app
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** Windows and Windows App SDK
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## project-docs

- **Category** Documentation
- **Tier** RECOMMENDED
- **Capabilities** project-documentation
- **Triggers** Write onboarding, architecture and debugging docs from repository evidence.
- **Non goals** Academic thesis sections and imaginary project details.
- **Source** Local-only
- **Source path** project-docs
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## frontend-design

- **Category** Frontend
- **Tier** DOMAIN
- **Capabilities** frontend-design
- **Triggers** Create a distinctive new interface or reshape an existing UI.
- **Non goals** Backend or performance-only requests.
- **Source** https://github.com/anthropics/skills
- **Source path** skills/frontend-design
- **License** Apache-2.0
- **Installation** stage-reference frontend-design; reviewed Markdown activation only
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Local source record and both source file hashes identify the upstream copy. Runtime evaluation remains separate.
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Pinned publisher copy. Auto-activation requires user-approved exact bytes and scope.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`

## vercel-react-best-practices

- **Category** Frontend
- **Tier** DOMAIN
- **Capabilities** react-performance
- **Triggers** Review React/Next.js performance against project versions.
- **Non goals** Static non-React sites and purely visual changes.
- **Source** https://github.com/vercel-labs/agent-skills
- **Source path** skills/react-best-practices
- **License** MIT declared in upstream frontmatter; the pinned tree has no separate license file
- **Installation** Review exact source and applicable legal terms using the native installer; no automatic bundle
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Local provenance records the exact upstream revision and adapted files. Full upstream runtime evaluation remains pending.
- **Dependencies** React/Next.js project
- **Conflicts** None recorded
- **Trust** Upstream reference; candidate review required
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `063bee94c3f4df8453406c830b0a7df0f2860278`

## web-accessibility

- **Category** Frontend
- **Tier** DOMAIN
- **Capabilities** web-accessibility
- **Triggers** Audit keyboard paths, semantics and assistive technology behavior.
- **Non goals** Legal compliance certification.
- **Source** https://github.com/addyosmani/web-quality-skills
- **Source path** skills/accessibility
- **License** MIT
- **Installation** stage-reference web-accessibility; isolated review, native adapter after authorization
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local provenance matches the pinned publisher and file inventory; the local variant carries adaptations. Runtime evaluation of the upstream bundle remains separate.
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Pinned upstream review lane. Keep independently maintained variants under their existing ownership.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `afa8da942115f2961fdbfa80807ea0b232ff6c00`

## gh-address-comments

- **Category** Git & GitHub
- **Tier** RECOMMENDED
- **Capabilities** pr-feedback
- **Triggers** Process requested code changes from existing review comments.
- **Non goals** Publishing replies or resolving threads without authorization.
- **Source** https://github.com/openai/skills
- **Source path** skills/.curated/gh-address-comments
- **License** Apache-2.0
- **Installation** stage-reference gh-address-comments; isolated review, native adapter after authorization
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local provenance matches the pinned publisher and file inventory; the local variant carries adaptations. Runtime evaluation of the upstream bundle remains separate.
- **Dependencies** GitHub connector or CLI
- **Conflicts** None recorded
- **Trust** Pinned upstream review lane. Keep independently maintained variants under their existing ownership.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `49f948faa9258a0c61caceaf225e179651397431`

## pr-authoring

- **Category** Git & GitHub
- **Tier** CORE
- **Capabilities** pr-authoring, pull-request, pr-body-lint
- **Triggers** Draft, update, review or validate a GitHub PR.
- **Non goals** General Git questions and ordinary coding.
- **Source** https://github.com/Koooki3/Engineering-Infrastructure
- **Source path** pr-authoring-kit/pr-authoring
- **License** Apache-2.0
- **Installation** Global bootstrap (bundled and hash-locked)
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Bundled source and offline regression suite
- **Dependencies** Python 3.9+ for lint
- **Conflicts** None recorded
- **Trust** Bundled core
- **Status** BUNDLED
- **Verified** 2026-11-26
- **Version** `afd40bd953fdef409d52f9f7fc382c4791cb5b83ff42eeaf4e64def9e50f8acf`

## playwright

- **Category** Runtime Verification
- **Tier** DOMAIN
- **Capabilities** browser-runtime-verification
- **Triggers** Use a browser CLI to inspect and verify a real web interaction.
- **Non goals** Ordinary edits already covered by native project tooling.
- **Source** https://github.com/openai/skills
- **Source path** skills/.curated/playwright
- **License** Apache-2.0
- **Installation** stage-reference playwright; isolated review, native adapter after authorization
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Publisher bundle files read and hash-pinned; functional runtime evaluation remains separate.
- **Dependencies** Node.js and the installed Playwright browser runtime
- **Conflicts** None recorded
- **Trust** Pinned upstream review lane with executable content.
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `49f948faa9258a0c61caceaf225e179651397431`

## adaptive-skills

- **Category** Skill Lifecycle
- **Tier** CORE
- **Capabilities** capability-resolution, skill-lifecycle, skill-review
- **Triggers** A required capability is missing or needs replacement.
- **Non goals** Routine work already covered by project tools.
- **Source** https://github.com/Koooki3/Engineering-Infrastructure
- **Source path** adaptive-skills-kit/adaptive-skills
- **License** Apache-2.0
- **Installation** Global bootstrap (bundled and hash-locked)
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Bundled source and offline regression suite
- **Dependencies** Python 3.9+
- **Conflicts** None recorded
- **Trust** Bundled core
- **Status** BUNDLED
- **Verified** 2026-11-26
- **Version** `247ae50343988726f187f75257d88e89456d16ece658d85187c2f528769e6b78`

## skills-maintenance

- **Category** Skill Lifecycle
- **Tier** RECOMMENDED
- **Capabilities** global-maintenance
- **Triggers** Maintaining a single user's skill catalog or global setup.
- **Non goals** Normal project delivery.
- **Source** Local-only
- **Source path** skills-maintenance
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## design-hub

- **Category** UI/UX
- **Tier** RECOMMENDED
- **Capabilities** design-routing
- **Triggers** Route Claude design tasks to the relevant visual skills.
- **Non goals** Pure engineering or business logic work.
- **Source** Local-only
- **Source path** design-hub
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** claude
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** design-workflow
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## design-workflow

- **Category** UI/UX
- **Tier** RECOMMENDED
- **Capabilities** design-routing
- **Triggers** Design work needs direction, implementation and evaluation skills.
- **Non goals** One small visual fix with an obvious route.
- **Source** Local-only
- **Source path** design-workflow
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** design-hub
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## oil-motion

- **Category** UI/UX
- **Tier** DOMAIN
- **Capabilities** media-animation
- **Triggers** Use cleared image sequences or video for scroll or gesture animation.
- **Non goals** Ordinary CSS micro-interactions.
- **Source** Local-only
- **Source path** oil-motion
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## oil-ui

- **Category** UI/UX
- **Tier** DOMAIN
- **Capabilities** ui-design, visual-review
- **Triggers** Design and validate a web or app interface against the existing product direction.
- **Non goals** Backend logic and circuit-level debugging.
- **Source** Local-only
- **Source path** oil-ui
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`
