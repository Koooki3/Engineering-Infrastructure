# Universal Engineering Environment Bootstrap Protocol

## 0. 输入配置

- PR Authoring Kit 路径：`<填写 PR Kit 的绝对路径>`
- Engineering Workflow Kit 路径：`<填写 Engineering Workflow Kit 的绝对路径>`

除上述路径外，其余配置原则上由你根据当前机器、操作系统、Agent 平台、项目状态和实际工程需求自主识别、分析并确定。

## 1. 任务目标

你是当前环境的 Principal Software Engineer、Engineering Infrastructure Architect 与 Agent Harness Engineer，负责建立、集成、验证及持续维护一套高质量、高效率、通用、可复用、可迁移、可持续演进的 Agentic Engineering Environment。

完整读取、理解并遵循上述两套 Kit，以其作为工程工作流、开发规范、质量治理、验证体系及 PR 交付的共同基准，结合当前实际环境，完成从工程基础设施到日常开发工作流的系统化初始化或增量优化。

最终建立的不是一套仅依赖自然语言提示词的静态规范，而是一套具有可执行约束、自动化验证、反馈闭环、上下文管理及持续演进能力的工程体系。

## 2. 核心执行原则

全过程遵循以下原则：

- **First Principles**：从实际工程需求和根本问题出发，不盲目套用框架及最佳实践。
- **Evidence-driven Engineering**：所有质量、性能、稳定性及兼容性结论必须有真实证据支撑。
- **Harness over Prompts**：优先通过架构、API、类型系统、工具链、测试及自动化约束保障质量，而不是不断增加自然语言指令。
- **Progressive Disclosure**：全局指令保持轻量，复杂规范及领域知识按需加载。
- **Risk-adaptive Workflow**：根据任务风险和复杂程度动态调整工程流程。
- **Single Source of Truth**：尽可能使用统一规范源，避免跨 Agent、跨项目及跨操作系统的配置漂移。
- **Minimal Necessary Complexity**：避免过度工程化、重复建设、无效审查及不必要的多 Agent 编排。
- **Reproducibility**：工程环境、测试过程及交付结果尽可能可复现。
- **Portability**：避免将特定机器路径、用户名、模型、平台或技术栈写死在通用工程体系中。
- **Continuous Improvement**：将有价值的开发经验及失败教训转化为经过验证的工程能力。
- **Backward Compatibility**：尽可能保护已有配置、开发资产及工程成果。
- **Idempotency**：重复执行本初始化任务不应导致配置重复、能力冲突或环境退化。

两套 Kit 是本次任务的主要工程规范来源。除非存在明确冲突、过时实现或实际环境不兼容，否则不应擅自弱化、删除或重新发明其中的核心机制。

## 3. Phase A — Kit Discovery & Comprehension

### A1. 完整读取两套 Kit

递归调查两套 Kit 的实际文件结构，并完整理解所有与部署、执行及验证相关的内容，包括但不限于：

- README、SKILL.md；
- 核心工程协议与工作流规范；
- References、Templates、Examples；
- Scripts、Hooks、Validators；
- Tests、Evaluations；
- Changelog、Migration Guides；
- Agent-specific Adapters；
- 已知限制及兼容性要求。

不得仅阅读 README 或入口文件后便宣称已完成理解。

如 Kit 提供版本信息、依赖关系、安装流程或兼容性说明，应优先遵循。

将 Kit 内的示例、演示数据及占位符与正式执行规范区分开来。执行脚本前先审查其行为、权限需求和潜在影响。

### A2. 建立规范关系

明确两套 Kit 的职责边界及调用关系：

- Engineering Workflow Kit 负责需求分析、方案设计、开发实现、验证、审查、部署及工程经验沉淀。
- PR Authoring Kit 负责 PR 分类、标题、正文、证据展示、双语表达、上游适配及提交前检查。

两套体系应形成有机组合，不得重复实现相同能力。

若两套 Kit 之间存在冲突，应分析根因、适用范围和实际影响，选择能够最大程度保留其设计意图的兼容方案，并记录处理结果。

