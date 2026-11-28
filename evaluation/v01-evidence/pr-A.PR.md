# Preserve valid rows in mixed batch imports

Branch: `fix/batch-import`

Previously, a malformed row in a mixed batch caused valid rows to be dropped. This fix preserves the valid rows and reports the malformed row, allowing users to retain valid data while identifying the row that needs correction.

Validation: `python -m unittest tests.test_batch_import` passed all 7 tests.

The Windows deployment probe has not run and remains outstanding. Release approval has not been given; the passing tests do not establish Windows deployment readiness or release approval.

中文摘要：此修复保留混合批次中的有效行，并报告格式错误的行，避免有效数据被丢弃。7 项单元测试已通过；Windows 部署探测尚未执行，发布尚未获批。
