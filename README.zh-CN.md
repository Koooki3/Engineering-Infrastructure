# Engineering Infrastructure

**面向 Coding Agents 的可迁移、跨平台工程工作流与规范体系。**

[English](README.md) · [初始化协议](BOOTSTRAP.md) · [优化协议](OPTIMIZE.md) · [许可证](LICENSE)

Engineering Infrastructure 将工程协议、Skills、模板及轻量 Python 工具组合为一套可复用的工程基础设施，用于初始化开发环境、优化已有工程体系，以及组织具有真实验证证据的 PR 交付。

项目追求的是实际工程成果，而不是提示词、规则、工具或自动化流程的数量。通过可执行约束、证据驱动验证、风险自适应流程和经验沉淀，在工程质量与开发成本之间取得合理平衡。

## 核心组成

| 组件 | 职责 |
| --- | --- |
| [BOOTSTRAP.md](BOOTSTRAP.md) | 新机器、新项目、新 Agent 的初始化、迁移及集成。 |
| [OPTIMIZE.md](OPTIMIZE.md) | 对已有工程环境进行审查、精简、清理、更新和优化。 |
| [Engineering Workflow Kit](engineering-workflow-kit/README.md) | 风险路由、工程任务生命周期、证据记录、机械检查及可逆 Skill 部署。 |
| [PR Authoring Kit](pr-authoring-kit/pr-authoring/SKILL.md) | 根据变更类型和上游要求，生成证据驱动、英文优先的双语 PR。 |

两套 Kit 是可独立维护的规范源；两个协议是初始化及持续治理的执行入口。项目开发中的优秀经验经过验证后，可通过独立变更反向贡献至 Kit，而不是直接将所有局部经验升级成全局规则。

## 设计原则

- Harness 优先：通过架构、API、类型系统、测试及可执行检查解决问题，而不是不断增加提示词。
- 证据先于断言：验证记录与仓库状态绑定，准确报告失败、阻塞及未执行事项。
- 风险自适应：根据任务实际影响和不确定性选择必要流程，风险升高时升级验证。
- 渐进式披露：轻量入口，复杂知识按需加载。
- 存量优先：保留有效实践，先复用、合并和精简，再考虑新增。
- 可迁移、可逆：适配真实 Agent、系统、项目和授权边界，保护已有工程资产。
- 持续演进：将重复失败转化为经过验证的工程约束，淘汰无实际收益的规则。

## 快速开始

### 1. 获取仓库

```bash
git clone https://github.com/Koooki3/Engineering-Infrastructure.git
```

需要拥有仓库访问权限。将规范源与本机部署状态分离；执行部署脚本前应审查配置，不要复用其他机器的实际部署计划或回滚状态。

### 2. 选择执行入口

| 场景 | 使用协议 |
| --- | --- |
| 全新机器、新项目、新 Agent | [BOOTSTRAP.md](BOOTSTRAP.md) |
| 现有项目首次接入 Kit | [BOOTSTRAP.md](BOOTSTRAP.md) |
| 现有规则膨胀、重复、过时 | [OPTIMIZE.md](OPTIMIZE.md) |
| Kit 升级、阶段性工程治理 | [OPTIMIZE.md](OPTIMIZE.md) |

### 3. 将以下指令交给 Coding Agent

```text
完整读取并执行所选协议。

执行协议：<BOOTSTRAP.md 或 OPTIMIZE.md 的绝对路径>
Engineering Workflow Kit：<engineering-workflow-kit 的绝对路径>
PR Authoring Kit：<pr-authoring-kit 的绝对路径>

先调查实际环境，再进行修改。优先复用已有能力，尊重项目规范
和授权边界，仅实施具有明确收益的变更。实际验证结果，报告
失败、限制及回滚方法。未经明确授权不得推送或发布任何内容。
```

Agent 应根据实际执行环境解析路径（包括适用的 WSL 路径映射），识别 Skill 加载机制，并完成必要的项目适配。目前协议主体主要使用中文，Agent 需要能够理解这些内容。

在本机安装 Workflow Skill 及指令块：把 [`plan.example.json`](engineering-workflow-kit/deploy/plan.example.json) 复制到仓库之外，将 `<ABS_PATH_TO>`、`<HOME>` 占位符替换为真实绝对路径（可交给 Bootstrap Agent 生成），再用该环境自己的 Python 执行：

