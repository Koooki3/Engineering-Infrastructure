# EI-Eval

EI-Eval is the project’s reproducible evaluation suite. It separates coding-agent comparisons, deterministic lifecycle checks and a public benchmark adaptation. Start with the [technical report](REPORT.md), or inspect the [frozen pilot protocol](PROTOCOL.md).

| Evidence | Reproduction |
| --- | --- |
| [Codex pilot receipts](pilot-results.json) | Rerun the summary and regenerate the plot from released data. Run the pilot separately to produce a new set of agent trials. |
| [Lifecycle receipts](lifecycle-results.json) | Run the local CLI scenarios in temporary Git repositories. No model account is required. |
| [Public benchmark attempt receipts](terminal-subset-results.json) and [verifier controls](terminal-subset-control.json) | Download three pinned upstream files and run the original CSV assertions on a WSL adaptation. |

## Reproduce the analysis

Python 3.9+ and Git suffice for the result checks and local lifecycle cases. To render figures use Matplotlib 3.11 and Pillow. The released evaluation code and project-authored fixtures use the repository’s [Apache-2.0 license](../LICENSE). The Terminal-Bench task retains its [upstream licensing and attribution](https://github.com/harbor-framework/terminal-bench-2-1/blob/12b7565679ce5006230b820666353673a133db93/LICENSE).

```sh
python -B evaluation/analyze.py evaluation/pilot-results.json
python -B evaluation/analyze.py evaluation/pilot-results.json --chart pilot-results.png --table results.md
python -B evaluation/lifecycle.py
```

The pilot receipt schema is declared in [analyze.py](analyze.py). Each row includes the frozen starting SHA, condition, UTC timestamps, timing, emitted token usage, result, verifier status, and artifact hashes. A null token field means the CLI did not emit final usage. The source order is retained. Raw transcripts and patch artifacts stay in the local run folder.

## Run fresh model trials

Use a trusted checkout that contains the pinned subject SHA, Linux or WSL, Python, Git, tar and a compatible Codex CLI, with the configured model available through a normal signed-in account. The documented run used Codex CLI 0.163.0. Choose new output directories for every invocation. These commands make real model requests.

```sh
python3 -B evaluation/pilot.py --preflight --out /tmp/ei-oracle-check
python3 -B evaluation/pilot.py --out /tmp/ei-pilot-next
python3 -B evaluation/terminal_subset.py --preflight --out /tmp/ei-terminal-check
python3 -B evaluation/terminal_subset.py --out /tmp/ei-terminal-next
```

The pilot preflight validates all six failing inputs and passing oracles. The terminal preflight checks an independent reference tally and a negative control without a model account. The live trial processes receive fresh Codex homes, native workspace-write sandbox permissions and an isolated task checkout. Use `--auth-file` for a supported, signed-in file-backed setup. The external adaptation uses its own schedule and makes HTTPS requests to the pinned public source.

## Follow-up ledger

| Item | Status | Next start condition |
| --- | --- | --- |
| Larger preregistered A/D experiment, repetitions and Workflow-only C | Deferred | Disambiguate the operation label, enable scoped Git metadata writes in disposable fixtures, balance order and agree the model-run budget. |
| WSL-adapted Terminal-Bench model score | Blocked in v0.1 | Resume on normal provider availability under a new run ID. The independent reference and negative controls are reproducible now. |
| Official Terminal-Bench, SkillsBench and SWE-bench Pro V2 results | Not run | Set up a supported isolated Harbor environment and agree the budget. Use the respective pinned data and official protocol. |
| New real-project repair acceptance and F09 remediation | Deferred | Run a fresh paired trial for the receipt defect when the service is available. Treat any production fix as a separate change and subject SHA. |
| Skill activation ablation, human PR review and cross-agent replication | Not run | Obtain the exact Skills approvals and independent reviewers or a second supported model environment. |
| Longitudinal deployment, context recovery and cross-project learning | Not run | Collect repeated observations and separate training tasks from a private holdout. Use real deployments with scoped authorization. |
| Provider billing and external independent replication | No data | Obtain an authorized metered source or an external replication. Retain failed cases and redacted receipts. |
| Independent post-results review | Blocked in v0.1 | Provider quota interrupted the second internal reviewer. Rerun the review on the immutable receipt and report files. |

## Report a replication or counterexample

Open a [repository issue](https://github.com/Koooki3/Engineering-Infrastructure/issues/new) with the evaluation version, subject SHA, agent/model, environment, condition, task, verdict and a redacted reproduction. Include timeout and failed results. Keep model transcripts, credentials and private paths out of the issue.
