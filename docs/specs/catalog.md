# OpenBookShop 图书目录与库存预警 SPEC

**版本**: 2.0  
**日期**: 2026-05-16  
**依赖**: [foundation.md](foundation.md), [merchant.md](merchant.md)  
**目标**: 定义 Category/Book 模型、库存预警、三端 API（管理端全量/商家端隔离/用户端公开）、图片处理、校验/错误/测试/迁移策略。**不包含**实现代码。

---

## 1. 模块边界

### In Scope

- **管理端**: 两级分类 CRUD + 树形查询；全平台图书 CRUD + 上下架；全平台库存预警 + 全局阈值
- **商家端**: 自己图书 CRUD（数据隔离 merchant_id）；上下架/补货/单品预警值；自己库存预警
- **用户端（公开/AllowAny）**: 分类菜单树；图书列表/详情（仅可售图书）；搜索自动补全 + 热门搜索

### Out of Scope

- 订单/支付/购物车/地址/评价/收藏（其它模块）
- 入库/出库流水与复杂库存报表（后续迭代）

---

## 2. 通用约定

- **URL 前缀**: `/api/bookshop/`，尾斜杠（与 DRF Router 一致）
- **JWT Header**: `Authorization: JWT <token>`
- **分页**: `CustomPagination` — `{code:2000, page, limit, total, is_next, is_previous, data:[...], msg}`
- **成功详情**: `DetailResponse` — `{code:2000, data:{...}, msg}`
- **业务错误**: `CustomValidationError` → `{code:4000, data:null, msg}`
- **权限不足**: DRF 403 → `{code:4000, msg:"..."}`

---

## 3. 数据模型

### 3.1 Category（两级分类）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `name` | CharField(max_length=50) | NOT NULL | 分类名称 |
| `parent` | FK('self') | null, blank, on_delete=CASCADE | 父分类（null=一级） |
| `sort` | IntegerField | default=0 | 排序 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_category`  
**ordering**: `sort`, `id`  
**索引**: `parent_id`, `sort`

**两级约束**: `parent` 为空 → 一级分类；`parent` 非空且 `parent.parent` 为空 → 二级分类；禁止三级（`parent.parent` 非空时拒绝创建/修改）。

### 3.2 Book（图书）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | — |
| `isbn` | CharField(max_length=20) | NOT NULL, UNIQUE | ISBN 全局唯一 |
| `title` | CharField(max_length=200) | NOT NULL | 书名 |
| `author` | CharField(max_length=100) | NOT NULL | 作者 |
| `publisher` | CharField(max_length=100) | NOT NULL | 出版社 |
| `publish_date` | DateField | NOT NULL | 出版日期 |
| `category` | FK(Category) | NOT NULL, on_delete=PROTECT | 必须为二级分类 |
| `merchant` | FK(Merchant) | NOT NULL, on_delete=CASCADE | 商家数据隔离关键字段 |
| `price` | DecimalField(10,2) | NOT NULL, >=0 | 售价 |
| `original_price` | DecimalField(10,2) | NOT NULL, >=price | 原价 |
| `stock` | IntegerField | default=0, >=0 | 库存 |
| `warning_stock` | IntegerField | default=10, >=0 | 单品预警阈值 |
| `cover_image` | CharField(max_length=255) | NOT NULL | 封面图 URL |
| `images` | JSONField | default=[] | 详情图 URL 列表，最多 10 张 |
| `description` | TextField | NOT NULL | 图书简介 |
| `content` | TextField | null, blank | 目录/试读 |
| `status` | CharField(max_length=20) | choices: draft/on_sale/off_sale, default=draft | 上架状态 |
| `sales_count` | IntegerField | default=0 | 销量 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | — |
| `create_datetime` / `update_datetime` | DateTimeField (CoreModel) | auto | — |

**表名**: `dvadmin_bookshop_book`  
**ordering**: `-create_datetime`

**索引**:
- `(merchant_id, status)` — 商家端列表过滤
- `(category_id, status)` — 用户端分类筛选
- `sales_count` — 畅销榜排序（可选）
- `isbn` — unique

### 3.3 全局库存预警阈值

复用现有 `dvadmin_system_config`（SystemConfig 模型）。  
配置键: `bookshop.warning_stock_default`，类型: number，默认值: 10。  
读取: `dispatch.get_system_config_values("bookshop.warning_stock_default") or 10`

**预警判定**:
- `effective_warning_stock = max(book.warning_stock, global_warning_stock)`
- 触发条件: `book.stock <= effective_warning_stock`

---

## 4. API 设计

### 4.1 管理端 — 分类 `/api/bookshop/admin/categories/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/categories/` | 分类列表（分页，可按 parent_id/name 筛选） | CustomPermission (Admin) |
| POST | `/api/bookshop/admin/categories/` | 创建分类 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/categories/{id}/` | 分类详情 | CustomPermission (Admin) |
| PUT | `/api/bookshop/admin/categories/{id}/` | 更新分类 | CustomPermission (Admin) |
| DELETE | `/api/bookshop/admin/categories/{id}/` | 删除分类 | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/categories/tree/` | 两级分类树 | CustomPermission (Admin) |

### 4.2 管理端 — 图书 `/api/bookshop/admin/books/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/books/` | 全平台图书列表（分页、status/merchant_id/category_id/q 筛选） | CustomPermission (Admin) |
| POST | `/api/bookshop/admin/books/` | 创建图书（需指定 merchant_id） | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/books/{id}/` | 图书详情 | CustomPermission (Admin) |
| PUT | `/api/bookshop/admin/books/{id}/` | 更新图书 | CustomPermission (Admin) |
| DELETE | `/api/bookshop/admin/books/{id}/` | 删除图书 | CustomPermission (Admin) |
| PATCH | `/api/bookshop/admin/books/{id}/status/` | 上下架 `{status:"on_sale"|"off_sale"}` | CustomPermission (Admin) |

