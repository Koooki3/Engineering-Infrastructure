# Operational verification

The initial acceptance covered `34ac407`, following `8bb4486`. Windows and WSL each passed 71 Engineering Workflow tests, 13 Adaptive Skills tests, and the generated catalog consistency check.

## Correctness boundaries

- The previous implementation reused the original deployment reference set after a different named ref resolved to the same commit. The regression now exercises receipt reconciliation, changed adapter content, a failed revalidation and a successful same-commit rebuild. The verified rollback records retain distinct identities even when the resulting artifact bytes match.
- A rejecting Git reference-transaction hook was bypassed by the previous invocation. The native regression confirms the hook can refuse a fast-forward and keep the branch tip intact.
- Contract discovery and dry-run review operate on tracked entrypoints. Registration uses the chosen candidate and an inactive-state probe. A differing existing contract requires explicit reconciliation. The delivery gate reports applicable checks, including blocked or pending work.

## Native project acceptance

Used a separate clone and installation target for [Skill Loom](https://github.com/Koooki3/skill-loom). Synced its GitHub upstream and the existing local project. Both pointed to `8ccd8f5`. The candidate recognized the selected local commit as already upstream.

- Built the project's v0.3.0 wheel offline with its existing Python packaging metadata. Ran the native unittest suite and `scripts/check_release.py` before install.
- Installed the verified wheel into the isolated target. Checked installed module bytes against the wheel and invoked the installed CLI to inventory the project's real bundled skill. The probe returned zero inventory errors, the expected SHA and the artifact fingerprint `64b464c32c8fde8979da11364ebc3eea84fa4a52c8a52cf9fe519e15d4b60bb1`.
- Saved and restored a project checkpoint, verified a lesson through named EWK evidence, and produced a review-only promotion proposal. The archived candidate and independently probed runtime passed the applicable closing checks.
- Preserved the original project checkout and normal installation. The deployment demonstration used an isolated target.

## Skills and knowledge

Verified 35 pinned [oil-ui publisher files](https://github.com/oil-oil/oil-ui/tree/82464b1ef8ff41808497642dba5342852ced70ae) and 56 pinned [oil-motion publisher files](https://github.com/oil-oil/oil-motion/tree/c930f4477304603b192c9633a449c9f4da98d75c). Both local instruction files differ from the newly pinned upstream bytes. The two public bundles are available for isolated review. Demos and test material remain available from the pinned upstream trees. The local design-hub and design-workflow variants remain local pending provenance and redistribution evidence.

Project checkpoints complement native compaction or work-handoff. Knowledge promotion emits a reviewed summary proposal and a deduplication fingerprint. Native Agent memory and transcripts stay under their original host ownership.

## Workstation acceptance

Windows and WSL verified the same distribution fingerprint `ac6cf2c7870770bba70ca654bf090e48eba87b86a78b35a667815f81b42640d1`. A repeat plan on both environments returned no changes. Third-party acquisition remains in `REPORT_ONLY`.

| Platform | User-level configuration | Fresh-session evidence |
| --- | --- | --- |
| Windows Codex | Integrity verified | Found all three CORE Skills. The read-only task in a disposable workspace ran the startup inspection and passed the applicable delivery gate. |
| WSL Codex | Integrity verified | Found all three CORE Skills and completed both lifecycle checks from a new session. |
| Windows OpenCode | Integrity verified | A new session invoked the installed lifecycle entry point for startup and delivery. Both checks completed. |
| WSL Claude Code | Integrity verified | Found all three CORE Skills. OAuth authentication blocked model execution. |
| Windows Claude Code | Integrity verified | Session invocation remains unverified. |
| Windows Antigravity | Integrity verified | Subsequent workstation acceptance on `2882ef1` confirmed global rule inheritance, discovery of all three CORE Skills, and basic tool invocation. |

The native project tests used a temporary installation of Skill Loom. Other software deployments depend on their own authorized contract and independent probe. The source and release CI remain the portable verification entry points. The workstation retains rollback history and local evidence.

## Readiness follow-up

Reproduced standalone runtime reporting `CURRENT` after changing a declared external input while the deployed artifact stayed healthy and the Git refs stayed unchanged. Regression coverage checks external drift after worktree archival, simultaneous Git and build drift, and unavailable checkout-specific inputs. The delivery gate blocks a stale or unverified build.

Resolved `frontend-design` through the catalog, staged the exact Apache-2.0 Markdown bundle, and reviewed both files. With explicit one-time user approval, used `TRUSTED_AUTO` for that digest in a disposable Windows Codex workspace with an expiring policy. Codex discovered and read the installed project Skill in a new session and completed the representative design-planning task. The rollback removed the isolated entry and fresh discovery confirmed its absence. The regular Windows and WSL states use `REPORT_ONLY`.

## Recovery and trigger follow-up

On `4496474`, Windows and WSL each passed 73 Engineering Workflow tests, 17 Adaptive Skills tests, and the generated catalog check. The recovery regression ends a real writer process after a filesystem replacement, both during first installation and during an update with unchanged instructions. The checkout locates the correct pending transaction and recovers it without changing the default state. Other checks cover history without a current deployment, malformed state, a relative entry point, and a linked runtime. Explicit state selection remains available when automatic discovery stops.

Windows updated its four existing adapters and WSL updated its two existing adapters. The installed CLI reported `OK` and `REPORT_ONLY` on both, and the repeat plan returned no changes. Both distributions used fingerprint `c09da3b568f95d99215474e85732c2ea49e35eafd418dc67b3efcf79933a9f21`. Read-only rollback preflight passed for all six Windows and all four WSL targets in the new transactions. The rollback itself was exercised in isolated tests.

Reused four Windows Claude Code subagent evaluations of the unchanged workflow rules on `c3f008f`. The low-risk one-line fix loaded the workflow, selected Fast, reproduced the bug, and passed a regression test. The one-line fix with deletion risk selected Standard and passed five tests after reproducing the failure. The README typo and standalone question did not load the workflow. These single-run samples came from subagents and did not use the EWK evidence runner.

A fresh WSL Codex session on the updated deployment loaded the installed workflow and inspected the scratch Git repository. A one-line default could overwrite user configuration. The session reproduced the overwrite using a temporary fixture, checked byte preservation and explicit apply in two passing tests, and validated the regression evidence with EWK. The trace did not state a risk tier.

A fresh Windows Codex session loaded the installed workflow for an ordinary registry defect, ran startup inspection, and reproduced three incorrect behaviors involving out-of-order revisions and unrelated events. It then passed three tests and validated the regression evidence with EWK. In both Codex sessions the task prompt described only the defect and expected behavior.

The Windows Antigravity session check above is historical. This follow-up checked its installed files, while full Antigravity lifecycle execution and additional top-level Claude Code session checks remain open.
