# 文档与代码一致性审查报告

**审查日期**: 2026-05-16

## 审查目标

验证 docs/PRD.md、docs/PLAN.md、docs/TASKS.md 中描述的项目结构、API设计和部署方案是否与实际代码对应，是否可行。

---

## 一、严重问题（文档与实际代码不一致）

### 1.1 Docker部署文档完全失效

**文件**: `docs/deployment/安装部署说明书-Docker版.md`

| 文档描述 | 实际情况 | 严重程度 |
|---------|---------|---------|
| `frontend/Dockerfile`, `backend/Dockerfile` | `docker_env/web/Dockerfile`, `docker_env/django/Dockerfile` | 🔴 高 |
| `.env.example` 在根目录 | 根目录无 .env.example，密码通过 `init.sh` 生成 | 🔴 高 |
| 服务名 `openbookshop_backend/frontend/db` | `dvadmin3-django/web/mysql` | 🔴 高 |
| 前端端口 80 | 实际监听 8080 | 🟡 中 |
| 数据库名 `bookstore` | 实际库名 `django-vue3-admin` | 🔴 高 |
| 数据库配置方式: settings.py环境变量 | 实际: `conf/env.py`硬编码 | 🔴 高 |

**结论**: 此文档来自旧项目，描述的架构与当前Django-Vue3-Admin框架完全不匹配，**不可用**。

### 1.2 Dockerfile IP地址错误

**文件**: `docker_env/django/Dockerfile`

Dockerfile中 `sed` 命令将 DATABASE_HOST 和 REDIS_HOST 改为 `177.10.0.1`（子网地址），而非正确的容器IP：
- MySQL容器IP: `177.10.0.13`
- Redis容器IP: `177.10.0.15`

而 `init.sh` 中正确使用了 `177.10.0.13` 和 `177.10.0.15`。

**结论**: 直接使用Dockerfile构建镜像时，后端无法连接数据库和Redis。只有通过 `init.sh` 启动才能正常工作。

### 1.3 密码不一致

| 位置 | MySQL密码 | Redis密码 |
|------|----------|----------|
| `env.example.py` | DVADMIN3（硬编码） | DVADMIN3（硬编码） |
| `init.sh` | 随机生成 | 随机生成 |
| `docker-compose.yml` | `.env`文件注入 | `.env`文件注入 |
| `Dockerfile` | 保留DVADMIN3 | 保留DVADMIN3 |

**结论**: Dockerfile构建路径密码与docker-compose.yml注入的随机密码不匹配，数据库连接会失败。

### 1.4 环境变量注入无效

`docker-compose.yml` 通过环境变量 `DATABASE_HOST: dvadmin3-mysql` 注入配置，但Django的 `settings.py` 从 `conf/env.py` 文件读取配置，**不读取环境变量**。注入的环境变量实际无效。

---

## 二、中等问题（版本和配置不一致）

### 2.1 Python版本不一致

| 来源 | 版本 |
|------|------|
| README.md | >= 3.11.0 |
| `docker_env/django/DockerfileBuild` | python:3.10-alpine |

### 2.2 Node版本不一致

| 来源 | 版本 |
|------|------|
| README.md | >= 18.0 |
| package.json engines | >= 16.0.0 |
| `docker_env/web/DockerfileBuild` | node:16.19-alpine |
| `docker_env/web/Dockerfile` | dvadmin3-base-web:18.20-alpine |

### 2.3 包管理器不一致

| 来源 | 包管理器 |
|------|---------|
| CLAUDE.md / AGENTS.md | pnpm |
| Dockerfile / DockerfileBuild | yarn |
| README.md（旧版） | yarn |

### 2.4 数据库名不合理

`env.example.py` 中数据库名为 `django-vue3-admin`（上游框架名），二次开发应改为 `openbookshop` 或 `bookshop`。

### 2.5 psycopg2冗余

`requirements.txt` 包含 `psycopg2==2.9.9`（PostgreSQL驱动），项目使用MySQL，此包无实际用途。

