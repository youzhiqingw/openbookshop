# OpenBookShop SPEC - 可执行契约

> 基于 docs/PRD.md 和 docs/PLAN.md 的修正版本生成
> **关键修正**: user_type扩展而非role_type新增，单Vue项目多布局，service.ts统一请求

---

## API Contracts

### 管理端 API

| Method | Path | Auth | Request | Response | Errors |
|--------|------|------|---------|----------|--------|
| GET | `/api/bookshop/admin/merchants` | JWT + Admin | `{page, limit, status, name}` | `{data: [{id, name, status, contact_name, ...}], count}` | 4000: 参数错误 |
| GET | `/api/bookshop/admin/merchants/{id}` | JWT + Admin | - | `{id, name, status, contact_name, contact_phone, ...}` | 404: 商家不存在 |
| POST | `/api/bookshop/admin/merchants/{id}/audit` | JWT + Admin | `{action: "approve"/"reject", reason}` | `{id, status}` | 4000: 已审核, 4004: 商家不存在 |
| GET | `/api/bookshop/admin/books` | JWT + Admin | `{page, limit, status, category, merchant_id, search}` | `{data: [{id, title, author, price, stock, ...}], count}` | - |
| GET | `/api/bookshop/admin/orders` | JWT + Admin | `{page, limit, status, merchant_id, date_range}` | `{data: [{id, order_no, status, total_amount, ...}], count}` | - |
| GET | `/api/bookshop/admin/statistics` | JWT + Admin | `{date_range, type}` | `{total_sales, total_orders, active_merchants, ...}` | - |
| POST | `/api/bookshop/admin/orders/{id}/refund_force` | JWT + Admin | `{reason}` | `{id, status: "refunded"}` | 4000: 订单状态不允许 |

### 商家端 API

| Method | Path | Auth | Request | Response | Errors |
|--------|------|------|---------|----------|--------|
| GET | `/api/bookshop/merchant/profile` | JWT + Merchant | - | `{id, name, logo, status, ...}` | - |
| PUT | `/api/bookshop/merchant/profile` | JWT + Merchant | `{name, logo, description, ...}` | `{id, name, ...}` | 4000: 审核通过后不可改名 |
| GET | `/api/bookshop/merchant/books` | JWT + Merchant | `{page, limit, status, search}` | `{data: [{id, title, stock, ...}], count}` | - |
| POST | `/api/bookshop/merchant/books` | JWT + Merchant | `{isbn, title, author, ...}` | `{id, title, ...}` | 4000: ISBN重复, 4000: 分类不存在 |
| PUT | `/api/bookshop/merchant/books/{id}` | JWT + Merchant | `{title, price, stock, ...}` | `{id, title, ...}` | 4004: 不是自己的书 |
| PATCH | `/api/bookshop/merchant/books/{id}/status` | JWT + Merchant | `{status: "on_sale"/"off_sale"}` | `{id, status}` | 4004: 不是自己的书 |
| POST | `/api/bookshop/merchant/books/{id}/replenish` | JWT + Merchant | `{quantity: int}` | `{id, stock: new_stock}` | 4000: quantity<=0, 4004: 不是自己的书 |
| GET | `/api/bookshop/merchant/orders` | JWT + Merchant | `{page, limit, status}` | `{data: [{id, order_no, ...}], count}` | - |
| GET | `/api/bookshop/merchant/orders/{id}` | JWT + Merchant | - | `{id, order_no, items, ...}` | 4004: 不是自己店铺的订单 |
| POST | `/api/bookshop/merchant/orders/{id}/ship` | JWT + Merchant | `{express_company, express_no}` | `{id, status: "shipped"}` | 4000: 订单未付款, 4004: 不是自己的订单 |
| POST | `/api/bookshop/merchant/orders/{id}/refund_approve` | JWT + Merchant | - | `{id, status: "refunded"}` | 4000: 订单状态不允许退款 |
| POST | `/api/bookshop/merchant/orders/{id}/refund_reject` | JWT + Merchant | `{reason}` | `{id, status: "paid"}` | 4000: 订单状态不允许 |
| GET | `/api/bookshop/merchant/reviews` | JWT + Merchant | `{page, limit}` | `{data: [{id, content, rating, ...}], count}` | - |
| POST | `/api/bookshop/merchant/reviews/{id}/reply` | JWT + Merchant | `{content}` | `{id, merchant_reply}` | 4004: 不是自己商品的评价 |

