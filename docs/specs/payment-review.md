# OpenBookShop 支付与评价模块 SPEC

**版本**: 1.0
**日期**: 2026-05-16
**依赖**: [foundation.md](foundation.md), [merchant.md](merchant.md), [catalog.md](catalog.md), [order.md](order.md)
**目标**: 定义 PaymentRecord 模型与模拟支付服务；Review 模型与已购评价规则、敏感词标记、商家回复；Collection 收藏模型；API、权限、校验、错误、测试、迁移与回滚。**不包含**实现代码。**禁止**接入真实第三方支付、短信、物流或邮件。

---

## 1. 模块边界

### In Scope

- **模拟支付服务**: MockPaymentService（mock_alipay / mock_wechat），PaymentRecord 记录
- **评价系统**: 已购图书评价（1-5 星 + 文字 + 图片）、DFA 敏感词检测、商家回复
- **收藏系统**: 图书收藏/取消收藏、收藏列表

### Out of Scope

- 真实第三方支付（支付宝/微信真实 API）
- 短信验证码
- 真实物流追踪
- 邮件发送
- 商家结算/提现
- 积分/优惠券

---

## 2. 通用约定

- **URL 前缀**: `/api/bookshop/`，尾斜杠
- **JWT Header**: `Authorization: JWT <token>`
- **分页**: `CustomPagination` — `{code:2000, page, limit, total, is_next, is_previous, data:[...], msg}`
- **成功详情**: `DetailResponse` — `{code:2000, data:{...}, msg}`
- **业务错误**: `CustomValidationError` → `{code:4000, data:null, msg}`
- **金额**: `DecimalField(max_digits=10, decimal_places=2)`，禁止 float
- **禁止真实第三方**: 支付仅模拟，短信/物流/邮件仅控制台输出或不实现

---

## 3. 数据模型

### 3.1 PaymentRecord（模拟支付记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `order` | OneToOneField(Order) | NOT NULL, on_delete=CASCADE, related_name='payment' | 关联订单 |
| `pay_method` | CharField(max_length=50) | NOT NULL | 支付方式：mock_alipay / mock_wechat |
| `pay_amount` | DecimalField(10,2) | NOT NULL, >=0 | 支付金额（= Order.pay_amount） |
| `pay_time` | DateTimeField | auto_now_add | 支付时间 |
| `transaction_no` | CharField(max_length=64) | NOT NULL, UNIQUE | 交易流水号（模拟：MOCK_ + UUID） |
| `status` | CharField(max_length=20) | NOT NULL, default='success' | 支付状态：success / failed |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_payment_record`
**ordering**: `-pay_time`
**索引**: `transaction_no`（unique）, `order_id`（unique, OneToOne）, `pay_method`

### 3.2 Review（图书评价）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `order` | FK(Order) | NOT NULL, on_delete=CASCADE, related_name='reviews' | 关联订单 |
| `book` | FK(Book) | NOT NULL, on_delete=CASCADE, related_name='reviews' | 关联图书 |
| `user` | FK(Users) | NOT NULL, related_name='reviews' | 评价人 |
| `rating` | IntegerField | NOT NULL, choices 1-5 | 评分（1=很差 2=差 3=一般 4=好 5=很好） |
| `content` | TextField | NOT NULL | 评价内容 |
| `images` | JSONField | default=[] | 评价图片 URL 列表，最多 9 张 |
| `merchant_reply` | TextField | null, blank | 商家回复 |
| `reply_time` | DateTimeField | null, blank | 回复时间 |
| `is_sensitive` | BooleanField | default=False | 是否包含敏感词（DFA 检测结果） |
| `is_visible` | BooleanField | default=True | 是否对外可见（含敏感词时设为 False，需管理员审核） |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_review`
**ordering**: `-create_datetime`
**唯一约束**: `unique_together = ['order', 'book', 'user']` — 同一用户同一订单同一图书只能评价一次
**索引**: `(book_id, is_visible)`, `user_id`, `(order_id, user_id)`

