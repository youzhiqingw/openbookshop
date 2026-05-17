# 02 PLAN Goal

目标：把已确认 PRD 转为可实施架构方案，明确 Django-Vue3-Admin 哪些复用、哪些扩展、哪些新建。

```text
/goal follow AGENTS.md and create or update the technical PLAN for OpenBookShop until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- accepted PRD facts are used as the source of truth
- local evidence is read from:
  - AGENTS.md
  - README.md
  - docs/PRD.md
  - docs/PLAN.md
  - docs/TASKS.md
  - backend/application/settings.py
  - backend/application/urls.py
  - backend/dvadmin/system/models.py
  - backend/dvadmin/utils/
  - web/src/router/
  - web/src/views/system/
  - web/src/utils/request.ts
  - web/package.json
  - backend/requirements.txt
  - docker-compose.yml
- architecture is defined without replacing the Django-Vue3-Admin base
- reuse/new/extend decisions are explicit:
  - reuse RBAC, menu, field permission, operation log, file management, JWT
  - extend Users only with a compatible role strategy
  - create backend/dvadmin/bookshop for bookstore business modules
  - create web/src/views/bookshop and web/src/api/bookshop for bookstore UI/API
- backend modules are mapped:
  - merchant
  - category/book
  - cart
  - order/order item/address
  - payment record/mock payment
  - review/sensitive words
  - statistics/stock warning
- frontend structure is planned:
  - admin bookshop pages
  - merchant shop pages
  - customer store pages
  - API modules and Pinia stores
- database changes, migrations, and rollback concerns are identified
- menu/RBAC integration strategy is defined
- API prefix and auth header remain compatible with current code:
  - /api/bookshop/
  - Authorization: JWT <token>
- risks and incompatibilities are listed, especially:
  - role_type vs existing role ManyToMany/current_role
  - merchant object-level permissions
  - inventory transaction and select_for_update
  - Celery timeout order release
  - frontend route/menu registration
- testing strategy covers backend, frontend build, and full flow
- update docs/PLAN.md only after the plan is coherent with current code

DO NOT write business code.
DO NOT create migrations.

Stop when PLAN exit criteria are satisfied or after 10 turns.
```

完成条件：
- 可以回答“先做哪个模块、为什么、会改哪些边界”。
- 每个主要风险都有缓解策略。