### 用户端 API

| Method | Path | Auth | Request | Response | Errors |
|--------|------|------|---------|----------|--------|
| GET | `/api/bookshop/books` | JWT + Customer | `{page, limit, category, search, sort}` | `{data: [{id, title, price, ...}], count}` | - |
| GET | `/api/bookshop/books/{id}` | JWT + Customer | - | `{id, title, price, stock, reviews, ...}` | 404: 图书不存在 |
| GET | `/api/bookshop/categories` | 无/可选 | - | `{data: [{id, name, parent, children}]}` | - |
| GET | `/api/bookshop/cart` | JWT + Customer | - | `{data: [{id, book_title, quantity, ...}]}` | - |
| POST | `/api/bookshop/cart` | JWT + Customer | `{book_id, quantity}` | `{id, book_title, quantity}` | 4000: 图书不存在/已下架, 4000: 库存不足 |
| PUT | `/api/bookshop/cart/{id}` | JWT + Customer | `{quantity}` | `{id, quantity}` | 4000: quantity<=0, 4004: 不是自己的购物车 |
| DELETE | `/api/bookshop/cart/{id}` | JWT + Customer | - | `{}` | 4004: 不是自己的购物车 |
| POST | `/api/bookshop/orders` | JWT + Customer | `{address_id, items: [{book_id, quantity}]}` | `{id, order_no, total_amount}` | 4000: 库存不足, 4000: 地址不存在 |
| GET | `/api/bookshop/orders` | JWT + Customer | `{page, limit, status}` | `{data: [{id, order_no, ...}], count}` | - |
| GET | `/api/bookshop/orders/{id}` | JWT + Customer | - | `{id, order_no, items, ...}` | 4004: 不是自己的订单 |
| POST | `/api/bookshop/orders/{id}/pay` | JWT + Customer | `{pay_method}` | `{payment_record}` | 4000: 订单未付款状态, 4004: 不是自己的订单 |
| POST | `/api/bookshop/orders/{id}/cancel` | JWT + Customer | - | `{id, status: "cancelled"}` | 4000: 订单已付款不可取消, 4004: 不是自己的订单 |
| POST | `/api/bookshop/orders/{id}/confirm` | JWT + Customer | - | `{id, status: "completed"}` | 4000: 订单未发货, 4004: 不是自己的订单 |
| POST | `/api/bookshop/orders/{id}/refund` | JWT + Customer | `{reason}` | `{id, status: "refunding"}` | 4000: 订单状态不允许, 4004: 不是自己的订单 |
| GET | `/api/bookshop/addresses` | JWT + Customer | - | `{data: [{id, receiver_name, ...}]}` | - |
| POST | `/api/bookshop/addresses` | JWT + Customer | `{receiver_name, phone, province, city, district, detail}` | `{id, ...}` | 4000: 地址超5个限制 |
| PUT | `/api/bookshop/addresses/{id}` | JWT + Customer | `{receiver_name, ...}` | `{id, ...}` | 4004: 不是自己的地址 |
| DELETE | `/api/bookshop/addresses/{id}` | JWT + Customer | - | `{}` | 4004: 不是自己的地址 |
| GET | `/api/bookshop/books/{id}/reviews` | 无/可选 | `{page, limit}` | `{data: [{id, rating, content, ...}], count}` | - |
| POST | `/api/bookshop/orders/{id}/review` | JWT + Customer | `{items: [{book_id, rating, content}]}` | `{data: [{id, ...}]}` | 4000: 订单未完成, 4004: 不是自己的订单 |
| POST | `/api/bookshop/books/{id}/collect` | JWT + Customer | - | `{id}` | 4000: 已收藏 |
| DELETE | `/api/bookshop/books/{id}/collect` | JWT + Customer | - | `{}` | 4000: 未收藏 |
| GET | `/api/bookshop/collections` | JWT + Customer | `{page, limit}` | `{data: [{id, book_id, ...}], count}` | - |