### 3.3 Collection（图书收藏）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `user` | FK(Users) | NOT NULL, on_delete=CASCADE, related_name='collections' | 收藏人 |
| `book` | FK(Book) | NOT NULL, on_delete=CASCADE, related_name='collectors' | 图书 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_collection`
**ordering**: `-create_datetime`
**唯一约束**: `unique_together = ['user', 'book']` — 同一用户同一图书只保留一条收藏
**索引**: `user_id`, `book_id`

---

## 4. 模拟支付服务（MockPaymentService）

### 4.1 设计原则

- **禁止真实第三方**: 不调用支付宝/微信/任何外部支付 API
- **模拟即成功**: 调用 MockPaymentService 后直接返回成功（模拟网络延迟 0-1 秒可选）
- **幂等**: 同一 order 多次调用不重复创建 PaymentRecord
- **事务内调用**: 支付服务在 `@transaction.atomic` 内被订单支付接口调用

### 4.2 服务接口（伪代码）

```
class MockPaymentService:
    @staticmethod
    def pay(order, pay_method):
        """
        模拟支付
        Args:
            order: Order 实例（status='pending'）
            pay_method: 'mock_alipay' | 'mock_wechat'
        Returns:
            PaymentRecord 实例
        Raises:
            CustomValidationError: 支付方式不合法 / 订单状态不允许
        """
        # 1. 校验 pay_method
        if pay_method not in ('mock_alipay', 'mock_wechat'):
            raise CustomValidationError("支付方式不合法")

        # 2. 校验订单状态
        if order.status != 'pending':
            raise CustomValidationError("订单状态不允许支付")

        # 3. 幂等检查
        if hasattr(order, 'payment') and order.payment is not None:
            raise CustomValidationError("订单已支付")

        # 4. 生成模拟流水号
        transaction_no = f"MOCK_{uuid.uuid4().hex[:24]}"

        # 5. 创建 PaymentRecord
        record = PaymentRecord.objects.create(
            order=order,
            pay_method=pay_method,
            pay_amount=order.pay_amount,
            transaction_no=transaction_no,
            status='success'
        )

        # 6. 更新订单状态
        order.status = 'paid'
        order.pay_time = now()
        order.pay_method = pay_method
        order.save(update_fields=['status', 'pay_time', 'pay_method', 'update_datetime'])

        return record
```

### 4.3 支付方式枚举

```
PAY_METHOD_CHOICES = (
    ('mock_alipay', '模拟支付宝'),
    ('mock_wechat', '模拟微信支付'),
)
```

### 4.4 流水号格式

- 前缀: `MOCK_`
- 主体: UUID4 hex 前 24 位
- 示例: `MOCK_a1b2c3d4e5f6a7b8c9d0e1f2`
- 全局唯一（CharField unique 约束）

### 4.5 禁止事项

- 禁止调用 `requests.get/post` 访问任何外部 URL
- 禁止导入 `alipay`、`wechatpay` 等第三方支付 SDK
- 禁止在 PaymentRecord 中存储真实银行卡/账户信息
- 禁止发送真实短信/邮件通知（仅 `logger.info` 或 `print`）

---

## 5. 敏感词过滤（DFA 算法）

### 5.1 设计原则

- **位置**: `backend/dvadmin/bookshop/utils/sensitive_word.py`
- **算法**: DFA（Deterministic Finite Automaton）确定有穷自动机
- **词库**: 初始词库内置（约 200 词），可通过管理命令更新
- **性能**: O(n) 时间复杂度，n 为待检测文本长度

### 5.2 服务接口（伪代码）

```
class SensitiveWordFilter:
    _instance = None  # 单例

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._build_tree()
        return cls._instance

    def _build_tree(self):
        """从词库构建 DFA 树"""

    def contains(self, text) -> bool:
        """检测文本是否包含敏感词"""

    def filter(self, text, replace='*') -> str:
        """替换敏感词为指定字符"""
