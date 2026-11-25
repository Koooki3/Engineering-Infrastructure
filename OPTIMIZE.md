# Engineering Environment Reconciliation & Optimization Protocol

## 0. Input Configuration

- PR Authoring Kit 路径：`<填写 PR Kit 路径>`
- Engineering Workflow Kit 路径：`<填写 Engineering Workflow Kit 路径>`

除此之外，其余配置、优化范围、执行策略及技术方案原则上由你依据当前实际环境自主调查、分析和确定。

## 1. Mission

你是当前项目的 Principal Software Engineer、Engineering Infrastructure Architect、Agent Harness Engineer 与独立工程审查专家。

以两套 Kit 的实际最新内容为共同基准，对当前项目及其相关开发环境、工程规范、工程工作流、Agent Harness、工具链、验证体系和工程知识沉淀进行一次系统性、深入、证据驱动的治理与优化。

本次任务不是从零建立工程体系，也不是简单地将两套 Kit 覆盖到现有环境中，而是：

**充分理解存量 → 恢复历史设计意图 → 对照最新规范 → 识别实际问题 → 保留优秀实现 → 精简冗余 → 合并重复 → 清理过时机制 → 更新必要能力 → 优化工程环境 → 实际验证 → 持续演进。**

最终目标是以尽可能低的工程复杂度、维护成本、上下文开销和运行成本，获得尽可能高的工程质量、开发效率、稳定性、可维护性、可复用性及可迁移性。

不得以文件数量、规则数量、Skills 数量、自动化流程数量或修改规模作为优化成功的依据。

## 2. Fundamental Principles

全过程遵循以下原则：

- **Existing Assets First**：优先理解、保留和复用经过真实工程实践验证的存量成果。
- **First Principles**：从问题本质及实际工程需求出发，不机械套用所谓最佳实践。
- **Subtraction before Addition**：优先考虑删除、合并、简化及复用，再考虑新增。
- **Harness over Prompts**：优先通过架构、API、类型系统、测试、工具链和可执行约束解决问题。
- **Evidence over Assumptions**：所有优化决策及质量结论均应具有实际依据。
- **Single Source of Truth**：消除不必要的多份规范、重复配置及版本漂移。
- **Progressive Disclosure**：默认上下文保持轻量，复杂知识与能力按需加载。
- **Risk-adaptive Engineering**：流程和验证深度与实际任务风险匹配。
- **Minimal Necessary Complexity**：不为形式上的完整性引入额外工程复杂度。
- **Preserve Behavioral Contracts**：精简实现时保护有效的工程行为及质量约束。
- **Reversibility & Idempotency**：所有重要修改尽可能可逆，重复执行不应产生额外冗余。
- **Continuous Evolution**：允许经过验证的本地优秀实践反向促进通用工程体系演进。

两套 Kit 是重要的规范基准，但不是要求机械复制的文件集合。

如果现有本地实现经过验证，在特定领域优于 Kit 中的通用方案，应当合理保留，并记录其适用范围和技术依据。

不得为了追求表面上的规范一致性而导致实际工程能力退化。

## 3. Phase A — Kit Discovery & Specification Recovery

完整读取两套 Kit 中所有与当前任务相关的实际内容，包括：

- README、SKILL.md；
- 工程原则、工作流和风险路由；
- References、Playbooks、Templates、Examples；
- Scripts、Hooks、Validators；
- Tests、Evaluations；
- Changelog、Migration Guides；
- 平台适配与已知限制。

识别 Kit 的实际版本、设计目标、强制要求、推荐实践、可选机制和适用边界。

明确两套 Kit 的职责：

- Engineering Workflow Kit：工程任务生命周期、开发环境、质量治理、验证、审查、交付与经验沉淀。
- PR Authoring Kit：PR 分类、标题、正文、视觉证据、双语表达、上游适配及提交规范。

不得根据 Kit 名称、目录结构或部分入口文件推测其完整实现。

如当前环境此前已经接入旧版本 Kit，应尽可能恢复历史版本、迁移记录及相关变更，识别新增、修改、废弃及存在兼容性风险的规范。

无需重复进行 Kit 已经完成的外部技术调研。仅当兼容性、版本差异或重要技术事实无法通过本地信息确认时，进行必要的定向核验。

