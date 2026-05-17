# OpenBookShop 统计与预警模块 SPEC

**版本**: 1.0
**日期**: 2026-05-16
**依赖**: [foundation.md](foundation.md), [merchant.md](merchant.md), [catalog.md](catalog.md), [order.md](order.md), [payment-review.md](payment-review.md)
**目标**: 定义管理员统计仪表盘数据源与 API；库存预警机制（全局阈值 + 图书级阈值 + 三级预警）；API、权限、校验、错误、测试、迁移与回滚。**不包含**实现代码。

---

## 1. 模块边界

### In Scope

- **统计仪表盘**: 管理员全平台运营数据统计（总览、趋势、分布、排行）
- **库存预警**: 管理员全平台预警 + 商家自店预警；三级预警（严重/警告/提醒）；全局阈值 + 图书级阈值覆盖

### Out of Scope

- 商家结算/提现统计（P2）
- 用户行为分析/推荐算法（P2）
- 实时推送通知（P2）
- 导出 Excel/CSV 报表（P1）

---

## 2. 通用约定

- **URL 前缀**: `/api/bookshop/`，尾斜杠
- **JWT Header**: `Authorization: JWT <token>`
- **分页**: `CustomPagination` — `{code:2000, page, limit, total, is_next, is_previous, data:[...], msg}`
- **成功详情**: `DetailResponse` — `{code:2000, data:{...}, msg}`
- **业务错误**: `CustomValidationError` → `{code:4000, data:null, msg}`
- **金额**: `DecimalField(max_digits=10, decimal_places=2)`，禁止 float
- **统计时间**: 所有时间范围筛选使用 Django `timezone.now()`，默认东八区

---

## 3. 库存预警机制

### 3.1 预警判定规则

**有效预警阈值** (`effective_warning_stock`):
```
effective_warning_stock = book.warning_stock
if effective_warning_stock is None or effective_warning_stock <= 0:
    effective_warning_stock = global_threshold  # 从 SystemConfig 读取
```

**预警触发条件**:
```
book.stock <= effective_warning_stock
```

### 3.2 全局阈值

- **存储位置**: `dvadmin_system.SystemConfig`（key-value 模式）
- **配置 key**: `bookshop_warning_stock_threshold`
- **默认值**: 10
- **类型**: 正整数
- **管理端可修改**: 通过统计 API 的 `warning_threshold` 端点设置

**读取方式**:
```python
from dvadmin.system.models import SystemConfig
config = SystemConfig.objects.filter(key='bookshop_warning_stock_threshold').first()
global_threshold = int(config.value) if config else 10
```

### 3.3 图书级阈值覆盖

- `Book.warning_stock` 字段（已在 catalog.md §3.2 定义）
- `null` 或 `0`: 使用全局阈值
- `>0`: 使用图书级阈值（覆盖全局）
- 仅商家或管理员可设置

### 3.4 预警等级

| 等级 | 条件 | 标签色 | 说明 |
|------|------|--------|------|
| 严重 (critical) | `stock == 0` | #e74c3c (红) | 已售罄 |
| 警告 (warning) | `0 < stock <= effective_threshold * 0.5` | #e67e22 (橙) | 库存紧张 |
| 提醒 (info) | `effective_threshold * 0.5 < stock <= effective_threshold` | #f1c40f (黄) | 库存偏低 |

**计算伪代码**:
```python
def get_warning_level(book):
    threshold = book.warning_stock or global_threshold
    if book.stock == 0:
        return 'critical'
    elif book.stock <= threshold * 0.5:
        return 'warning'
    elif book.stock <= threshold:
        return 'info'
    return None  # 无预警
```

### 3.5 预警列表过滤

| 参数 | 类型 | 说明 |
|------|------|------|
| `level` | string | 预警等级筛选: critical / warning / info |
| `merchant_id` | int | 按商家筛选（管理员可用） |
| `category_id` | int | 按分类筛选 |
| `is_warning` | bool | 是否仅显示预警图书（默认 True） |