---

## Data Model

| Entity/Table | Field | Type | Constraint | Notes |
|--------------|-------|------|------------|-------|
| Users (dvadmin_users) | user_type | IntegerField | choices: 0=管理员,1=前台,2=商家,3=消费者 | **扩展已有字段，不新增role_type** |
| Users (dvadmin_users) | merchant | OneToOneField(bookshop.Merchant) | null=True, blank=True, on_delete=SET_NULL | 仅user_type=2时有效 |
| bookshop_merchant | name | CharField(100) | not null | 店铺名称 |
| bookshop_merchant | logo | CharField(255) | null, blank | 店铺Logo |
| bookshop_merchant | status | CharField(20) | choices: pending/approved/rejected/disabled, default=pending | 审核状态 |
| bookshop_merchant | contact_name | CharField(50) | not null | 联系人 |
| bookshop_merchant | contact_phone | CharField(20) | not null | 联系电话 |
| bookshop_merchant | description | TextField | null, blank | 店铺描述 |
| bookshop_merchant | address | CharField(255) | not null | 店铺地址 |
| bookshop_merchant | is_open | BooleanField | default=True | 营业状态 |
| bookshop_category | name | CharField(50) | not null | 分类名称 |
| bookshop_category | parent | FK(self) | null, blank, on_delete=CASCADE | 两级分类 |
| bookshop_category | sort | IntegerField | default=0 | 排序 |
| bookshop_book | isbn | CharField(20) | unique | ISBN |
| bookshop_book | title | CharField(200) | not null | 书名 |
| bookshop_book | author | CharField(100) | not null | 作者 |
| bookshop_book | publisher | CharField(100) | not null | 出版社 |
| bookshop_book | publish_date | DateField | not null | 出版日期 |
| bookshop_book | category | FK(bookshop_category) | on_delete=PROTECT | 分类 |
| bookshop_book | merchant | FK(bookshop_merchant) | on_delete=CASCADE | **商家数据隔离关键字段** |
| bookshop_book | price | Decimal(10,2) | not null | 售价（Decimal禁止float） |
| bookshop_book | original_price | Decimal(10,2) | not null | 原价 |
| bookshop_book | stock | IntegerField | default=0 | 库存 |
| bookshop_book | warning_stock | IntegerField | default=10 | 库存预警值 |
| bookshop_book | cover_image | CharField(255) | not null | 封面图 |
| bookshop_book | description | TextField | not null | 图书简介 |
| bookshop_book | status | CharField(20) | choices: draft/on_sale/off_sale, default=draft | 上架状态 |
| bookshop_book | sales_count | IntegerField | default=0 | 销量 |
| bookshop_order | order_no | CharField(32) | unique | 订单号 |
| bookshop_order | user | FK(Users) | on_delete=PROTECT | 下单用户 |
| bookshop_order | merchant | FK(bookshop_merchant) | on_delete=PROTECT | 商家 |
| bookshop_order | status | CharField(20) | choices: pending/paid/shipped/received/completed/cancelled/refunding/refunded | 订单状态 |
| bookshop_order | total_amount | Decimal(10,2) | not null | 订单金额（Decimal） |
| bookshop_order | discount_amount | Decimal(10,2) | default=0 | 优惠金额 |
| bookshop_order | freight_amount | Decimal(10,2) | default=0 | 运费 |
| bookshop_order | pay_amount | Decimal(10,2) | not null | 实付金额 |
| bookshop_order | receiver_name | CharField(50) | not null | 收货人 |
| bookshop_order | receiver_phone | CharField(20) | not null | 联系电话 |
| bookshop_order | receiver_address | CharField(255) | not null | 收货地址 |
| bookshop_order | pay_time | DateTimeField | null, blank | 支付时间 |
| bookshop_order | pay_method | CharField(50) | null, blank | 支付方式 |
| bookshop_order | ship_time | DateTimeField | null, blank | 发货时间 |
| bookshop_order_item | order | FK(bookshop_order) | on_delete=CASCADE | 关联订单 |
| bookshop_order_item | book | FK(bookshop_book) | on_delete=PROTECT | 图书 |
| bookshop_order_item | book_title | CharField(200) | not null | 商品名称快照 |
| bookshop_order_item | book_cover | CharField(255) | not null | 商品图片快照 |
| bookshop_order_item | price | Decimal(10,2) | not null | 单价快照 |
| bookshop_order_item | quantity | IntegerField | not null | 数量 |
| bookshop_order_item | total_price | Decimal(10,2) | not null | 小计 |
| bookshop_cart_item | user | FK(Users) | on_delete=CASCADE | 用户 |
| bookshop_cart_item | book | FK(bookshop_book) | on_delete=CASCADE | 图书 |
| bookshop_cart_item | quantity | IntegerField | default=1 | 数量 |
| bookshop_cart_item | unique_together | [user, book] | - | 同一商品只保留一条 |
| bookshop_address | user | FK(Users) | on_delete=CASCADE | 用户 |
| bookshop_address | receiver_name | CharField(50) | not null | 收货人 |
| bookshop_address | receiver_phone | CharField(20) | not null | 联系电话 |
| bookshop_address | province | CharField(50) | not null | 省份 |
| bookshop_address | city | CharField(50) | not null | 城市 |
| bookshop_address | district | CharField(50) | not null | 区/县 |
| bookshop_address | detail_address | CharField(255) | not null | 详细地址 |
| bookshop_address | is_default | BooleanField | default=False | 默认地址 |
| bookshop_review | order | FK(bookshop_order) | on_delete=CASCADE | 关联订单 |
| bookshop_review | book | FK(bookshop_book) | on_delete=CASCADE | 图书 |
| bookshop_review | user | FK(Users) | on_delete=CASCADE | 评价人 |
| bookshop_review | rating | IntegerField | 1-5 | 评分 |
| bookshop_review | content | TextField | not null | 评价内容 |
| bookshop_review | images | JSONField | default=[] | 评价图片 |
| bookshop_review | merchant_reply | TextField | null, blank | 商家回复 |
| bookshop_review | is_sensitive | BooleanField | default=False | 敏感词标记 |
| bookshop_review | is_visible | BooleanField | default=False | 是否显示(审核后) |
| bookshop_collection | user | FK(Users) | on_delete=CASCADE | 用户 |
| bookshop_collection | book | FK(bookshop_book) | on_delete=CASCADE | 图书 |
| bookshop_collection | unique_together | [user, book] | - | 不可重复收藏 |
| bookshop_payment_record | order | OneToOneField(bookshop_order) | on_delete=CASCADE | 订单 |
| bookshop_payment_record | pay_method | CharField(50) | not null | mock_alipay/mock_wechat |
| bookshop_payment_record | pay_amount | Decimal(10,2) | not null | 支付金额 |
| bookshop_payment_record | transaction_no | CharField(64) | unique | 交易流水号 |
| bookshop_payment_record | status | CharField(20) | default=success | 支付状态 |

