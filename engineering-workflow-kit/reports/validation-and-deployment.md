# 验证、对抗性审核与部署记录

环境：Windows 11 + Python 3.12.8（anaconda）、git 2.49；WSL Ubuntu-26.04 + Python 3.14.4。kit 版本 1.0.0，无 git 仓库，故不存在 commit SHA；以文件哈希为版本凭据（部署后 `SKILL.md` 前 12 位 `0e1b4177d545`，四处安装一致）。

## 1. 离线测试（真实执行）

| 检查 | 命令 | 结果 |
|---|---|---|
| 全量单测 | `python -I -B -W error::ResourceWarning -m unittest discover -s tests` | Windows 56 项 OK；WSL 56 项 OK（ResourceWarning 当错误） |
| 覆盖 | `ewk`：run/check/guard/route 各正反例，含路径含空格与中文、超时杀孙进程、子模块、删除/重命名；deploy：安装/幂等/外来目录拒绝/漂移/更新回滚/后续编辑存活/多目标同秒备份；skill 卫生：入口体积 <6.5 KB、无本机路径或项目名、链接存在、状态词与脚本一致、PR 规则未复制 | 见 `tests/` |
| 变异测试（改坏脚本看测试是否变红） | 对 `ewk.py` 副本做 6 处改动 | 4 处被杀；“超时记 PASS”存活 → 补断言后现被杀；“route 回退理由”为等价变异（无行为差异）。 |
| 真实内容回滚演练 | 把部署前备份的真实 CLAUDE.md、AGENTS.md 复制到临时目录，apply → verify → rollback | 字节完全一致；安装目录已移除。 |

## 2. 对抗性审核（独立子代理，只读，真实复现）

发现 9 条，5 条 high/med 会造成虚假 PASS 或漏检，全部复现后修复并加回归测试：guard 漏检删除/重命名的受保护文件（high）；`++` 开头的新增行绕过密钥检测（med）；脏子模块不进状态指纹（high）；命令改动工作树后 PASS 仍绑定“运行后”状态（med）；非 git 目录 PASS 默认通过（med）。另修：畸形记录崩溃、相对路径可执行文件、链接目录拒绝、块比较统一行尾。未修并已写入限制：`.gitignore` 忽略文件不进指纹。文本层面：description 与正文矛盾已改；与 work-handoff/constraint-ladder 的重叠通过“边界澄清”处理，`correction-ladder.md` 与 `constraint-ladder` 并存为已知重复（退役条件见决策表）。
部署阶段另由我自查发现并修复 1 条：Windows 更新时两目标同一秒备份目录同名，第二目标更新失败（当时 `~/.agents/skills` 仍是旧版）；已修、加确定性回归、重新 apply，四处安装哈希一致。

## 3. 路由评测（模拟，不是真实自动触发）

由独立子代理仅凭 5 个 skill 的描述对 12 条提示选择：正例 6/6 选 engineering-workflow 并给出合理档位（幂等重试→Standard，用户表迁移→Critical，批量替换→Standard）；负例 6/6 正确不选（问答、单行文档、PR 文案→pr-authoring、落地页→design-hub、接手→work-handoff、论文→无）；含注入日志的提示不执行日志里的 `git push --force`，只做用户要求的重构。样本 12 条、同一模型自评，不能代表真实触发率。

## 4. 部署

只增不删，全部可逆。部署前后指纹：

| 文件 | 部署前 SHA-256（前 12 位） | 部署后 |
|---|---|---|
| Windows `.claude\CLAUDE.md` | 08f6ad0f1437 | 3b23049ef9ec |
| WSL `~/.claude/CLAUDE.md` | 08f6ad0f1437 | 3b23049ef9ec（与 Windows 一致，符合“WSL 为主、Windows 副本”） |
| Windows `.codex\AGENTS.md` | a98c8ad54a8f | 480eced69a52 |
| WSL `~/.codex/AGENTS.md` | 3a7a73811f03 | 39fdd35f1d8d |
| 两侧 `.claude/settings.json` | 94ccc86f0abf / d9b30ec98757 | 未改动 |

- 新增 4 个复制安装：Windows 与 WSL 的 `~/.claude/skills/engineering-workflow`、`~/.agents/skills/engineering-workflow`（含 `.ewk-manifest.json`）。同步来源：本 kit 的 `engineering-workflow/`；一致性检查：`deploy.py verify`。
- 4 个指令文件各追加一个 `<!-- ewk:begin -->…<!-- ewk:end -->` 块（约 450 B，常驻上下文净增）；原有 Lauren Tan 段落及其他内容未动。
- 未改动：pr-authoring 的链接、constraint-ladder、work-handoff、任何 hook/权限/插件/MCP、BrimDeck 及其他真实仓库。未推送、未开 PR、未联网、未装远程依赖。
- 生效证据：本会话中途 Windows 侧 skill 清单已出现 `engineering-workflow` 及其描述（自动发现生效）；`deploy.py verify` 两侧 OK。

状态文件（`reports/deployments/`）：Windows `state-windows.json`（首装）→ `-2`（部分，仅 `.claude` 更新，因上述备份冲突失败）→ `-3`（`.agents` 更新）；WSL `state-wsl.json` → `-2`。

## 5. 回滚（按相反顺序，各环境用各自 Python）

```powershell
cd D:\桌面\engineering-workflow-kit
python -I -B tools\deploy.py rollback --state reports\deployments\state-windows-3.json
python -I -B tools\deploy.py rollback --state reports\deployments\state-windows-2.json
python -I -B tools\deploy.py rollback --state reports\deployments\state-windows.json
wsl.exe -d Ubuntu-26.04 -- python3 -I -B "/mnt/d/桌面/engineering-workflow-kit/tools/deploy.py" rollback --state "/mnt/d/桌面/engineering-workflow-kit/reports/deployments/state-wsl-2.json"
wsl.exe -d Ubuntu-26.04 -- python3 -I -B "/mnt/d/桌面/engineering-workflow-kit/tools/deploy.py" rollback --state "/mnt/d/桌面/engineering-workflow-kit/reports/deployments/state-wsl.json"
```

回滚前自动核对安装目录哈希，被手改则拒绝（`--force` 覆盖）；指令块若被手改也拒绝；块之外的后续编辑保留。回滚已在临时目录对真实内容演练通过；对当前真实部署未执行（执行即撤销部署）。

## 6. 未执行 / 未验证

- Codex 对 `~/.agents/skills/engineering-workflow` 的实际发现与路由块生效：NOT_RUN（本机 PATH 无 codex CLI）。
- WSL Claude Code 无头触发测试：BLOCKED（`OAuth session expired`）。因此没有真实自动触发率数据。
- A/B 效率对照（耗时、返工、缺陷检出、token）：NOT_RUN。没有旧版可重建的同任务基线，也没有足够样本；不宣称任何效率或质量提升。本 kit 的证据是“机制正确且可逆”，不是“更有效”。
- Python 3.9 兼容：声明但未在 3.9 实测。Windows 符号链接/junction 目标的 deploy 行为只靠代码路径，未建 junction 实测。
- 其他项目类型（Web/ML/服务端）的领域规则仅有通用写法，未做本机深读。
- 没有对任何真实项目仓库做试点改动（授权边界：项目级只提建议）。建议试点：在 BrimDeck 一次 Standard 任务里用 `ewk run/check` 取代手工“按完整提交登记”，观察一周后按决策表的条件处理 consolidate。