## 4. Phase B — Existing Engineering Environment Audit

在修改任何内容之前，先进行只读调查。

默认以当前项目及其实际依赖的共享工程环境为审查范围。

### B1. Agent Infrastructure

调查实际存在且与当前项目相关的：

- AGENTS.md、CLAUDE.md、项目 Rules；
- 全局与项目级 Skills；
- Plugins、MCP Servers、Hooks；
- Agent 配置及能力发现机制；
- Agent 自动触发、路由与协作机制；
- Subagents、任务编排与交接机制；
- Memory、Checkpoint、Session Recovery；
- Context Engineering 及知识检索机制；
- 权限、沙箱及安全约束；
- Windows、WSL、Linux、macOS 等实际存在的环境适配。

重点识别哪些机制被真实使用、如何触发、何时加载、依赖哪些组件，以及是否真正产生预期效果。

### B2. Engineering Workflow

调查现有工程任务生命周期，包括：

- 需求理解及验收定义；
- 上下文调查；
- 任务规划与风险分类；
- 方案设计及对抗性审核；
- 增量实现；
- 构建、测试及回归验证；
- 运行时验证；
- 性能和资源占用分析；
- Code Review；
- PR 规划及提交；
- CI/CD、Release、Deployment；
- 工程知识沉淀与持续优化。

分析实际执行流程，而不是仅分析文档中宣称存在的流程。

### B3. Repository Harness

调查当前项目的：

- 项目结构、技术栈、核心架构；
- Architecture Constraints；
- Build System；
- Lint、Format、Type Check；
- Unit、Integration、E2E Tests；
- Runtime Verification；
- Performance Baselines；
- Observability；
- Security Checks；
- CI/CD Quality Gates；
- Git、Branch、Worktree 管理机制；
- CONTRIBUTING、PR Templates、Release Policies；
- 开发脚本、自动化工具及其依赖。

### B4. Historical Engineering Knowledge

在合理且授权的范围内，调查与当前工程环境相关的：

- 历史工程优化记录；
- Architecture Decision Records；
- CHANGELOG、技术报告及设计文档；
- Git Commit、PR、Issue；
- 已有测试和性能基线；
- 历史 Bug、回归问题及失败教训；
- 已经沉淀的项目级、领域级及全局工程能力。

优先恢复已有设计决策的真实原因，避免将具有重要历史背景的工程约束误判为冗余。

不无目的扫描整台机器、其他无关项目、完整历史会话及私人数据。

## 5. Phase C — Adversarial Gap Analysis

将现有体系与两套 Kit 进行系统性对照，并从工程质量、效率、稳定性、上下文成本、维护成本和迁移能力等方面进行对抗性分析。

重点识别以下问题。

### C1. Redundancy & Duplication

- 多份重复或近似的工程规则。
- 全局配置与项目配置之间的无意义重复。
- 多个功能重叠的 Skills、Hooks、Scripts 或工具。
- 重复加载的工程知识。
- 相同检查被多个阶段重复执行。
- 多个 Agent 对同一问题进行低价值重复分析。
- 可以由原生工具可靠解决、却额外实现的复杂封装。

### C2. Obsolescence & Drift

- 已失效、过时或无人使用的规则与工具。
- 已被新机制替代的旧实现。
- 不再适用的技术栈或平台假设。
- 失效路径、错误命令、无效引用及废弃依赖。
- Claude Code、Codex 或其他 Agent 之间的配置漂移。
- 文档与真实代码、配置、运行行为之间的不一致。
- 与最新 Kit 发生冲突的历史实现。

### C3. Overengineering & Context Bloat

- 过长的默认 AGENTS.md、CLAUDE.md 或其他常驻指令。
- 应当按需加载却始终加载的知识和规则。
- 低风险任务被迫执行重量级工程流程。
- 形式化但无实际收益的多轮审查。
- 不必要的多 Agent 协作及任务编排。
- 过量的过程性文档、报告及状态文件。
- 无意义的全量测试、全量扫描及重复构建。
- 维护成本明显高于实际收益的自动化机制。

### C4. Missing or Ineffective Capabilities

