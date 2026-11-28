# EI-Eval v0.2 protocol and launch status

The [task manifest](tasks.json) specifies six matched Native/Full task blocks, with three A-first and three D-first blocks. It retains a low-risk operation fix to expose overhead and adds checks for stale evidence, preserved Git state, installed artifact identity, failed deployment rollback and workspace cleanup. Primary success is the artifact and preservation outcome. Invoking an Engineering-Infrastructure command is a process observation.

## Offline preflight

```sh
python3 -B evaluation/v02/preflight.py
```

The preflight uses system Python, Git and Bubblewrap on Linux/WSL. Only the disposable workspace is writable from the sandbox. The child has a minimal environment, read-only system tools, private temporary space, separate user, process and network namespaces, and CPU, file-size, descriptor, memory and wall-time limits. The controls probe host-only paths, a synthetic environment secret, host localhost reachability, workspace writes and descendant cleanup after a deadline. Never point the runner at a live project or credential directory.

Each task has a known bad control and an independently checked passing artifact. The Git control changes real refs and the object database in a disposable repository. The checks compare the original refs, index, unstaged diff and untracked file after integration. The scorer and private workspaces sit outside the candidate mount.

## Live launch gates

The [preflight receipt](preflight-results.json) covers deterministic controls. A new live run requires an adapter that separates provider authentication from the model's shell and filesystem tools, with the same policy for both conditions. A provider account without sufficient quota is an unavailable trial environment. The legacy v0.1 live entries have been retired. The standalone public-Benchmark verifier controls remain available.

Before launching, freeze a **private holdout** separate from these public examples and keep its oracle outside the model namespace. Run disposable Git ref probes in both live conditions and verify credential and grader isolation. Record model ID, serving version if available, effort, tool and resource budgets and the fixture/grade digests. Use the manifest order for this illustrative bank, or publish a salted commitment to the private holdout and its order before the first scored trial.

Start with six independent tasks, two conditions and one attempt per condition. Preserve every planned slot and classify provider unavailability, environment blockage, unsuccessful artifacts, verifier faults and acceptance separately. Charge all observed session time to its condition, retain missing usage as missing and record interventions only when the runner collects events. Compare paired artifacts by task, with preservation and false-pass counts, time and usage reported separately. Proceed to repeated runs or the Workflow-only ablation after the pilot establishes the execution and scoring contracts.

Terminal-Bench stays next in the public-benchmark queue once the isolated provider adapter is available. Longitudinal validation requires consented real task series, with a separate future holdout for transfer. These stages carry no new model results in this protocol.
