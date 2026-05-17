# OpenBookShop 订单模块 SPEC

**版本**: 1.0
**日期**: 2026-05-16
**依赖**: [foundation.md](foundation.md), [merchant.md](merchant.md), [catalog.md](catalog.md)
**目标**: 定义 CartItem、Address、Order、OrderItem 模型与状态流转；库存扣减（下单时）与 30 分钟未支付释放；事务锁规则；三端权限与数据隔离；API、校验、错误、测试、迁移与回滚。**不包含**实现代码。

---

## 1. 模块边界

### In Scope

- **消费者端**: 购物车 CRUD；收货地址 CRUD（最多 5 个）；下单（库存扣减）；模拟支付；订单列表/详情；取消/确认收货/申请退款
- **商家端**: 自己店铺订单列表/详情；发货；退款审核（同意/拒绝）
- **管理端**: 全平台订单列表/详情；强制退款

### Out of Scope

- 评价系统（review 模块）
- 图书收藏（collection 模块）
- 商家结算/提现/积分/优惠券
- 真实支付/短信/物流

---

## 2. 通用约定

- **URL 前缀**: `/api/bookshop/`，尾斜杠
- **JWT Header**: `Authorization: JWT <token>`
- **分页**: `CustomPagination` — `{code:2000, page, limit, total, is_next, is_previous, data:[...], msg}`
- **成功详情**: `DetailResponse` — `{code:2000, data:{...}, msg}`
- **业务错误**: `CustomValidationError` → `{code:4000, data:null, msg}`
- **权限不足**: DRF 403 → `{code:4000, msg:"..."}`
- **金额**: 所有金额字段 `DecimalField(max_digits=10, decimal_places=2)`，禁止 float

---

## 3. 数据模型

### 3.1 CartItem（购物车项）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `user` | FK(Users) | NOT NULL, on_delete=CASCADE, related_name='cart_items' | 消费者 |
| `book` | FK(Book) | NOT NULL, on_delete=CASCADE | 图书 |
| `quantity` | IntegerField | NOT NULL, default=1, >=1 | 数量 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_cart_item`
**ordering**: `-create_datetime`
**唯一约束**: `unique_together = ['user', 'book']` — 同一用户同一图书只保留一条
**索引**: `user_id`

### 3.2 Address（收货地址）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `user` | FK(Users) | NOT NULL, on_delete=CASCADE, related_name='addresses' | 消费者 |
| `receiver_name` | CharField(max_length=50) | NOT NULL | 收货人 |
| `receiver_phone` | CharField(max_length=20) | NOT NULL, regex `^1[3-9]\d{9}$` | 联系电话 |
| `province` | CharField(max_length=50) | NOT NULL | 省份 |
| `city` | CharField(max_length=50) | NOT NULL | 城市 |
| `district` | CharField(max_length=50) | NOT NULL | 区/县 |
| `detail_address` | CharField(max_length=255) | NOT NULL | 详细地址 |
| `is_default` | BooleanField | default=False | 默认地址 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_address`
**ordering**: `-is_default`, `-create_datetime`
**索引**: `user_id`
**业务约束**: 每用户最多 5 个地址（serializer 层校验）