---

## 4. 统计数据设计

### 4.1 总览数据 (Overview)

| 指标 | 来源 | 说明 |
|------|------|------|
| `total_books` | Book.objects.count() | 全平台图书总数 |
| `on_sale_books` | Book.objects.filter(status='on_sale').count() | 在售图书数 |
| `total_merchants` | Merchant.objects.count() | 商家总数 |
| `approved_merchants` | Merchant.objects.filter(status='approved').count() | 已通过商家数 |
| `total_orders` | Order.objects.count() | 订单总数 |
| `pending_orders` | Order.objects.filter(status='pending').count() | 待支付订单数 |
| `total_sales_amount` | sum(Order.objects.filter(status__in=['paid','shipped','received','completed']).values('pay_amount')) | 总销售额 |
| `total_users` | Users.objects.filter(user_type=3).count() | 消费者总数 |
| `warning_count` | 预警图书数 | 库存预警数 |

### 4.2 趋势数据 (Trend)

**时间维度**: 近 30 天，按天聚合

| 指标 | 来源 | 说明 |
|------|------|------|
| `date` | — | 日期 (YYYY-MM-DD) |
| `order_count` | 按 create_datetime__date 分组 count | 每日订单数 |
| `sales_amount` | 按 create_datetime__date 分组 sum(pay_amount) | 每日销售额 |
| `new_users` | Users 按 date_joined__date 分组 count | 每日新用户 |

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `days` | int | 天数（默认 30，最大 90） |
| `start_date` | string | 起始日期 (YYYY-MM-DD)，与 days 互斥 |
| `end_date` | string | 结束日期 (YYYY-MM-DD)，与 days 互斥 |

### 4.3 分类分布 (Category Distribution)

| 指标 | 来源 | 说明 |
|------|------|------|
| `category_id` | — | 分类 ID |
| `category_name` | Category.name | 分类名称 |
| `book_count` | 按 category 分组 count | 该分类图书数 |
| `sales_count` | OrderItem 按 book__category 分组 sum(quantity) | 该分类销量 |

### 4.4 商家排行 (Merchant Ranking)

| 指标 | 来源 | 说明 |
|------|------|------|
| `merchant_id` | — | 商家 ID |
| `merchant_name` | Merchant.name | 商家名称 |
| `book_count` | 按 merchant 分组 count | 图书数量 |
| `order_count` | OrderItem 按 book__merchant 分组 count(distinct order_id) | 订单数 |
| `sales_amount` | OrderItem 按 book__merchant 分组 sum(price * quantity) | 销售额 |

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `limit` | int | 排行数量（默认 10，最大 50） |
| `order_by` | string | 排序字段: sales_amount / order_count / book_count（默认 sales_amount） |

---

## 5. API 设计

### 5.1 管理端 — 统计 `/api/bookshop/admin/statistics/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/statistics/overview/` | 总览数据 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/statistics/trend/` | 趋势数据 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/statistics/category-distribution/` | 分类分布 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/statistics/merchant-ranking/` | 商家排行 | CustomPermission (Admin) |

#### GET overview 响应示例

```json
{
  "code": 2000,
  "data": {
    "total_books": 1200,
    "on_sale_books": 980,
    "total_merchants": 15,
    "approved_merchants": 12,
    "total_orders": 5680,
    "pending_orders": 23,
    "total_sales_amount": "128560.50",
    "total_users": 3200,
    "warning_count": 45
  },
  "msg": "success"
}
```

#### GET trend 响应示例

```json
{
  "code": 2000,
  "data": {
    "dates": ["2026-04-16", "2026-04-17", "..."],
    "order_count": [120, 135, "..."],
    "sales_amount": ["5600.00", "6200.50", "..."],
    "new_users": [45, 52, "..."]
  },
  "msg": "success"
}
```

#### GET category-distribution 响应示例