---

## 三、PLAN.md设计是否可行

### 3.1 后端模块设计 ✅ 可行

PLAN.md中设计的 `backend/dvadmin/bookshop/` 模块结构：
- 可以正确注册到 `INSTALLED_APPS`
- 可以复用 `dvadmin.utils` 中的 `CoreModel`, `CustomModelViewSet`
- 可以在 `application/urls.py` 中注册路由
- 表名前缀 `dvadmin_` 与现有系统一致

**但需注意**:
- `Users` 模型已有 `user_type` 字段（0=后台用户, 1=前台用户），与PLAN.md的 `role_type` 字段功能重叠。建议**复用现有 `user_type` 并扩展选项**，而非新增字段。
- `Users` 模型已有 `role` ManyToManyField（关联Role表），RBAC角色机制已存在。`role_type` 字段应作为简化角色标识，与现有Role体系共存。

### 3.2 前端路由设计 ⚠️ 需调整

PLAN.md描述前端为三端分离（admin/merchant/customer），但实际框架是**单前端应用**，通过后端返回的菜单动态注册路由。这意味着：
- 不需要三个独立的Vue项目
- 商家端和消费者端应通过**不同的菜单集**在同一前端中实现
- 消费者端可能需要独立布局（不同于管理端布局），但仍在同一Vue项目内

### 3.3 前端双请求封装 ⚠️ 需统一

存在两套axios封装并行使用：
- `service.ts`: 状态码2000=成功, 400=参数错误, 4000=业务错误
- `request.ts`: 状态码0=成功, 401/4001=认证失败

新增bookshop API时必须**选择一套封装**并统一使用，避免状态码混乱。

### 3.4 API设计 ✅ 大体可行

PLAN.md的API路由设计（如 `/api/bookshop/books/`）可以注册到 `application/urls.py`，但需注意：
- 现有系统路由前缀是 `/api/system/`
- bookshop路由应使用 `/api/bookshop/` 前缀
- ViewSet必须继承 `CustomModelViewSet` 以复用权限/过滤/分页

---

## 四、TASKS.md任务是否可执行

### 4.1 任务1.2: 扩展Users模型 ⚠️ 需调整

**计划**: 添加 `role_type` 和 `merchant` 字段

**实际问题**:
- `Users` 模型已有 `user_type`（0=后台, 1=前台），功能与 `role_type` 重叠
- `Users` 已有 `role` ManyToManyField，RBAC角色已存在
- 建议改为: 扩展 `user_type` 选项（0=管理员, 1=商家, 2=消费者），新增 `merchant` FK

### 4.2 任务1.6: 配置Docker MySQL ⚠️ 需细化

**计划**: 确保 docker-compose.yml 正确配置MySQL

**实际问题**:
- Dockerfile IP地址错误（177.10.0.1）
- 密码不一致（DVADMIN3 vs 随机密码）
- 环境变量注入对Django无效
- 数据库名应为 `bookshop` 而非 `django-vue3-admin`

**需要额外工作**:
- 修复 `docker_env/django/Dockerfile` 的IP地址
- 统一密码配置方式
- 更改数据库名

### 4.3 任务4.5: 订单超时释放库存 ⚠️ 需Celery

**计划**: Celery定时任务扫描超时订单

**实际问题**:
- 项目已安装 `dvadmin3-celery` 插件，docker-compose.yml中有celery容器
- 但 `backend/plugins/` 目录为空，celery作为外部包运行
- 需确认celery定时任务（celery-beat）的配置方式

---

## 五、产品闭环审查

### 5.1 核心业务流程闭环

