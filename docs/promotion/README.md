# Engineering-Infrastructure promotion kit

Use the [2:1 project cover](../diagrams/engineering-infrastructure.png) for a GitHub social preview and the [pilot chart](../diagrams/ei-eval-pilot.png) where the evaluation is discussed. The cover is an illustrated workflow. The chart is generated from the [released pilot receipts](../../evaluation/pilot-results.json). The drafts below are ready for manual review and posting.

## GitHub summary

**From code change to verified delivery.** Engineering-Infrastructure gives coding agents a shared workflow, on-demand Skills, and evidence-backed PR authoring. It can keep active work separate, check what actually runs, and recover the previous verified release after a failed deployment. Install once per Windows or WSL user environment. [Quick start](../../README.md#quick-start) · [Evidence and reproduction](../../evaluation/README.md).

## Hacker News

**Show HN: Engineering-Infrastructure – a portable verification and recovery workflow for coding agents**

I built Engineering-Infrastructure for tasks where an agent’s edit is only the beginning. What happened to the upstream ref? Does the installed artifact match the candidate? Can we recover if installation stops halfway? The project brings those checks to Codex, Claude Code, OpenCode and Antigravity through their native user-level setup.

In an offline lifecycle evaluation, an artifact-existence check missed a changed installation and a clean working tree missed a stale input ref. Runtime checks caught both. In a separate six-task Codex pilot, both groups accepted 3/6 artifacts, and Full took a median 9.7 seconds longer per pair. I’d be interested in replications, counterexamples and cases where the workflow creates unnecessary work. [Repository](https://github.com/Koooki3/Engineering-Infrastructure) · [Report and reproduction](https://github.com/Koooki3/Engineering-Infrastructure/tree/main/evaluation).

## Reddit

**How do you know which version your coding agent actually deployed?**

I’ve been building a shared engineering workflow for coding agents that covers active worktrees, evidence tied to commits, deployed artifact identity and rollback. One useful test kept the checkout clean while moving an input ref. The runtime correctly reported the deployment stale, and the delivery gate blocked it. The project also includes versioned Skills discovery and PR authoring.

The paired pilot and example fixtures are public. Raw model logs stay local; normalized receipts, a report and reproducible runs are in the repo. I’d appreciate examples of false passes or recovery failures worth turning into test cases. [Project and evidence](https://github.com/Koooki3/Engineering-Infrastructure).

## X

Your Git checkout can be clean while the running build is stale. Engineering-Infrastructure gives coding agents checks for the actual deployment, plus recovery and evidence-backed PRs. Eight lifecycle scenarios passed. Reproduce them: https://github.com/Koooki3/Engineering-Infrastructure

## 中文介绍

**从代码改动到可验证交付。** Coding Agent 修改代码之后，Engineering-Infrastructure 还能核对输入引用、验证实际安装版本，在部署失败时恢复上一版，并把已经执行的检查写入 PR。专项实验展示了只看 Git 状态和只看产物是否存在会漏掉什么。配对试验的收益与开销也一并公开。欢迎用自己的任务提交复现结果和反例。[项目首页](../../README.zh-CN.md) · [评测与复现](../../evaluation/README.md)。
