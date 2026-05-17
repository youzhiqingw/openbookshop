# 04 TASK Goal

目标：把已确认 SPEC 拆成小任务，确保每个任务可以自动执行、可验证、可回滚。

注意：如果 SPEC 内容较长，不要直接使用本总入口。改用 `docs/goals/04-task/04a-task-one-spec-goal.md`，一次只处理一个 SPEC 文件。

```text
/goal follow AGENTS.md and break the accepted SPEC into executable tasks until:

- STATE / LOCAL DOCS / MEMORY / MISSING INPUT / NEXT is reported in each turn
- docs/PRD.md, docs/PLAN.md, the target docs/specs/<module-name>.md, and current docs/TASKS.md are read
- each task has:
  - ID
  - Goal
  - User value
  - Role affected
  - Inputs
  - Files/modules owned
  - Dependencies
  - Implementation steps
  - Validation
  - Done criteria
  - Risk
  - Rollback
- each task owns no more than 3 files unless the reason is explicitly justified
- task dependencies are acyclic and match the implementation order
- P0 tasks come before P1/P2 tasks
- backend tasks and frontend tasks are split when they can be validated independently
- database migration tasks include rollback notes
- permission and data isolation tasks include negative test cases
- update docs/TASKS.md with the refined tasks for the target module
- identify the exact next task for EXECUTION

DO NOT write business code.
DO NOT edit implementation files.

Stop when TASK exit criteria are satisfied or after 10 turns.
```

完成条件：
- 下一步可以直接进入 EXECUTION，并且知道要改哪些文件、跑什么验证。