```bash
python -I -B engineering-workflow-kit/tools/deploy.py apply  --plan ~/.ewk/plan.json --state ~/.ewk/deployments/state-1.json
python -I -B engineering-workflow-kit/tools/deploy.py verify --state ~/.ewk/deployments/state-1.json
python -I -B engineering-workflow-kit/tools/deploy.py rollback --state ~/.ewk/deployments/state-1.json
```

计划、状态文件与备份应放在仓库之外（放在仓库内也已被 `.gitignore` 排除）。每次 `apply` 使用新的 `--state` 文件，回滚时按相反顺序进行。

本项目目前不提供适用于所有环境的一键安装程序。Bootstrap 协议负责整体集成，Workflow Kit 的部署工具负责根据本机计划安装其 Skill 及标记指令块。

## Engineering Workflow Kit

工程任务根据风险采用最小必要流程：

| 风险档位 | 适用场景 | 最低要求 |
| --- | --- | --- |
| Fast | 低风险局部修改 | 针对性检查及简洁交付 |
| Standard | 常规功能、非平凡缺陷修复 | 验收条件、回归测试及自审查 |
| Critical | 架构、并发、迁移、安全、发布等 | 显式验收契约、深入审查、隔离验证和回滚规划 |

`ewk.py` 提供四项轻量能力：

| 命令 | 用途 |
| --- | --- |
| `run` | 带超时执行命令，记录结果及仓库状态。 |
| `check` | 检查证据一致性、时效性及必需检查结果。 |
| `guard` | 对受保护路径、编码及部分凭据模式执行机械检查。 |
| `route` | 根据变更路径和风险标志建议工作流档位。 |

证据绑定不是不可伪造的执行证明；Git 指纹不能完整覆盖被忽略文件及外部运行环境，guard 也不能代替专业的安全扫描。部署、验证和回滚详情见 [Workflow Kit 文档](engineering-workflow-kit/README.md)。

## PR Authoring Kit

- 英文标题，上游允许时采用 Conventional Commits 风格。
- 完整英文正文及精简简体中文正文，以目标仓库政策为准。
- 截图、录屏、图表、架构图等视觉证据仅出现在英文正文。
- 根据实际变更提供真实测试结果、性能测试方法、风险及审查重点。
- 不虚构证据，不擅自发布，不覆盖上游贡献规范或 AI 政策。

使用 [Skill](pr-authoring-kit/pr-authoring/SKILL.md)、[PR 模板](pr-authoring-kit/pr-authoring/pull_request_template.md) 和 [示例](pr-authoring-kit/pr-authoring/example.md) 即可接入。

## 验证与兼容性

v1.0.0 的原始验证记录为 56 项离线测试通过。加固后，全部 62 项离线测试已在本机 Windows（Python 3.12）和 WSL Ubuntu（Python 3.14）通过；CI 在 Ubuntu 和 Windows 上运行（见 `.github/workflows/ci.yml`）。这些是特定环境的结果，不代表所有安装均已验证。

| 环境 | 已记录的状态 |
| --- | --- |
| Windows Claude Code | 已部署，观察到 Skill 自动发现 |
| WSL Claude Code | 已部署并通过完整性验证，无头触发测试受阻 |
| Windows / WSL Codex | 已部署文件，实际发现及调用尚未验证 |
| 其他 Agent / 操作系统 | 需要适配，尚未验证 |
| Python 3.9+ | 声明支持的最低版本，由 CI 覆盖（以最新 Actions 结果为准） |

执行离线测试：

```bash
cd engineering-workflow-kit
python -I -B -W error::ResourceWarning -m unittest discover -s tests
```

目前尚无受控任务级实验能够证明具体的任务完成率、缺陷数量、耗时或 Token 消耗改善幅度。已知限制见 [Workflow Kit README](engineering-workflow-kit/README.md)。

## 参考与贡献

项目吸收了 [Lauren Tan 的工程实践分享](https://ai.engineer/code/2026/talks/lauren-tan)、[OpenAI Harness Engineering](https://openai.com/index/harness-engineering/)、[Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) 及 [Google Engineering Practices](https://google.github.io/eng-practices/) 等工程思想。本项目采用自定义工程规范，不代表官方行业标准或上述机构的认可。

欢迎基于真实工程问题提出可验证的改进。优先通过测试和可执行约束实现长期收益，避免重复建设，并将通用规范与私人项目数据、本机部署状态分离。

## 许可证

[Apache License 2.0](LICENSE)。
