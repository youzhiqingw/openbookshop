# 05c Verify One Task Goal

使用前把 `<TASK-ID>` 替换为 docs/TASKS.md 中的具体任务 ID。

```text
/goal verify only task <TASK-ID> until:

- read AGENTS.md and docs/TASKS.md
- inspect changed files for <TASK-ID>
- run only the validation commands listed for <TASK-ID>
- if a command fails, capture the exact failure and stop
- update task status only if validation passes
- report verification result and next recommended phase

Do not edit implementation code unless the task explicitly says verify-and-fix.
Stop after verification is complete or blocked.
```