---

## Validation Rules

### 金额校验
- 所有金额字段使用 `DecimalField(max_digits=10, decimal_places=2)`，禁止 `float`
- 后端校验: `pay_amount = total_amount - discount_amount + freight_amount`
- 前端显示金额与后端结算金额必须一致

### 库存校验
- 下单时: `select_for_update()` 锁行 + 检查 `stock >= quantity`
- 下单成功后: `stock -= quantity`（事务内）
- 超时释放: Celery beat 每5分钟扫描 `status=pending AND created_at < now()-30min` 的订单
- 取消订单: `stock += quantity`（事务内）
- 退款通过: `stock += quantity`（事务内）
- 补货: `stock += replenish_quantity`（商家操作，需审核通过后才有权限）

### 地址校验
- 每个用户最多5个地址（serializer层限制）
- 设置默认地址时，取消其他默认地址（事务）

### 评价校验
- 只有已完成订单(`status=completed`)可评价
- 评分 `1 <= rating <= 5`
- 评价内容经过DFA敏感词过滤后才显示(`is_visible=True`)
- 同一订单同一书不可重复评价

### 订单状态校验（状态机）
```
pending → paid (支付)
pending → cancelled (取消/超时)
paid → shipped (发货)
paid → refunding (退款申请)
shipped → received (确认收货)
received → completed (自动/手动完成)
refunding → refunded (退款通过)
refunding → paid (退款拒绝)
```