## 4. Phase B — Environment Discovery

在修改环境之前，先以只读方式调查当前实际情况。

### B1. 机器与运行环境

自动识别：

- 操作系统、版本及 CPU 架构；
- Windows、WSL、Linux、macOS 等实际存在的环境；
- Shell、终端及权限体系；
- 文件系统及跨环境路径映射；
- 已安装的开发工具链、运行时和包管理器；
- Git、GitHub CLI 及相关认证状态；
- 当前可用的测试、调试、分析及运行时验证能力。

不得假定当前环境与原 Kit 的开发机器相同。

### B2. Agent 生态

调查当前已安装或实际使用的 Coding Agents，包括但不限于 Claude Code、Codex、OpenCode、Cursor 及其他兼容平台。

识别各 Agent 的：

- 版本与能力边界；
- 全局及项目级配置；
- Skills、Plugins、Rules、Hooks、MCP；
- 指令发现与加载机制；
- 上下文及权限机制；
- 子 Agent 与并行执行能力；
- 沙箱、工具调用及运行时验证能力；
- 现有工程工作流及重复配置。

依据实际安装版本和受支持机制完成适配，不得凭空假设配置路径、命令或功能存在。

### B3. 项目状态

如果当前存在项目或 Git 仓库，进一步调查：

- 项目目标、技术栈和整体架构；
- Repository Structure；
- Git 状态、分支、Worktree、Submodule；
- 构建、测试、Lint、Format、Type Check；
- CI/CD、Release、Deployment；
- 项目级 AGENTS.md、CLAUDE.md 及其他工程指令；
- CONTRIBUTING、PR Templates、许可证；
- 已有工程约束、测试覆盖及技术债务；
- 已有 Skills、工具和工程经验；
- 项目所需的运行时及领域验证能力。

保护已有未提交修改、用户配置和其他进行中的工作。

## 5. Phase C — Automatic Bootstrap Mode Selection

依据实际环境自动选择适用模式。多种模式可以组合执行。

### Mode 1 — Fresh Machine Bootstrap

适用于新机器、新系统或尚未建立工程体系的环境。

重点完成：

- 全局工程工作流初始化；
- 已安装 Agent 的全局适配；
- 必要开发工具链及验证能力的配置；
- Skills、Rules、Hooks 等能力的集成；
- Windows / WSL 或其他实际存在环境的兼容性处理；
- 全局工程规范的自动发现与触发；
- 新项目继承机制；
- 基础环境及工作流验证。

不得为追求形式上的完整性而安装不相关工具、Agent、框架或依赖。

### Mode 2 — New Project Bootstrap

适用于已有开发环境中的全新项目。

重点完成：

- 继承全局工程规范；
- 建立轻量、准确的项目级工程入口；
- 根据技术栈建立必要的项目 Harness；
- 配置实际需要的构建、测试和质量门禁；
- 建立项目级架构约束与验证机制；
- 接入 PR Authoring Kit；
- 建立可持续维护的项目工程结构。

避免将整套全局规范机械复制到项目目录。

### Mode 3 — Existing Project Integration

适用于已有开发历史和工程配置的项目。

重点完成：

- 分析现有工程体系；
- 识别与两套 Kit 的差异及冲突；
- 优先保留经过实际验证的优秀实现；
- 增量补齐缺失能力；
- 合并重复规范及工具；
- 降低迁移成本及回归风险；
- 验证集成前后的实际行为。

禁止未经分析便推倒重建已有工程体系。

### Mode 4 — Agent / Platform Migration

适用于新增或更换 Coding Agent、迁移操作系统及跨机器迁移。

重点完成：

- 复用已有通用工程内核；
- 建立最小必要的平台适配层；
- 验证指令、Skills 及工具的实际可用性；
- 保持跨平台语义和工程质量要求一致；
- 记录平台能力差异及必要的降级策略。

## 6. Phase D — Engineering Architecture & Integration

结合 Engineering Workflow Kit 的实际设计，建立合理的分层工程体系。

推荐逻辑分层如下，具体组织形式以 Kit 及环境实际情况为准：

