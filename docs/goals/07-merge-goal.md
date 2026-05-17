# 07 MERGE Goal

目标：把已完成和已审查的任务整理成可交付状态，准备 PR、提交或进入下一任务。

```text
/goal follow AGENTS.md and prepare OpenBookShop merge handoff until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- docs/reports/review-latest.md is read
- git diff and changed file list are inspected
- no secrets, local credentials, .env files, generated keys, or unwanted build artifacts are included
- PRD/PLAN/SPEC/TASK docs are updated if behavior changed
- migrations and rollback notes are present for database changes
- tests or manual verification are recorded
- unresolved findings are either fixed or explicitly listed as accepted risk
- output handoff includes:
  - Completed Phase
  - Changed Files
  - Verification
  - Residual Risk
  - Next Task
- write or update docs/reports/merge-ready-latest.md

Do not push to main.
Do not deploy production.
Do not delete user changes.

Stop when MERGE exit criteria are satisfied or after 10 turns.
```

完成条件：
- 当前任务可交付。
- 下一个任务清楚。
- 工作区风险被记录。

