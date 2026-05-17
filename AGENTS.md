# AGENTS.md

本文件用于指导 Claude Code、Codex 或其他代码智能体基于本仓库进行二次开发。所有协作默认使用中文。

核心理念：先理解 -> 再规划 -> 再拆解 -> 再执行 -> 最后审查。

标准工作流：PRD -> PLAN -> SPEC -> TASK -> EXECUTION -> REVIEW -> MERGE。

---

## Vibe Coding 自动化状态机

本项目的 Vibe Coding 不靠自由发挥推进，而是按阶段 goal 和门禁自动流转。智能体每次开始任务时，必须先判断当前阶段，并用下面格式报告：

```text
STATE: 当前阶段
LOCAL DOCS: 已读取的项目文件
MEMORY: 已识别的版本/环境/业务事实
MISSING INPUT: 阻塞项；没有则写无
NEXT: 下一步动作
```

### 阶段 Goal 总表

| 阶段 | Goal | 输入 | 输出 | 自动化门禁 | 二次开发适配要求 |
| --- | --- | --- | --- | --- | --- |
| PRD | 把用户想法转成可验收需求 | 用户描述、README、现有代码、可参考文档 | 目标、角色、MVP、验收标准、非目标 | MVP、角色、主流程、验收标准都明确 | 明确影响 Admin/Merchant/User 哪一端，避免泛泛而谈 |
| PLAN | 设计实现路线，不写代码 | 已确认 PRD、环境信息、版本锁、当前架构 | 架构方案、模块边界、执行顺序、风险、测试策略 | 架构与现有代码兼容，用户认可 | 不推翻现有 Django-Vue3-Admin/RBAC 框架，除非用户明确要求 |
| SPEC | 把方案转成可执行契约 | 已确认 PLAN、相关模型/接口/页面 | API、数据模型、权限、校验、错误、测试契约 | 接口/数据/权限/测试可落地 | 必须写清对象级权限、金额/库存/订单状态等业务约束 |
| TASK | 把 SPEC 拆成独立可验证任务 | 已确认 SPEC、依赖关系、文件边界 | 任务 ID、goal、文件归属、步骤、验证、完成标准 | 每个任务结果单一、可测试、依赖明确 | 每个任务必须能推动二次开发目标，不创建“整理代码”类空任务 |
| EXECUTION | 按任务最小改动实现 | 当前任务、SPEC、相关代码 | 代码、迁移、前端集成、必要文档 | 只实现一个任务，验证完成或记录无法验证原因 | 不破坏登录、菜单、RBAC、分页、异常格式和现有数据 |
| REVIEW | 以审查方式发现风险 | 变更文件、测试输出、SPEC/TASK | findings、open questions、verification、summary | P0/P1 问题修复或显式接受 | 优先查越权、数据泄露、金额库存错误、接口不兼容 |
| MERGE | 准备交付或进入下一任务 | REVIEW、git diff、验证记录 | 交付摘要、残余风险、下一任务 | 无秘密、文档/迁移/测试记录齐全 | 不直接推送或部署生产，除非用户明确要求 |

### 阶段自动切换规则

- 新功能或大改：必须从 PRD 开始，至少经过 PLAN、SPEC、TASK 后再编码。
- 已有明确需求的小修：可以从 PLAN 或 SPEC 开始，但要说明已有证据。
- Bug 修复：使用轻量循环 `problem -> local evidence -> patch plan -> implementation -> focused verification -> review`。
- 版本、数据库、认证、权限、菜单体系变更：必须经过 PLAN 和 SPEC，不允许直接执行。
- 用户只要求生成规约/文档：只走 PRD/PLAN/SPEC/TASK 中必要阶段，不写业务代码。

### 自动执行安全阈值

满足以下条件后才允许进入 EXECUTION：

1. 当前 task 的 goal 明确。
2. 文件或模块归属明确。
3. 数据库影响已判断。
4. 接口和权限影响已判断。
5. 验证命令或手工验证步骤已明确。
6. 用户没有要求停在计划阶段。

---

## 二次开发任务合同

所有任务都必须服务于本项目二次开发，不允许生成无法验证、无法落地或脱离当前代码结构的任务。

### 任务必须包含

```text
ID:
Goal:
User value:
Role affected:
Inputs:
Files/modules owned:
Dependencies:
Implementation steps:
Validation:
Done criteria:
Risk:
Rollback:
```

