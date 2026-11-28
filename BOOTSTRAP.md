# Global bootstrap

Use this runbook to configure a workstation, migrate an earlier installation, or restore the same distribution on another machine. Work from a trusted, tested checkout of one revision across all environments.

## 1. Inspect

Record the distribution revision and confirm native Python 3.9+. Identify installed agents, home overrides, and their discovery paths. Run `python tools/setup.py inventory` with optional `--root` for known plugin/shared roots and `--project` for representative workspaces. Keep its output private.

| Agent | Global Skills | Global instructions |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills/) | `~/.agents/skills` | `$CODEX_HOME/AGENTS.md`, default `~/.codex/AGENTS.md` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `~/.claude/skills` | `~/.claude/CLAUDE.md` |
| [OpenCode](https://opencode.ai/docs/skills/) | `$XDG_CONFIG_HOME/opencode/skills`, default `~/.config/opencode/skills` | Same config root, `AGENTS.md` |
| [Antigravity](https://antigravity.google/docs/skills) | `~/.gemini/config/skills` | `~/.gemini/GEMINI.md` |

Claude honors `CLAUDE_CONFIG_DIR` in the adapter. Review custom discovery overrides or same-name project/legacy skills before applying. Use an explicit `--state` or `ENGINEERING_INFRA_HOME` to place data on the desired volume. The default is `~/.engineering-infrastructure`; once a deployment exists, a checkout run without `--state` follows the runtime path in the managed instruction block instead of planning a second install. Windows and WSL use the same source revision and independent native state. For an alternate distribution root, pass `--source PATH` before the command.

## 2. Plan, apply, verify

```sh
python tools/setup.py plan --agents codex claude
python tools/setup.py apply --agents codex claude
python tools/setup.py verify
```

For a verified v1 migration, add `--migrate` to both commands. This recognizes an unchanged EWK manifest or a bundled-content match, including linked targets, and migrates a marked legacy block. For another reviewed historical copy, use `--adopt-fingerprints FILE` with its exact destination and confirmed portable hash from inventory. Optionally pass `--obsolete-rules FILE` containing a local JSON map from adapter to one exact obsolete rule line to remove with backup. Use `--retire-alias PATH` for a verified duplicate CORE alias in a supported legacy Codex or Antigravity root. Other same-name conflicts stop the deployment. Compare planned paths to the intended home before applying.

The local runtime is the canonical deployed snapshot. Adapters receive hash-verified copies for compatibility. Always refresh from the same reviewed distribution. Keep the reported transaction ID and its rollback snapshots. Adjusting the adapter set requires rolling back the previous deployment first.

## 3. Test inheritance

In a new session, start a substantive task in a disposable Git repository. Confirm that the agent runs the installed repository inspection before proposing implementation. The [project lifecycle](engineering-workflow-kit/engineering-workflow/references/lifecycle.md) covers optional integration, native deployment and recovery.

From a clean directory with no per-project setup, open a new session, confirm the CORE names and run a small engineering task. Capture real discovery, skill use, and successful evidence tooling separately. Repeat for a representative project. Windows and WSL configurations are independent and need separate filesystem checks.

## Recovery

Use `python tools/setup.py recover` with the original state path after an interrupted transaction. Use `rollback TRANSACTION_ID` for a successful transaction. Roll back in reverse order when state overlaps. Rollback checks for drift before making any changes and restores prior originals including migrated links. Inspect later edits before reattempting a refused rollback. Keep the repository checkout available as a recovery entry point if a rollback removes the installed runtime. Filesystem side effects are journaled and reversible. Upgrades may briefly remove a target while switching directories.

See [OPTIMIZE](OPTIMIZE.md) for regular maintenance.