```

### 5.3 评价提交时的处理流程

1. 用户提交评价（rating + content + images）
2. 调用 `SensitiveWordFilter.get_instance().contains(content)`
3. 若含敏感词:
   - `is_sensitive = True`
   - `is_visible = False`（需管理员审核后才可见）
4. 若不含敏感词:
   - `is_sensitive = False`
   - `is_visible = True`（直接可见）
5. 图片中的文字不检测（仅检测 `content` 文本字段）

### 5.4 管理员审核评价可见性

- 管理员可设置 `is_visible = True`（人工审核通过后可见）
- 管理员可设置 `is_visible = False`（隐藏评价）
- 不修改 `is_sensitive` 标记（保留检测结果）

---

## 6. 权限规则

### 6.1 端点权限矩阵

| 端点组 | Admin | Merchant | Customer | 匿名 |
|--------|-------|----------|----------|------|
| admin/payment-records | ✅ | ❌ | ❌ | ❌ |
| admin/reviews | ✅ | ❌ | ❌ | ❌ |
| merchant/reviews | ❌ | ✅（仅自己图书） | ❌ | ❌ |
| customer/orders/{id}/pay | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/orders/{id}/review | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/reviews | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/collections | ❌ | ❌ | ✅（仅自己） | ❌ |
| customer/books/{id}/reviews | ❌ | ❌ | ✅(AllowAny) | ✅ |
| customer/books/{id}/collect | ❌ | ❌ | ✅（仅自己） | ❌ |

### 6.2 数据隔离规则

- **管理端 PaymentRecord**: `get_queryset()` 返回 `PaymentRecord.objects.all()`
- **管理端 Review**: `get_queryset()` 返回 `Review.objects.all()`（含 is_visible=False 的）
- **商家端 Review**: `get_queryset()` 过滤 `book__merchant=request.user.merchant`；MerchantPermission 校验
- **消费者端 Review**: `get_queryset()` 过滤 `user=request.user`；OwnerPermission 校验
- **消费者端 Collection**: `get_queryset()` 过滤 `user=request.user`；OwnerPermission 校验
- **公开图书评价**: `get_queryset()` 过滤 `is_visible=True AND book__status='on_sale'`

### 6.3 已购评价规则

**核心约束**: 只有已购买且订单状态为 `completed` 的用户才能评价。

校验逻辑:
1. 用户提交评价时，必须指定 `order_id` 和 `book_id`
2. 校验 `order.user_id == request.user.id`（订单归属）
3. 校验 `order.status == 'completed'`（订单已完成）
4. 校验 `OrderItem` 中存在 `book_id` 对应的记录（确实购买了该书）
5. 校验 `unique_together = ['order', 'book', 'user']`（同一订单同一书不可重复评价）

---

## 7. API 设计

### 7.1 消费者端 — 支付（复用订单接口）

支付 API 已在 [order.md](order.md) §7.3 中定义（`POST /api/bookshop/customer/orders/{id}/pay/`），内部调用 MockPaymentService。本节不重复定义，仅补充 PaymentRecord 查询接口。

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/customer/orders/{id}/payment/` | 查看自己订单的支付记录 | OwnerPermission |

### 7.2 管理端 — 支付记录 `/api/bookshop/admin/payment-records/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/payment-records/` | 全平台支付记录列表（分页、pay_method/order_no 筛选） | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/payment-records/{id}/` | 支付记录详情 | CustomPermission (Admin) |

### 7.3 消费者端 — 评价 `/api/bookshop/customer/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/bookshop/customer/orders/{id}/review/` | 提交评价 | OwnerPermission |
| GET | `/api/bookshop/customer/reviews/` | 我的评价列表 | OwnerPermission |
| GET | `/api/bookshop/customer/books/{id}/reviews/` | 图书评价列表（公开，仅 is_visible=True） | AllowAny |

#### POST 提交评价请求体

```json
{
  "book_id": 1,
  "rating": 5,
  "content": "非常好看，强烈推荐！",
  "images": ["url1", "url2"]
}
```

**处理流程**:
1. 校验订单归属 + 状态 completed + 包含该 book_id
2. 校验未重复评价（unique_together）
3. DFA 敏感词检测 content
4. 设置 is_sensitive / is_visible
5. 创建 Review
6. 返回评价详情

#### GET 图书评价列表查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `limit` | int | 每页数量 |
| `rating` | int | 按评分筛选（1-5） |
| `ordering` | string | 排序：`-create_datetime`（默认）/ `-rating` |

**返回数据**: 仅 `is_visible=True` 的评价；含 `merchant_reply`（如有）；不返回 `is_sensitive` 字段给用户端

### 7.4 商家端 — 评价 `/api/bookshop/merchant/reviews/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/reviews/` | 自己图书的评价列表 | MerchantPermission |
| POST | `/api/bookshop/merchant/reviews/{id}/reply/` | 回复评价 | MerchantPermission |

#### GET 商家端评价列表查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `limit` | int | 每页数量 |
| `book_id` | int | 按图书筛选 |
| `rating` | int | 按评分筛选 |
| `is_sensitive` | bool | 按敏感词标记筛选 |
| `has_reply` | bool | 是否已回复筛选 |

**返回数据**: 含所有评价（含 is_visible=False）；含 `is_sensitive` 标记

#### POST 回复评价请求体

```json
{
  "content": "string (必填, max=500)"
}
```