| 流程 | 起点 | 终点 | 闭环？ |
|------|------|------|--------|
| 商家入驻 | 商家提交资质 → 管理员审核 → 商家开通 | 商家可管理商品 | ✅ 闭环 |
| 用户购买 | 浏览→加购→下单→扣减库存→模拟支付→商家发货→物流→收货→评价 | 用户完成评价 | ✅ 闭环 |
| 库存管理 | 商家设置预警→库存不足触发→管理员/商家响应→补货 | 库存恢复 | ⚠️ 补货流程未定义 |
| 退款 | 用户申请退款→商家审核→退款→库存释放 | 订单关闭 | ⚠️ 退款流程未定义 |

### 5.2 缺失的产品闭环

1. **补货流程**: 库存预警后如何补货？TASKS.md没有补货任务
2. **退款流程**: PRD.md提到"支持退款"，但TASKS.md没有退款相关任务
3. **商家结算**: 论文中提到支付结算、提现申请，但TASKS.md没有结算任务
4. **消费者收藏/消息通知**: PRD.md提到但TASKS.md未涉及

### 5.3 数据隔离验证闭环

PLAN.md设计了 `MerchantPermission` 和 `OwnerPermission`，但TASKS.md只有任务3.3/3.4涉及数据隔离。需要**在每个涉及商家/用户数据的任务中明确验证数据隔离**。

---

## 六、修复建议

### 🔴 必须修复（阻塞二次开发）

1. **废弃旧Docker部署文档**: ✅ 已完成（移至垃圾箱）
2. **修复docker_env/django/Dockerfile**: ✅ 已完成（IP改为Docker服务名 dvadmin3-mysql/dvadmin3-redis）
3. **统一密码配置**: ✅ 在TASKS T0.1中覆盖（确认docker-compose密码与env.py一致）
4. **更改数据库名**: ✅ 已完成（env.example.py中DATABASE_NAME改为bookshop）

### 🟡 建议修复（影响开发效率）

5. **统一Users模型设计**: ✅ 已完成（PLAN.md/SPEC.md/TASKS.md均已改为扩展user_type，T1.1任务覆盖）
6. **统一前端请求封装**: ✅ 已完成（SPEC.md Error Format章节明确service.ts状态码2000体系，所有前端任务注明使用service.ts）
7. **前端单项目多布局**: ✅ 已完成（PLAN.md前端模块改为单Vue项目+MerchantLayout/CustomerLayout，T3.1/T4.1任务覆盖）
8. **统一Node版本**: ⏳ 待执行（需对齐Docker镜像和package.json到Node 18）
9. **移除psycopg2**: ✅ 在TASKS T0.1中覆盖（移除冗余PostgreSQL驱动）

### 🟢 可选修复（长期优化）

10. **补货流程**: ✅ 已完成（T6.2商家库存补货任务，SPEC.md API含replenish接口）
11. **退款流程**: ✅ 已完成（T5.5退款流程任务，SPEC.md API含refund_approve/reject/refund接口）
12. **商家结算**: ⏳ 待后续版本（TASKS未含结算任务，不影响MVP）
13. **环境变量支持**: ⏳ 待后续版本（SPEC.md Environment Variables章节注明env.py方案，暂不从环境变量读取）

---

## 七、验证结论（2026-05-16更新）

| 维度 | 状态 | 说明 |
|------|------|------|
| PLAN后端模块设计 | ✅ 可行 | user_type扩展已修正（T1.1） |
| PLAN前端路由设计 | ✅ 已修正 | 单Vue项目多布局（T3.1/T4.1） |
| PLAN API设计 | ✅ 已修正 | 统一service.ts+退款/补货/收藏API已补充 |
| SPEC契约完整性 | ✅ 新建 | API/Data/Auth/Validation/Test/Migration六维度覆盖 |
| TASKS任务可执行性 | ✅ 已重写 | 26个vibe coding格式任务，含审计修正清单 |
| Docker部署可行性 | ✅ 已修复 | Dockerfile IP+数据库名已修正，密码统一在T0.1 |
| 产品闭环完整性 | ✅ 已补全 | 补货(T6.2)/退款(T5.5)/收藏(T6.1)已添加，结算待后续 |
| 旧Docker部署文档 | ❌ 废弃 | 与当前框架不匹配 |