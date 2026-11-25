# engineering-workflow-kit v1.0.0

跨项目、跨 Agent（Claude Code / Codex）、跨 OS（Windows / WSL）的最小工程闭环：风险路由（Fast/Standard/Critical）+ 证据绑定 + 机械检查。形态参照同级的 `pr-authoring-kit`：一个可部署的 skill 目录 + 说明；PR 阶段只交接给 `pr-authoring`，不复制、不改变其行为。

## 目录

```text
engineering-workflow/        # 唯一可部署单元（复制到各 skills 目录）
  SKILL.md                   # 5.9 KB 路由入口：边界、风险路由、不可妥协项、工具
  references/                # workflow / verification / correction-ladder / lessons，按需读取
  templates/                 # task-card、delivery（仅两个）
  scripts/ewk.py             # run / check / guard / route，stdlib Python ≥3.9
tools/deploy.py              # 可逆部署：复制安装 + 带标记的指令块；apply / verify / rollback
deploy/                      # plan.example.json（通用模板）与指令块；真实计划/状态/备份留在本机仓库之外
tests/                       # 61 项：脚本、部署、skill 卫生（体积/可移植/链接/PR 契约不回退）
reports/                     # 已脱敏的证据、决策、验证记录（不含本机路径与部署状态）
```

## 使用

- 默认：实质工程任务开始时 Agent 自动载入；你也可以直接说“按 engineering-workflow，Critical 档做”。不想要流程就说“直接做”。
- 档位：Fast（文档/低风险小修）、Standard（一般功能/非平凡修复）、Critical（架构、并发、数据迁移、安全、发布）。`ewk.py route` 给建议，风险升高立即升档，降档要写理由。
- 证据：`ewk.py run --evidence E.json --id unit -- <命令>`，交付前 `ewk.py check --evidence E.json --require unit`。代码一改旧 PASS 即 STALE。
- 机械检查：`ewk.py guard --base <基线>`（或 `--worktree-only`）；项目配置放仓库根 `.ewk.json`：`{"protected_paths":[],"local_path_re":"","bases":[]}`。
- 扩展领域：在 `references/verification.md` 的领域表加一行，只写已被本机项目验证的能力；项目专属命令和不变量留在项目自己的 AGENTS.md / 脚本。
- 部署：复制 `deploy/plan.example.json` 到仓库之外（如 `~/.ewk/plan.json`），把 `<ABS_PATH_TO>`、`<HOME>` 换成本机真实绝对路径（Windows 与 WSL 各用各自环境的路径与原生 Python）；先 `deploy.py apply --plan <plan> --state <state>`，状态文件与备份目录同样放在仓库之外（如 `~/.ewk/deployments/`），再 `verify`。目标指令文件不存在时会被创建，回滚时删除。
- 升级：改源目录 → `python -m unittest discover -s tests` → `deploy.py apply`（用新的 `--state` 文件）→ `verify`。
- 恢复：`deploy.py rollback --state <state.json>`；多次 apply 按相反顺序逐个回滚。`state` 已在 `.gitignore` 中排除；验证记录见 `reports/validation-and-deployment.md`。

## 兼容矩阵

| 目标 | 状态 | 证据 |
|---|---|---|
| Claude Code · Windows | 已部署；本会话 skill 清单已出现该 skill（自动发现生效） | `reports/validation-and-deployment.md` |
| Claude Code · WSL | 已部署；`verify` OK；无头触发测试 BLOCKED（登录过期） | 同上 |
| Codex · Windows / WSL | 已复制到 `~/.agents/skills` 并在 AGENTS.md 加路由块；Codex 自动发现 NOT_RUN（本机 PATH 无 codex CLI，未做 app-server 发现检查） | 同上 |
| 其他 Agent | 手动：把 `SKILL.md` 内容或路径交给它，脚本独立可用 | — |
| Python | 3.12（Windows）、3.14（WSL）测试通过；声明 ≥3.9 未在 3.9 实测 | 测试输出 |

## 已知限制

- 状态指纹不覆盖 `.gitignore` 忽略的文件；命令若改动工作树，`run` 会把 PASS 降为 FAIL。
- deploy 遇到目标是符号链接/junction 会拒绝，不会替换。
- `ewk.py` 的 evidence 是“状态绑定与一致性检查”，不是密码学证明，记录可被手工改写；多个 Agent 并行时各自使用独立的 `--evidence` 文件，工具不做并发写入协调。
- `route` 只是路径+标志的启发式建议。
- 本 kit 没有测量过“用它是否让任务更快/缺陷更少”：只有部署与行为层面的离线证据，见报告。
