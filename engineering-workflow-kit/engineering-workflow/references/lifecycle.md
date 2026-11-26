# Repository and workspace lifecycle

Run the installed Skill's `scripts/lifecycle.py` with native Python 3.9+ and Git 2.31+ from the project, or pass `--repo DIRECTORY` before the command. Keep project build and installation commands with the project.

| Event | Action |
| --- | --- |
| Start or resume substantive Git work | Run `inspect --event start` or `resume`. Check tracking, merge base, dirty state, worktrees and the existing handoff before choosing a baseline. |
| Integration, delivery, or stale baseline | Select target and remotes using project policy, relevant PR metadata and local ownership. Use `fetch REMOTE` and `compare BASE TIP`. The default fetch cooldown is 15 minutes. |
| Deployment | Verify an explicit candidate through the authorized native contract. Probe the actual running product. |
| Close and maintenance | Review release of owned worktrees. Preserve useful receipts, resume state and evidence-backed lessons. |

Fast tasks can stay offline. Resolve relevant PR dependencies using an authorized connector or project tool. Agent awareness of a remote, PR or branch grants no permission to publish or change it.

## Reconcile

```sh
python lifecycle.py fetch origin
python lifecycle.py compare refs/remotes/origin/main refs/heads/feature
python lifecycle.py plan --base refs/remotes/origin/main --include refs/heads/feature FULL_BOUNDARY_SHA
python lifecycle.py integrate task-id --owner agent-id --path /path/to/new-worktree --base refs/remotes/origin/main --include refs/heads/feature FULL_BOUNDARY_SHA
```

Repeat `--include FULL_REF BOUNDARY_REF_OR_SHA` in dependency order. Use `--exclude REF REASON` for relevant omissions. Prefer reviewed exact hashes if refs may move between preview and application. The deployment gate detects moved named inputs. `fetch` updates the selected remote-tracking heads while preserving local branches. `fast-forward --expected SHA --target FULL_REF` operates on a clean, attached branch with ancestry proof. Keep independent PRs on their own branches.

Integration records an exact manifest under `ewk-lifecycle/tasks/` in the Git common directory. Patch equivalence can identify an already applied change. Squashed, reverted or semantically equivalent changes still warrant review. Select linear ranges, and address conflicts in isolation. An incomplete candidate cannot deploy. Initialize verified submodules with the project's existing tools. See `git help cherry` and `git help worktree` for the underlying behavior.

## Deploy and observe

For an authorized deployment target, create `ewk-lifecycle/contract.json` in the Git common directory.

```json
{
  "schema": 1,
  "artifact": "dist/package.zip",
  "timeout": 120,
  "build": ["/absolute/python", "/absolute/reviewed/adapter.py", "build"],
  "test": ["/absolute/python", "/absolute/reviewed/adapter.py", "test"],
  "install": ["/absolute/python", "/absolute/reviewed/adapter.py", "install"],
  "probe": ["/absolute/python", "/absolute/reviewed/adapter.py", "probe"],
  "stop": ["/absolute/python", "/absolute/reviewed/adapter.py", "stop"]
}
```

The contract uses trusted native executable argv. `deploy TASK` builds a fresh artifact, runs tests, checks source and artifact integrity, archives verified bytes and then installs. The installer receives `EWK_DEPLOY_SHA`, `EWK_DEPLOY_SHA256` and `EWK_DEPLOY_ARTIFACT`. Build and tests may produce the specified artifact plus ignored build files. Other source changes invalidate verification.

The probe reads the actual binary, loaded extension, model, CLI or service. Report `active: false` when no instance runs. Otherwise report `active: true`, `healthy: true`, actual source `sha`, installed artifact `sha256` and a nonempty `instance`. The probe receives no expected identifiers. The receipt records source and artifact hashes, Git, Python, submodules and the observed runtime. Keep install, stop and probe runnable independently of candidate source. Failure restores the previously verified bytes or calls stop on first deployment. `recover` retries interrupted recovery. `runtime` detects drift. `rollback` restores the previous verified version under the same contract. Projects without a contract return `NOT_APPLICABLE`.

## Close and retain

- Review owner, process use, dependencies, and Git state before releasing a worktree. Preview `cleanup TASK --released`. Add `--apply` to archive the exact candidate in a local Git ref and remove only that clean owned worktree. Tracked, untracked or ignored changes, a changed checkout or pending rollback block cleanup.
- Prefer existing work-handoff or native compaction. If needed, save a project-local `checkpoint TASK --from-json FILE` with owner, goal, constraints, acceptance, decisions, evidence and next step. `checkpoint TASK` restores it and flags HEAD drift.
- Use `knowledge ID --from-json FILE` for an observed problem worth retaining. Include observation, evidence, root cause, invariant, mechanism and verification. Duplicate invariants are reported, corrections retain prior records and `--archive` keeps an item recoverable. Verify with `--evidence FILE --require CHECK_IDS` against named EWK checks on the current tree. Keep project facts local and review any proposed promotion into shared guidance. Turn repeated failures into mechanical constraints where practical.

State lives under the Git common directory. After a targeted fetch, use `runtime` to see whether the healthy installed release is stale against its named input refs. Its receipts are evidence records, and their strength depends on the actual build and probe. The tool leaves original conversations, Agent-managed memory, unrelated branches, stashes and worktrees under their existing ownership.
