# Changelog

## Empirical evaluation

- Publish a six-task paired Codex pilot, standalone lifecycle scenarios, and a reproducible Terminal-Bench verifier adaptation.
- Update the English and Chinese project introductions with a workflow cover, an evidence chart, and links to reproduce the results.

## Field feedback

- Run from a checkout without `--state`, the CLI targets the live deployment named in the managed instruction block, rather than planning a duplicate install under `~/.engineering-infrastructure`.
- State discovery checks every adapter's managed block with the existing block parser, verifies the named state owns that instruction file, and fails closed on duplicate or malformed blocks, missing deployments or agents that point to different states. A leftover `~/.engineering-infrastructure` no longer shadows the live deployment; a state with pending recovery stays locatable.
- The managed instruction block, `SKILL.md`, `ewk.py route` and the legacy v1 blocks now share one rule: route by impact and risk, not line count; low-risk fixes may run Fast with the reason recorded, and one-line changes touching concurrency, permissions, security or data escalate.
- `engineering-workflow` now covers defect fixes of any size, including one-line fixes, on the Fast tier. Recorded trigger runs had skipped one-line bug fixes (0/4).

## Runtime readiness

- Distinguish Git input freshness from build input drift and missing verification evidence in live runtime and delivery checks.
- Document exact, expiring approval and rollback for isolated Skills validation.

## Operational reliability

- Honor project Git hooks and revalidate changed build inputs even when the candidate commit is unchanged.
- Discover project deployment entrypoints and register reviewed contracts against a clean integration candidate.
- Check applicable delivery conditions, resume with existing checkpoints and propose verified lessons for review.
- Pin root-level oil-ui and oil-motion review bundles to their publishers.

## Project lifecycle and portable references

- Inspect Git topology and reconcile selected upstream and downstream changes in owned detached worktrees.
- Gate native deployment on candidate, artifact and runtime verification, with recoverable rollback.
- Archive clean released worktrees and retain repository-local checkpoints and evidence-backed knowledge.
- Fetch selected pinned publisher bundles into isolated review, preserving exact per-file hashes and existing activation gates.

## vNext

- Add Adaptive Skills Kit with a curated registry, generated reference, and exact CORE content locks.
- Unify global deployment for Codex, Claude Code, OpenCode, and Antigravity using native user discovery paths and a shared runtime per environment.
- Add exact review-based staging and activation, transaction recovery, reversible retirement and bounded local feedback.
- Integrate capability resolution into engineering workflow and keep PR policy in its own Kit.
- Replace the maintenance runbooks with executable workflows. Keep the v1 deployment helper for existing states.