- 仅图书所属商家可回复
- 已回复的评价再次回复为更新（覆盖原回复）
- 回复时记录 `reply_time`

### 7.5 管理端 — 评价 `/api/bookshop/admin/reviews/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/reviews/` | 全平台评价列表 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/reviews/{id}/` | 评价详情 | CustomPermission (Admin) |
| PATCH | `/api/bookshop/admin/reviews/{id}/visibility/` | 设置评价可见性 | CustomPermission (Admin) |

#### PATCH 设置可见性请求体

```json
{
  "is_visible": true | false
}
```

### 7.6 消费者端 — 收藏 `/api/bookshop/customer/collections/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/customer/collections/` | 收藏列表（分页） | OwnerPermission |
| POST | `/api/bookshop/customer/books/{id}/collect/` | 收藏图书 | OwnerPermission |
| DELETE | `/api/bookshop/customer/books/{id}/collect/` | 取消收藏 | OwnerPermission |

#### POST 收藏

- 图书必须可售（`status='on_sale'`）
- 已收藏则返回 4000（幂等：不重复创建）
- `unique_together = ['user', 'book']` 防重复

#### DELETE 取消收藏

- 未收藏则返回 4000

---

## 8. 校验规则

### 8.1 支付校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 支付方式 | pay_method ∈ ('mock_alipay', 'mock_wechat') | 4000 | 支付方式不合法 |
| 订单状态 | order.status == 'pending' | 4000 | 订单状态不允许支付 |
| 重复支付 | order 无已有 PaymentRecord | 4000 | 订单已支付 |
| 订单归属 | order.user_id == request.user.id | 4003 | 无权操作此订单 |

### 8.2 评价校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 评分 | 1-5 整数 | 4000 | 评分必须在1-5之间 |
| 评价内容 | 非空, max=500 字符 | 4000 | 评价内容不能为空 |
| 评价图片 | JSON array, 最多 9 张 | 4000 | 评价图片最多9张 |
| 图片 URL 格式 | 以 /media/ 或 http(s):// 开头 | 4000 | 图片URL格式不正确 |
| 订单归属 | order.user_id == request.user.id | 4003 | 无权操作此订单 |
| 订单状态 | order.status == 'completed' | 4000 | 仅已完成订单可评价 |
| 已购校验 | OrderItem 中存在该 book_id | 4000 | 未购买该图书，无法评价 |
| 重复评价 | unique_together (order, book, user) | 4000 | 该图书已评价，不可重复评价 |

### 8.3 商家回复校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 回复内容 | 非空, max=500 | 4000 | 回复内容不能为空 |
| 评价归属 | review.book.merchant_id == request.user.merchant_id | 4003 | 无权回复此评价 |
| 商家状态 | merchant.status == 'approved' | 4003 | 商家未通过审核 |

### 8.4 收藏校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 图书可售 | book.status == 'on_sale' | 4000 | 该图书已下架 |
| 重复收藏 | unique_together (user, book) | 4000 | 已收藏该图书 |
| 未收藏取消 | Collection 存在 | 4000 | 未收藏该图书 |

---

## 9. 错误码定义

| 错误码 | 含义 | 本模块典型场景 |
|--------|------|----------------|
| 2000 | 成功 | — |
| 4000 | 业务错误 | 支付方式不合法、订单状态不允许、未购买不可评价、重复评价、已收藏、校验失败 |
| 4001 | 未认证 | JWT 缺失/过期 |
| 4003 | 无权限 | 操作他人订单/评价、商家回复非自己图书的评价、未审核商家操作 |

---

## 10. 测试策略

### 10.1 单元测试