### 4.3 管理端 — 库存预警

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/stock-warnings/` | 全平台预警列表（分页、merchant_id/category_id/q 筛选） | CustomPermission (Admin) |
| GET | `/api/bookshop/admin/stock-warning-setting/` | 全局预警阈值 | CustomPermission (Admin) |
| PUT | `/api/bookshop/admin/stock-warning-setting/` | 设置全局预警阈值 `{global_warning_stock: int>=0}` | CustomPermission (Admin) |

### 4.4 商家端 — 分类（只读）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/categories/tree/` | 两级分类树 | MerchantPermission |

### 4.5 商家端 — 图书 `/api/bookshop/merchant/books/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/books/` | 自己的图书列表（分页、status/category_id/q 筛选） | MerchantPermission |
| POST | `/api/bookshop/merchant/books/` | 创建图书（merchant_id 自动取 request.user.merchant_id） | MerchantPermission |
| GET | `/api/bookshop/merchant/books/{id}/` | 图书详情（仅自己） | MerchantPermission |
| PUT | `/api/bookshop/merchant/books/{id}/` | 更新图书（仅自己） | MerchantPermission |
| DELETE | `/api/bookshop/merchant/books/{id}/` | 删除图书（仅自己） | MerchantPermission |
| PATCH | `/api/bookshop/merchant/books/{id}/status/` | 上下架 `{status:"on_sale"|"off_sale"}` | MerchantPermission |
| POST | `/api/bookshop/merchant/books/{id}/restock/` | 补货 `{quantity: int>0}` → stock += quantity | MerchantPermission |
| PATCH | `/api/bookshop/merchant/books/{id}/warning-stock/` | 设置单品预警值 `{warning_stock: int>=0}` | MerchantPermission |

