# OpenBookShop 阶段式 /goal 使用说明

本目录把 Vibe Coding 工作流拆成可执行的阶段化 `/goal` 文件。不要用一个 `/goal` 做完整项目，必须按阶段运行：

```text
01 PRD -> 02 PLAN -> 03 SPEC -> 04 TASK -> 05 EXECUTION -> 06 REVIEW -> 07 MERGE
```

## 当前项目事实

- 项目基座：Django-Vue3-Admin。
- 后端现状：已有 `backend/dvadmin/system/`、`backend/dvadmin/utils/`、`backend/dvadmin/test_app/`，尚未发现 `backend/dvadmin/bookshop/`。
- 前端现状：已有 `web/src/views/system/`、`web/src/router/`、`web/src/utils/request.ts`，尚未发现 `web/src/views/bookshop/`。
- 产品蓝图：`docs/PRD.md`、`docs/PLAN.md`、`docs/TASKS.md`。
- 关键约束：管理员 > 商家 > 消费者；商家数据隔离；模拟支付；下单扣库存，30 分钟未支付释放；Docker + MySQL 8.0；前端使用 pnpm。

## 使用方式

1. 打开对应阶段文件。
2. 复制文件中的 `/goal` 代码块到 Claude Code。
3. 等该阶段 exit criteria 满足后，再进入下一阶段。
4. 如果阶段输出发现文档与代码冲突，优先修正 PRD/PLAN/SPEC/TASK，不直接编码。

## 长 goal 工具调用问题处理

从 03 SPEC 开始，不再建议使用“大段总 goal”一次性推进。原因是 Claude 在自动执行时可能把过长上下文塞进工具 `command` 参数，导致工具调用 JSON/Bash 参数生成失败。

解决方式：

- 03 SPEC：按模块运行 `docs/goals/03-spec/` 下的短 goal。
- 04 TASK：只针对一个 SPEC 拆任务。
- 05 EXECUTION：一次只执行一个任务，且任务 ID 必须明确。
- 每个 goal 只引用文件路径，不把长文档内容粘进命令。
- 如果工具调用开始失败，立即停止当前 goal，改用更小的单文件/单函数任务。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `01-prd-goal.md` | 明确需求、角色、MVP、验收标准 |
| `02-plan-goal.md` | 对齐架构、复用策略、模块边界、风险 |
| `03-spec-goal.md` | 为单个模块生成接口/模型/权限/测试契约 |
| `04-task-goal.md` | 把 SPEC 拆成可执行任务 |
| `05-execution-goal.md` | 按任务逐个实现并验证 |
| `06-review-goal.md` | 审查安全、正确性、数据完整性和测试 |
| `07-merge-goal.md` | 准备交付、PR 或下一任务 |

## 推荐微型 goal 入口

| 目录 | 用途 |
| --- | --- |
| `03-spec/` | 按 foundation、merchant、catalog、order、payment-review、frontend 拆 SPEC |
| `04-task/` | 按单个 SPEC 生成任务，或只选择下一个任务 |
| `05-execution/` | 按一个后端任务、一个前端任务或一次验证拆执行 |