- 重要工程约束仅存在于自然语言文档中。
- 缺少针对历史重复缺陷的可执行回归测试。
- 缺少必要的运行时验证或性能基线。
- 测试、构建和质量门禁不能有效发现实际问题。
- Agent 无法正确发现或调用相关能力。
- 风险路由失效。
- PR Authoring Kit 未有效集成。
- 工程知识沉淀缺少验证、晋升或淘汰机制。
- 关键工程流程无法可靠恢复、迁移或回滚。

### C5. Conflicts & Safety Risks

- 指令优先级冲突。
- 循环引用和重复触发。
- Hooks、Scripts 或自动化操作之间的冲突。
- 不安全的权限配置。
- 可能破坏工作区、用户配置或其他项目的机制。
- 过度依赖特定 Agent、机器路径或操作系统。
- 可能泄露凭据、私有代码及其他敏感数据的配置。
- 可能产生虚假测试通过、虚假完成或证据污染的机制。

每项重要发现应明确：

现象 → 证据 → 根因 → 实际影响 → 适用范围 → 推荐处置 → 风险 → 验证方法。

避免为了生成大量审查发现而人为夸大低价值问题。

## 6. Phase D — Asset Classification & Optimization Decisions

对具有实际工程意义的现有资产进行分类，并选择最合理的处置方式。

统一使用以下决策类型：

| Decision | 含义 |
|---|---|
| KEEP | 保留已有优秀实现 |
| REUSE | 复用已有机制，避免重复实现 |
| MERGE | 合并具有重叠职责的机制 |
| SIMPLIFY | 精简过度复杂的实现 |
| REFACTOR | 改善结构、职责及可维护性 |
| UPDATE | 更新过时规范、实现或依赖 |
| REPLACE | 使用已验证的更优机制替代 |
| REMOVE | 移除确认无效、过时或冗余的内容 |
| ARCHIVE | 保留历史价值，但退出活跃工作流 |
| ADD | 补齐具有明确实际收益的缺失能力 |
| DEFER | 证据不足或风险过高，暂缓处置 |

优先顺序：

KEEP / REUSE → MERGE / SIMPLIFY → UPDATE / REFACTOR → REPLACE / REMOVE → ADD。

该顺序是工程治理倾向，不是机械执行顺序。

对于每项重要资产，应考虑：

- 当前是否实际生效；
- 是否具有独立工程价值；
- 是否存在更简单的等价实现；
- 是否与其他机制重复；
- 是否值得长期维护；
- 是否具有可复用性；
- 是否存在隐含依赖；
- 修改后能否保持原有有效行为；
- 预期收益是否足以覆盖迁移及验证成本。

删除文件前应检查其引用关系、加载机制、运行依赖及历史设计意图。

无法确定是否安全移除时，优先保留、隔离或归档，而不是直接删除。

## 7. Phase E — Target Architecture & Optimization Plan

基于实际调查结果，形成适用于当前项目的目标工程体系。

原则上采用清晰分层、职责单一、按需加载的架构：

### L1 — Global Engineering Core

跨项目通用的工程原则、风险路由、质量标准、证据协议及持续演进机制。

### L2 — Domain Playbooks

具有领域特异性的工程知识及验证方法，仅在相关任务中加载。

### L3 — Project-specific Harness

当前项目真正需要的架构约束、开发工具、测试、运行时验证、性能基线及交付门禁。

### L4 — Agent & Environment Adapters

各 Agent、操作系统、Shell 及工具链的最小必要适配。

实际结构应以两套 Kit 的设计和当前环境为准。

不要为了满足分层形式而强制拆分文件、迁移目录或新增抽象。

优化方案应明确：

- 当前真实问题及其优先级；
- 优化目标及非目标；
- 计划保留、合并、精简、更新、移除及新增的内容；
- 预期收益及其测量方法；
- 潜在风险与兼容性影响；
- 实施顺序及依赖关系；
- 回归验证及回滚方案。

对高风险、不可逆或影响多个项目的变更进行必要的独立或对抗性方案审核。

低风险变更采用轻量方案，不要求无意义的重量级规划。

## 8. Phase F — Incremental Implementation

在完成必要分析和方案审核后，实际执行授权范围内的优化。

### F1. Instruction & Context Optimization

优化 AGENTS.md、CLAUDE.md、Rules 及其他指令体系：