### 4.6 商家端 — 库存预警

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/stock-warnings/` | 自己的预警列表（分页、category_id/q 筛选） | MerchantPermission |

### 4.7 用户端（公开）— `/api/bookshop/customer/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/customer/categories/tree/` | 两级分类树 | AllowAny |
| GET | `/api/bookshop/customer/books/` | 图书列表（分页、category_id/q/排序） | AllowAny |
| GET | `/api/bookshop/customer/books/{id}/` | 图书详情 | AllowAny |
| GET | `/api/bookshop/customer/search/suggest/` | 搜索自动补全 + 热门搜索 `{q?}` | AllowAny |

**用户端可见性过滤**（必须）:
- `book.status == "on_sale"`
- `book.merchant.status == "approved"`
- `book.merchant.is_open == True`

**排序选项**: `-sales_count`（畅销）, `-publish_date`（新书）, `price` / `-price`（价格）

**搜索规则**:
- `q` 缺省或长度 < 2: 仅返回 `hot_keywords`（销量 Top N 的 book.title）
- `q` 长度 >= 2: 按 title/author/isbn 模糊匹配返回 suggestions（前 10 条）+ hot_keywords

---

## 5. 图片与文件处理

### 5.1 图片上传

- **复用现有文件上传接口**: `dvadmin/system/views/file_list.py` — POST `/api/system/file/upload/`
- Book 的 `cover_image` 和 `images` 字段存储的是上传后返回的 URL 字符串
- 商家/管理员上传图片时，先调用文件上传接口获取 URL，再传入 Book 创建/更新接口

### 5.2 图片字段规则

| 字段 | 格式 | 约束 |
|------|------|------|
| `cover_image` | 单个 URL string | 必填，max=255 |
| `images` | JSON array of URL strings | 默认 []，最多 10 张 |

### 5.3 图片验证

- URL 格式校验（以 `/media/` 开头或完整 http(s) URL）
- 不做文件大小/格式校验（由上传接口负责）
- 详情图超过 10 张时返回 4000

---

## 6. 校验规则

### 6.1 分类校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 分类名称 | 非空, max=50 | 4000 | 分类名称不能为空 |
| 父分类不存在 | parent_id 指向不存在的分类 | 4000 | 父分类不存在 |
| 禁止三级 | parent_id 指向的分类已是二级（其 parent 非空） | 4000 | 仅允许两级分类 |
| 删除—有子分类 | 分类下存在 children | 4000 | 存在子分类不可删除 |
| 删除—有图书 | 分类下存在 Book | 4000 | 分类下存在图书不可删除 |

### 6.2 图书校验（管理端/商家端共用）

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| ISBN | 非空, regex `^[0-9-]{10,20}$`, 全局唯一 | 4000 | ISBN已存在 / ISBN格式不正确 |
| 书名 | 非空, max=200 | 4000 | 书名不能为空 |
| 作者 | 非空, max=100 | 4000 | 作者不能为空 |
| 出版社 | 非空, max=100 | 4000 | 出版社不能为空 |
| 出版日期 | 非空, 有效日期 | 4000 | 出版日期不合法 |
| 分类 | 必须存在且为二级分类（category.parent 非空） | 4000 | 分类不存在 / 仅允许二级分类 |
| 售价 | 非空, Decimal(10,2), >=0 | 4000 | 售价格式不正确 |
| 原价 | 非空, Decimal(10,2), >=price | 4000 | 原价不能低于售价 |
| 库存 | >=0 | 4000 | 库存不能为负 |
| 预警阈值 | >=0 | 4000 | 预警阈值不能为负 |
| 封面图 | 非空, max=255 | 4000 | 封面图不能为空 |
| 详情图 | JSON array, 最多 10 张 | 4000 | 详情图最多10张 |
| 商家端禁止传 merchant_id | 商家端请求体含 merchant_id 字段 → 忽略或拒绝 | 4000 | 无权指定商家 |

### 6.3 上架条件校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 商家状态 | `merchant.status == "approved"` | 4000 | 商家未通过审核，不可上架 |
| 封面图 | `cover_image` 非空 | 4000 | 上架图书必须有封面图 |
| 价格 | `price` 与 `original_price` 合法 | 4000 | 价格信息不完整 |

### 6.4 补货/预警值校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 补货数量 | quantity > 0 | 4000 | 补货数量必须大于0 |
| 预警值 | warning_stock >= 0 | 4000 | 预警阈值不能为负 |
| 全局阈值下限（可选） | warning_stock >= global_warning_stock | 4000 | 预警阈值不能低于全局阈值 |

### 6.5 搜索校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| q 长度 | max=50 | 4000 | 搜索关键词长度不能超过50 |

---

## 7. 权限规则

### 7.1 端点权限矩阵

| 端点组 | Admin | Merchant | Customer/匿名 |
|--------|-------|----------|---------------|
| admin/categories | ✅ | ❌ | ❌ |
| admin/books | ✅ | ❌ | ❌ |
| admin/stock-warnings | ✅ | ❌ | ❌ |
| merchant/categories (只读) | ❌ | ✅ | ❌ |
| merchant/books | ❌ | ✅（仅自己） | ❌ |
| merchant/stock-warnings | ❌ | ✅（仅自己） | ❌ |
| customer/* | ✅（可访问） | ✅（可访问） | ✅ (AllowAny) |

### 7.2 对象级数据隔离

- **商家端 Book**: `get_queryset()` 过滤 `merchant=request.user.merchant`；`MerchantPermission.has_object_permission()` 校验 `obj.merchant_id == request.user.merchant_id`
- **用户端 Book**: `get_queryset()` 过滤 `status="on_sale" AND merchant__status="approved" AND merchant__is_open=True`
- **管理端 Book**: 无隔离，全平台数据

### 7.3 MerchantPermission 规则

同 [merchant.md](merchant.md) §3.3 — user_type=2 且 merchant 存在且 status=approved。商家端图书/分类/预警 ViewSet 均使用此权限。

---

## 8. 错误码

| 错误码 | 含义 | 典型场景 |
|--------|------|----------|
| 2000 | 成功 | — |
| 4000 | 业务错误 | 校验失败、ISBN 重复、分类下有图书不可删除、上架条件不满足 |
| 4001 | 未认证 | JWT 缺失/过期 |
| 4003 | 无权限 | 商家访问他人图书、非管理员访问管理端接口 |

---

## 9. 测试策略

### 9.1 单元测试

| 测试类 | 测试用例 | 验证点 |
|--------|----------|--------|
| `TestCategoryModel` | 创建一级/二级分类 | parent 为空/非空正确 |
| `TestCategoryModel` | 禁止三级分类 | 返回 4000 |
| `TestCategoryModel` | 删除有子分类的分类 | 返回 4000 |
| `TestCategoryModel` | 删除有图书的分类 | 返回 4000 |
| `TestCategoryModel` | 分类树查询 | 返回两级嵌套结构 |
| `TestBookModel` | 创建图书验证默认值 | status=draft, stock=0, sales_count=0 |
| `TestBookModel` | ISBN 唯一约束 | 重复 ISBN 返回 4000 |
| `TestBookModel` | original_price < price | 返回 4000 |
| `TestBookModel` | 分类必须为二级 | 一级分类返回 4000 |
| `TestBookModel` | 上架条件校验 | merchant 未审核返回 4000; 缺封面返回 4000 |
| `TestBookStatus` | draft → on_sale | 上架成功 |
| `TestBookStatus` | on_sale → off_sale | 下架成功 |
| `TestBookStatus` | draft → off_sale | 返回 4000（只能先上架再下架，或允许直接下架） |
| `TestMerchantBookIsolation` | 商家 A 创建图书 | merchant_id 自动设为 A |
| `TestMerchantBookIsolation` | 商家 A 访问商家 B 图书 | 返回 4003 |
| `TestMerchantBookIsolation` | 商家 A 更新商家 B 图书 | 返回 4003 |
| `TestMerchantBookIsolation` | 商家 A 删除商家 B 图书 | 返回 4003 |
| `TestMerchantBookIsolation` | 商家端请求体含 merchant_id | 忽略或返回 4000 |
| `TestBookRestock` | 补货 quantity=10 | stock += 10 |
| `TestBookRestock` | 补货 quantity=0 | 返回 4000 |
| `TestBookRestock` | 补货 quantity=-1 | 返回 4000 |
| `TestBookWarningStock` | 更新 warning_stock=5 | 更新成功 |
| `TestBookWarningStock` | warning_stock=-1 | 返回 4000 |
| `TestStockWarning` | global_warning_stock 缺省回退 10 | 阈值正确 |
| `TestStockWarning` | effective_warning_stock = max(book, global) | 逻辑正确 |
| `TestStockWarning` | book.stock <= effective 时出现在预警列表 | 列表包含该书 |
| `TestCustomerBookVisibility` | 仅返回 on_sale + approved + is_open 的图书 | 下架/未审核/关闭商家图书不可见 |
| `TestCustomerBookVisibility` | 匿名访问图书列表 | 返回 2000 |
| `TestSearchSuggest` | q 长度 < 2 | 仅返回 hot_keywords |
| `TestSearchSuggest` | q 长度 >= 2 | 返回 suggestions + hot_keywords |
| `TestSearchSuggest` | q 长度 > 50 | 返回 4000 |

### 9.2 集成测试场景

| 场景 | 步骤 | 验证 |
|------|------|------|
| 管理员创建分类与图书 | 创建一级→二级分类→创建图书→上架 | 用户端可见该图书 |
| 商家管理自己的图书 | 商家创建→上架→补货→调预警值 | 操作成功；其他商家不可见 |
| 库存预警触发 | 设置全局阈值=5→创建图书 stock=3, warning_stock=10 | 出现在管理端和商家端预警列表 |
| 用户端搜索 | 创建多本图书→搜索关键词 | suggestions 返回匹配结果；不返回下架图书 |

---

## 10. 迁移与回滚

### 10.1 迁移批次

| 批次 | 内容 | 依赖 |
|------|------|------|
| 003 | 创建 `dvadmin_bookshop_category` 表 | 无 |
| 003 | 创建 `dvadmin_bookshop_book` 表 | 002(Merchant), 003(Category) |

**说明**: Category 和 Book 在同一批次 003 中创建（Book FK 依赖 Category 和 Merchant）。

### 10.2 回滚策略

| 批次 | 回滚操作 |
|------|----------|
| 003 | 先删 `dvadmin_bookshop_book`（有 FK），再删 `dvadmin_bookshop_category` |

**回滚安全**: Book 表通过 `merchant` FK 关联 Merchant（on_delete=CASCADE），删除 Book 表不影响 Merchant 表。Category 通过 `on_delete=PROTECT` 保护，需先删除所有 Book 引用才能删除 Category。

### 10.3 初始数据

- 通过 `init` 命令或 SQL 脚本插入 `SystemConfig` 父节点 `bookshop` 和子节点 `bookshop.warning_stock_default = 10`
- 预置常见图书分类（可选，如: 文学/小说/散文、科技/计算机/工程 等）

---

## 11. 前端集成要点

### 11.1 管理端页面

- **分类管理页**: `web/src/views/bookshop/admin/category.vue` — 两级分类树 + CRUD
- **图书管理页**: `web/src/views/bookshop/admin/books.vue` — 全平台图书列表 + CRUD + 上下架
- **库存预警页**: `web/src/views/bookshop/admin/stock_warning.vue` — 预警列表 + 全局阈值设置
- **API**: `web/src/api/bookshop/book.ts`, `web/src/api/bookshop/statistics.ts`

### 11.2 商家端页面

- **图书管理页**: `web/src/views/bookshop/merchant/books/index.vue` — 自己的图书 + CRUD + 补货
- **API**: `web/src/api/bookshop/book.ts`（复用，不同端点）

### 11.3 用户端页面

- **首页/分类页/详情页**: `web/src/views/bookshop/customer/home.vue`, `category.vue`, `book.vue`
- **API**: `web/src/api/bookshop/book.ts`

### 11.4 菜单注册

| 菜单 | component | 可见角色 |
|------|-----------|----------|
| 书店管理 > 分类管理 | `bookshop/admin/category` | 管理员 |
| 书店管理 > 图书管理 | `bookshop/admin/books` | 管理员 |
| 书店管理 > 库存预警 | `bookshop/admin/stock_warning` | 管理员 |
| 我的店铺 > 图书管理 | `bookshop/merchant/books/index` | 商家 |
| 书城 > 分类浏览 | `bookshop/customer/category` | 消费者/匿名 |

---

## 12. 验收要点

- [x] Category 两级模型与约束已定义
- [x] Book 模型字段、索引、库存预警字段已定义
- [x] 全局预警阈值机制（SystemConfig）已定义
- [x] 管理端全量 CRUD + 上下架 API 已定义
- [x] 商家端隔离 CRUD + 补货 + 预警值 API 已定义
- [x] 用户端公开浏览 + 搜索建议 API 已定义
- [x] 用户端可见性过滤规则已定义
- [x] 图片处理方案（复用上传接口 + URL 存储）已定义
- [x] 校验规则（分类/图书/上架/补货/搜索）已定义
- [x] 权限矩阵与数据隔离规则已定义
- [x] 测试清单（30+ 用例 + 4 集成场景）已定义
- [x] 迁移批次与回滚策略已定义
- [x] 前端页面与菜单集成已定义
