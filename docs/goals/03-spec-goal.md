# 03 SPEC Goal

目标：把 PLAN 转成单模块可执行契约。每次只为一个模块写 SPEC，不一次性覆盖全系统。

注意：如果使用 `/goal` 时出现工具调用参数过长、Bash command 无法生成、JSON 参数无效等问题，不要使用本总入口。改用 `docs/goals/03-spec/` 下的微型 goal。

推荐模块顺序：
1. foundation：bookshop app、路由、权限基础、用户角色策略。
2. merchant：商家模型、审核、商家身份绑定。
3. catalog：分类、图书、库存预警。
4. order：购物车、地址、订单、库存扣减、超时释放。
5. payment-review：模拟支付、评价、敏感词、商家回复。
6. frontend：管理端、商家端、用户端页面与菜单。

```text
/goal follow AGENTS.md and create a SPEC for the next OpenBookShop module until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- the module name and scope are explicit
- the SPEC is based on accepted PRD and PLAN
- local code evidence is read before writing contracts
- API contracts are defined:
  - method
  - path
  - auth
  - request
  - response
  - errors
- data models are defined:
  - table name
  - fields
  - types
  - constraints
  - indexes
  - migration and rollback notes
- validation rules are defined for every external input
- authorization rules are defined for every protected action
- object-level rules are included for Merchant and Customer data isolation
- error format follows existing dvadmin.utils.json_response patterns
- environment variables or settings changes are listed, with examples only
- tests are specified:
  - unit
  - API/integration
  - frontend build or E2E if UI is affected
  - manual verification
- output is written to docs/specs/<module-name>.md
- docs/TASKS.md is not changed in this phase unless the user explicitly asks

DO NOT implement code.
DO NOT create migrations.
DO NOT add dependencies.

Stop when SPEC exit criteria are satisfied or after 10 turns.
```

完成条件：
- 后端、前端、数据库、权限、测试契约足够让 TASK 阶段直接拆任务。
