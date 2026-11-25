# Changelog

## 1.0.1 — 2026-11-25
- deploy：目标指令文件缺失时创建；回滚可还原被替换的旧标记块；Skill 更新先改名保留旧目录再替换；中断时保存部分状态。强杀/断电不保证可恢复。
- ewk：git 状态读取失败不再静默绑定（Git 仓库内取证失败的 `run` 记为 FAIL，非 git 目录仍可用）；子模块路径含空格；evidence 记录基本校验；路径规范化用 realpath（Windows 短路径）。
- 部署计划改为 `deploy/plan.example.json`，本机状态与备份不再随仓库分发。

## 1.0.0 — 2026-11-25
- 新增 engineering-workflow skill（风险路由、证据绑定、纠正阶梯入口、领域验证表、两个模板）。
- 新增 `ewk.py`（run/check/guard/route）与 `tools/deploy.py`（复制安装 + 标记块，可校验可回滚）。
- 对抗性审核后修复：guard 漏检删除/重命名的受保护文件；`++` 开头行绕过密钥检测；脏子模块不进状态指纹；命令改动工作树时 PASS 未降级；非 git 目录的 PASS 默认通过；畸形记录崩溃；相对路径可执行文件解析；多目标更新备份目录同名冲突；块比较未统一行尾。
- 迁移：Lauren Tan 一轮的 CLAUDE.md 段落、`constraint-ladder`、Codex 的 `engineering-verification.md` 均保留不动；本版只追加路由块（见 `reports/evidence-and-decisions.md` 的 consolidate 条件）。
