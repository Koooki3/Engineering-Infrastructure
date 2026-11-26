# Adaptive Skills Kit

Use the [global bootstrap](../BOOTSTRAP.md) for installation. Examples use `python tools/setup.py`; the installed global instructions give the native runtime path. Put `--state PATH` before the subcommand when using a custom state directory from a checkout.

## Resolve and evaluate

- `resolve --agent codex --need web-accessibility` checks the local discovery root and registry. Add `--native CAPABILITY` for proven project/native coverage, `--available ID` for session-local capabilities such as plugins, and `--exclude ID` when constraints rule out an option. A filesystem match warrants runtime confirmation.
- `discover --agent codex --need missing-capability --public-query "public capability words"` contacts public GitHub only for unresolved needs and policy allows it. Use generic capability terms. The bounded search returns up to four repository leads and caches the public result for an hour. Native public search can supplement it. No candidate is a reasonable outcome.
- `stage ID --repo OWNER/REPO --commit FULL_SHA --skill-path skills/ID --license-path LICENSE` stages exact Markdown and license bytes outside discovery. `--local DIRECTORY` supports a reviewed local fixture or mirror with the same pinned provenance. The resolver deliberately does not execute candidate text.
- `stage-reference ID` uses catalog pins directly, verifies each file and reuses the exact isolated snapshot. A Markdown reference accepts `--activate` only when the matching scoped approval is already present. Review-only bundles, including scripts and Agent manifests, stay inert for inspection and independent authorized evaluation. Pinned upstream files may differ from local adaptations.

The oil-ui and oil-motion pins stage runtime instructions and assets for review. The exact publisher revision also contains upstream demos and test material. Keep privately maintained design routing skills under their existing ownership. If their owner approves private migration, copy the reviewed source into an isolated directory on the destination, compare hashes, and verify discovery before using it. Public distribution requires separate provenance and license evidence.

Use [the evaluation guide](adaptive-skills/references/evaluation.md) to compare 2–5 relevant candidates as available. Compare against current tooling on positive, negative, near-miss and overlapping tasks before voting for a change.

## Permission policy

Create `policy.json` yourself under the native state root. Default `REPORT_ONLY` permits explicit search and inert staging. `OFF` disables external discovery, staging and activation. `TRUSTED_AUTO` allows exact, pre-reviewed content only in the already established global adapter set. The policy and review evidence are machine-local.

```json
{
  "schema": 1,
  "mode": "TRUSTED_AUTO",
  "approvals": [{
    "id": "reviewed-skill",
    "source": "https://github.com/owner/repo/tree/full-commit/skills/reviewed-skill",
    "sha256": "replace-with-the-exact-staged-content-hash",
    "license": "MIT",
    "agents": ["codex"],
    "os": ["windows"],
    "capabilities": ["public-capability-id"],
    "expires_utc": "2030-01-01T00:00:00Z",
    "gates": {
      "provenance": "Record how the exact source and revision were independently verified.",
      "license": "Record evidence that the license applies to all staged content.",
      "instructions": "Record the review of every instruction and reference.",
      "permissions": "Record why the requested behavior fits the authorized scope.",
      "compatibility": "Record the OS and adapter evals.",
      "functional": "Record representative task checks and the baseline.",
      "rollback": "Record the isolated activation and recovery check."
    }
  }]
}
```

Approval is a user-owned attestation. Static checks reject unsafe structure and selected patterns. Review for indirect instructions and unsafe behavior even in prose. The supported automatic lane is `SKILL.md` and `LICENSE` only. Skills needing scripts, hooks, MCP, dependencies, asset bundles or restricted licenses require an independent, authorized install and evaluation. Keep rejected or unapproved material outside the discovery paths.

## Update, archive and restore

- `activate ID SHA256` performs a locked transaction. `update` uses the same command and requires an approval for the new hash. Review differences and run isolated evals before approving. The manager preserves the current version when preflight or activation fails.
- With `TRUSTED_AUTO` enabled, `archive ID --reason replacement --dependents-cleared` removes managed copies from discovery and retains the previous version for rollback. Check reverse dependencies and live tasks first. CORE updates and removal belong to the distribution lifecycle.
- `verify` checks content and instruction blocks. `doctor` adds inventory and transaction IDs. `rollback TRANSACTION_ID` checks drift and restores the prior transaction. `recover` handles a pending write.
- `feedback ID VERIFIED --agent codex` records an observed event. Add `--seconds` or `--tokens` only for measured values. Feedback is bounded and local. Pair it with project evidence when evaluating benefit.

[Registry](skills-registry.json) describes capabilities, [lock](skills-lock.json) pins bundled trees, and `sync-reference` regenerates both the lock and the [human reference](skills%20reference.md). Machine state records adapter locations and active hashes. Store and backups remain local. No background process, recursive updater, or blanket ecosystem installation is required.