- 保留关键且不可替代的约束。
- 删除重复、矛盾及过时内容。
- 将非必要常驻知识迁移至按需加载的 Skills 或 References。
- 合理划分全局、领域级及项目级职责。
- 建立清晰的规范来源与引用关系。
- 避免循环引用及重复加载。
- 保证指令精简后仍能正确触发必要工程能力。

不得仅通过减少文本长度来证明优化有效。

### F2. Skills & Agent Infrastructure Optimization

优化实际存在的 Skills、Plugins、Hooks、Scripts、MCP 及 Agent 协作机制：

- 保留高质量、高复用且实际有效的能力。
- 合并功能重复的机制。
- 更新存在兼容性问题的实现。
- 清理确认无效的入口及引用。
- 优化自动发现、任务路由及组合调用。
- 减少非必要常驻资源占用。
- 优先使用成熟原生机制，减少自建封装。
- 默认采用能够可靠完成任务的最简执行方式。

不得未经授权移除用户主动安装、但与当前项目无关的全局工具、插件或 Skills。

### F3. Workflow Optimization

依据 Engineering Workflow Kit 优化任务执行生命周期。

重点确保：

- 简单任务采用 Fast Path。
- 常规任务采用 Standard Path。
- 高风险任务采用与风险匹配的 Critical Path。
- 不必要的规划、报告和重复审核被合理精简。
- 关键验收条件和质量门禁不会被绕过。
- 实际运行行为能够在必要时得到验证。
- 长任务具备合理的中断恢复及交接机制。
- 失败和异常能够被准确报告。
- 工程经验能够有效沉淀，而非无限增加规则。

具体流程与分类名称以 Kit 的实际内容为准。

### F4. Executable Harness Optimization

将有价值且反复出现的工程经验尽可能转化为：

- 更合理的 API 和架构设计；
- 类型系统约束；
- 静态分析；
- 架构检查；
- 回归测试；
- Runtime Verification；
- 性能分析工具；
- 自动化质量门禁。

优先复用项目现有的测试及工具链。

不得为了形式上的机械化约束而引入大量低价值规则、误报或高成本检查。

如果某项约束只适合当前项目，应保留在项目级，不应盲目提升为全局规则。

本任务主要治理工程环境与工作流，不默认授权无关业务功能重构、大规模产品代码修改或技术栈迁移。

涉及产品架构调整时，应明确区分必要的 Harness 改进与独立的业务重构任务。

### F5. PR Authoring Kit Reconciliation

检查现有 PR 规范是否与最新 PR Authoring Kit 一致。

在目标上游允许的前提下，确保：

- 英文 PR 标题；
- 完整英文正文；
- 精简中文翻译正文；
- 图标、图片、GIF、视频、架构图及图表等非文字内容仅出现在英文正文；
- 根据 PR 类型、风险和规模动态选择正文结构；
- 测试结果、性能数据及视觉证据真实可追溯；
- 明确未验证事项、风险及兼容性限制；
- 遵循上游贡献指南、AI 贡献政策及自动化要求；
- PR 拆分、依赖关系及审查范围合理。

消除现有重复、冲突和过时的 PR 模板及生成规则。

不得机械覆盖目标仓库原生 PR 模板，也不得重复实现 PR Authoring Kit 已经提供的能力。

### F6. Cleanup & Consolidation

在完成依赖分析后，清理实际确认无效的：

- 重复规则；
- 废弃配置；
- 失效引用；
- 无用脚本；
- 过时模板；
- 冗余工作流；
- 无效自动化入口；
- 不再需要的临时工程文件。

对于仍有历史价值的资料，按需归档。

保留未提交修改、历史记录、测试证据、用户数据及有效工程经验。

清理不能破坏原有工程能力，也不能仅为了减少文件数量而进行。

## 9. Phase G — Engineering Knowledge Reconciliation

将当前项目已经积累的工程经验与 Engineering Workflow Kit 进行双向对照。

使用以下蒸馏逻辑：

Concrete Experience → Root Cause → Transferable Invariant → Enforceable Mechanism → Evaluation → Knowledge Promotion

判断本地经验是否应当：

- 保留为项目级约束；
- 晋升为领域级 Playbook；
- 提炼为通用 Skill；
- 转化为测试或验证工具；
- 推广为全局工程原则；
- 与已有知识合并；
- 因过时、无效或成本过高而淘汰。

尤其关注本地已经存在、但两套 Kit 尚未覆盖的优秀实践。

