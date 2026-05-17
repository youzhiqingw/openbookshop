# QWEN.md - OpenBookShop 项目上下文

## 📚 项目概述

**OpenBookShop** 是一个基于 **Django + Vue3** 的完整在线图书销售系统，采用前后端分离架构，支持**管理端、用户端、商家端**三端独立运营。这是一个毕业设计项目，实现了完整的电商平台功能。

### 核心特性

- **三端分离**: Admin 管理端、Merchant 商家端、Customer 用户端
- **RESTful API**: 基于 Django REST Framework 的标准化接口
- **JWT 认证**: 使用 djangorestframework-simplejwt 进行身份验证
- **数据隔离**: 商家数据严格隔离，仅能管理自己的商品和订单
- **本地模拟**: 支付、物流、短信等功能均为本地模拟实现

---

## 🏗️ 技术架构

### 后端技术栈

| 技术    | 版本  | 说明              |
| ------- | ----- | ----------------- |
| Python  | 3.11+ | 编程语言          |
| Django  | 4.x   | Web 框架          |
| DRF     | 3.14+ | RESTful API       |
| JWT     | 5.x   | 认证 (SimpleJWT)  |
| SQLite  | 3.x   | 开发数据库        |
| MySQL   | 8.x   | 生产数据库 (可选) |
| Pillow  | 10.x  | 图片处理          |
| JAZZMIN | 3.x   | Admin 美化        |

### 前端技术栈

| 技术         | 版本 | 说明        |
| ------------ | ---- | ----------- |
| Vue          | 3.3+ | 前端框架    |
| Vite         | 4.x+ | 构建工具    |
| Element Plus | 2.3+ | UI 组件库   |
| Pinia        | 2.1+ | 状态管理    |
| Vue Router   | 4.x  | 路由管理    |
| ECharts      | 5.x  | 数据可视化  |
| Axios        | 1.4+ | HTTP 客户端 |

---

## 📁 项目结构

```
E:\opencode\openbookshop\
├── openbookshop/                    # 主项目目录
│   ├── backend/                     # Django 后端
│   │   ├── apps/                    # 业务应用模块
│   │   │   ├── users/               # 用户管理 (扩展 AbstractUser)
│   │   │   ├── merchants/           # 商家管理
│   │   │   ├── books/               # 图书管理 (Book, Category)
│   │   │   ├── orders/              # 订单管理 (Order, OrderItem)
│   │   │   ├── cart/                # 购物车
│   │   │   ├── reviews/             # 评价管理
│   │   │   ├── payments/            # 支付模拟
│   │   │   ├── logistics/           # 物流模拟
│   │   │   ├── promotions/          # 促销活动
│   │   │   ├── announcements/       # 公告管理
│   │   │   ├── analytics/           # 数据统计
│   │   │   ├── chat/                # 客服 (WebSocket)
│   │   │   └── finance/             # 财务管理
│   │   ├── config/                  # Django 配置
│   │   │   ├── settings.py          # 主配置 (JAZZMIN, DRF, JWT)
│   │   │   ├── urls.py              # 根路由
│   │   │   └── asgi.py              # WebSocket 支持
│   │   ├── utils/                   # 工具模块
│   │   │   ├── sensitive_words/     # 敏感词过滤 (DFA 算法)
│   │   │   └── mock_services/       # 模拟服务
│   │   ├── media/                   # 用户上传文件
│   │   ├── manage.py                # Django 管理脚本
│   │   └── requirements.txt         # Python 依赖
│   │
│   ├── frontend/                    # Vue3 前端
│   │   ├── src/
│   │   │   ├── api/                 # API 接口封装
│   │   │   ├── views/               # 页面视图
│   │   │   │   ├── auth/            # 认证页面
│   │   │   │   ├── home/            # 首页
│   │   │   │   ├── book/            # 图书浏览
│   │   │   │   ├── cart/            # 购物车
│   │   │   │   ├── order/           # 订单
│   │   │   │   ├── user/            # 用户中心
│   │   │   │   ├── admin/           # 管理端
│   │   │   │   └── merchant/        # 商家端
│   │   │   ├── components/          # 公共组件
│   │   │   ├── router/              # 路由配置
│   │   │   ├── store/               # Pinia 状态管理
│   │   │   └── utils/               # 工具函数
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   ├── docker-compose.yml           # Docker 编排
│   └── docs/                        # 文档资料
│
├── 安装部署说明书-Docker 版.md
├── 安装部署说明书-Windows 版.md
├── 测试使用.md
├── 后端配置.md
├── 项目结构.md
└── README.md
```

---

## 🚀 快速开始

### 方式一：Docker 部署 (推荐)

```bash
cd openbookshop

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务 (保留数据)
docker-compose down
```

**访问地址**:

- 前端：http://127.0.0.1:8080
- 后端 API: http://127.0.0.1:8000
- Django Admin: http://127.0.0.1:8000/admin/

### 方式二：本地开发

#### 后端启动

```bash
cd openbookshop/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

#### 前端启动

```bash
cd openbookshop/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 📋 测试账户

| 用户名            | 密码               | 角色   | 说明             |
| ----------------- | ------------------ | ------ | ---------------- |
| `admin`         | `admin123456`    | 管理员 | 超级权限         |
| `merchant_test` | `merchant123456` | 商家   | 商品管理、订单   |
| `customer_test` | `customer123456` | 用户   | 浏览、购物、订单 |

