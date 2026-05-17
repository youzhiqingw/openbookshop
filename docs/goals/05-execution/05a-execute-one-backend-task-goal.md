# 05a Execute One Backend Task Goal

使用前把 `<TASK-ID>` 替换为 docs/TASKS.md 中的具体任务 ID。

```text
/goal implement only backend task <TASK-ID> until:

- read AGENTS.md, docs/TASKS.md, and the matching docs/specs file
- read only affected backend files before editing
- change only files owned by <TASK-ID>
- keep API auth as Authorization: JWT <token>
- use dvadmin.utils patterns
- add or update migration only if the task requires it
- run focused validation: python manage.py check
- report modified files and validation result

Do not start another task.
Stop after this task is complete or blocked.
```