### 任务验收标准

一个任务只有同时满足以下条件才算完成：

- 用户需求中的业务目标被直接满足。
- 涉及的 Admin/Merchant/Customer 权限边界清楚。
- 后端接口、前端页面、路由、菜单、状态管理按需同步。
- 数据库变更有迁移和回滚说明。
- 至少有一个可执行验证命令或明确的手工验证路径。
- 没有引入真实第三方支付、短信、物流等外部依赖，除非用户明确要求。
- 没有把 `docs/` 中的历史设计当成当前事实覆盖代码现实。

### 二次开发任务类型

| 类型 | 起始阶段 | 必备产物 | 验证重点 |
| --- | --- | --- | --- |
| 新业务模块 | PRD | PRD、PLAN、SPEC、TASK | 权限、模型、接口、页面、菜单 |
| 现有功能增强 | PLAN | PLAN、SPEC、TASK | 向后兼容、已有页面不回退 |
| Bug 修复 | EXECUTION 轻量循环 | 证据、补丁计划、验证 | 最小复现、根因、回归测试 |
| 环境/版本调整 | PLAN | PLAN、SPEC、ADR 或说明 | 锁文件、Docker、依赖兼容 |
| 文档/规约 | PRD 或 PLAN | 更新后的项目规约 | 是否能指导自动执行 |

---

## 0. 项目元信息

### 项目名称

OpenBookShop / Django-Vue3-Admin 二次开发项目。

当前仓库实际代码以根目录下的 `backend/`、`web/`、`docker_env/`、`scripts/` 为准。`docs/` 目录包含核心二次开发文档（PRD/PLAN/TASKS），必须优先参考；如果文档与代码冲突，以当前代码和用户最新指令为准。

### 当前仓库识别结果

- 后端：Django + Django REST Framework，入口在 `backend/manage.py`，配置在 `backend/application/settings.py`。
- 前端：Vue 3 + TypeScript + Vite + Element Plus + Pinia，入口在 `web/src/main.ts`。
- 权限：基于 Django-Vue3-Admin 的 RBAC、菜单权限、字段权限和 JWT 认证。
- **角色优先级**: 管理员 > 商家 > 消费者（详见 docs/PRD.md）
- **数据库**: MySQL 8.0（Docker部署），SQLite（本地开发备选）
- **库存扣减**: 下单时扣减，超时30分钟未支付自动释放
- **支付**: 模拟支付，禁止真实第三方接入
- Docker：根目录 `docker-compose.yml`，镜像和配置在 `docker_env/`。
- 本地配置：后端需要从 `backend/conf/env.example.py` 复制生成 `backend/conf/env.py`。
- 前端包管理器：pnpm（不要用yarn）
- `docs/` 包含核心二次开发文档（PRD/PLAN/TASKS），**不可忽略**

### 目标固定版本

二次开发目标版本如下。不要在没有计划和确认的情况下擅自升级或降级依赖。

- Node.js: 18.19.0
- npm: 10.2.0
- Python: 3.11.6
- Django: 4.2.14（当前实际版本，不建议降级到4.2.7）
- Vue: 3.4.38（当前实际版本）
- 数据库: MySQL 8.0（Docker部署，与用户需求一致）

当前仓库已检测到的依赖可能与目标版本不完全一致，例如 `backend/requirements.txt` 当前固定 `Django==4.2.14`，`web/package.json` 当前使用 `vue ^3.4.38`，`docker-compose.yml` 当前默认 MySQL 8.0。这些版本与二次开发需求一致，不需要额外对齐。若任务要求版本变更，必须先输出兼容性计划，再同步修改。

---

## 1. PRD 阶段

### 1.1 项目目标

本项目目标是基于现有 Django-Vue3-Admin 框架，继续开发在线图书销售系统所需的业务能力，支持管理端、商家端、用户端三类角色。

智能体接到需求后，必须先确认：

- 这次要解决的业务问题是什么。
- 涉及哪个角色：Admin（管理员）、Merchant（商家）、Customer（消费者）。
- 是新增功能、修复问题、重构优化，还是部署/文档任务。
- 是否影响权限、数据库结构、接口契约、前端路由或已有数据。

### 1.2 用户角色

