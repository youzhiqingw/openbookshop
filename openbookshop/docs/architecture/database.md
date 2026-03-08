# 数据库设计文档

## ER 图概述

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │  Merchant   │    │    Book     │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │──┐ │ id (PK)     │◄──────│ merchant_id │
│ username    │  └──►│ user_id(FK) │    │ category_id │
│ email       │    │ store_name  │    │ title       │
│ role        │    │ status      │    │ price       │
│ is_vip      │    └─────────────┘    │ stock       │
└─────────────┘    └─────────────┘    └─────────────┘
       │
       │ ┌─────────────┐    ┌─────────────┐
       └────────►│   Order     │◄──────│ OrderItem   │
                 ├─────────────┤    ├─────────────┤
                 │ id (PK)     │    │ id (PK)     │
                 │ user_id(FK) │    │ order_id(FK)│
                 │ status      │    │ book_id(FK) │
                 │ total_amount│    │ quantity    │
                 └─────────────┘    └─────────────┘
```

## 核心表结构

### User (用户表)
扩展 Django AbstractUser

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| username | CharField | 用户名 |
| email | EmailField | 邮箱 |
| phone | CharField | 手机号 |
| avatar | ImageField | 头像 |
| role | CharField | 角色 (customer/merchant/admin) |
| is_vip | BooleanField | 是否VIP |
| vip_level | IntegerField | VIP等级 |
| points | IntegerField | 积分 |
| risk_score | IntegerField | 风险评分 |
| created_at | DateTimeField | 创建时间 |

### Merchant (商家表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| user | OneToOneField(User) | 关联用户 |
| store_name | CharField | 店铺名称 |
| logo | ImageField | 店铺Logo |
| description | TextField | 店铺描述 |
| status | CharField | 状态 (pending/approved/rejected) |
| business_license | CharField | 营业执照号 |
| address | CharField | 地址 |
| created_at | DateTimeField | 创建时间 |

### Category (分类表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| name | CharField | 分类名称 |
| parent | ForeignKey(self) | 父分类 (null为一级) |
| sort_order | IntegerField | 排序 |
| is_active | BooleanField | 是否启用 |

### Book (图书表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| merchant | ForeignKey(Merchant) | 所属商家 |
| category | ForeignKey(Category) | 分类 |
| title | CharField | 书名 |
| author | CharField | 作者 |
| isbn | CharField | ISBN |
| publisher | CharField | 出版社 |
| publish_date | DateField | 出版日期 |
| price | DecimalField | 售价 |
| original_price | DecimalField | 原价 |
| stock | IntegerField | 库存 |
| warning_stock | IntegerField | 预警库存 |
| sales_count | IntegerField | 销量 |
| cover_image | ImageField | 封面图 |
| description | TextField | 详情 |
| status | CharField | 状态 (on_sale/offline) |
| tags | JSONField | 标签 |
| created_at | DateTimeField | 创建时间 |

### Cart (购物车表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| user | ForeignKey(User) | 用户 |
| book | ForeignKey(Book) | 图书 |
| merchant | ForeignKey(Merchant) | 商家 (冗余) |
| quantity | IntegerField | 数量 |
| is_selected | BooleanField | 是否选中 |
| created_at | DateTimeField | 创建时间 |
| **约束**: unique_together (user, book) |

### Order (订单表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| order_no | CharField | 订单号 (唯一) |
| user | ForeignKey(User) | 用户 |
| merchant | ForeignKey(Merchant) | 商家 |
| status | CharField | 状态 |
| total_amount | DecimalField | 总金额 |
| discount_amount | DecimalField | 优惠金额 |
| pay_amount | DecimalField | 实付金额 |
| address_snapshot | JSONField | 地址快照 |
| remark | TextField | 备注 |
| pay_time | DateTimeField | 支付时间 |
| ship_time | DateTimeField | 发货时间 |
| receive_time | DateTimeField | 收货时间 |
| tracking_no | CharField | 物流单号 |
| created_at | DateTimeField | 创建时间 |
| **状态流转**: pending → paid → shipped → delivered → completed |

### OrderItem (订单项表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| order | ForeignKey(Order) | 订单 |
| book | ForeignKey(Book) | 图书 |
| quantity | IntegerField | 数量 |
| unit_price | DecimalField | 单价 |
| total_price | DecimalField | 总价 |
| is_reviewed | BooleanField | 是否评价 |

### Review (评价表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| order_item | OneToOneField(OrderItem) | 订单项 |
| user | ForeignKey(User) | 用户 |
| book | ForeignKey(Book) | 图书 |
| rating | IntegerField | 评分 (1-5) |
| content | TextField | 内容 |
| is_approved | BooleanField | 是否通过审核 |
| is_sensitive | BooleanField | 是否含敏感词 |
| reply | TextField | 商家回复 |
| created_at | DateTimeField | 创建时间 |

### Address (地址表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| user | ForeignKey(User) | 用户 |
| name | CharField | 收货人 |
| phone | CharField | 手机号 |
| province | CharField | 省 |
| city | CharField | 市 |
| district | CharField | 区 |
| detail | CharField | 详细地址 |
| is_default | BooleanField | 是否默认 |
| created_at | DateTimeField | 创建时间 |
| **约束**: 每个用户最多5条 (应用层限制) |

### Announcement (公告表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| title | CharField | 标题 |
| content | TextField | 内容 (富文本) |
| type | CharField | 类型 (announcement/help/agreement) |
| is_published | BooleanField | 是否发布 |
| publish_time | DateTimeField | 发布时间 |
| version | CharField | 版本号 |
| history_versions | JSONField | 历史版本 |
| created_by | ForeignKey(User) | 创建人 |
| created_at | DateTimeField | 创建时间 |

### OperationLog (操作日志表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| user | ForeignKey(User) | 操作用户 |
| action | CharField | 操作类型 |
| module | CharField | 模块 |
| detail | TextField | 详情 |
| ip_address | GenericIPAddressField | IP地址 |
| user_agent | TextField | 用户代理 |
| created_at | DateTimeField | 创建时间 |

### FinanceRecord (财务记录表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAutoField | 主键 |
| merchant | ForeignKey(Merchant) | 商家 |
| type | CharField | 类型 (settlement/withdrawal) |
| amount | DecimalField | 金额 |
| status | CharField | 状态 |
| related_orders | JSONField | 关联订单 |
| invoice_info | JSONField | 发票信息 |
| created_at | DateTimeField | 创建时间 |
| completed_at | DateTimeField | 完成时间 |

## 索引设计

```sql
-- 常用查询索引
CREATE INDEX idx_book_merchant ON books(merchant_id);
CREATE INDEX idx_book_category ON books(category_id);
CREATE INDEX idx_book_status ON books(status);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_merchant ON orders(merchant_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_review_book ON reviews(book_id);
CREATE INDEX idx_cart_user ON cart(user_id);
```

## 数据隔离策略

### 商家端查询 (必须)
```python
# 所有商家端视图必须添加过滤
queryset = Model.objects.filter(merchant=request.user.merchant)
```

### 管理端查询
```python
# 管理员可查看全部，但支持按商家筛选
queryset = Model.objects.all()
if merchant_id := request.query_params.get('merchant_id'):
    queryset = queryset.filter(merchant_id=merchant_id)
```