### 3.3 Order（订单主表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `order_no` | CharField(max_length=32) | NOT NULL, UNIQUE | 订单号：YYYYMMDDHHMMSS + 6 位随机 |
| `user` | FK(Users) | NOT NULL, on_delete=PROTECT, related_name='orders' | 下单用户 |
| `merchant` | FK(Merchant) | NOT NULL, on_delete=PROTECT, related_name='orders' | 所属商家 |
| `status` | CharField(max_length=20) | NOT NULL, default='pending', 见 3.4 | 订单状态 |
| `total_amount` | DecimalField(10,2) | NOT NULL, >=0 | 订单金额（商品小计之和） |
| `discount_amount` | DecimalField(10,2) | NOT NULL, default=0 | 优惠金额 |
| `freight_amount` | DecimalField(10,2) | NOT NULL, default=0 | 运费 |
| `pay_amount` | DecimalField(10,2) | NOT NULL, >=0 | 实付金额 = total - discount + freight |
| `receiver_name` | CharField(max_length=50) | NOT NULL | 收货人（下单时快照） |
| `receiver_phone` | CharField(max_length=20) | NOT NULL | 联系电话（下单时快照） |
| `receiver_address` | CharField(max_length=255) | NOT NULL | 完整收货地址（下单时快照） |
| `pay_time` | DateTimeField | null, blank | 支付时间 |
| `pay_method` | CharField(max_length=50) | null, blank | 支付方式（mock_alipay / mock_wechat） |
| `ship_time` | DateTimeField | null, blank | 发货时间 |
| `express_company` | CharField(max_length=50) | null, blank | 快递公司（模拟） |
| `express_no` | CharField(max_length=50) | null, blank | 快递单号（模拟） |
| `cancel_reason` | CharField(max_length=255) | null, blank | 取消/退款原因 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_order`
**ordering**: `-create_datetime`
**索引**: `(user_id, status)`, `(merchant_id, status)`, `order_no`（unique）, `create_datetime`（超时扫描）

### 3.4 Order 状态枚举与流转

```
STATUS_CHOICES = (
    ('pending',   '待付款'),
    ('paid',      '已付款'),
    ('shipped',   '已发货'),
    ('received',  '已收货'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
    ('refunding', '退款中'),
    ('refunded',  '已退款'),
)
```

**状态流转图**:

```
                    ┌──────────┐
         下单成功    │ pending  │ ← 初始状态
                   └────┬─────┘
                        │
           ┌────────────┼────────────┐
           │ 支付       │ 手动取消    │ 超时30min自动取消
           ▼            ▼            ▼
      ┌────────┐  ┌──────────┐  ┌──────────┐
      │  paid  │  │cancelled │  │cancelled │
      └───┬────┘  └──────────┘  └──────────┘
          │ 商家发货
          ▼
      ┌─────────┐
      │ shipped │
      └────┬────┘
           │ 用户确认收货
           ▼
      ┌──────────┐
      │ received │
      └────┬─────┘
           │ 系统自动完成(7天) 或 用户手动完成
           ▼
      ┌───────────┐
      │ completed │
      └───────────┘

      退款分支（从 paid 或 shipped 状态发起）:
      ┌────────┐  用户申请退款  ┌───────────┐  商家同意  ┌──────────┐
      │  paid  │ ──────────→  │ refunding │ ────────→ │ refunded │
      └────────┘              └───────────┘           └──────────┘
      ┌─────────┐             ┌───────────┐  商家拒绝
      │ shipped │ ──────────→ │ refunding │ ────→ 回到原状态
      └─────────┘             └───────────┘
```

**合法转换表**:

| 从 → 到 | 触发者 | 条件 | 库存影响 |
|----------|--------|------|----------|
| `pending` → `paid` | 消费者 | 模拟支付成功 | — |
| `pending` → `cancelled` | 消费者 / Celery | 手动取消 或 超时30分钟 | **释放**（stock += quantity） |
| `paid` → `shipped` | 商家 | 填写物流信息 | — |
| `paid` → `refunding` | 消费者 | 申请退款 | — |
| `shipped` → `received` | 消费者 | 确认收货 | — |
| `shipped` → `refunding` | 消费者 | 申请退款 | — |
| `received` → `completed` | 系统/消费者 | 7天自动 或 手动确认 | — |
| `refunding` → `refunded` | 商家（同意）/ 管理员（强制） | 审核同意 | **释放**（stock += quantity） |
| `refunding` → `paid` | 商家 | 拒绝退款 | — |
| `refunding` → `shipped` | 商家 | 拒绝退款（原状态为 shipped） | — |
| 其他转换 | **禁止** | — | — |

### 3.5 OrderItem（订单项）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `order` | FK(Order) | NOT NULL, on_delete=CASCADE, related_name='items' | 关联订单 |
| `book` | FK(Book) | NOT NULL, on_delete=PROTECT | 图书（PROTECT：有订单项时不允许删书） |
| `book_title` | CharField(max_length=200) | NOT NULL | 下单时快照书名 |
| `book_cover` | CharField(max_length=255) | NOT NULL | 下单时快照封面图 URL |
| `price` | DecimalField(10,2) | NOT NULL, >=0 | 下单时快照单价 |
| `quantity` | IntegerField | NOT NULL, >=1 | 数量 |
| `total_price` | DecimalField(10,2) | NOT NULL, >=0 | 小计 = price × quantity |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_order_item`
**ordering**: `id`
**索引**: `order_id`, `book_id`

---

## 4. 库存扣减与释放规则

### 4.1 核心原则

- **扣减时机**: 创建订单时（Order 状态变为 `pending`），在事务内扣减
- **释放时机**: 订单取消（手动/超时）或退款通过时，在事务内释放
- **禁止超卖**: 使用 `select_for_update()` 行级悲观锁

### 4.2 下单扣减流程（伪代码）

```
@transaction.atomic
def create_order(user, address_id, items):
    # 1. 锁定图书行（按 id 排序防死锁）
    book_ids = sorted([item['book_id'] for item in items])
    books = Book.objects.select_for_update().filter(id__in=book_ids, status='on_sale')

    # 2. 校验
    for item in items:
        book = books.get(id=item['book_id'])
        if book.stock < item['quantity']:
            raise CustomValidationError("库存不足")

    # 3. 扣减库存
    for item in items:
        book = books.get(id=item['book_id'])
        book.stock -= item['quantity']
        book.save(update_fields=['stock'])

    # 4. 创建 Order + OrderItem（快照地址和图书信息）
    # 5. 计算金额
    # 6. 返回订单
```

**关键约束**:
- `select_for_update()` 必须在 `@transaction.atomic` 内
- 锁定行按 `id` 排序，防止并发死锁
- 校验 `book.status == 'on_sale'`，下架书不可下单
- 校验 `book.merchant.status == 'approved'` 且 `book.merchant.is_open == True`
- 任何步骤失败，整个事务回滚（库存不扣减）

### 4.3 库存释放规则

| 触发场景 | 释放方式 | 时机 |
|----------|----------|------|
| 消费者手动取消 pending 订单 | `book.stock += quantity` | 事务内立即释放 |
| Celery 超时自动取消（30min） | `book.stock += quantity` | 事务内立即释放 |
| 退款通过（商家同意/管理员强制） | `book.stock += quantity` | 事务内立即释放 |
| 订单完成（completed） | 不释放 | 库存已在下单时扣减 |

### 4.4 30 分钟超时释放（Celery beat）

**定时任务**: `dvadmin.bookshop.tasks.cancel_timeout_orders`
**执行频率**: 每 5 分钟
**扫描条件**: `status='pending' AND create_datetime < now() - 30min`
**执行流程**:

```
@transaction.atomic
def cancel_timeout_orders():
    timeout = now() - timedelta(minutes=30)
    orders = Order.objects.select_for_update().filter(
        status='pending', create_datetime__lt=timeout
    )
    for order in orders:
        order.status = 'cancelled'
        order.cancel_reason = '超时未支付，自动取消'
        order.save(update_fields=['status', 'cancel_reason', 'update_datetime'])
        # 释放库存
        for item in order.items.all():
            Book.objects.filter(id=item.book_id).update(
                stock=F('stock') + item.quantity
            )
```

**Celery beat 配置**:
```python
CELERY_BEAT_SCHEDULE = {
    'cancel_timeout_orders': {
        'task': 'dvadmin.bookshop.tasks.cancel_timeout_orders',
        'schedule': crontab(minute='*/5'),
    },
}
```

---

## 5. 事务锁规则（select_for_update）

### 5.1 必须使用 select_for_update 的场景

| 场景 | 锁定对象 | 说明 |
|------|----------|------|
| 创建订单 | `Book` 行（按 id 排序） | 防止并发超卖 |
| 取消订单释放库存 | `Order` 行 + `Book` 行 | 防止库存重复释放 |
| Celery 超时释放 | `Order` 行 + `Book` 行 | 防止与手动取消/支付并发冲突 |
| 退款通过释放库存 | `Order` 行 + `Book` 行 | 防止库存计算错误 |
| 模拟支付 | `Order` 行 | 防止与超时释放并发 |

### 5.2 锁定顺序（防死锁）

1. `Order` 行（按 `id` 排序）
2. `Book` 行（按 `id` 排序）

**原则**: 所有事务中锁定多行时，统一按 `id` 升序锁定。

### 5.3 禁止事项

- 禁止在事务外执行库存扣减/释放
- 禁止先扣后校验（必须先 `select_for_update` 锁定 → 校验 → 扣减）
- 禁止使用乐观锁（`F()` + `filter(stock__gte=quantity)` 可作为补充校验，但不替代悲观锁）

---

## 6. 权限规则

### 6.1 端点权限矩阵

| 端点组 | Admin | Merchant | Customer | 匿名 |
|--------|-------|----------|----------|------|
| admin/orders | ✅ | ❌ | ❌ | ❌ |
| merchant/orders | ❌ | ✅（仅自己店铺） | ❌ | ❌ |
| customer/cart | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/addresses | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/orders | ❌ | ❌ | ✅（仅自己） | ❌ |

### 6.2 数据隔离规则

- **管理端 Order**: `get_queryset()` 返回 `Order.objects.all()`，无隔离
- **商家端 Order**: `get_queryset()` 过滤 `merchant=request.user.merchant`；`MerchantPermission.has_object_permission()` 校验 `obj.merchant_id == request.user.merchant_id`
- **消费者端 CartItem**: `get_queryset()` 过滤 `user=request.user`；`OwnerPermission.has_object_permission()` 校验 `obj.user_id == request.user.id`
- **消费者端 Address**: `get_queryset()` 过滤 `user=request.user`；`OwnerPermission` 校验
- **消费者端 Order**: `get_queryset()` 过滤 `user=request.user`；`OwnerPermission` 校验

### 6.3 OwnerPermission 详细规则（本模块）

**has_permission(request, view)**:
1. `request.user.is_authenticated` → 否则 401
2. `request.user.is_superuser` → 直通
3. `request.user.user_type == 3` → 否则 4003（仅消费者可操作自己购物车/地址/订单；商家通过商家端接口操作）
4. 通过

**has_object_permission(request, view, obj)**:
1. `request.user.is_superuser` → 直通
2. `obj` 有 `user` 属性 → `obj.user_id == request.user.id`
3. 不匹配 → 4003

### 6.4 特殊权限场景

- **消费者下单**: `OwnerPermission` 校验 `address.user_id == request.user.id`（地址归属）
- **商家发货**: `MerchantPermission` 校验 `order.merchant_id == request.user.merchant_id`
- **商家退款审核**: `MerchantPermission` 校验 `order.merchant_id == request.user.merchant_id`
- **管理员强制退款**: `CustomPermission`（管理员直通）

---

## 7. API 设计

### 7.1 消费者端 — 购物车 `/api/bookshop/customer/cart/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/customer/cart/` | 购物车列表 | OwnerPermission |
| POST | `/api/bookshop/customer/cart/` | 加入购物车 | OwnerPermission |
| PUT | `/api/bookshop/customer/cart/{id}/` | 更新数量 | OwnerPermission |
| DELETE | `/api/bookshop/customer/cart/{id}/` | 删除购物车项 | OwnerPermission |

#### POST 加入购物车请求体

```json
{
  "book_id": 1,
  "quantity": 2
}
```

**逻辑**: 若 `user+book` 已存在，`quantity += 新数量`（合并）；否则新建。校验 `book.status == 'on_sale'`，`quantity` 上限 99。

#### PUT 更新数量请求体

```json
{
  "quantity": 3
}
```

### 7.2 消费者端 — 收货地址 `/api/bookshop/customer/addresses/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/customer/addresses/` | 地址列表 | OwnerPermission |
| POST | `/api/bookshop/customer/addresses/` | 新增地址 | OwnerPermission |
| PUT | `/api/bookshop/customer/addresses/{id}/` | 更新地址 | OwnerPermission |
| DELETE | `/api/bookshop/customer/addresses/{id}/` | 删除地址 | OwnerPermission |
| PATCH | `/api/bookshop/customer/addresses/{id}/default/` | 设为默认 | OwnerPermission |

#### POST/PUT 地址请求体

```json
{
  "receiver_name": "string (max=50)",
  "receiver_phone": "string (max=20, regex)",
  "province": "string (max=50)",
  "city": "string (max=50)",
  "district": "string (max=50)",
  "detail_address": "string (max=255)",
  "is_default": false
}
```

**设为默认逻辑**: 设置 `is_default=True` 时，自动将该用户其他地址 `is_default=False`。

### 7.3 消费者端 — 订单 `/api/bookshop/customer/orders/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/bookshop/customer/orders/` | 创建订单 | OwnerPermission |
| GET | `/api/bookshop/customer/orders/` | 订单列表（分页、status 筛选） | OwnerPermission |
| GET | `/api/bookshop/customer/orders/{id}/` | 订单详情 | OwnerPermission |
| POST | `/api/bookshop/customer/orders/{id}/pay/` | 模拟支付 | OwnerPermission |
| POST | `/api/bookshop/customer/orders/{id}/cancel/` | 取消订单 | OwnerPermission |
| POST | `/api/bookshop/customer/orders/{id}/confirm/` | 确认收货 | OwnerPermission |
| POST | `/api/bookshop/customer/orders/{id}/refund/` | 申请退款 | OwnerPermission |

#### POST 创建订单请求体

```json
{
  "address_id": 1,
  "items": [
    {"book_id": 1, "quantity": 2},
    {"book_id": 3, "quantity": 1}
  ]
}
```

**创建流程**:
1. 校验 `address_id` 归属当前用户
2. `@transaction.atomic` + `select_for_update` 锁定 Book 行
3. 校验每本书可售（`status='on_sale'`, `merchant.status='approved'`, `merchant.is_open=True`）
4. 校验库存充足（`book.stock >= quantity`）
5. 扣减库存（`book.stock -= quantity`）
6. 从 Address 快照收货信息到 Order
7. 从 Book 快照书名、封面、单价到 OrderItem
8. 计算 `total_amount` = Σ(price × quantity)
9. `pay_amount = total_amount - discount_amount + freight_amount`（当前 discount=0, freight=0）
10. 生成 `order_no`（YYYYMMDDHHMMSS + 6 位随机）
11. 创建 Order（status='pending'）+ OrderItem
12. 删除已下单的 CartItem（清空已下单商品）
13. 返回订单详情

**响应**: `{code:2000, data:{order_no, status, pay_amount, items:[...], ...}, msg:"下单成功"}`

#### POST 模拟支付请求体

```json
{
  "pay_method": "mock_alipay" | "mock_wechat"
}
```

**支付流程**:
1. 校验 `order.status == 'pending'`
2. `@transaction.atomic` + `select_for_update` 锁定 Order
3. Order.status → 'paid', pay_time=now(), pay_method
4. 创建 PaymentRecord（transaction_no, pay_amount, status='success'）
5. 返回支付成功

#### POST 取消订单

- 仅 `status='pending'` 可取消
- 事务内：`status='cancelled'`，释放库存

#### POST 确认收货

- 仅 `status='shipped'` 可确认
- `status='received'`

#### POST 申请退款请求体

```json
{
  "reason": "string (必填, max=255)"
}
```

- 仅 `status='paid'` 或 `'shipped'` 可申请
- `status='refunding'`，记录 `cancel_reason`

### 7.4 商家端 — 订单 `/api/bookshop/merchant/orders/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/orders/` | 自己店铺订单列表（分页、status 筛选） | MerchantPermission |
| GET | `/api/bookshop/merchant/orders/{id}/` | 订单详情 | MerchantPermission |
| POST | `/api/bookshop/merchant/orders/{id}/ship/` | 发货 | MerchantPermission |
| POST | `/api/bookshop/merchant/orders/{id}/refund-approve/` | 同意退款 | MerchantPermission |
| POST | `/api/bookshop/merchant/orders/{id}/refund-reject/` | 拒绝退款 | MerchantPermission |

#### POST 发货请求体

```json
{
  "express_company": "string (必填, max=50)",
  "express_no": "string (必填, max=50)"
}
```

- 仅 `status='paid'` 可发货
- `status='shipped'`, ship_time=now()

#### POST 同意退款

- 仅 `status='refunding'` 可操作
- `@transaction.atomic` + `select_for_update`
- `status='refunded'`，释放库存
- 记录退款金额

#### POST 拒绝退款请求体

```json
{
  "reason": "string (可选, max=255)"
}
```

- 仅 `status='refunding'` 可操作
- 回退到退款前状态（'paid' 或 'shipped'，需记录原始状态）

### 7.5 管理端 — 订单 `/api/bookshop/admin/orders/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/orders/` | 全平台订单列表（分页、status/merchant_id/user_id 筛选） | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/orders/{id}/` | 订单详情 | CustomPermission (Admin) |
| POST | `/api/bookshop/admin/orders/{id}/force-refund/` | 强制退款 | CustomPermission (Admin) |

#### POST 强制退款

- 任意非终态（`cancelled`/`refunded`/`completed` 除外）可强制退款
- `@transaction.atomic` + `select_for_update`
- `status='refunded'`，释放库存
- 记录操作人和原因

---

## 8. 校验规则

### 8.1 购物车校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 图书存在 | book_id 指向存在的图书 | 4000 | 图书不存在 |
| 图书可售 | book.status == 'on_sale' | 4000 | 该图书已下架 |
| 商家可售 | book.merchant.status == 'approved' AND book.merchant.is_open == True | 4000 | 商家暂停营业 |
| 数量 | >=1, <=99 | 4000 | 数量不合法 |
| 合并后数量上限 | 已有项 quantity + 新 quantity <= 99 | 4000 | 购物车数量超出上限 |

### 8.2 地址校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 收货人 | 非空, max=50 | 4000 | 收货人不能为空 |
| 联系电话 | 非空, regex `^1[3-9]\d{9}$` | 4000 | 联系电话格式不正确 |
| 省份 | 非空, max=50 | 4000 | 省份不能为空 |
| 城市 | 非空, max=50 | 4000 | 城市不能为空 |
| 区县 | 非空, max=50 | 4000 | 区/县不能为空 |
| 详细地址 | 非空, max=255 | 4000 | 详细地址不能为空 |
| 地址数量上限 | 每用户最多 5 个 | 4000 | 最多添加5个收货地址 |
| 非本人地址 | address.user_id != request.user.id | 4003 | 无权操作此地址 |

### 8.3 创建订单校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 地址归属 | address_id 指向的地址属于当前用户 | 4003 | 收货地址不属于当前用户 |
| 商品列表非空 | items 至少 1 项 | 4000 | 订单商品不能为空 |
| 图书可售 | 每本 book.status == 'on_sale' | 4000 | 图书"{title}"已下架 |
| 商家可售 | book.merchant.status == 'approved' AND is_open | 4000 | 商家暂停营业 |
| 库存充足 | book.stock >= quantity | 4000 | 图书"{title}"库存不足 |
| 数量合法 | quantity >= 1 | 4000 | 数量不合法 |
| 重复图书 | items 中不可有重复 book_id | 4000 | 订单中存在重复图书 |
| 单笔订单上限 | items 数量 <= 50 | 4000 | 单笔订单商品种类不能超过50 |

### 8.4 订单状态转换校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 支付 | order.status == 'pending' | 4000 | 订单状态不允许支付 |
| 取消 | order.status == 'pending' | 4000 | 订单状态不允许取消 |
| 确认收货 | order.status == 'shipped' | 4000 | 订单状态不允许确认收货 |
| 申请退款 | order.status ∈ ('paid', 'shipped') | 4000 | 订单状态不允许申请退款 |
| 发货 | order.status == 'paid' | 4000 | 订单状态不允许发货 |
| 同意退款 | order.status == 'refunding' | 4000 | 订单不在退款中状态 |
| 拒绝退款 | order.status == 'refunding' | 4000 | 订单不在退款中状态 |
| 退款原因 | 申请退款时 reason 非空 | 4000 | 退款原因不能为空 |
| 发货信息 | express_company 和 express_no 非空 | 4000 | 物流信息不完整 |

### 8.5 支付校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 支付方式 | pay_method ∈ ('mock_alipay', 'mock_wechat') | 4000 | 支付方式不合法 |
| 重复支付 | order.status != 'pending' 时拒绝 | 4000 | 订单状态不允许支付 |

---

## 9. 错误码定义

| 错误码 | 含义 | 订单模块典型场景 |
|--------|------|-----------------|
| 2000 | 成功 | — |
| 4000 | 业务错误 | 库存不足、图书下架、状态不允许操作、地址上限、校验失败 |
| 4001 | 未认证 | JWT 缺失/过期 |
| 4003 | 无权限 | 操作他人地址/订单、商家访问非自己店铺订单、未审核商家操作 |

---

## 10. 测试策略

### 10.1 单元测试

| 测试类 | 测试用例 | 验证点 |
|--------|----------|--------|
| `TestCartItemModel` | 创建购物车项 | user+book 唯一约束 |
| `TestCartItemModel` | 重复 book 合并 | quantity 累加 |
| `TestCartItemModel` | 数量上限 | quantity > 99 返回 4000 |
| `TestAddressModel` | 创建地址验证默认值 | is_default=False |
| `TestAddressModel` | 地址上限 | 第 6 个地址返回 4000 |
| `TestAddressModel` | 设为默认 | 其他地址 is_default 自动变 False |
| `TestAddressModel` | 手机号格式 | 非法手机号返回 4000 |
| `TestOrderModel` | 创建订单验证默认值 | status='pending', discount=0, freight=0 |
| `TestOrderModel` | order_no 唯一约束 | 重复 order_no 抛异常 |
| `TestOrderCreation` | 正常下单 | Order+OrderItem 创建; 库存扣减; 金额正确 |
| `TestOrderCreation` | 库存不足 | 返回 4000; 库存不变 |
| `TestOrderCreation` | 图书下架 | 返回 4000 |
| `TestOrderCreation` | 商家未审核 | 返回 4000 |
| `TestOrderCreation` | 地址不归属 | 返回 4003 |
| `TestOrderCreation` | 空商品列表 | 返回 4000 |
| `TestOrderCreation` | 重复 book_id | 返回 4000 |
| `TestOrderCreation` | 并发超卖 | select_for_update 防超卖; 第二个请求返回 4000 |
| `TestOrderCreation` | 事务回滚 | 创建中途异常; 库存不扣减; Order 不创建 |
| `TestOrderCreation` | 下单后清空购物车 | 已下单商品从购物车移除 |
| `TestOrderCreation` | 快照正确性 | OrderItem 的 price/book_title/book_cover 与下单时一致（非当前值） |
| `TestOrderPayment` | 正常支付 | status='paid'; PaymentRecord 创建 |
| `TestOrderPayment` | 支付方式不合法 | 返回 4000 |
| `TestOrderPayment` | 重复支付 | 返回 4000 |
| `TestOrderPayment` | 已取消订单支付 | 返回 4000 |
| `TestOrderCancel` | 取消 pending 订单 | status='cancelled'; 库存释放 |
| `TestOrderCancel` | 取消非 pending | 返回 4000 |
| `TestOrderShip` | 商家发货 | status='shipped'; ship_time 记录 |
| `TestOrderShip` | 非本人店铺订单发货 | 返回 4003 |
| `TestOrderShip` | 物流信息不完整 | 返回 4000 |
| `TestOrderConfirm` | 确认收货 | status='received' |
| `TestOrderConfirm` | 非 shipped 状态确认 | 返回 4000 |
| `TestOrderRefund` | 申请退款（paid） | status='refunding' |
| `TestOrderRefund` | 申请退款（shipped） | status='refunding' |
| `TestOrderRefund` | 非 paid/shipped 申请退款 | 返回 4000 |
| `TestOrderRefund` | 退款原因空 | 返回 4000 |
| `TestRefundApprove` | 商家同意退款 | status='refunded'; 库存释放 |
| `TestRefundApprove` | 非本人店铺退款审核 | 返回 4003 |
| `TestRefundReject` | 商家拒绝退款 | 回退到原状态（paid/shipped） |
| `TestTimeoutCancel` | 30 分钟超时取消 | status='cancelled'; 库存释放 |
| `TestTimeoutCancel` | 已支付订单不被取消 | status 不变 |
| `TestTimeoutCancel` | 与手动取消并发 | 无死锁; 库存不重复释放 |
| `TestMerchantOrderIsolation` | 商家 A 查看商家 B 订单 | 返回 4003 |
| `TestOwnerPermission` | 用户 A 操作用户 B 订单 | 返回 4003 |
| `TestOwnerPermission` | 用户 A 操作用户 B 地址 | 返回 4003 |
| `TestOwnerPermission` | 用户 A 操作用户 B 购物车 | 返回 4003 |
| `TestForceRefund` | 管理员强制退款 | status='refunded'; 库存释放 |
| `TestForceRefund` | 终态订单强制退款 | 返回 4000 |

### 10.2 集成测试场景

| 场景 | 步骤 | 验证 |
|------|------|------|
| 完整购物流程 | 加购→下单→支付→发货→收货→完成 | 库存扣减/状态流转/金额正确 |
| 取消释放库存 | 下单→取消 | 库存恢复; 订单状态正确 |
| 超时自动取消 | 下单→等待超时→Celery 扫描 | 库存释放; status='cancelled' |
| 退款流程 | 下单→支付→申请退款→商家同意 | 库存释放; status='refunded' |
| 退款拒绝 | 下单→支付→申请退款→商家拒绝 | 回到 paid; 库存不变 |
| 并发超卖 | 库存=1, 两个用户同时下单 | 仅一个成功; 另一个返回 4000 |
| 支付与超时并发 | 下单→超时任务与支付同时到达 | 无死锁; 状态一致 |
| 数据隔离 | 商家 A 查看商家 B 订单; 用户 A 操作用户 B 地址 | 返回 4003 |
| 快照隔离 | 下单后修改图书价格/名称 | OrderItem 仍为下单时快照 |

---

## 11. 迁移与回滚

### 11.1 迁移批次

| 批次 | 内容 | 依赖 |
|------|------|------|
| 005 | 创建 `dvadmin_bookshop_cart_item` 表 | 001(Users), 003(Book) |
| 005 | 创建 `dvadmin_bookshop_address` 表 | 001(Users) |
| 004 | 创建 `dvadmin_bookshop_order` 表 | 001(Users), 002(Merchant) |
| 004 | 创建 `dvadmin_bookshop_order_item` 表 | 004(Order), 003(Book) |

**说明**: CartItem 和 Address 在批次 005（与 PLAN 一致）；Order 和 OrderItem 在批次 004。CartItem/Address 不依赖 Merchant 或 Order，可与 Order 表同批次或分开，此处按 PLAN 拆分。

### 11.2 回滚策略

| 批次 | 回滚操作 |
|------|----------|
| 004 | 先删 `dvadmin_bookshop_order_item`（FK → Order），再删 `dvadmin_bookshop_order` |
| 005 | DROP TABLE `dvadmin_bookshop_cart_item`; DROP TABLE `dvadmin_bookshop_address` |

**回滚安全**:
- OrderItem 通过 `on_delete=CASCADE` 随 Order 删除
- Order 通过 `on_delete=PROTECT` 保护 Users 和 Merchant（删除 Order 不影响用户/商家）
- OrderItem 的 `book` FK 为 `PROTECT`，有订单项时不可删书

### 11.3 数据兼容性

- 现有 Users/Merchant/Book/Category 表不受影响
- Order.merchant FK 为 `PROTECT`，保证有订单的商家不可被直接删除
- OrderItem.book FK 为 `PROTECT`，保证有订单项的图书不可被直接删除
- `pay_amount` 默认等于 `total_amount`（当前无优惠/运费）

---

## 12. 前端集成要点

### 12.1 消费者端页面

- **购物车页**: `web/src/views/bookshop/customer/cart.vue` — 购物车列表 + 数量修改 + 全选/批量下单
- **地址管理页**: `web/src/views/bookshop/customer/user/addresses.vue` — 地址 CRUD + 设默认
- **下单页**: `web/src/views/bookshop/customer/checkout.vue` — 选择地址 + 确认商品 + 提交订单
- **订单列表页**: `web/src/views/bookshop/customer/orders/index.vue` — 按 status 筛选
- **订单详情页**: `web/src/views/bookshop/customer/orders/detail.vue` — 状态流转 + 操作按钮
- **API**: `web/src/api/bookshop/cart.ts`, `web/src/api/bookshop/address.ts`, `web/src/api/bookshop/order.ts`

### 12.2 商家端页面

- **订单管理页**: `web/src/views/bookshop/merchant/orders/index.vue` — 自己店铺订单列表
- **订单详情页**: `web/src/views/bookshop/merchant/orders/detail.vue` — 发货 + 退款审核
- **API**: `web/src/api/bookshop/order.ts`（复用，不同端点）

### 12.3 管理端页面

- **订单监控页**: `web/src/views/bookshop/admin/orders.vue` — 全平台订单列表 + 强制退款
- **API**: `web/src/api/bookshop/order.ts`

### 12.4 菜单注册

| 菜单 | component | 可见角色 |
|------|-----------|----------|
| 书城 > 购物车 | `bookshop/customer/cart` | 消费者 |
| 书城 > 我的订单 | `bookshop/customer/orders/index` | 消费者 |
| 个人中心 > 收货地址 | `bookshop/customer/user/addresses` | 消费者 |
| 我的店铺 > 订单管理 | `bookshop/merchant/orders/index` | 商家 |
| 书店管理 > 订单监控 | `bookshop/admin/orders` | 管理员 |

---

## 13. Settings 变更

| 变更 | 文件 | 说明 |
|------|------|------|
| CELERY_BEAT_SCHEDULE 添加 `cancel_timeout_orders` | `backend/application/celery.py` 或 `settings.py` | 每 5 分钟扫描超时订单 |

**无新增环境变量**。订单模块使用现有 MySQL/Redis/JWT 配置。

---

## 14. 验收要点

- [x] CartItem 模型字段、唯一约束、合并逻辑已定义
- [x] Address 模型字段、5 个上限校验、默认地址切换已定义
- [x] Order 模型字段、8 种状态枚举已定义
- [x] Order 状态流转图与合法转换表已定义（含库存影响列）
- [x] OrderItem 模型字段、快照策略已定义
- [x] 下单时库存扣减流程（select_for_update + @transaction.atomic）已定义
- [x] 30 分钟超时释放（Celery beat）已定义
- [x] 库存释放规则（4 种场景）已定义
- [x] 事务锁规则（锁定顺序、防死锁、禁止事项）已定义
- [x] 三端权限矩阵与数据隔离规则已定义
- [x] OwnerPermission 详细判定逻辑已定义
- [x] 消费者端 API（购物车 4 + 地址 5 + 订单 7 = 16 端点）已定义
- [x] 商家端 API（订单 5 端点）已定义
- [x] 管理端 API（订单 3 端点）已定义
- [x] 校验规则（5 类 30+ 条）已定义
- [x] 错误码已定义（2000/4000/4001/4003）
- [x] 单元测试（40+ 用例）与集成测试（9 场景）已定义
- [x] 迁移批次、回滚策略、数据兼容性已定义
- [x] 前端页面与菜单集成已定义
