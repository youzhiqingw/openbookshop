# 📚 在线图书销售系统

基于 Django + Vue3 的完整电商平台毕业设计，支持管理端、用户端、商家端三端分离。

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+

### 启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](./CLAUDE.md) | 项目核心记忆与指令 |
| [docs/architecture/design.md](./docs/architecture/design.md) | 架构设计 |
| [docs/architecture/api.md](./docs/architecture/api.md) | API 规范 |
| [docs/architecture/database.md](./docs/architecture/database.md) | 数据库设计 |
| [docs/runbooks/deployment.md](./docs/runbooks/deployment.md) | 部署手册 |
| [docs/decisions/](./docs/decisions/) | 架构决策记录 |

## ✨ 功能特性

### 🛡️ 管理端
- 用户管理、图书管理、订单管理
- 库存监控、数据统计、财务管理
- 日志管理

### 👤 用户端
- 图书浏览、购物车、订单系统
- 评价系统、会员中心、物流追踪
- 客服咨询

### 🏪 商家端
- 图书管理、订单处理、数据仪表盘
- 财务结算、促销管理、在线客服

## 🛠️ 技术栈

- **后端**: Django 4.x + DRF + JWT + SQLite/MySQL
- **前端**: Vue 3 + Vite + Element Plus + Pinia
- **架构**: RESTful API + 前后端分离 + B/S 架构

## ⚠️ 重要约束

✅ 商家数据严格隔离
✅ 敏感词自动过滤 (DFA)
✅ 操作日志完整记录
❌ 无真实支付/短信/IP验证
🔄 支付物流均为本地模拟

## 🧪 测试数据

```bash
cd backend
python ../scripts/generate_mock_data.py
```

## 📁 项目结构

```
openbookshop/
├── backend/                    # Django后端
├── frontend/                   # Vue3前端
├── docs/                       # 文档
├── scripts/                    # 脚本工具
└── .claude/                    # 开发工具配置
```

## 🎯 开发阶段

1. **Week 1**: 基础架构、认证体系、权限控制
2. **Week 2-3**: 图书/订单/购物车核心流程、模拟支付
3. **Week 4**: 三端功能完善（管理端/商家端/用户端）
4. **Week 5**: 数据统计(ECharts)、库存预警、敏感词过滤、日志财务
5. **Week 6**: 测试优化、论文撰写