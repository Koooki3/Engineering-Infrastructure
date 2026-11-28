# EI-Eval

EI-Eval is the project’s reproducible evaluation suite. It separates coding-agent comparisons, deterministic lifecycle checks and a public benchmark adaptation. Start with the [technical report](REPORT.md), or inspect the [frozen pilot protocol](PROTOCOL.md).

| Evidence | Reproduction |
| --- | --- |
| [Codex pilot receipts](pilot-results.json) and [selected original artifacts](v01-evidence/manifest.json) | Regenerate the summary and plot, verify frozen source provenance, and inspect hashes for seven public artifacts. |
| [Lifecycle receipts](lifecycle-results.json) | Run the local CLI scenarios in temporary Git repositories. No model account is required. |
| [Public benchmark attempt receipts](terminal-subset-results.json) and [verifier controls](terminal-subset-control.json) | Download three pinned upstream files and run the original CSV assertions inside the WSL sandbox. |
| [v0.2 protocol](v02/PROTOCOL.md) and [offline preflight](v02/preflight-results.json) | Reproduce namespace probes and positive/negative controls for the six revised tasks. |

## Reproduce the analysis

Python 3.9+ and Git suffice for the result checks and local lifecycle cases. To render figures use Matplotlib 3.11 and Pillow. The released evaluation code and project-authored fixtures use the repository’s [Apache-2.0 license](../LICENSE). The Terminal-Bench task retains its [upstream licensing and attribution](https://github.com/harbor-framework/terminal-bench-2-1/blob/12b7565679ce5006230b820666353673a133db93/LICENSE).

```sh
python -B evaluation/analyze.py evaluation/pilot-results.json --check-frozen
python -B evaluation/analyze.py evaluation/pilot-results.json --chart pilot-results.png --table results.md
python -B evaluation/lifecycle.py
```

The pilot receipt schema is declared in [analyze.py](analyze.py). Each row includes the frozen starting SHA, condition, UTC timestamps, timing, emitted token usage, result, verifier status, and artifact hashes. A null token field means the CLI did not emit final usage. The source order is retained. The frozen runner and protocol are checked against their original Git blob objects in a full checkout. The recorded subject commit ID is historical provenance, while the offline replay uses its unchanged tree object.

The public evidence subset contains original diffs for the operation and preview tasks and the three original PR drafts. Their checksums match the frozen receipts. The remaining artifacts and all raw model transcripts stay in the local run folder.

## Run offline controls

Use a trusted full checkout, Linux or WSL, Python, Git, tar, and Bubblewrap 0.11 or later with working unprivileged namespaces. Choose new output directories for each invocation.

```sh
python3 -B evaluation/pilot.py --preflight --out /tmp/ei-oracle-check
python3 -B evaluation/terminal_subset.py --preflight --out /tmp/ei-terminal-check
python3 -B evaluation/v02/preflight.py
```

The legacy controls replay trusted fixtures only. The terminal preflight downloads its pinned public inputs over HTTPS and then runs the instructions' acceptance assertions in the sandbox. Both controls run without a model account. See the v0.2 protocol for the requirements before live evaluation.

## Follow-up ledger

| Item | Status | Next start condition |
| --- | --- | --- |
| Revised A/D pilot, repetitions and Workflow-only C | Offline preflight complete | Add and verify a credential-separated live adapter and private holdout. Use the balanced schedule and agree the model-run budget. |
| WSL-adapted Terminal-Bench model score | Blocked in v0.1 | Use a safe live adapter and available model quota under a new run ID. |
| Official Terminal-Bench, SkillsBench and SWE-bench Pro V2 results | Not run | Set up a supported isolated Harbor environment and agree the budget. Use the respective pinned data and official protocol. |
| New real-project repair acceptance and F09 remediation | Production regression addressed | Preserve the original subject and use a separate evaluation cohort for the failed v0.1 pair. |
| Skill activation ablation, human PR review and cross-agent replication | Not run | Obtain the exact Skills approvals and independent reviewers or a second supported model environment. |
| Longitudinal deployment, context recovery and cross-project learning | Not run | Collect repeated observations and separate training tasks from a private holdout. Use real deployments with scoped authorization. |
| Provider billing and external independent replication | No data | Obtain an authorized metered source or an external replication. Retain failed cases and redacted receipts. |
| Independent post-results review | Internal review completed | Recomputed trial counts, paired times and observed token totals. Verified frozen sources, the generated table and seven public artifact hashes. Full regrading and external review remain open. |

## Report a replication or counterexample

Open a [repository issue](https://github.com/Koooki3/Engineering-Infrastructure/issues/new) with the evaluation version, subject SHA, agent/model, environment, condition, task, verdict and a redacted reproduction. Include timeout and failed results. Keep model transcripts, credentials and private paths out of the issue.