对于具有通用价值的改进，形成独立的 Kit Feedback / Patch Proposal，包含：

- 实际来源及证据；
- 所解决的问题；
- 可迁移的工程不变量；
- 适用范围及限制；
- 推荐实现；
- 验证结果；
- 与现有 Kit 的兼容性。

原则上不要未经授权直接修改作为输入的两套 Kit 原始文件。

避免将未经充分验证的个别经验污染全局工程规范。

## 10. Phase H — Adversarial Verification

将优化后的工程体系视为需要实际测试的软件产品。

不得以文档更新、文件删除、配置写入或静态检查通过作为最终验收依据。

### H1. Functional Verification

根据当前实际环境验证：

- Agent 能否实际发现并加载正确的工程规范；
- Skills 是否能够按需触发；
- 必要工程能力是否仍然有效；
- 两套 Kit 是否能够正确协同；
- 风险路由是否符合预期；
- 项目原有构建、测试、验证及交付机制是否正常；
- PR 是否能够按最新规范正确生成；
- 失败、未执行及阻塞状态是否得到正确报告；
- 必要的任务恢复及交接机制是否正常。

### H2. Regression Verification

重点攻击本次优化可能引入的回归：

- 精简指令导致关键约束丢失；
- 合并规则导致适用范围错误；
- 移除文件导致隐含依赖失效；
- Skills 路由错误或触发冲突；
- Hooks 重复触发或不再触发；
- 跨 Agent、跨 OS 配置不一致；
- 轻量工作流错误绕过高风险任务的必要检查；
- 工程能力表面精简、实际转移到其他重复机制；
- PR 规范失效或违反上游要求；
- 因优化而增加 Token、耗时、返工或人工干预。

### H3. Comparative Evaluation

在实施前记录必要基线，在实施后尽可能使用相同环境、任务、初始状态、模型配置及测试条件进行对照。

根据实际可测量性选择指标：

- 默认指令加载量；
- 实际任务上下文及 Token 开销；
- 重复规则及无效机制数量；
- Skills 路由正确率；
- 工具调用次数；
- 构建及验证耗时；
- 任务完成率；
- 缺陷检出率；
- 回归情况；
- 返工次数；
- 人工干预次数；
- 工程质量及维护成本；
- 跨平台及跨项目迁移能力。

明确区分：

- 实际测量结果；
- 静态分析结果；
- 合理推断；
- 预计收益；
- 尚未验证的假设。

不得将预计收益、文本精简比例或单次随机测试结果直接宣称为整体工程效率提升。

### H4. Representative Task Evaluation

使用少量但具有代表性的工程任务，对优化后的环境进行真实或隔离测试。

优先覆盖：

- 简单 Bug Fix；
- 常规 Feature；
- 非平凡 Refactoring；
- 高风险或跨模块变更；
- 测试失败及异常处理；
- PR 生成；
- 中断恢复；
- 必要的跨 Agent 或跨平台适配。

使用临时测试项目、隔离 Worktree、Dry Run 或其他低风险机制。

不未经授权创建真实远程 PR、上传附件、推送代码或修改生产环境。

### H5. Repair & Revalidation

发现问题后执行：

定位根因 → 修复 → 针对性验证 → 必要回归测试。

审查应具有明确停止条件。

当适用的关键质量门禁已经满足、剩余风险明确可接受，且继续优化的边际收益不足以覆盖成本时，应结束本轮治理。

不进行没有新证据、新发现或明确目标的无限循环审核。

## 11. Phase I — Safety, Scope & Reversibility

本任务默认授权当前项目及其实际依赖工程环境的非破坏性审查、精简、更新、配置优化和本地验证。

默认不授权：

- 无关项目的批量修改；
- 全机无差别清理；
- 擅自变更系统安全设置；
- 删除用户主动维护的无关全局配置；
- 破坏未提交修改；
- 清除历史记录、用户数据或凭据；
- 未经授权修改原始 Kit；
- 大规模业务代码重构；
- 未经授权的远程提交、推送、发布及部署。

对于影响多个项目的共享配置，应先明确影响范围、检查依赖、评估兼容性，并取得必要授权。

优先采用项目级修正或局部适配，避免将项目特定需求污染全局环境。

如果确实发现具有普遍意义的全局问题，可形成独立的 Global Optimization Proposal。

