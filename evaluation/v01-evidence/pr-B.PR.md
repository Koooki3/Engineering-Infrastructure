# Preserve valid rows in mixed batch imports

Branch: `fix/batch-import`

Previously, a malformed row in a mixed batch caused valid rows to be dropped. The fix preserves valid rows and reports the malformed row, allowing users to retain valid data while identifying the row that needs correction.

## Validation evidence

`change.txt` records that `python -m unittest tests.test_batch_import` passed all 7 tests. This is recorded evidence; the tests were not rerun while drafting this PR.

## Outstanding work and release status

- The Windows deployment probe did not run and remains outstanding.
- Release approval has not been given. The recorded test success does not constitute release approval.
- This is a local PR draft only; no PR has been published and no deployment has been performed as part of this drafting task.

## 中文摘要

此修复保留混合批次中的有效行，并报告格式错误的行，避免有效数据被丢弃。根据 `change.txt` 的记录，7 项单元测试已通过；本次撰写未重新运行测试。Windows 部署探测尚未执行，发布尚未获批。本文仅为本地 PR 草稿。