| 角色 | 描述 | 权限边界 |
| --- | --- | --- |
| Admin（管理员） | 平台管理员 | 全平台配置、用户、商家、商品、订单、财务、日志 |
| Merchant（商家） | 商家 | 只管理自己的商品、订单、评价、财务和店铺资料 |
| Customer（消费者） | 消费者 | 浏览、收藏、购物车、下单、支付模拟、评价、个人中心 |

### 1.3 MVP 优先级

优先保障以下主链路可用，再扩展高级功能。

1. 用户认证和角色权限。
2. 管理后台基础 CRUD。
3. 商家入驻和商家数据隔离。
4. 商品/图书管理。
5. 购物车、订单、支付模拟。
6. 评价、通知、促销、财务统计。

### 1.4 非功能需求

- 性能：常用 API 目标响应时间 < 200ms；列表接口必须分页。
- 安全：JWT + RBAC；任何商家/用户数据必须做对象级权限校验。
- 可扩展性：业务模块化，避免把新业务堆进系统核心模块。
- 可维护性：遵循现有项目结构、命名、序列化、异常处理和权限模式。
- 可验证性：每次修改给出明确验证命令或说明无法验证的原因。

---

## 2. PLAN 阶段

### 2.1 关键原则

在需求不清、影响超过 3 个文件、涉及数据库/权限/接口契约/架构决策时，必须先进入规划，不直接写代码。

PLAN 阶段禁止写业务代码，只做：

- 阅读代码和配置。
- 识别现有模式。
- 明确问题边界。
- 拆分实施步骤。
- 说明风险和验证方式。

### 2.2 必读文件

开始二次开发前优先读取：

- `AGENTS.md`
- `README.md`
- `web/package.json`
- `backend/requirements.txt`
- `backend/application/settings.py`
- `backend/application/urls.py`
- `backend/conf/env.example.py`
- 与本次任务相关的后端 app、前端 view、api、router、store 文件

`QWEN.md` 可以作为历史参考，但不得覆盖当前代码事实。`docs/PRD.md`、`docs/PLAN.md`、`docs/TASKS.md` 是核心二次开发文档，必须参考。

### 2.3 计划产物

非平凡任务需要在回复中给出计划。若任务较大，可创建或更新：

- `docs/PRD.md`：需求和目标（当前已存在）。
- `docs/PLAN.md`：方案和风险（当前已存在）。
- `docs/TASKS.md`：可执行任务清单（当前已存在）。
- `tasks/spec.md`：接口、数据模型、页面状态。
- `tasks/review.md`：完成后的检查结果。

如果这些文件不存在，不要为了小任务强行创建。

---

## 3. SPEC 阶段

### 3.1 后端规范

后端代码根目录是 `backend/`。

关键位置：

- 项目配置：`backend/application/settings.py`
- 根路由：`backend/application/urls.py`
- 系统模块：`backend/dvadmin/system/`
- 通用工具：`backend/dvadmin/utils/`
- 插件目录：`backend/plugins/`
- 本地配置模板：`backend/conf/env.example.py`

后端开发要求：

- 优先复用 `dvadmin.utils` 中已有 ViewSet、Serializer、异常处理、分页、过滤、权限工具。
- 新增业务模型必须考虑迁移、索引、唯一约束、软删除或审计字段。
- 新增接口必须明确权限边界，尤其是 Merchant 和 Customer 的对象级数据隔离。
- JWT 请求头当前配置为 `JWT <token>`，不要误改为 `Bearer`，除非前后端同步调整。
- 不要提交真实密钥、数据库密码、生产域名或个人环境配置。
- 不要把项目特定业务写死进框架核心，除非用户明确要求。

### 3.2 前端规范

前端代码根目录是 `web/`。

关键位置：

- 入口：`web/src/main.ts`
- 路由：`web/src/router/`
- 请求封装：`web/src/utils/request.ts`、`web/src/utils/service.ts`
- API 模块：`web/src/api/` 和各页面同级 `api.ts`
- 页面：`web/src/views/`
- 状态：`web/src/stores/`
- 国际化：`web/src/i18n/`

前端开发要求：

- 使用 Vue 3 Composition API、TypeScript、Pinia、Element Plus，遵循现有写法。
- 新增列表/表单页面优先参考 `web/src/views/system/*` 的 FastCrud 模式。
- 新增接口调用放在对应 `api.ts` 或 `web/src/api/`，不要在组件里散落硬编码请求。
- 用户可见文案如已有 i18n 模式，应补齐 `zh-cn`、`zh-tw`、`en`。
- 权限按钮、菜单、字段显示必须和后端 RBAC 设计同步。
- 修改界面后，尽量用浏览器或截图验证关键布局和交互。