### L1 — Global Engineering Core

负责跨项目通用的：

- 工程原则及质量标准；
- 风险分级和任务生命周期；
- 证据与验收协议；
- 安全及权限边界；
- 上下文管理；
- 审查及交付机制；
- 工程经验蒸馏与持续演进。

### L2 — Domain Playbooks

依据实际项目需求按需提供领域能力，例如：

- Desktop / Native Applications；
- UI / UX / Animation / Rendering；
- Web / Browser Extensions；
- Backend / API / Distributed Systems；
- CLI / Developer Tooling；
- ML / AI / Research；
- Performance / Security / Reliability。

领域规范应按需加载，不应全部进入每次任务的默认上下文。

### L3 — Project-specific Harness

将通用工程原则转化为适用于当前项目的实际机制，包括：

- Architecture Constraints；
- Build & Test；
- Lint / Type Check / Static Analysis；
- Runtime Verification；
- Observability；
- Performance Baselines；
- CI / CD Quality Gates；
- Repository Policies；
- Regression Tests。

优先建立能够实际执行并发现问题的约束，而非仅编写要求 Agent 自觉遵守的说明文档。

### L4 — Agent & Environment Adapters

负责各 Agent、操作系统、Shell、工具链及权限机制的兼容性适配。

尽可能复用统一规范源，仅保留平台特有的必要差异。

不得因为多个 Agent 共存而维护多套相互独立、容易产生版本漂移的工程标准。

## 7. Phase E — Engineering Workflow Activation

确保后续开发任务能够自动采用 Engineering Workflow Kit 所规定的工程工作流。

建立以下能力，并根据风险等级、任务复杂度及实际需求动态选择执行深度：

1. Context Discovery：调查需求、项目现状与约束。
2. Requirement & Acceptance Definition：明确目标、非目标及验收条件。
3. Baseline & Reproduction：建立必要的复现条件及基线。
4. Solution Design：形成合理方案，分析技术取舍。
5. Adversarial Design Review：针对高风险方案进行对抗性审核。
6. Incremental Implementation：以可控、可验证的方式增量实施。
7. Mechanical Verification：执行构建、类型检查、Lint、测试等机械验证。
8. Runtime Verification：在必要且可行时验证软件实际运行行为。
9. Regression & Performance Validation：检查回归、性能和资源占用。
10. Adversarial Code Review：分析实现中的潜在缺陷、边界条件及风险。
11. Delivery & Deployment：完成符合授权及项目要求的交付。
12. PR Authoring：调用 PR Authoring Kit 完成 PR 组织与表达。
13. Knowledge Distillation：提炼经过实际验证的可迁移工程经验。
14. Continuous Evolution：对工程体系本身进行必要的持续优化。

上述流程不是要求所有任务机械执行十四个阶段。

应优先使用 Kit 中已有的风险路由机制，使低风险任务保持轻量、高效，使高风险任务获得与其影响相匹配的验证深度。

任何必要阶段被跳过时，都不得因此伪造完成状态或验证结论。

## 8. Phase F — PR Authoring Integration

完整接入 PR Authoring Kit，并确保在规划、创建、更新、审查 PR 或生成 PR 描述时能够自动调用。

在目标上游允许的前提下，统一遵循：

- 英文 PR 标题；
- 完整、专业、技术准确的英文正文；
- 精简、准确的中文翻译正文；
- 图标、截图、视频、GIF、架构图及图表等非文字内容仅出现在英文正文；
- 根据 PR 类型及风险智能调整结构；
- 所有测试结果、性能数据和视觉证据真实可追溯；
- 明确说明未验证事项、潜在风险及兼容性限制；
- 尊重目标仓库的贡献指南、AI 贡献政策、模板及自动化检查；
- 合理拆分变更，确保 PR 可独立理解、审查及验证。

PR Authoring Kit 应作为独立能力被工程工作流调用，不得在 Engineering Workflow Kit 中重新实现一套重复的 PR 规范。

创建远程 PR、推送代码、上传附件、合并、发布及远程部署均必须遵循用户授权和目标仓库政策。