---

## Authorization Rules

### 角色判断
- `request.user.user_type == 0`: 管理员 — 全平台权限
- `request.user.user_type == 2`: 商家 — 仅访问自己店铺数据
- `request.user.user_type == 3`: 消费者 — 仅访问自己个人数据

### 数据隔离规则

| 资源 | Admin | Merchant | Customer |
|------|-------|----------|----------|
| Merchant | 全部 | 自己(profile) | 无 |
| Book | 全部 | `merchant_id == request.user.merchant_id` | 仅上架图书 |
| Order | 全部 | `merchant_id == request.user.merchant_id` | `user_id == request.user.id` |
| CartItem | 无 | 无 | `user_id == request.user.id` |
| Address | 无 | 无 | `user_id == request.user.id` |
| Review | 全部(审核) | 自己商品的review | 自己的review |
| Collection | 无 | 无 | `user_id == request.user.id` |

### 商家准入
- 商家必须 `user_type == 2` 且 `merchant.status == "approved"` 才可操作店铺数据
- `merchant.status == "pending"` 时只能查看审核状态
- `merchant.status == "rejected"/"disabled"` 时禁止所有商家操作

---

## Error Format

所有bookshop API统一使用 `service.ts` 的错误格式（状态码2000体系）:

```json
// 成功
{
  "code": 2000,
  "msg": "success",
  "data": {...}
}

// 参数错误
{
  "code": 4000,
  "msg": "具体错误信息",
  "data": null
}

// 认证失败
{
  "code": 4001,
  "msg": "认证失败",
  "data": null
}

// 权限不足
{
  "code": 4003,
  "msg": "权限不足",
  "data": null
}

// 资源不存在
{
  "code": 4004,
  "msg": "资源不存在",
  "data": null
}

// 系统错误
{
  "code": 5000,
  "msg": "系统内部错误",
  "data": null
}
```

> **注意**: 禁止使用 `request.ts` 的状态码0体系。新增bookshop API模块必须统一使用 `service.ts`。

---

## Environment Variables

| Name | Required | Example | Secret | Purpose |
|------|----------|---------|--------|---------|
| DATABASE_ENGINE | Yes | django.db.backends.mysql | No | 数据库引擎 |
| DATABASE_NAME | Yes | bookshop | No | 数据库名（已从django-vue3-admin改为bookshop） |
| DATABASE_HOST | Yes | 127.0.0.1 / dvadmin3-mysql | No | 数据库地址 |
| DATABASE_PORT | Yes | 3306 | No | 数据库端口 |
| DATABASE_USER | Yes | root | No | 数据库用户 |
| DATABASE_PASSWORD | Yes | DVADMIN3 | Yes | 数据库密码 |
| REDIS_HOST | Yes | 127.0.0.1 / dvadmin3-redis | No | Redis地址 |
| REDIS_PASSWORD | Yes | DVADMIN3 | Yes | Redis密码 |
| CELERY_BROKER_URL | Yes | redis://...@redis:6379/3 | No | Celery broker |

> **配置方式**: `backend/conf/env.py`（从 `env.example.py` 复制）。Django不从环境变量读取，docker-compose的环境变量注入无效，需通过env.py硬编码或init.sh脚本修改。

---

## Test Contracts