```json
{
  "code": 2000,
  "data": [
    {
      "category_id": 1,
      "category_name": "文学小说",
      "book_count": 320,
      "sales_count": 1580
    }
  ],
  "msg": "success"
}
```

#### GET merchant-ranking 响应示例

```json
{
  "code": 2000,
  "data": [
    {
      "merchant_id": 1,
      "merchant_name": "优书阁",
      "book_count": 85,
      "order_count": 1200,
      "sales_amount": "45600.00"
    }
  ],
  "msg": "success"
}
```

### 5.2 管理端 — 预警 `/api/bookshop/admin/warnings/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/warnings/` | 全平台预警图书列表（分页） | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/warnings/threshold/` | 获取全局预警阈值 | CustomPermission (Admin) |
| PUT | `/api/bookshop/admin/warnings/threshold/` | 设置全局预警阈值 | CustomPermission (Admin) |

#### GET 预警图书列表

**查询参数**: 见 §3.5 + 通用分页参数

**响应数据**: 每条记录包含:

| 字段 | 类型 | 说明 |
|------|------|------|
| `book_id` | int | 图书 ID |
| `book_name` | string | 图书名称 |
| `isbn` | string | ISBN |
| `cover` | string | 封面图 URL |
| `stock` | int | 当前库存 |
| `warning_stock` | int/null | 图书级阈值（null 表示使用全局） |
| `effective_warning_stock` | int | 有效预警阈值 |
| `warning_level` | string | 预警等级: critical / warning / info |
| `merchant_id` | int | 商家 ID |
| `merchant_name` | string | 商家名称 |
| `category_name` | string | 分类名称 |

#### PUT 设置全局阈值请求体

```json
{
  "threshold": 15
}
```

- threshold 必须 > 0 整数
- 写入 `SystemConfig(key='bookshop_warning_stock_threshold', value=str(threshold))`
- 若 key 已存在则更新 value

### 5.3 商家端 — 预警 `/api/bookshop/merchant/warnings/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/warnings/` | 自己店铺预警图书列表 | MerchantPermission |

**响应数据**: 与管理端预警列表相同结构，但自动过滤 `merchant=request.user.merchant`

---

## 6. 权限规则

### 6.1 端点权限矩阵