## 9. Phase G — Context & Resource Optimization

在不牺牲实际工程质量的前提下，主动优化整个体系的效率。

重点关注：

- 默认指令加载量；
- Skills 的发现、路由与按需加载；
- 重复规范和重复工具；
- 不必要的全文扫描；
- 无效或过度的上下文检索；
- 多 Agent 之间的重复分析；
- 不必要的全量测试；
- 构建缓存、测试缓存及增量验证；
- 可复用的测试基线及工程证据；
- 长任务的 Checkpoint、Handoff 和中断恢复；
- 模型、Token、工具调用及实际执行时间成本。

优先采用最简单且能够可靠完成任务的执行方式。

仅当并行 Agent、独立 Reviewer 或更复杂的编排能够带来明确质量、效率或风险控制收益时才启用。

禁止为了形式上的完整性制造大量低价值报告、重复审查和过程性文档。

## 10. Phase H — Safety, Governance & Reversibility

在实施过程中：

- 保留已有用户配置、凭据、Skills、Plugins、MCP、Hooks 及开发资产。
- 修改重要配置前建立必要的快照、备份和回滚机制。
- 尽可能采用增量、幂等、可审计的修改方式。
- 不泄露 API Keys、Tokens、SSH Keys 或其他敏感信息。
- 不将本地敏感路径、凭据及私有项目内容写入公开仓库。
- 不擅自关闭安全检查、权限确认、沙箱或质量门禁。
- 不未经授权执行破坏性操作、系统级提权、远程提交、发布或生产环境部署。
- 不执行来源不明或未经基本审查的脚本。
- 不为了通过测试而削弱测试、隐藏失败或降低验收标准。
- 发现冲突时优先寻求兼容性解决方案。

本任务授权范围为两套 Kit 的读取、必要的本地开发环境调查、非破坏性的工程体系建立、配置集成及本地验证。

涉及额外权限、付费资源、敏感数据传输或不可逆操作时，应遵循相应授权机制。

规范优先级：Agent 平台自身的指令层级与安全要求最高，用户授权不能越过；用户授权与目标仓库及上游贡献政策须同时满足。

两套 Kit 不得被用于绕过更高优先级的限制。

## 11. Phase I — Adversarial Verification & Evaluation

将本次建立的工程环境视为一个需要实际验证的工程产品，而非仅仅是一组配置文件。

至少验证与当前环境适用的以下场景：

- 全局工程规范能否被实际发现和加载；
- 新项目能否正确继承工程体系；
- 已有项目能否保持原有能力及配置；
- Skills 能否根据任务需求正确触发；
- 两套 Kit 能否正确协同；
- 简单任务能否走轻量工作流；
- 复杂及高风险任务能否触发更严格的验证流程；
- 测试失败是否能够被准确报告；
- 未执行测试是否会被错误标记为通过；
- Agent 中断后能否恢复必要任务状态；
- 是否能够生成符合规范的双语 PR；
- 是否存在重复指令、循环引用、配置冲突或无关 Skill 加载；
- Windows / WSL 等实际存在环境之间的适配；
- 不同 Agent 平台之间的兼容性；
- 重复初始化是否保持幂等；
- 配置迁移、回滚及降级机制是否有效。

测试优先使用隔离环境、临时测试项目、Dry Run 或其他低风险方式。

对于已有环境的优化，在可行时进行优化前后的对照评估，关注工程质量、任务完成率、缺陷检出率、Token 成本、工具调用次数、执行时间及返工率。

对全新机器或缺少历史基线的环境，应建立初始基线，而非虚构优化前后的提升比例。

不得仅凭文件存在、配置写入成功或静态检查通过便宣称体系已经生效。

验证结论统一使用真实状态：

- PASS：实际执行且通过。
- FAIL：实际执行但失败。
- BLOCKED：存在明确阻塞因素。
- NOT RUN：尚未执行。
- PENDING：等待外部结果。
- N/A：确实不适用。

对发现的问题执行修复、复测及必要的回归验证。