在执行重要修改前：

- 记录初始状态。
- 建立必要快照及备份。
- 明确回滚方法。
- 保护用户现有工作。
- 检查相关依赖。
- 避免暴露敏感信息。

禁止通过关闭质量门禁、削弱测试、隐藏失败、放宽权限或降低验收标准获得表面上的优化收益。

遵循 Agent 平台指令优先级、安全边界、用户授权及上游仓库规范。

## 12. Final Deliverables

完成必要实施、测试及修复后，提供精炼、真实、具有可操作性的最终报告。

原则上复用已有报告机制，不创建大量重复文档。

### 12.1 Executive Summary

概括优化前的主要问题、实际完成的治理工作、最终工程状态及关键限制。

### 12.2 Audit Findings

按影响程度、实际价值和风险整理重要发现。

明确问题、证据、根因、影响及处理状态。

### 12.3 Optimization Manifest

记录重要工程资产的实际处置结果。

| Asset / Mechanism | Previous State | Decision | New State | Rationale | Verification |
|---|---|---|---|---|---|

涵盖保留、复用、合并、精简、重构、更新、替换、移除、归档及新增的内容。

### 12.4 Before / After Evaluation

提供具有真实证据的优化前后对照。

| Metric | Before | After | Delta | Evidence |
|---|---|---|---|---|

不编造无法测量的指标。

### 12.5 Verification Report

列出必要验证命令、测试结果、运行证据及回归情况。

统一使用：

- PASS：实际执行且通过。
- FAIL：实际执行但失败。
- BLOCKED：存在明确阻塞。
- NOT RUN：尚未执行。
- PENDING：等待外部结果。
- N/A：确实不适用。

### 12.6 Remaining Risks & Limitations

记录未解决问题、暂缓事项、能力限制及需要额外授权的变更。

### 12.7 Kit Feedback

总结当前项目中值得反向贡献给两套 Kit 的优秀工程实践及经过验证的通用优化。

不存在实际有价值的反馈时，无需强行生成。

### 12.8 Maintenance & Rollback

说明：

- 优化后工程体系如何实际生效；
- 后续如何使用和维护；
- Kit 更新后如何进行增量对照；
- 如何迁移及回滚；
- 哪些机制不应重复建设。

## 13. Definition of Done

只有在适用的关键条件得到真实验证后，才可以宣告本轮优化完成：

- 已充分理解两套 Kit 与现有工程体系。
- 已识别并处理具有实际价值的问题。
- 已合理保留经过验证的优秀存量实现。
- 冗余、重复、过时及冲突机制得到合理治理。
- 工程体系保持必要的能力完整性。
- 默认上下文及工程工作流得到合理精简。
- 必要的验证和质量门禁仍然有效。
- PR Authoring Kit 与 Engineering Workflow Kit 正确协同。
- 不存在未解决的重大回归及关键安全问题。
- 重要修改具有真实依据及可逆机制。
- 优化收益、失败事项及剩余限制均得到准确记录。

如果现有体系已经足够成熟，且进一步修改没有明确收益，则允许最终结果为 NO-OP 或仅进行少量针对性修复。

不要求每轮治理必须产生大量修改。

## 14. Execution Directive

现在开始实际执行。

首先完整理解两套 Kit，调查并恢复现有工程环境的实际状态、历史设计意图和有效工程经验。

然后完成：

存量审查 → 差异分析 → 对抗性评估 → 资产分类 → 优化方案 → 必要方案审核 → 增量实施 → 精简清理 → 实际验证 → 回归修复 → 最终交付 → 有价值的 Kit Feedback。

自主选择与任务风险、实际复杂程度及预期收益匹配的执行深度。

不重复进行已经完成的外部技术调研，不盲目新增 Skills、工具、框架、文档或流程。

不局限于表面上的文件整理，而应深入实际工程机制、运行行为、上下文开销、验证有效性及长期维护成本。

不停止于分析、建议或方案设计，应完成授权范围内具有明确价值的实际优化工作。

最终目标不是使现有工程体系在形式上更加复杂、全面或规范，而是使其在实际使用中更加精简、可靠、高效、智能、可维护、可复用、可迁移，并具备持续演进能力。

**Optimize for engineering outcomes, not infrastructure volume.**
