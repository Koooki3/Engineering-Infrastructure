# Global maintenance

Run these workflows when a project reveals a capability gap, verification regresses, or a reviewed upstream release warrants an update. Use the bootstrap state location for each OS. Run `doctor` using the installed entry point linked from global instructions, or a trusted checkout.

1. Verify the active deployment and inventory relevant discovery roots. Identify aliases, same-name conflicts, independent sources, copies, and measured problems. Keep raw reports local.
2. Decide which assets to retain, reuse, update, isolate, archive, or defer. Start with the smallest change that addresses an observed issue. Review project dependencies and live sessions before changing discoverable skills.
3. For CORE updates, inspect and test the candidate distribution, then repeat [plan, apply and verify](BOOTSTRAP.md#2-plan-apply-verify) using the same state and adapters. Use a fresh agent session for discovery or trigger evaluation. For other skills follow [Adaptive Skills](adaptive-skills-kit/README.md).
4. Compare before and after behavior on a relevant task. Record actual results with `feedback` or project evidence. Separate installation, discovery, invocation and verification. Roll back when integrity, compatibility or behavior regresses.
5. Consolidate reusable lessons in the owning skill, interface, test or reference. Keep project-specific evidence in that project. Review catalog generation with `sync-reference --check` before shipping a change.

For project maintenance, use the [repository lifecycle](engineering-workflow-kit/engineering-workflow/references/lifecycle.md) to check stale inputs and runtime drift, then review owned worktree release, handoff checkpoints and evidence-backed knowledge.

Retain rollback snapshots until their dependencies are understood and recovery is no longer needed. Archive decisions require a dependency and active-task review. Leave standalone user assets and platform configuration under their existing ownership.

[Project verification commands](README.md#verification) · [Bootstrap and recovery](BOOTSTRAP.md)
