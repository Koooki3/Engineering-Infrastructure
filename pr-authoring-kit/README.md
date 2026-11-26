# PR Authoring Kit

Global [bootstrap](../BOOTSTRAP.md) installs `pr-authoring`. For standalone use, place the whole `pr-authoring` folder in an agent's supported skills directory. The [skill](pr-authoring/SKILL.md) handles planning, drafting, updates, review, and evidence requirements according to the target upstream policy.

Use the [optional scaffold](pr-authoring/pull_request_template.md) and [fictional example](pr-authoring/example.md) as references. Validate a draft with the offline linter.

```sh
python pr-authoring/tools/lint_pr_body.py --title "feat: add a verified engineering workflow" body.md
```

Use `--upstream-english-only` when required. Review claims against real evidence and obtain publication authority independently of lint.

For a live PR, confirm the actual target and merge base with the [repository lifecycle](../engineering-workflow-kit/engineering-workflow/references/lifecycle.md). Keep local combined integration worktrees separate from the proposed PR's actual head and diff.
