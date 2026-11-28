Title: fix(batch-import): preserve valid rows in mixed batches

## Summary

Previously, a malformed row in a mixed batch caused valid rows to be dropped. The fix preserves the valid rows and reports the malformed row, so users retain valid input while being informed of the invalid row.

## Validation

- PASS (recorded in `change.txt`): `python -m unittest tests.test_batch_import` — 7 tests passed.
- NOT RUN: the Windows deployment probe remains outstanding. Windows deployment behavior is unverified.

The supplied workspace contains the change record only; implementation, tests, and raw test logs are unavailable. The reported test result was not independently rerun while drafting.

## Release status

Release approval has not been given. Keep this as a draft pending the Windows deployment probe and release approval; the passing unit tests do not establish deployment readiness or release authorization.

## Local preflight

The record identifies `fix/batch-import` as the fix branch. This checkout is on `main` at `1c0ceaa56c2eaa024e8612526fcdc2a1b15121b7` and contains only `change.txt`; the fix branch, implementation diff, and intended PR base cannot be verified here. No remote, upstream policies, or PR template are available in the supplied project. Confirm those before publication. This artifact is a local draft only.

## 中文摘要

修复混合批次中遇到格式错误行时丢弃有效行的问题：保留有效行，并报告错误行。记录显示批量导入单元测试共 7 项通过，本次起草未独立重跑。Windows 部署探测尚未执行，发布尚未获批；应保持草稿状态，等待部署探测和发布批准。当前工作区仅含变更记录，无法核验修复分支及代码差异，发布前还需确认上游规范。