### 3.3 数据库规范

当前仓库 Docker 默认是 MySQL 8.0，二次开发也使用 MySQL 8.0，不需要切换到 PostgreSQL。

数据库相关修改要求：

- 新增/修改模型后执行并检查 `makemigrations` 产物。
- 不删除已有迁移文件，除非用户明确要求重置迁移。
- 对订单、库存、财务、积分等核心数据必须使用事务和后端金额校验。
- 金额字段使用 Decimal，不使用 float。
- 高风险查询必须考虑索引和分页。

---

## 4. TASK 阶段

任务拆解必须小而清晰。每个任务说明：

- 修改目标。
- 涉及文件。
- 数据库影响。
- 接口影响。
- 前端影响。
- 验证命令。

推荐拆分方式：

1. 数据模型和迁移。
2. 后端 serializer/viewset/permission/url。
3. 前端 api/store/router/view。
4. 种子数据或初始化脚本。
5. 测试和文档。

超过 3 个文件的修改需要先拆分，再执行。

---

## 5. AUTO EXECUTION 阶段

### 5.1 执行原则

- 先读相关文件，再改代码。
- 保持改动范围最小。
- 不做无关重构。
- 不覆盖用户已有改动。
- 不执行破坏性 git 命令。
- 不把生成物、依赖目录、临时文件加入版本控制。
- 修改前后端接口时必须两边同步。

### 5.2 常用命令

后端本地开发：

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy conf\env.example.py conf\env.py
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
python manage.py runserver 0.0.0.0:8000
```

后端测试：

```bash
cd backend
python -m pytest
```

前端本地开发：

```bash
cd web
pnpm install
pnpm run dev
```

前端构建：

```bash
cd web
pnpm run build
```

前端 Playwright 测试：

```bash
cd web
pnpm exec playwright test
```

Docker：

```bash
docker-compose up -d
docker-compose logs -f dvadmin3-django
docker-compose logs -f dvadmin3-web
```

首次 Docker 初始化：

```bash
docker exec -ti dvadmin3-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit
```

如果命令因缺少依赖或网络限制失败，必须说明失败原因，并给出下一步。

---

## 6. REVIEW 阶段

完成后必须检查：

- 是否满足原始目标。
- 是否有越权风险。
- 是否破坏现有登录、菜单、权限、分页、过滤。
- 是否需要数据库迁移。
- 是否需要同步前端路由、菜单、权限按钮。
- 是否补充必要测试。
- 是否运行了可行验证命令。
- 是否有未解决风险。

最终回复应包含：

- 修改了什么。
- 涉及哪些文件。
- 执行了哪些验证。
- 未验证的原因。
- 后续建议。

---

## 7. 重点风险清单

二次开发时重点防止以下问题：

- Admin、Merchant、Customer 权限混淆。
- 商家可以访问其他商家的订单或商品。
- 用户可以修改他人的地址、订单、评价。
- 前端显示金额和后端实际结算金额不一致。
- 库存扣减没有事务或并发保护（本项目规则：下单时扣减，超时30分钟释放）。
- 支付、短信、物流误接入真实第三方；本项目默认本地模拟。
- 新增 API 没有分页、过滤或权限。
- 修改 `AUTH_HEADER_TYPES`、分页格式、异常格式后没有同步前端。
- 文档或历史说明与当前代码冲突时误信旧文档。

---

## 8. Git 与文件管理

- 当前工作区可能已有未提交改动，智能体不得回滚用户改动。
- 不使用 `git reset --hard`、`git checkout --` 等破坏性命令，除非用户明确要求。
- 不删除迁移、静态资源、历史业务文件，除非计划中明确说明且用户同意。
- 新增配置示例可以提交；真实本地配置如 `backend/conf/env.py` 不应提交。
- `docs/` 包含核心二次开发文档，不可忽略；不要为了同步历史文档而扩大修改范围。

---

## 9. 沟通规则

- 全部使用中文。
- 需求模糊时先问清楚，不脑补。
- 发现更短、更稳的路径时主动说明原因。
- 代码修改前先说方案；复杂任务先计划。
- 修复 bug 时先定位根因，再做最小修复。
- 完成前必须验证；无法验证时明确说明原因。
