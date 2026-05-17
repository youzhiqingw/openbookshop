# OpenBookShop - 在线图书销售系统

基于 [Django-Vue3-Admin](https://gitee.com/huge-dream/django-vue3-admin) 二次开发的三端在线图书销售平台。

## 项目简介

OpenBookShop 是一个基于 Django + Vue3 的在线图书销售系统，采用前后端分离的 B/S 架构，支持管理端、商家端、消费者端三端功能。

**角色优先级**: 管理员 > 商家 > 消费者

### 三端功能

| 端 | 角色 | 核心功能 |
|---|------|---------|
| 管理端 | 管理员 | 商家审核、全平台管控、数据统计、库存预警 |
| 商家端 | 商家 | 商品管理、订单处理、数据统计（数据隔离） |
| 消费者端 | 消费者 | 浏览购买、购物车、下单支付（模拟）、评价 |

### 关键业务规则

- **库存扣减**: 下单时扣减，超时30分钟自动释放
- **支付方式**: 模拟支付，禁止真实第三方接入
- **数据隔离**: 商家只能访问自己的数据

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端 | Django + DRF | 4.2.x |
| 认证 | SimpleJWT | 5.4.x |
| 前端 | Vue 3 + TypeScript + Vite | 3.4.x |
| UI | Element Plus + FastCrud | 2.8.x |
| 状态 | Pinia | 2.x |
| 数据库 | MySQL | 8.0 |
| 部署 | Docker + docker-compose | - |

## 环境要求

- Python >= 3.11.0
- Node.js >= 18.0
- MySQL >= 8.0
- pnpm (前端包管理器)

## 快速开始

### 后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy conf\env.example.py conf\env.py  # 编辑env.py配置MySQL
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
python manage.py runserver 0.0.0.0:8000
```

### 前端

```bash
cd web
pnpm install
pnpm run dev    # 开发服务器 http://localhost:8080
pnpm run build  # 生产构建
```

### Docker部署

```bash
docker-compose up -d
# 首次初始化
docker exec -ti dvadmin3-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit
```

**禁止**: `docker-compose down -v`（会删除所有数据）
**正确**: `docker-compose down`（只停止容器，保留数据）

## 默认账号

- 管理员: `superadmin` / `admin123456`

## 核心文档

| 文档 | 位置 | 说明 |
|------|------|------|
| PRD | [docs/PRD.md](docs/PRD.md) | 产品需求、UI设计、功能模块 |
| PLAN | [docs/PLAN.md](docs/PLAN.md) | 架构规划、数据模型、API设计 |
| TASKS | [docs/TASKS.md](docs/TASKS.md) | 25个可执行任务、6周开发路线 |
| 指南 | [AGENTS.md](AGENTS.md) | 二次开发工作流和规范 |
| 配置 | [CLAUDE.md](CLAUDE.md) | Claude Code操作指南 |

## 上游框架

本项目基于 [Django-Vue3-Admin](https://gitee.com/huge-dream/django-vue3-admin) 开源框架二次开发。

- 上游文档: [https://www.django-vue-admin.com](https://www.django-vue-admin.com)
- 上游Demo: [https://demo.dvadmin.com](https://demo.dvadmin.com)
- 插件市场: [https://bbs.django-vue-admin.com/plugMarket.html](https://bbs.django-vue-admin.com/plugMarket.html)