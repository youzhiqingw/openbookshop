# OpenBookShop 测试指南

> 更新时间: 2026-05-17
> 环境: Docker (dvadmin3-django:8000, dvadmin3-web:8080)

---

## 测试账户

| 角色 | 用户名 | 密码 | user_type | 说明 |
|------|--------|------|-----------|------|
| 管理员 | superadmin | admin123 | 0 | 超级管理员，拥有全部权限 |
| 管理员 | admin | admin123 | 0 | 普通管理员 |
| 管理员 | test | test123 | 0 | 测试管理员 |
| 商家 | merchant1 | merchant123 | 2 | 已绑定商家"TestMerchant_Verify"(approved) |
| 消费者 | customer1 | customer123 | 3 | 测试消费者 |
| 消费者 | testcustomer | customer123 | 3 | 测试消费者 |

**登录API**: `POST http://localhost:8000/api/login/`
```json
{"username": "superadmin", "password": "admin123"}
```

**登录注意**: 连续5次密码错误会锁定账户。如需解锁，在Django shell中执行:
```python
from dvadmin.system.models import Users
Users.objects.filter(username='xxx').update(login_error_count=0, is_active=True)
```

---

## 当前进度 (13/28 任务完成)

### 已完成任务

| 任务 | 说明 | 验证状态 |
|------|------|----------|
| T0.2 | bookshop app骨架 | ✅ manage.py check通过 |
| T1.1 | user_type扩展+merchant FK | ✅ 4种user_type + merchant关联 |
| T1.2 | Merchant模型+管理员审核API | ✅ 审核/禁用/启用 |
| T1.3 | Category+Book模型+API | ✅ 管理端CRUD+用户端只读 |
| T1.4 | URL路由注册三端前缀 | ✅ admin/merchant/customer |
| T1.5 | MerchantPermission+OwnerPermission | ✅ 20测试通过 |
| T1.6 | 管理端前端页面(3个) | ✅ 商家审核/图书管理/分类管理 |
| T2.1 | CartItem+Address+消费者API | ✅ 购物车+地址CRUD |
| T2.2 | Order+OrderItem+管理端订单API | ✅ 8种状态+强制退款 |
| T2.3 | 库存预警后端API | ✅ 三级预警+阈值设置 |
| T2.4 | 统计仪表盘后端API | ✅ 4组统计(总览/趋势/分布/排行) |
| T2.5 | 库存预警前端页面 | ✅ FastCrud列表+阈值弹窗 |
| T2.5a | 统计仪表盘前端页面 | ✅ ECharts 4组图表 |
| T2.6 | 订单监控+支付记录前端 | ✅ 订单详情+强制退款(支付记录待T4.5) |

### 待完成任务

| 任务 | 说明 | Phase |
|------|------|-------|
| T3.1 | 商家端布局+动态菜单+入驻申请 | Phase 3 |
| T3.2 | 商家端图书管理(数据隔离) | Phase 3 |
| T3.3 | 商家端订单管理(数据隔离) | Phase 3 |
| T4.1 | 用户端布局+动态菜单 | Phase 4 |
| T4.2 | 首页+分类浏览+图书详情 | Phase 4 |
| T4.3 | 购物车+地址管理前端 | Phase 4 |
| T4.4 | 下单流程(库存扣减+事务锁) | Phase 4 |
| T4.5 | 模拟支付+30分钟超时释放 | Phase 4 |
| T5.1 | Review模型+DFA敏感词+评价API | Phase 5 |
| T5.2 | Collection模型+收藏API | Phase 5 |
| T5.3 | 评价前端页面 | Phase 5 |
| T5.4 | 退款流程完善 | Phase 5 |
| T6.1 | i18n翻译文件 | Phase 6 |
| T6.2 | 后端单元测试+集成测试 | Phase 6 |
| T6.3 | Docker部署完善 | Phase 6 |
| T6.4 | 前端E2E测试+构建验证 | Phase 6 |

---

## 后端API端点清单

### 管理端 (需JWT, CustomPermission)