| 端点组 | Admin | Merchant | Customer | 匿名 |
|--------|-------|----------|----------|------|
| admin/statistics/* | ✅ | ❌ | ❌ | ❌ |
| admin/warnings/* | ✅ | ❌ | ❌ | ❌ |
| merchant/warnings/ | ❌ | ✅（仅自己店铺） | ❌ | ❌ |

### 6.2 数据隔离规则

- **管理端统计**: 无数据隔离，全平台聚合
- **管理端预警**: 无数据隔离，全平台预警图书
- **商家端预警**: `get_queryset()` 过滤 `merchant=request.user.merchant`；MerchantPermission 校验

### 6.3 统计查询性能

- 总览数据: 建议使用 `aggregate()` + `Count()` / `Sum()` 单次查询
- 趋势数据: 使用 `TruncDate` + `values()` + `annotate()` 按天聚合
- 分类分布: 使用 `values('category')` + `annotate()` 分组聚合
- 商家排行: 使用 `values('merchant')` + `annotate()` 分组聚合 + `order_by()` 排序

**性能要求**: 统计 API 响应时间应 < 2 秒（10 万级订单数据下）

---

## 7. 校验规则

### 7.1 统计查询校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| days 范围 | 1-90 整数 | 4000 | 天数必须在1-90之间 |
| start_date 格式 | YYYY-MM-DD | 4000 | 日期格式不正确 |
| end_date 格式 | YYYY-MM-DD | 4000 | 日期格式不正确 |
| 日期范围 | start_date <= end_date | 4000 | 起始日期不能晚于结束日期 |
| limit 范围 | 1-50 整数 | 4000 | 排行数量必须在1-50之间 |
| order_by 枚举 | sales_amount / order_count / book_count | 4000 | 排序字段不合法 |

### 7.2 预警阈值校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| threshold 类型 | 正整数 | 4000 | 预警阈值必须为正整数 |
| threshold 范围 | 1-99999 | 4000 | 预警阈值必须在1-99999之间 |

### 7.3 预警列表校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| level 枚举 | critical / warning / info | 4000 | 预警等级不合法 |
| merchant_id 存在 | Merchant 存在 | 4000 | 商家不存在 |
| category_id 存在 | Category 存在 | 4000 | 分类不存在 |

---

## 8. 错误码定义

| 错误码 | 含义 | 本模块典型场景 |
|--------|------|----------------|
| 2000 | 成功 | — |
| 4000 | 业务错误 | 参数不合法、阈值校验失败 |
| 4001 | 未认证 | JWT 缺失/过期 |
| 4003 | 无权限 | 商家访问非自己店铺预警 |

---

## 9. 测试策略

### 9.1 单元测试

| 测试类 | 测试用例 | 验证点 |
|--------|----------|--------|
| `TestWarningLevel` | stock=0 | 返回 'critical' |
| `TestWarningLevel` | stock=1, threshold=10 (0 < 1 <= 5) | 返回 'warning' |
| `TestWarningLevel` | stock=7, threshold=10 (5 < 7 <= 10) | 返回 'info' |
| `TestWarningLevel` | stock=15, threshold=10 (15 > 10) | 返回 None（无预警） |
| `TestWarningLevel` | book.warning_stock=20 覆盖全局阈值=10 | 使用 20 作为阈值 |
| `TestWarningLevel` | book.warning_stock=0 使用全局阈值 | 使用全局阈值 |
| `TestWarningLevel` | book.warning_stock=None 使用全局阈值 | 使用全局阈值 |
| `TestGlobalThreshold` | 读取默认全局阈值 | 返回 10 |
| `TestGlobalThreshold` | 设置全局阈值为 15 | SystemConfig value 更新 |
| `TestGlobalThreshold` | 设置阈值为 0 | 返回 4000 |
| `TestGlobalThreshold` | 设置阈值为负数 | 返回 4000 |
| `TestGlobalThreshold` | 设置阈值为非整数 | 返回 4000 |
| `TestAdminStatisticsOverview` | 正常请求 | 返回所有总览指标 |
| `TestAdminStatisticsOverview` | 金额精度 | DecimalField 不丢失精度 |
| `TestAdminStatisticsTrend` | 默认 30 天 | 返回 30 天数据 |
| `TestAdminStatisticsTrend` | days=7 | 返回 7 天数据 |
| `TestAdminStatisticsTrend` | days=100 | 返回 4000 |
| `TestAdminStatisticsTrend` | 自定义日期范围 | 正确筛选 |
| `TestAdminStatisticsTrend` | start_date > end_date | 返回 4000 |
| `TestAdminCategoryDistribution` | 正常请求 | 返回各分类图书数和销量 |
| `TestAdminCategoryDistribution` | 无图书分类 | 返回空列表 |
| `TestAdminMerchantRanking` | 默认按销售额排序 | 正确排序 |
| `TestAdminMerchantRanking` | order_by=order_count | 按订单数排序 |
| `TestAdminMerchantRanking` | limit=5 | 返回前 5 名 |
| `TestAdminWarnings` | 正常请求 | 仅返回预警图书 |
| `TestAdminWarnings` | level=critical | 仅返回售罄图书 |
| `TestAdminWarnings` | merchant_id 筛选 | 仅返回指定商家预警 |
| `TestMerchantWarnings` | 商家查看自己预警 | 仅自己店铺图书 |
| `TestMerchantWarnings` | 商家查看其他商家预警 | 返回空列表 |

### 9.2 集成测试场景

| 场景 | 步骤 | 验证 |
|------|------|------|
| 统计全流程 | 创建商家/图书/订单→查看总览→查看趋势→查看分布→查看排行 | 数据一致 |
| 预警触发 | 图书库存从 20 降至 5→查看预警列表 | 预警等级从 None 变为 info/warning |
| 全局阈值变更 | 默认阈值 10→修改为 20→重新查看预警 | 预警范围扩大 |
| 数据隔离 | 商家 A 查看预警→仅见自己图书 | 无其他商家数据 |

### 9.3 性能测试

| 场景 | 数据量 | 预期响应时间 |
|------|--------|-------------|
| 总览统计 | 10 万订单 | < 2s |
| 趋势数据 | 10 万订单 / 30 天 | < 2s |
| 分类分布 | 10 万订单 | < 2s |
| 商家排行 | 10 万订单 | < 2s |
| 预警列表 | 1 万图书 | < 1s |

---

## 10. 迁移与回滚

### 10.1 迁移批次

本模块**无新增数据库表**。所有数据来源于已有的 Book、Order、OrderItem、Merchant、Category、Users 等模型。

**初始数据**:

| 数据 | 方式 | 说明 |
|------|------|------|
| `SystemConfig(key='bookshop_warning_stock_threshold', value='10')` | SQL 或管理命令 | 全局预警阈值默认值 |

### 10.2 回滚策略

| 操作 | 说明 |
|------|------|
| 删除 SystemConfig 记录 | `DELETE FROM dvadmin_system_systemconfig WHERE key='bookshop_warning_stock_threshold'` |
| 无表删除 | 本模块不创建表 |

---

## 11. 前端集成要点

### 11.1 管理端页面

- **统计仪表盘**: `web/src/views/bookshop/admin/dashboard/index.vue`
  - ECharts 图表: 趋势折线图 + 分类饼图 + 商家排行柱状图
  - 顶部卡片: 总览数据 4 宫格
  - API: `web/src/api/bookshop/statistics.ts`

- **库存预警**: `web/src/views/bookshop/admin/stock_warning/index.vue`
  - FastCrud 表格: 预警图书列表 + 等级标签 + 全局阈值设置弹窗
  - API: `web/src/api/bookshop/book.ts`（预警端点在 book API 中或独立）

### 11.2 商家端页面

- **库存预警**: 商家图书管理页内嵌预警提示或独立预警 tab
  - API: `web/src/api/bookshop/book.ts`

### 11.3 菜单注册

| 菜单 | component | 可见角色 |
|------|-----------|----------|
| 书店管理 > 数据统计 | `bookshop/admin/dashboard/index` | 管理员 |
| 书店管理 > 库存预警 | `bookshop/admin/stock_warning/index` | 管理员 |

---

## 12. Settings 变更

| 变更 | 文件 | 说明 |
|------|------|------|
| 无 | — | 本模块无 settings 变更 |

**无新增环境变量**。统计与预警模块使用现有 MySQL/JWT 配置。

---

## 13. 验收要点

- [x] 预警机制三级定义已明确（critical/warning/info + 判定条件）
- [x] 全局阈值 + 图书级阈值覆盖机制已定义
- [x] SystemConfig 存储全局阈值方式已定义
- [x] 统计总览 9 项指标已定义
- [x] 趋势数据 3 项指标 + 时间筛选参数已定义
- [x] 分类分布 + 商家排行数据结构已定义
- [x] 管理端 API（统计 4 + 预警 3 = 7 端点）已定义
- [x] 商家端 API（预警 1 端点）已定义
- [x] 权限矩阵与数据隔离规则已定义
- [x] 校验规则（3 类 8+ 条）已定义
- [x] 错误码已定义（2000/4000/4001/4003）
- [x] 单元测试（24 用例）+ 集成测试（4 场景）+ 性能测试已定义
- [x] 迁移（无新表）+ 回滚策略已定义
- [x] 前端页面与菜单集成已定义