---

## 🌐 API 端点

### 认证相关

- `POST /api/users/login/` - 用户登录 (返回 JWT Token)
- `POST /api/users/register/` - 用户注册
- `POST /api/users/token/refresh/` - 刷新 Token

### 业务接口

- `GET/POST /api/books/` - 图书列表/创建
- `GET/PUT/DELETE /api/books/{id}/` - 图书详情/更新/删除
- `GET/POST /api/orders/` - 订单列表/创建
- `GET/POST /api/cart/` - 购物车操作
- `GET/POST /api/reviews/` - 评价管理

### 管理端接口

- `GET /api/admin/users/` - 用户管理
- `GET /api/admin/merchants/` - 商家管理
- `GET /api/admin/analytics/` - 数据统计

---

## 🔐 权限控制

### 角色定义

- **admin**: 超级管理员，拥有全部权限
- **merchant**: 商家，仅管理自己的商品和订单
- **customer**: 普通用户，可浏览、购物、评价

### 权限类 (permissions.py)

- `IsAdminOrReadOnly`: 管理员可写，其他人只读
- `IsMerchantOrAdmin`: 商家或管理员可访问
- `IsOwnerOrAdmin`: 仅所有者或管理员可操作

---

## 📦 核心模块说明

### 1. 用户模块 (users)

- 扩展 `AbstractUser` 模型
- 支持 `role` 字段区分用户类型
- JWT Token 认证

### 2. 图书模块 (books)

- `Book` 模型：书名、作者、价格、库存、封面等
- `Category` 模型：两级分类体系
- 支持 ISBN 管理、上下架控制

### 3. 订单模块 (orders)

- `Order` 模型：订单主表 (状态、总价、收货地址)
- `OrderItem` 模型：订单明细
- 状态流转：待支付 → 待发货 → 待收货 → 已完成

### 4. 评价模块 (reviews)

- `Review` 模型：评分、评论内容
- 敏感词过滤 (DFA 算法)
- 商家可回复评价

### 5. 敏感词过滤 (utils/sensitive_words)

- DFA (Deterministic Finite Automaton) 算法
- 自动过滤评论、用户名等敏感内容

---

## 🧪 开发注意事项

### 重要约束

✅ 商家数据严格隔离
✅ 敏感词自动过滤 (DFA)
✅ 操作日志完整记录
❌ 无真实支付/短信/IP 验证 (均为本地模拟)

### 数据库操作

```bash
# 迁移数据库
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 初始化测试数据
python init_data_persistent.py
```

### 常用调试命令

```bash
# 查看数据库用户
docker exec openbookshop_backend python manage.py shell -c "
from apps.users.models import User
for user in User.objects.all():
    print(f'{user.username}: {user.role}')
"

# 查看图书数量
docker exec openbookshop_backend python manage.py shell -c "
from apps.books.models import Book
print(f'图书总数：{Book.objects.count()}')
"
```

---

## 📄 相关文档

| 文档                                                         | 说明               |
| ------------------------------------------------------------ | ------------------ |
| [README.md](./README.md)                                        | 项目主文档         |
| [测试使用.md](./测试使用.md)                                    | 测试账户和访问指南 |
| [后端配置.md](./后端配置.md)                                    | 后端配置说明       |
| [项目结构.md](./项目结构.md)                                    | 详细项目结构       |
| [安装部署说明书-Docker 版.md](./安装部署说明书-Docker 版.md) | Docker 部署指南    |
| [ADMIN_DESIGN_GUIDE.md](./ADMIN_DESIGN_GUIDE.md)                | 管理端设计指南     |

---

## 🐛 已知问题与修复

- ✅ 登录问题已修复 (详见 `LOGIN_ISSUE_DIAGNOSIS_AND_FIX.md`)
- ✅ 图片 URL 问题已修复 (详见 `IMAGE_URL_FIX.md`)
- ✅ 启动问题已修复 (详见 `HOTFIX_STARTUP_ISSUES.md`)

---

## 📊 功能实现状态

| 模块         | 状态    | 说明                 |
| ------------ | ------- | -------------------- |
| 用户认证     | ✅ 完成 | JWT Token、role 隔离 |
| 用户端       | ✅ 完成 | 商品浏览、购物、订单 |
| 商家端       | ✅ 完成 | 商品管理、订单、数据 |
| Admin 端     | ✅ 完成 | 仪表板、管理功能     |
| Django Admin | ✅ 完成 | JAZZMIN 美化         |
| 支付模拟     | ✅ 完成 | 本地模拟支付         |
| 物流模拟     | ✅ 完成 | 本地模拟物流         |
| 敏感词过滤   | ✅ 完成 | DFA 算法             |
| 数据统计     | ✅ 完成 | ECharts 可视化       |

---

**最后更新**: 2026 年 3 月 16 日
**项目类型**: 毕业设计 - 在线图书销售系统
**开发语言**: Python 3.11+, JavaScript/TypeScript
**架构模式**: 前后端分离 + RESTful API + B/S 架构




系统管理平台

* 数据统计
* 用户管理
* 风控分析
* 图书管理
* 分类管理
* 标签管理
* 商家审核
* 评论审核
* 财务报表
* 客服中心
* 订单管理
* 公告管理
* 提现管理
* 库存监控
* 操作日志
* 返回商城
