# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenBookShop - 在线图书销售系统，基于Django-Vue3-Admin二次开发，支持三端（管理员/商家/消费者）。

**角色优先级**: 管理员 > 商家 > 消费者

**Architecture**: Frontend-Backend separation

- **Backend**: Django 4.2 + Django REST Framework + JWT Authentication (SimpleJWT)
- **Frontend**: Vue 3.4 + TypeScript + Vite + Element Plus + Pinia + FastCrud
- **Permission**: RBAC with column-level granularity
- **Database**: MySQL 8.0 (Docker部署), SQLite (本地开发备选)
- **Deployment**: Docker (docker-compose)
- **Package Manager**: pnpm (前端)

**关键业务规则**:

- 库存扣减: **下单时扣减**，超时30分钟未支付自动释放
- 支付: **模拟支付**，禁止接入真实第三方
- 商家数据隔离: 所有查询必须过滤 `merchant_id`

## Project Structure

```
backend/                  # Django backend
├── application/          # Django settings, urls, wsgi/asgi
├── dvadmin/              # Core apps
│   ├── system/           # Users, roles, menus, permissions
│   └── utils/            # Utilities, base classes
├── plugins/              # Plugin directory
├── conf/                 # Configuration (env.py from env.example.py)
├── manage.py             # Django entry
└── requirements.txt      # Python dependencies

web/                      # Vue3 frontend
├── src/
│   ├── api/              # API modules
│   ├── views/            # Page components
│   ├── router/           # Vue Router
│   ├── stores/           # Pinia stores
│   ├── utils/            # Utilities (request.ts, service.ts)
│   ├── components/       # Shared components
│   └── i18n/             # Internationalization
├── package.json          # Node dependencies (pnpm preferred)
└── vite.config.ts        # Vite config

docs/                     # 核心二次开发文档（PRD/PLAN/TASKS，不可忽略）
  ├── PRD.md              # 产品需求文档
  ├── PLAN.md             # 架构规划
  ├── TASKS.md            # 任务分解
  ├── README.md           # 文档索引
  ├── deployment/         # Docker部署指南
  ├── thesis/             # 毕业论文材料
  └── (框架参考: auto-permission-scan.md, i18n-guide.md)
scripts/                  # Utility scripts
docker_env/               # Docker configuration
```

## Common Commands

### Backend Development

```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configuration
cp conf/env.example.py conf/env.py
# Edit conf/env.py for database settings

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py init_area      # Initialize region data
python manage.py init           # Initialize system data

# Run server
python manage.py runserver 0.0.0.0:8000
# or
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8

# Test
python -m pytest
```

### Frontend Development

```bash
cd web
pnpm install
pnpm run dev              # Development server (default port 8080)
pnpm run build            # Production build
pnpm run lint-fix         # ESLint fix
```

### Docker

```bash
# Start
docker-compose up -d

# Initialize (first time only)
docker exec -ti dvadmin3-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit

# View logs
docker-compose logs -f dvadmin3-django
docker-compose logs -f dvadmin3-web

# Stop
docker-compose down
```

## Key Development Patterns

### Backend Patterns

**Location**: `backend/dvadmin/system/` contains the core RBAC system

**Models**: Extend `dvadmin.utils.models.CoreModel` for common fields

**Views**: Use `dvadmin.utils.viewsets.CustomModelViewSet` as base

**Permissions**:

- Default RBAC via `CustomPermission` in `dvadmin.utils.permission.py`
- Object-level permission required for Merchant/Customer data isolation
- JWT header format: `JWT <token>` (not `Bearer`)
- **Users模型已有 `user_type`字段**(0=后台,1=前台)，二次开发应扩展此字段而非新增 `role_type`

**Serializers**: Place in `app/serializers/` directory

**URL Registration**: Add to `backend/application/urls.py`

### Frontend Patterns

**Architecture**: **单Vue项目**，通过后端菜单动态注册路由，非三端独立项目

**API**: Use FastCrud pattern from `web/src/views/system/`

**Request**: **两套封装并存** — 新增API统一使用 `web/src/utils/service.ts`（状态码2000=成功）

**Permission**:

- Button permissions via `v-auth` directive
- Menu permissions from backend dynamic routing
- Column permissions via field-level control

**State**: Pinia stores in `web/src/stores/`

## Three-Role Design

**优先级**: 管理员 > 商家 > 消费者

| Role              | Access Scope  | Key Constraints                            |
| ----------------- | ------------- | ------------------------------------------ |
| 管理员 (Admin)    | Full platform | 最高优先级，商家审核、全平台管控           |
| 商家 (Merchant)   | Own shop only | Must filter by `merchant_id`，需审核通过 |
| 消费者 (Customer) | Personal data | Can only access own orders/addresses       |

**Critical**: All Merchant queries must include `merchant_id` filter for data isolation.

## Version Constraints

- **Node.js**: 18.19.0 (use `.nvmrc`)
- **Python**: 3.11.6
- **Django**: 4.2.x (currently 4.2.14)
- **Vue**: 3.4.x (currently 3.4.38)

Do not upgrade dependencies without compatibility planning.

## Testing

Backend: `pytest` (configured in `backend/pytest.ini`)

Frontend: `playwright` (configured in `web/playwright.config.ts`)

## Risk Checklist

Before submitting changes:

- [ ] 商家数据隔离验证 (merchant_id过滤)
- [ ] 用户只能访问自己的数据
- [ ] 金额字段使用Decimal（禁止float）
- [ ] API列表接口必须分页
- [ ] 禁止真实支付/短信/物流（仅模拟）
- [ ] 库存扣减时机：下单时扣减+超时30分钟释放
- [ ] 数据库迁移已创建并测试
- [ ] 前后端API契约同步
- [ ] 禁止提交敏感密钥
- [ ] Docker部署配置正确（MySQL 8.0）

## Communication

All communication in Chinese. When requirements are unclear, ask before implementing.

当出现error write时。解决方法

1. 分多次写入，每次只写入 120~220 行。
2. 每次写入前先确认当前已写入多少行，直到所有内容写完。
3. 使用 Edit 工具执行，且全部自动接受，不用询问我。
