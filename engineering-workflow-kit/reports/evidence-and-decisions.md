# 证据索引、追溯矩阵与决策表

本机 BrimDeck 项目记忆（`~/.claude/projects/<project>/memory/`，40+ 条，按相关性抽样 9 条）是唯一有返工案例的项目；其他类型（Web/ML/服务端）只有目录存在，未做深读，故对应领域规则不晋升。字段：场景 / 事实 / 机制 / 收益代价 / 适用·不适用 / 状态 / 去向。

## 发现与追溯（Fxx ↔ skill/lessons 的 Lxx）

| ID | 来源 | 场景与事实 | 机制 | 适用 / 不适用 | 状态 | 去向 |
|---|---|---|---|---|---|---|
| F01 | R01–R03 | 上轮规则落地；收益未测 | 文字规则易被忽略 | 全局 / — | 保留，不删 | L01 L10 |
| F02 | R05 | 含中文 .ps1 无 BOM 乱码、本地路径进 PR、改了 releases/ 反复出现 → guard.sh + pre-push | 阶梯第 2 层成功 | Windows+中文源码、公开仓库 / 纯英文私有项目收益小 | Validated | L11，`ewk guard` |
| F03 | memory `no-zombie-tasks` | 子 Agent 的 `until [ -s file ]` 循环空转 4 小时，自述“已清理”未核对 | 无上限等待 + 信任自述 | 全局 | Validated | L02，`ewk run --timeout`（超时杀进程树，已测） |
| F04 | memory `never-test-posting-tools-live` | 负向测试发帖脚本，检查失效，两条测试评论真的发到上游 PR | 外发工具无 dry-run | 全局 | Validated | L03 |
| F05 | memory `probe-removal` | `git checkout` 清探针，同时抹掉未提交改动 | 清理手段越界 | 全局 | Validated | L04 |
| F06 | memory `no-source-scan-tests` | 维护者拒绝“正则读源码”的测试 | 测文本不测行为 | 上游 PR；本 kit 的卫生测试是文档 lint，不是产品测试 | Validated | L05 |
| F07 | memory `brimdeck-review-lessons`（#33–#105） | 绝对时间阈值在慢 CI 挂；断言依赖仓库位置；订阅未在 Closed 移除泄漏；`TickCount64` 15.6ms 误排序 | 环境/时序假设 | L06 全局；L12 L13 仅桌面 | Validated | L06 L12 L13 |
| F08 | memory `adversarial-review-loop` | 用户拒绝多轮液态玻璃：自检漏掉黑页/金属条；“检查用硬编码决策所以有 bug 也过” | 检查未走真实路径、复核者不连续 | Critical 视觉/系统；Fast/Standard 不适用 | Validated domain | L05 负控制，L15 |
| F09 | memory `no-unapproved-settings-changes` | 上游合并折叠 HoverPage、枚举重编号，部署后用户设置含义变了 | 持久化状态迁移未对照 | 有持久设置的项目 | Validated | L07，verification.md“持久化状态”行 |
| F10 | memory `hang-diagnosis` | 自我重投递的重试循环占满 UI 线程并饿死设置保存 | 无条件重试 | 桌面/UI 线程 | Validated domain | L12 |
| F11 | memory `gpu-test-caution` | TDR 后用户说“保持谨慎即可，别过度防御” | 过度门禁的反例 | 仅 GPU fixture | 限定 | L16（Candidate） |
| F12 | memory `hands-on-testing`/COLLAB | 副屏实测、不抢前台、设置只读 | 实机测试会干扰用户 | 桌面实机 | Validated domain | L14 |
| F13 | `deploy-gate.tests.ps1`、`workflow-shell.tests.sh`、`deploy-ledger.txt` | 部署门禁自身有测试、git/gh 桩化、台账 | 验证工具也会错 | 有部署脚本的项目 | Validated | L09 L17 |
| F14 | memory `review-lessons` #43 | 在 Claude 容器里写注册表，向维护者断言“关横幅无效”，实为容器私有副本，多两轮返工 | 环境不是用户环境 | 容器/WSL/注册表类结论 | Validated | L08 |
| F15 | memory `quota-pacing`、AGENTS 并行规则 | 用户移除所有额度节流；项目允许“无限子 Agent” vs Windows Codex 默认 SOLO | 并行默认值在各处冲突 | — | 冲突记录 | 本 kit 默认单 Agent，项目显式许可则以项目为准（workflow.md） |
| F16 | R01–R04 对比 | 三处分叉、Codex 无 guard | 同上 G1 | — | 新 | 统一入口，不删旧 |

