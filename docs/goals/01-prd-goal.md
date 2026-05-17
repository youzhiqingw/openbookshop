# 01 PRD Goal

目标：确认 OpenBookShop 的需求边界，让后续开发不会基于错误假设执行。

适用场景：
- 用户提出新业务、新页面、新角色、新流程。
- `docs/PRD.md` 与当前代码、用户新需求可能不一致。
- 需要重新确认 MVP 和验收标准。

```text
/goal follow AGENTS.md and complete the PRD phase for OpenBookShop until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- local evidence is read from AGENTS.md, README.md, docs/PRD.md, docs/PLAN.md, docs/TASKS.md, backend/application/urls.py, backend/dvadmin/system/models.py, web/src/router/index.ts, and web/src/utils/request.ts
- the current implementation state is explicitly recorded:
  - Django-Vue3-Admin base exists
  - backend/dvadmin/bookshop does not yet exist unless found during inspection
  - web/src/views/bookshop does not yet exist unless found during inspection
- Admin, Merchant, and Customer roles are defined with permission boundaries
- MVP scope is explicitly listed and separated from later scope
- core flows are described:
  - merchant onboarding and audit
  - book/category management
  - cart and order creation
  - simulated payment
  - inventory deduction and 30-minute unpaid release
  - review and merchant reply
- constraints are confirmed:
  - no real payment, SMS, logistics, or email integration
  - merchant data isolation is mandatory
  - Docker + MySQL 8.0 is the deployment baseline
  - pnpm is the frontend package manager
- every P0 feature has Given/When/Then acceptance criteria
- contradictions between docs and code are listed as open questions
- output is a structured PRD update proposal, and update docs/PRD.md only if the requested behavior is clear

DO NOT write business code.
DO NOT create migrations.
DO NOT assume missing business rules.

Stop when PRD exit criteria are satisfied or after 10 turns.
```

完成条件：
- PRD 中的角色、MVP、业务流程、验收标准可测试。
- 未解决问题被列为 `MISSING INPUT`，而不是被脑补。

