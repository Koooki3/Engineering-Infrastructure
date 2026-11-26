# Operational verification

The implementation checked in this round is `34ac407`, following `8bb4486`. Windows and WSL each passed 71 Engineering Workflow tests, 13 Adaptive Skills tests, and the generated catalog consistency check.

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
| Windows Antigravity | Integrity verified | Session invocation was deferred because the reported weekly quota was exhausted. |

The native project tests used a temporary installation of Skill Loom. Other software deployments depend on their own authorized contract and independent probe. The source and release CI remain the portable verification entry points. The workstation retains rollback history and local evidence.
