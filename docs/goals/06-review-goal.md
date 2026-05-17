# 06 REVIEW Goal

目标：对已完成任务做代码审查，优先发现会影响二次开发质量的高风险问题。

```text
/goal follow AGENTS.md and review the completed OpenBookShop task until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- changed files are read directly, not only summarized from conversation
- relevant SPEC and task done criteria are read
- test or validation output is read if available
- review findings are ordered by severity:
  - P0 security/data loss/system cannot run
  - P1 broken business flow, permission leak, money/inventory/order bug
  - P2 maintainability, missing test, unclear edge case
- review checks include:
  - auth bypass and data leakage
  - merchant/customer object-level isolation
  - order state transitions
  - inventory transaction and release logic
  - payment simulation boundaries
  - API request/response compatibility
  - frontend route/menu/RBAC compatibility
  - migration and rollback risk
  - missing tests or manual verification
- output format is:
  Findings
  Open Questions
  Verification
  Summary
- write or update docs/reports/review-latest.md with the review result

Do not implement fixes unless explicitly asked or the task goal includes auto-fix.
Do not merge while P0/P1 findings are unresolved.

Stop when REVIEW exit criteria are satisfied or after 10 turns.
```

完成条件：
- P0/P1 问题明确。
- 验证状态明确。
- 是否可进入 MERGE 明确。