| 测试类 | 测试用例 | 验证点 |
|--------|----------|--------|
| `TestPaymentRecordModel` | 创建支付记录 | 默认 status='success'; transaction_no 唯一 |
| `TestPaymentRecordModel` | OneToOne 约束 | 同一订单不可创建两条 PaymentRecord |
| `TestMockPaymentService` | 正常支付（mock_alipay） | PaymentRecord 创建; Order.status='paid' |
| `TestMockPaymentService` | 正常支付（mock_wechat） | PaymentRecord 创建; pay_method 正确 |
| `TestMockPaymentService` | 支付方式不合法 | 返回 4000 |
| `TestMockPaymentService` | 非 pending 订单支付 | 返回 4000 |
| `TestMockPaymentService` | 重复支付 | 返回 4000 |
| `TestMockPaymentService` | transaction_no 格式 | 以 MOCK_ 开头; 长度 <= 64 |
| `TestMockPaymentService` | pay_amount 等于 order.pay_amount | 金额一致 |
| `TestReviewModel` | 创建评价 | 默认 is_sensitive=False, is_visible=True |
| `TestReviewModel` | unique_together | 同一订单同一书同一用户重复评价返回 4000 |
| `TestReviewSubmit` | 正常提交评价（无敏感词） | is_sensitive=False, is_visible=True |
| `TestReviewSubmit` | 提交评价含敏感词 | is_sensitive=True, is_visible=False |
| `TestReviewSubmit` | 非 completed 订单评价 | 返回 4000 |
| `TestReviewSubmit` | 未购买图书评价 | 返回 4000 |
| `TestReviewSubmit` | 重复评价 | 返回 4000 |
| `TestReviewSubmit` | 评分越界（0/6） | 返回 4000 |
| `TestReviewSubmit` | 内容为空 | 返回 4000 |
| `TestReviewSubmit` | 图片超过 9 张 | 返回 4000 |
| `TestReviewSubmit` | 操作他人订单 | 返回 4003 |
| `TestSensitiveWordFilter` | 包含敏感词 | contains() 返回 True |
| `TestSensitiveWordFilter` | 不包含敏感词 | contains() 返回 False |
| `TestSensitiveWordFilter` | 替换敏感词 | filter() 返回替换后文本 |
| `TestSensitiveWordFilter` | 空文本 | 不报错 |
| `TestMerchantReply` | 商家回复评价 | merchant_reply 更新; reply_time 记录 |
| `TestMerchantReply` | 再次回复（更新） | merchant_reply 被覆盖; reply_time 更新 |
| `TestMerchantReply` | 非自己图书的评价回复 | 返回 4003 |
| `TestMerchantReply` | 回复内容为空 | 返回 4000 |
| `TestMerchantReviewList` | 商家查看自己图书评价 | 仅返回自己图书的评价 |
| `TestMerchantReviewList` | 商家查看其他商家评价 | 返回空列表或 4003 |
| `TestAdminReviewVisibility` | 管理员设置 is_visible=True | 评价对外可见 |
| `TestAdminReviewVisibility` | 管理员设置 is_visible=False | 评价对外不可见 |
| `TestPublicReviewList` | 用户端评价列表 | 仅返回 is_visible=True 的评价 |
| `TestPublicReviewList` | 不返回 is_sensitive 字段 | 用户端响应不含 is_sensitive |
| `TestCollectionModel` | 创建收藏 | user+book 唯一约束 |
| `TestCollectionModel` | 重复收藏 | 返回 4000 |
| `TestCollectionToggle` | 收藏图书 | Collection 创建 |
| `TestCollectionToggle` | 取消收藏 | Collection 删除 |
| `TestCollectionToggle` | 收藏下架图书 | 返回 4000 |
| `TestCollectionToggle` | 取消未收藏图书 | 返回 4000 |
| `TestCollectionToggle` | 操作他人收藏 | 返回 4003 |

### 10.2 集成测试场景

| 场景 | 步骤 | 验证 |
|------|------|------|
| 模拟支付全流程 | 下单→支付→查看支付记录 | PaymentRecord 创建; Order.status='paid'; 金额一致 |
| 评价全流程 | 下单→支付→发货→收货→完成→提交评价 | 评价创建; is_visible=True(无敏感词) |
| 敏感词评价 | 提交含敏感词评价→管理员审核→设为可见 | is_sensitive=True; is_visible 先 False 后 True |
| 商家回复 | 商家查看评价→回复→用户端可见回复 | merchant_reply 非空; 用户端评价详情含回复 |
| 收藏流程 | 浏览图书→收藏→收藏列表→取消收藏 | Collection CRUD 正确 |
| 数据隔离 | 商家 A 查看商家 B 的评价; 用户 A 操作用户 B 的收藏 | 返回 4003 |

---

## 11. 迁移与回滚

### 11.1 迁移批次

| 批次 | 内容 | 依赖 |
|------|------|------|
| 006 | 创建 `dvadmin_bookshop_payment_record` 表 | 004(Order) |
| 006 | 创建 `dvadmin_bookshop_review` 表 | 004(Order), 003(Book) |
| 006 | 创建 `dvadmin_bookshop_collection` 表 | 001(Users), 003(Book) |