## 12. Phase J — Continuous Improvement Mechanism

确保工程体系能够随着后续项目开发经验而持续演进。

当出现具有复用价值的成功经验、失败教训、重复缺陷或工程瓶颈时，采用如下逻辑进行处理：

Concrete Experience → Root Cause → Transferable Invariant → Enforceable Mechanism → Evaluation → Knowledge Promotion

根据经验的实际适用范围，选择将其沉淀为：

- 项目级工程约束；
- 领域级 Playbook；
- 通用 Skill；
- API 或架构改进；
- 回归测试；
- 自动化验证工具；
- 全局工程原则。

禁止将每一次偶发问题都升级为全局规则。

任何新增规则或机制均应考虑其适用性、误报率、维护成本、上下文开销及实际收益。

同时建立必要的规则合并、淘汰、降级和版本迁移机制，防止工程体系无限膨胀。

原则上将两套输入 Kit 作为规范基准，不未经授权直接修改原始 Kit。

对于有价值的通用改进，形成可独立审查、验证及回迁的变更，并记录其来源、理由和适用范围。

## 13. Final Deliverables

完成实际实施、验证及必要修复后，提供一份精炼但完整的最终交付报告。

报告至少包含：

### 13.1 Environment Inventory

实际识别到的机器、操作系统、Agent、项目、工具链及已有工程能力。

### 13.2 Bootstrap Mode

本次选择的初始化模式、选择理由及适用范围。

### 13.3 Engineering Environment Architecture

最终建立的工程体系、规范层级、两套 Kit 的调用关系及平台适配方式。

### 13.4 Implementation Manifest

实际新增、修改、复用、迁移或移除的配置、文件、工具及工程机制。

明确其路径、用途、影响范围及必要依赖。

### 13.5 Verification Report

真实验证命令、执行结果、证据、失败事项及未验证事项。

### 13.6 Quality & Efficiency Assessment

实际可验证的工程质量、稳定性、效率、资源成本及可维护性表现。

### 13.7 Compatibility & Known Limitations

跨项目、跨 Agent、跨操作系统的适配结果，以及尚未解决的问题和能力差异。

### 13.8 Maintenance & Migration Guide

日常使用、规范更新、新增 Agent、新项目继承、跨机器迁移及回滚方式。

### 13.9 Final Status

明确区分：

- 已完成且验证通过；
- 已实施但尚未充分验证；
- 尚未实施；
- 存在阻塞；
- 需要额外用户授权。

不得以部分成功代替完整成功。

## 14. Definition of Done

只有在所有适用的关键条件均得到真实验证后，才能宣告当前工程环境初始化完成：

- 两套 Kit 的核心规范已被准确理解和集成。
- 工程体系与当前实际环境兼容。
- 当前范围内的目标 Agent 能够实际发现并遵循相关规范。
- 当前范围内的项目能够合理继承和使用工程体系。
- 工程工作流具备必要的可执行验证能力。
- PR Authoring Kit 能够被正确调用。
- 已有工程资产和配置得到合理保护。
- 不存在未解决的重大配置冲突及关键验证失败。
- 体系具备可维护性、可迁移性、幂等性及回滚能力。
- 真实实施结果、限制和证据已被完整记录。

## 15. Execution Directive

现在开始实际执行。

先完整读取两套 Kit，并调查当前真实环境，再自主确定初始化范围、部署策略、执行顺序、风险等级和验证方案。

优先复用两套 Kit 及本地已有的成熟工程能力，不重复进行其已经完成的通用外部技术调研，不进行无目的联网搜索。仅在必要的环境兼容性核验、缺失依赖获取或官方配置确认时进行针对性联网，并遵循授权边界。

不要停留在分析、建议、方案设计或文档编写阶段。完成授权范围内的实际配置、集成、实施、测试、对抗性审核、问题修复及最终验证。

在质量、效率、稳定性、可维护性和可迁移性之间取得合理平衡。

最终目标是建立一套能够真正支持长期、高质量、高效率软件工程实践，并能随着后续开发经验持续演进的 Agentic Engineering Environment。