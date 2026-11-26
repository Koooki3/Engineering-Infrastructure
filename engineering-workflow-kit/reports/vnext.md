# vNext verification and deployment

## Baseline and inventory

The starting local and GitHub `main` pointed to `115c1a1`. The pre-migration inventory covered documented global roots, compatibility roots, scoped plugin caches, the shared store, and representative workspace roots. The figures are filesystem observations. Plugin packages may be installed, cached, disabled or bundled, and aliases can share a physical source.

| Environment | Distinct source locations | Entries | Same-name groups | Same-content groups | Description bytes across sources |
| --- | ---: | ---: | ---: | ---: | ---: |
| Windows | 412 | 442 | 24 | 15 | 68,361 |
| WSL Ubuntu | 188 | 190 | 34 | 2 | 41,773 |

Store locations and paths stay in local evidence. Same-name and same-content entries are review leads. Names can intentionally collide across adapters, project scopes or package versions. The global integration adds one 612-byte managed router per configured instructions file on this machine. Agent context and native tool overhead depend on the host configuration and session. No workload-level efficiency improvement has been established.

## Evidence

| Verification | Evidence and scope |
| --- | --- |
| Existing EWK tools | 62 offline tests per native environment. The restricted Windows process sandbox previously blocked two Git submodule tests and the process-tree timeout regression. Native Windows and WSL runs passed. |
| Adaptive Skills and PR lint | Offline tests cover initial global setup, idempotence, alias migration, rollback, drift, failure recovery, writer exclusivity, reference-first routing, online timeout handling, exact approval gates, scope, lifecycle update and archive, and PR body lint. |
| Public discovery | A read-only `discover` request with the generic phrase `design tokens` returned four GitHub repository leads. No discovered candidate was promoted. |
| Global integrity | The same distribution was read by native Python on Windows and WSL. Windows configured Codex, Claude Code, OpenCode and Antigravity. WSL configured Codex and Claude Code. Integrity verification checked the runtime, all managed copies, and each global instruction block. |
| Codex discovery | Native `app-server` `skills/list` discovered exactly three enabled CORE Skills in user scope, in both an empty workspace and this repository, on both Windows and WSL. |
| Codex invocation | Fresh read-only Codex CLI sessions in the empty workspace returned `Critical` from `ewk.py route` for a data migration, selected the installed `engineering-workflow` via `resolve`, and passed PR body lint. All three commands exited 0 on both platforms. |

Runtime tests used Windows Codex `0.171.0-alpha.13.2` and WSL Codex `0.163.0`. Use the test commands from [Verification](../../README.md#verification) for deterministic checks and [Bootstrap](../../BOOTSTRAP.md#3-test-inheritance) for fresh-session smoke tests. Claude Code, OpenCode and Antigravity invocation were left to their respective agent sessions. GitHub Actions results are tracked by the workflow for each published revision.

## Optimization decisions

| Decision | Asset and reason |
| --- | --- |
| KEEP / REUSE | Keep EWK risk routing, execution evidence, the PR linter, and the v1 recovery mechanism for existing deployments. |
| MERGE / SIMPLIFY | Centralize global bootstrap and consolidate overlapping deployment prose in the two maintenance runbooks. Use one portable reference generated from the registry and lock. |
| REPLACE / UPDATE | Migrate owned copies and equivalent legacy aliases to three pinned CORE capabilities. Back up old instructions and preserve unrelated text. |
| ADD | Add local inventory, reference-first resolution, inert staging, guarded activation and a drift-aware rollback journal. |
| REMOVE / ARCHIVE | Retire the verified legacy Codex PR alias and superseded managed instructions. Keep recovery snapshots. Group project diagrams in one directory. |
| DEFER | Keep independent and platform assets under their existing ownership. Global third-party activation requires a specific reviewed source, content pin, and scope. Behavioral comparison, long-term trigger quality and additional platform runtimes require more observations. |