**说明**: 三个表同属批次 006（与 PLAN 一致），均依赖 Order/Book/Users 表。

### 11.2 回滚策略

| 批次 | 回滚操作 |
|------|----------|
| 006 | DROP TABLE `dvadmin_bookshop_collection`; DROP TABLE `dvadmin_bookshop_review`; DROP TABLE `dvadmin_bookshop_payment_record` |

**回滚安全**:
- PaymentRecord 通过 `on_delete=CASCADE` 随 Order 删除
- Review 通过 `on_delete=CASCADE` 随 Order/Book 删除
- Collection 通过 `on_delete=CASCADE` 随 User/Book 删除
- 三个表之间无 FK 依赖，删除顺序不限

### 11.3 初始数据

- 通过管理命令或 SQL 插入初始敏感词库（约 200 词）
- 敏感词库存储位置建议: `backend/dvadmin/bookshop/fixtures/sensitive_words.txt`
- 加载方式: `SensitiveWordFilter` 初始化时读取文件构建 DFA 树

---

## 12. 前端集成要点

### 12.1 消费者端页面

- **支付页**: 订单详情页内嵌支付按钮（选择 mock_alipay / mock_wechat）
- **评价提交页**: `web/src/views/bookshop/customer/orders/review.vue` — 评分组件 + 文本框 + 图片上传
- **我的评价页**: `web/src/views/bookshop/customer/reviews.vue` — 评价列表
- **收藏页**: `web/src/views/bookshop/customer/collections.vue` — 收藏图书列表 + 取消收藏
- **图书评价区**: 图书详情页内嵌评价列表组件
- **API**: `web/src/api/bookshop/payment.ts`, `web/src/api/bookshop/review.ts`, `web/src/api/bookshop/collection.ts`

### 12.2 商家端页面

- **评价管理页**: `web/src/views/bookshop/merchant/reviews/index.vue` — 自己图书评价列表 + 回复
- **API**: `web/src/api/bookshop/review.ts`

### 12.3 管理端页面

- **评价管理页**: `web/src/views/bookshop/admin/reviews.vue` — 全平台评价列表 + 可见性控制
- **支付记录页**: `web/src/views/bookshop/admin/payment_records.vue` — 全平台支付记录
- **API**: `web/src/api/bookshop/review.ts`, `web/src/api/bookshop/payment.ts`

### 12.4 菜单注册

| 菜单 | component | 可见角色 |
|------|-----------|----------|
| 书城 > 我的收藏 | `bookshop/customer/collections` | 消费者 |
| 书城 > 我的评价 | `bookshop/customer/reviews` | 消费者 |
| 我的店铺 > 评价管理 | `bookshop/merchant/reviews/index` | 商家 |
| 书店管理 > 评价管理 | `bookshop/admin/reviews` | 管理员 |
| 书店管理 > 支付记录 | `bookshop/admin/payment_records` | 管理员 |

---

## 13. Settings 变更

| 变更 | 文件 | 说明 |
|------|------|------|
| 无 | — | 本模块无 settings 变更；Celery beat 配置已在 order.md 中定义 |

**无新增环境变量**。支付与评价模块使用现有 MySQL/Redis/JWT 配置。

---

## 14. 验收要点

- [x] PaymentRecord 模型字段、唯一约束、索引已定义
- [x] MockPaymentService 接口与流程已定义（模拟即成功、幂等、事务内调用）
- [x] 禁止真实第三方支付/短信/物流/邮件已明确
- [x] Review 模型字段、已购评价规则、unique_together 已定义
- [x] DFA 敏感词过滤服务接口与评价处理流程已定义
- [x] is_sensitive / is_visible 标记与管理员审核流程已定义
- [x] 商家回复规则（仅自己图书、覆盖更新）已定义
- [x] Collection 模型字段、唯一约束已定义
- [x] 三端权限矩阵与数据隔离规则已定义
- [x] 消费者端 API（支付查询 1 + 评价 3 + 收藏 3 = 7 端点）已定义
- [x] 商家端 API（评价 2 端点）已定义
- [x] 管理端 API（支付记录 2 + 评价 3 = 5 端点）已定义
- [x] 校验规则（4 类 20+ 条）已定义
- [x] 错误码已定义（2000/4000/4001/4003）
- [x] 单元测试（38 用例）与集成测试（6 场景）已定义
- [x] 迁移批次、回滚策略、初始数据已定义
- [x] 前端页面与菜单集成已定义