```
GET/POST  /api/bookshop/admin/merchants/              # 商家列表
POST      /api/bookshop/admin/merchants/{id}/audit/   # 审核(approve/reject)
POST      /api/bookshop/admin/merchants/{id}/disable/ # 禁用
POST      /api/bookshop/admin/merchants/{id}/enable/  # 启用

GET/POST  /api/bookshop/admin/categories/             # 分类CRUD
GET       /api/bookshop/admin/categories/tree/        # 分类树

GET/POST  /api/bookshop/admin/books/                  # 图书CRUD
PATCH     /api/bookshop/admin/books/{id}/status/      # 上下架

GET       /api/bookshop/admin/orders/                 # 订单列表(支持status/merchant/user筛选)
GET       /api/bookshop/admin/orders/{id}/            # 订单详情(含items嵌套)
POST      /api/bookshop/admin/orders/{id}/force_refund/ # 强制退款

GET       /api/bookshop/admin/warnings/               # 预警图书列表(level/merchant_id/category_id筛选)
GET       /api/bookshop/admin/warnings/threshold/     # 获取全局阈值
PUT       /api/bookshop/admin/warnings/threshold/     # 设置全局阈值

GET       /api/bookshop/admin/statistics/overview/           # 总览(9项指标)
GET       /api/bookshop/admin/statistics/trend/              # 趋势(days/start_date/end_date)
GET       /api/bookshop/admin/statistics/category_distribution/ # 分类分布
GET       /api/bookshop/admin/statistics/merchant_ranking/   # 商家排行(limit/order_by)
```

### 商家端 (需JWT, MerchantPermission)

```
GET       /api/bookshop/merchant/warnings/            # 自己店铺预警
```

### 用户端 (部分AllowAny, 部分需JWT+OwnerPermission)

```
GET       /api/bookshop/customer/categories/          # 分类(AllowAny)
GET       /api/bookshop/customer/books/               # 图书列表(AllowAny, 仅可售)
GET/POST  /api/bookshop/customer/cart/                # 购物车(需登录)
GET/POST  /api/bookshop/customer/addresses/           # 地址CRUD(需登录)
```

---

## 前端页面清单

| 菜单路径 | 组件 | 状态 |
|----------|------|------|
| 书店管理 > 商家审核 | bookshop/admin/merchant_audit/index | ✅ |
| 书店管理 > 图书管理 | bookshop/admin/books/index | ✅ |
| 书店管理 > 分类管理 | bookshop/admin/category/index | ✅ |
| 书店管理 > 订单监控 | bookshop/admin/orders/index | ✅ |
| 书店管理 > 库存预警 | bookshop/admin/stock_warning/index | ✅ |
| 书店管理 > 数据统计 | bookshop/admin/dashboard/index | ✅ |
| 书店管理 > 支付记录 | bookshop/admin/payment_records/index | ⚠️ 待T4.5 |

---

## 数据库测试数据

### 商家 (3条)

| id | name | status |
|----|------|--------|
| 1 | 测试商家 | approved |
| 2 | 验证商家 | approved |
| 3 | TestMerchant_Verify | approved |

### 图书 (2条)

| id | title | status | stock | merchant |
|----|-------|--------|-------|----------|
| 1 | 测试图书1 | on_sale | 0 | 测试商家 |
| 3 | 可见图书 | on_sale | 11 | 验证商家 |

### 订单 (4条, 测试用)

| id | order_no | status | pay_amount |
|----|----------|--------|------------|
| 1 | ORD64591945298527 | refunded | 54.80 |
| 2 | ORD38914530578132 | paid | 54.80 |
| 3 | ORD05521898519322 | shipped | 54.80 |
| 4 | ORD21474209294416 | completed | 54.80 |

### 分类 (6条)

小说/文学 等两级分类结构

---

## 快速验证命令

```bash
# 获取管理员Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"admin123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['data']['access'])")

# 验证各API
curl -s -H "Authorization: JWT $TOKEN" http://localhost:8000/api/bookshop/admin/merchants/ | python -m json.tool
curl -s -H "Authorization: JWT $TOKEN" http://localhost:8000/api/bookshop/admin/orders/ | python -m json.tool
curl -s -H "Authorization: JWT $TOKEN" http://localhost:8000/api/bookshop/admin/warnings/ | python -m json.tool
curl -s -H "Authorization: JWT $TOKEN" http://localhost:8000/api/bookshop/admin/statistics/overview/ | python -m json.tool

# 验证前端
# 浏览器访问 http://localhost:8080
# 用superadmin/admin123登录
# 侧边栏应显示"书店管理"菜单(7个子菜单)
```
