# 05 EXECUTION Goal

目标：一次只执行一个已确认任务，做到最小改动、可验证、可继续。

注意：如果自动执行时出现工具调用失败，不要继续扩大上下文。改用 `docs/goals/05-execution/` 下的微型 goal，并明确任务 ID 与文件范围。

```text
/goal follow AGENTS.md and implement OpenBookShop tasks one by one until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- before editing, read:
  - the current task in docs/TASKS.md
  - the matching SPEC in docs/specs/
  - affected backend/frontend files
  - AGENTS.md execution rules
- only one task is implemented at a time
- changes follow current project conventions:
  - backend uses dvadmin.utils viewset/serializer/json_response patterns
  - API auth remains Authorization: JWT <token>
  - API paths remain under /api/bookshop/ unless SPEC says otherwise
  - frontend uses Vue3 + TypeScript + Pinia + Element Plus/FastCrud patterns
  - frontend package manager remains pnpm
- no existing RBAC, menu, field permission, pagination, exception format, login flow, or operation log behavior is broken
- merchant and customer object-level permissions are enforced where relevant
- inventory/order/payment changes use transactions and Decimal-safe calculations
- no real third-party payment, SMS, logistics, or email service is introduced
- relevant validation is run after each task:
  - backend: python manage.py check, python manage.py makemigrations --check when appropriate, python -m pytest when tests exist
  - frontend: pnpm run build or focused route/page check when UI changes
  - Docker: only when deployment files changed
- command failures are reported honestly with next steps
- docs/TASKS.md is updated with completion status only after validation

Do not continue to the next task if current validation fails.
Do not push or deploy.

Stop when the current task is complete and reviewed, or after 20 turns.
```

完成条件：
- 当前任务代码已完成。
- 验证已运行或原因已记录。
- 可以进入 REVIEW。
