# 上一轮（Lauren Tan，2026-11-15）优化恢复报告

事实来源：本机文件元数据与内容（2026-11-25 读取）。状态词：DEPLOYED 已部署且存在 / PARTIAL 部分覆盖 / UNVERIFIED 未验证 / CONFLICT 与现状冲突。

| ID | 产物 | 位置 | 状态 | 事实与限制 |
|---|---|---|---|---|
| R01 | Claude 全局规则段“工程约束优先” | Windows/WSL `CLAUDE.md`（两份 SHA-256 一致 `08f6ad0f…`，部署前） | DEPLOYED | 7 条原则，约 1.9 KB 常驻上下文；含外部数字边界说明。行为收益从未测量（上轮自己的 deployment.md 也这么写）。 |
| R02 | `constraint-ladder` skill + `guard.sh` + `paradigm_guard.sh` | 两侧 `~/.claude/skills/constraint-ladder` | DEPLOYED / PARTIAL | `guard.sh` 依赖 bash+git，Windows 需 Git Bash；配置是 bash 语法 `.guard.conf`；Codex 侧没有该 skill。 |
| R03 | Codex 手册 `engineering-verification.md` | `<local path>` | DEPLOYED | Codex 两侧 AGENTS.md 按需指向它；Claude 侧不引用。→ 同一思想两处分叉。 |
| R04 | Codex AGENTS.md “任务范围、工程验证与交付”“跨会话上下文”段 | Windows 3.8 KB / WSL | DEPLOYED | 上轮精简后：Windows 5,886→3,153 B。Windows 与 WSL 的 AGENTS.md 本来就不同（Team Mode、D 盘约定 vs 研究库、work-handoff）。 |
| R05 | BrimDeck `pr-plan/tools/guard.sh` + `.git/hooks/pre-push`→`pre-push.sh` | <project> | DEPLOYED（试点） | 覆盖 releases/、U+FFFD、含中文 .ps1 缺 BOM、新增行本地路径；取证失败退出 2。pre-push 在 git common dir，不进提交。 |
| R06 | BrimDeck 衍生工具：`wait-for.sh`、`no-open-wait.py`（PreToolUse hook）、`leftovers.ps1`、`deploy-gate.tests.ps1`、`workflow-shell.tests.sh` | `pr-plan/tools/` | DEPLOYED | 是纠正阶梯第 2 步的实际成功案例；`no-open-wait` 看不到脚本文件内部的循环（记忆里自述）。 |
| R07 | 上轮部署/回退脚本 | `<local path> refine.py` | DEPLOYED（工作目录） | 回退按原始字节恢复；文件后续被改会停止。本轮 deploy 改为“只移除标记块”，保留后续无关编辑。 |

## 现状问题（本轮发现）

- **G1 双份分叉**：同一阶梯思想存在于 CLAUDE.md 段落、constraint-ladder、Codex 手册三处，互不引用；Codex 拿不到 `guard`，Windows 拿不到免 bash 的 guard。→ 本轮用 `ewk.py guard`（纯 Python）补齐，三处保留不动。
- **G2 无统一的风险分级与证据绑定**：现有规则只说“按风险选最小充分验证”，没有档位、没有防“旧 PASS 沿用”的机制。BrimDeck 靠人工纪律（“结果绑定完整提交”）。→ `ewk run/check`。
- **G3 交接**：work-handoff 仅 WSL 侧存在；Windows 会话需 `wsl.exe` 调用（CLAUDE.md 已声明）。→ 不新增交接工具，task-card 只留 Resume 区作兜底。
- **G4 无冲突**：Hook 仅 WSL 有 Stop/Notification 通知钩子，与本轮无交互；两侧 settings.json 未被修改（部署前后哈希相同）。
- **G5 路由相邻**：新 skill 与 constraint-ladder / pr-authoring / design-hub / work-handoff 相邻；已在描述与“边界澄清”中划界，并做了模拟路由（见验证报告）。
- **UNVERIFIED**：上轮部署后的 token/耗时/质量收益；Codex 对 `~/.agents/skills` 的实际发现（上轮 design-skills 有 app-server 发现记录，本轮未复跑）。
