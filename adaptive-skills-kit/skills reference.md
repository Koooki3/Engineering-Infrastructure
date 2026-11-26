# Skills reference

Generated from `skills-registry.json` and `skills-lock.json`.
The CORE tree hashes pin bundled content. Local references require their own reviewed source and pin.

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

## gh-fix-ci

- **Category** CI & Release
- **Tier** RECOMMENDED
- **Capabilities** ci-debugging
- **Triggers** An existing GitHub Actions PR check fails.
- **Non goals** Pipeline design and general debugging.
- **Source** Local-only
- **Source path** gh-fix-ci
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** Authenticated GitHub CLI
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

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
- **Capabilities** engineering-workflow, implementation, debugging, verification, risk-routing, quality-gates
- **Triggers** Substantive implementation, bug fixes, verification and delivery.
- **Non goals** Simple questions and domain-specific workflow rules.
- **Source** https://github.com/Koooki3/Engineering-Infrastructure
- **Source path** engineering-workflow-kit/engineering-workflow
- **License** Apache-2.0
- **Installation** Global bootstrap (bundled and hash-locked)
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Bundled source and offline regression suite
- **Dependencies** Python 3.9+, Git for bound evidence
- **Conflicts** None recorded
- **Trust** Bundled core
- **Status** BUNDLED
- **Verified** 2026-11-26
- **Version** `3915ad2418688674912dbb9fad9e86b33c6edb49182a33c6075c5ede1a7c540f`

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
- **License** Publisher-specific terms; read LICENSE.txt
- **Installation** Review upstream terms and pin an exact revision before acquisition
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Publisher source and corresponding local name reviewed; exact content equivalence unverified
- **Dependencies** None recorded
- **Conflicts** None recorded
- **Trust** Upstream reference; candidate review required
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## vercel-react-best-practices

- **Category** Frontend
- **Tier** DOMAIN
- **Capabilities** react-performance
- **Triggers** Review React/Next.js performance against project versions.
- **Non goals** Static non-React sites and purely visual changes.
- **Source** https://github.com/vercel-labs/agent-skills
- **Source path** skills/react-best-practices
- **License** MIT upstream; local derivative requires separate review
- **Installation** Review upstream terms and pin an exact revision before acquisition
- **Agents** codex, claude, opencode, antigravity
- **Os** windows, linux, macos
- **Evidence** Publisher source and corresponding local name reviewed; exact content equivalence unverified
- **Dependencies** React/Next.js project
- **Conflicts** None recorded
- **Trust** Upstream reference; candidate review required
- **Status** REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

## web-accessibility

- **Category** Frontend
- **Tier** DOMAIN
- **Capabilities** web-accessibility
- **Triggers** Audit keyboard paths, semantics and assistive technology behavior.
- **Non goals** Legal compliance certification.
- **Source** Local-only
- **Source path** web-accessibility
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

## gh-address-comments

- **Category** Git & GitHub
- **Tier** RECOMMENDED
- **Capabilities** pr-feedback
- **Triggers** Process requested code changes from existing review comments.
- **Non goals** Publishing replies or resolving threads without authorization.
- **Source** Local-only
- **Source path** gh-address-comments
- **License** Distribution permission unverified
- **Installation** Use an independently installed, reviewed copy
- **Agents** codex
- **Os** windows, linux, macos
- **Evidence** Local metadata inspected; independent runtime evaluation required
- **Dependencies** GitHub connector or CLI
- **Conflicts** None recorded
- **Trust** Independent local asset; do not redistribute
- **Status** LOCAL_REFERENCE
- **Verified** 2026-11-26
- **Version** `Pin during local review`

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
- **Version** `d8a7b82e4164f2d7f0572ac6d1b72d4e3947aa4fc3e071b40431f2e7317ab562`

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