## 决策表

| 项 | 决策 | 理由 / 条件 |
|---|---|---|
| CLAUDE.md “工程约束优先”段 | **retain** | 删除会减少常驻规则，而无行为对照数据；满足“consolidate 条件”后再缩短：新 skill 在 ≥10 个真实任务中被触发且无回归，则把该段缩成 3 行指针（可用 rollback 恢复）。 |
| constraint-ladder | **retain + defer consolidate** | 与 `references/correction-ladder.md` 同阶梯，已声明“择一执行”；同条件退役其一。 |
| Codex `engineering-verification.md` | **retain** | Codex 仍引用；新 skill 的 verification.md 覆盖其内容的超集，可在 Codex 路由稳定后把手册改为指针。 |
| BrimDeck guard.sh 与 hooks | **retain**（项目级） | 不改真实仓库；`ewk guard` 可作迁移选项，需用户授权。 |
| 风险路由 Fast/Standard/Critical | **add** | 填补 G2；`route` 只做建议。 |
| 证据绑定 `ewk run/check` | **add** | 填补 G2；变异测试证明关键判定有测试守护。 |
| 跨平台 guard | **add**（Python 版） | 填补 G1；与 bash 版并存。 |
| 通用 handoff 模板 | **add 不做** | work-handoff 已有；task-card 仅留 Resume 区。 |
| 形式化验证（TLA+/Lean） | **defer** | 仅在 verification.md 以“按价值选择”一行保留；本机无需求证据，不安装。 |
| DORA 类指标 | **defer** | 无部署数据；不用本地 PR 数替代。 |
| 固定轮数多 Agent 评审 | **reject** | 外部 E06/E09 与本机 F08 均指向“按新发现决定”。 |

## 外部实践采纳（E01–E16，仅离线使用提示词附录）

| ID | 处置 | 落点 |
|---|---|---|
| E01 Lauren Tan | 采纳阶梯与内环优先；拒绝照搬框架禁令/注释策略/自动合并/PR 数目标 | correction-ladder.md |
| E02 OpenAI Harness | 采纳“可导航可验证、可执行约束”；不照搬组织结构 | verification.md、guard |
| E03 迭代工作流 | 采纳：工作流本身要有评估 | 本轮测试+变异测试+审核 |
| E04 skills 封装 | 采纳：流程入 skill，项目规则留仓库 | 结构 |
| E05 长任务 harness | 采纳：持久化进度+真实运行判进展 | workflow.md“长任务” |
| E06 评估分离 | 采纳：Critical 才分离；不默认多 Agent | 风险路由 |
| E07 上下文工程 | 采纳：入口 5.9 KB，其余按需 | SKILL 结构+体积测试 |
| E08 渐进披露 | 同上 | 同上 |
| E09 简单优先 | 采纳 | “降噪”不可妥协项 |
| E10 可脚本化验证入口 | 采纳思想；未安装 pstack（先查本机已有） | `ewk run` |
| E11 小而完整变更 | 采纳；不以行数硬切 | workflow.md |
| E12 DORA | defer | 无部署数据 |
| E13 受保护分支 | 采纳：服从上游，不绕过 | SKILL §1，pr-authoring |
| E14 SSDF | 采纳“按风险配置安全检查”；不宣称合规 | verification.md 安全行 |
| E15 无责复盘 | 采纳为 Learn 阶段“只在有新发现时” | workflow.md |
| E16 Fowler CI/传感器 | 采纳：传感器要有价值，不以单指标替代判断 | guard 只做机械项 |

外部资料未联网复核，按提示词转述使用；其主张不构成本机验证。

## 与 pr-authoring 的接口

只在 Deliver 阶段单向交接：本 skill 负责产出“变更清单+证据”，PR 标题/双语正文/附件/授权全部由 `pr-authoring` 与目标仓库规则决定。测试 `test_pr_interface_delegates_not_copies` 防止把其规则（中文摘要、Conventional Commits、`--attach`）复制进本 skill。`pr-authoring` 的目录、junction/symlink 与内容在本轮未被改动（部署后其链接仍指向 `/mnt/d/codex/skills/pr-authoring`）。