### Unit Tests
- `test_merchant_permission`: 商家只能访问自己店铺的数据，访问其他商家数据返回4003
- `test_owner_permission`: 消费者只能访问自己的订单/地址/购物车
- `test_stock_deduction`: 下单时库存扣减，事务内 `select_for_update` 防超卖
- `test_stock_release_timeout`: 超时订单库存释放
- `test_stock_release_cancel`: 取消订单库存释放
- `test_stock_release_refund`: 退款通过库存释放
- `test_address_limit`: 用户最多5个地址
- `test_review_sensitive`: 评价敏感词检测和标记
- `test_order_state_machine`: 订单状态转换合法性

### Integration Tests
- 商家入驻完整流程: 申请 → 管理员审核 → 商家开通 → 操作店铺
- 用户购物完整流程: 浏览 → 加购 → 下单 → 模拟支付 → 商家发货 → 收货 → 评价
- 退款流程: 用户申请 → 商家审核 → 退款 → 库存释放
- 超时释放流程: 下单 → 30分钟不支付 → Celery扫描 → 自动取消 → 库存释放

### E2E Tests
- 管理端: 登录 → 商家审核 → 图书查看 → 订单监控 → 统计仪表盘
- 商家端: 登录 → 店铺管理 → 图书上架 → 订单处理 → 评价回复
- 用户端: 登录 → 浏览 → 加购 → 下单 → 支付 → 收货 → 评价 → 收藏

### Manual Tests
- 商家端布局切换: 登录商家账号后菜单切换为商家端布局
- 用户端布局切换: 登录消费者账号后菜单切换为用户端布局
- Docker一键部署: `docker-compose up -d` 后全部服务正常
- 库存预警: 设置预警值后，库存低于预警时前端显示提醒

---

## Migration And Rollback

### 001: 扩展user_type + 新增merchant FK
- **迁移**: 修改 `Users.user_type` choices, 新增 `merchant FK` (null=True)
- **回滚**: 删除merchant FK, user_type choices回退为原值(0,1)
- **注意**: 不删除旧数据，user_type=1的旧前台用户保留

### 002: 创建bookshop_merchant表
- **迁移**: 新建表
- **回滚**: 删除表

### 003: 创建bookshop_category + bookshop_book表
- **迁移**: 新建表及FK
- **回滚**: 先删book(有FK), 后删category

### 004: 创建bookshop_order + bookshop_order_item表
- **迁移**: 新建表及FK
- **回滚**: 先删order_item, 后删order

### 005: 创建bookshop_cart_item + bookshop_address表
- **迁移**: 新建表及FK/unique_together
- **回滚**: 删除表

### 006: 创建bookshop_review + bookshop_collection + bookshop_payment_record表
- **迁移**: 新建表及FK/unique_together
- **回滚**: 删除表

### 007: 注册bookshop菜单数据（无迁移，通过init命令/SQL）
- **方式**: 通过 `backend/dvadmin/bookshop/fixtures/init_menu.json` + management command 或 SQL脚本插入 `dvadmin_system_menu` 表
- **菜单结构**: 书店管理(6子菜单, 管理端) + 我的店铺(4子菜单, 商家端) + 书城(6子菜单, 用户端)
- **component映射**: menu.component字段值如 `bookshop/admin/books` 对应 `web/src/views/bookshop/admin/books/index.vue`
- **回滚**: DELETE FROM dvadmin_system_menu WHERE app='bookshop'

### 008: 注册Celery beat定时任务（无迁移，settings.py配置）
- **配置**: 在 `application/celery.py` 或 settings.py 中添加 `CELERY_BEAT_SCHEDULE`:
  ```python
  'cancel_timeout_orders': {
      'task': 'dvadmin.bookshop.tasks.cancel_timeout_orders',
      'schedule': crontab(minute='*/5'),
  }
  ```
- **前提**: dvadmin3-celery插件已安装(requirements.txt:31), celery容器已含 `-B` 参数
- **回滚**: 删除CELERY_BEAT_SCHEDULE中的bookshop条目