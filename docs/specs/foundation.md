# OpenBookShop 基础 SPEC

**版本**: 1.0  
**日期**: 2026-05-16  
**目标**: 定义 OpenBookShop 书店模块的基础架构（后端 Django app、URL 前缀、角色策略、权限基类、菜单/RBAC 集成）。**不包含**实现代码与数据库迁移。

---

## 1. 项目上下文与约束

### 1.1 现有架构事实

- **认证**: Django REST Framework + SimpleJWT，`AUTH_HEADER_TYPES = ("JWT",)` — header 格式 `JWT <token>`
- **用户模型**: `backend/dvadmin/system/models.py` 中的 `Users`
  - `user_type` 字段: `((0,"后台用户"),(1,"前台用户"))`（现有值）
  - `role` 字段: `ManyToManyField(Role)` — 细粒度 RBAC
  - `current_role` 字段: `ForeignKey(Role)` — 角色切换
  - `AUTH_USER_MODEL = "system.Users"`
- **权限基类**: `dvadmin.utils.permission.CustomPermission`（超级用户直通 → `RoleMenuButtonPermission` 检查）
- **视图基类**: `dvadmin.utils.viewsets.CustomModelViewSet`（自带分页、异常处理、导入导出、日志中间件、`DataLevelPermissionMargeFilter`）
- **表前缀**: `dvadmin_`（`table_prefix = "dvadmin_"`）
- **金额**: 所有金额使用 `DecimalField(max_digits=10, decimal_places=2)`，禁用 float

### 1.2 角色优先级

**管理员 > 商家 > 消费者**

- 管理员（Admin）: 全平台管控、商家审核、数据统计
- 商家（Merchant）: 仅自有店铺数据，需审核通过
- 消费者（Customer）: 仅个人数据

---

## 2. user_type 扩展策略（与 Role 协同）

### 2.1 扩展定义

在 `Users` 模型中扩展 `user_type` choices（保留 0/1 不变，新增 2/3）:

```
0 = 管理员   （原“后台用户”）
1 = 前台用户 （旧数据兼容，新注册消费者建议用 3）
2 = 商家
3 = 消费者
```

**原则**: `user_type` 用于**粗粒度身份与布局判定**，`role` 保持用于**细粒度 RBAC 权限与按钮控制**，二者共存不替代。

### 2.2 商家与消费者关联

- 为 `Users` 新增 `merchant` 字段（OneToOne，`null=True, blank=True`）
  - 仅 `user_type=2` 时有效
  - 管理员/消费者 `merchant=None`
- 商家审核通过后设置 `user_type=2` 并建立关联
- 用户注册默认 `user_type=3`（或保持 1），不关联 merchant

### 2.3 角色映射建议（非强制）

- 商家账号 RBAC `role` 应包含 key="merchant" 的角色
- 消费者账号 RBAC `role` 可包含 key="customer" 的角色
- `current_role` 暂不启用多角色切换，预留字段

---

## 3. backend/dvadmin/bookshop 结构设计

### 3.1 目录结构（不创建文件，仅定义）

```
backend/dvadmin/bookshop/
├── __init__.py
├── apps.py
├── urls.py                     # /api/bookshop/ 路由
├── models/
│   ├── __init__.py
│   ├── merchant.py             # Merchant
│   ├── category.py             # Category（两级）
│   ├── book.py                 # Book（含库存、封面、详情）
│   ├── order.py                # Order + OrderItem
│   ├── cart.py                 # CartItem
│   ├── address.py              # Address（收货地址，最多5个）
│   ├── review.py               # Review（含敏感词、商家回复）
│   ├── collection.py           # Collection（收藏）
│   └── payment.py              # PaymentRecord（模拟支付）
├── serializers/
│   ├── __init__.py
│   ├── merchant.py
│   ├── book.py
│   ├── order.py
│   ├── cart.py
│   ├── address.py
│   ├── review.py
│   └── payment.py
├── views/
│   ├── __init__.py
│   ├── merchant.py             # 商家信息、审核相关
│   ├── book.py                 # 图书管理（分管理端/商家端/用户端视图）
│   ├── order.py                # 订单（含创建、支付回调、发货、退款）
│   ├── cart.py                 # 购物车
│   ├── address.py              # 地址
│   ├── review.py               # 评价
│   ├── collection.py           # 收藏
│   ├── payment.py              # 模拟支付
│   ├── admin/
│   │   ├── merchant_audit.py   # 管理端：商家审核
│   │   ├── statistics.py       # 管理端：统计/预警
│   │   └── order_monitor.py    # 管理端：订单监控
│   └── permissions.py          # 见 4.1-4.2
├── tasks.py                    # Celery 定时任务（超时释放）
├── fixtures/
│   └── init_menu.json          # 菜单初始化数据
└── utils/
    └── sensitive_word.py       # DFA 敏感词过滤
```

### 3.2 Django 配置

- 将 `"dvadmin.bookshop"` 加入 `settings.py` 的 `INSTALLED_APPS`
- 在 `application/urls.py` 中注册路由：  
  `path("api/bookshop/", include("dvadmin.bookshop.urls"))`

---

## 4. URL 前缀与 API 命名

**统一前缀**: `/api/bookshop/`

### 4.1 三端 API 划分

| 用途 | 前缀 | 示例 |
|------|------|------|
| 管理端（全平台） | `/api/bookshop/admin/` | `GET /api/bookshop/admin/merchants` |
| 商家端（自有店铺） | `/api/bookshop/merchant/` | `GET /api/bookshop/merchant/books` |
| 用户端（消费者） | `/api/bookshop/`（无前缀子路径） | `GET /api/bookshop/books` |

### 4.2 典型端点（示意）

- 管理端
  - `GET /api/bookshop/admin/merchants` — 商家列表
  - `POST /api/bookshop/admin/merchants/{id}/audit` — 审核
  - `GET /api/bookshop/admin/statistics` — 统计
- 商家端
  - `GET /api/bookshop/merchant/profile` — 商家信息
  - `GET/POST /api/bookshop/merchant/books` — 自己的图书
  - `GET /api/bookshop/merchant/orders` — 自己的订单
- 用户端
  - `GET /api/bookshop/books` — 图书列表
  - `POST /api/bookshop/cart` — 加购
  - `POST /api/bookshop/orders` — 下单
  - `POST /api/bookshop/orders/{id}/pay` — 模拟支付
  - `POST /api/bookshop/orders/{id}/refund` — 申请退款

### 4.3 响应格式

与 `service.ts` 兼容：

```json
{
  "code": 2000,
  "msg": "success",
  "data": { ... }
}
```

错误码沿用系统规范（4000/4003/4004 等）。

---

## 5. 用户角色策略与数据隔离

### 5.1 身份判定优先级

```
if user.is_superuser → 管理员（全权限）
elif user.user_type == 2 → 商家（需 merchant 关联且 status=approved）
elif user.user_type == 3（或 1） → 消费者
```

### 5.2 数据隔离规则

| 角色 | 允许范围 | 隔离要求 |
|------|----------|----------|
| 管理员 | 全平台所有商家与用户数据 | 无隔离 |
| 商家 | 仅 `merchant_id == request.user.merchant_id` 的数据 | 所有查询须带 `merchant` 过滤；对象级权限校验 |
| 消费者 | 仅 `user_id == request.user.id` 的数据 | 所有查询须带 `user` 过滤；对象级权限校验 |

### 5.3 商家审核状态约束

- 商家账号需 `merchant.status == "approved"` 才能访问商家端数据接口
- `MerchantPermission.has_permission()` 校验 `user_type==2` 与 `merchant.status`
- 审核中/拒绝/禁用状态返回 4003（无权限）

### 5.4 控制器基类建议（不写实现）

- 商家端 `ViewSet` 应在 `get_queryset()` 中自动过滤 `merchant=request.user.merchant`
- 消费者端 `ViewSet` 应在 `get_queryset()` 中自动过滤 `user=request.user`
- 管理端 `ViewSet` 不过滤（全平台）

---

## 6. 权限基类与 RBAC/菜单集成

### 6.1 权限类定义（位置：`bookshop/permissions.py`）

**MerchantPermission**（对象级）
- `has_permission`: 校验 `user_type==2` 且 `merchant` 存在且 `status==approved`
- `has_object_permission`: 校验 `obj.merchant_id == request.user.merchant_id`

**OwnerPermission**（对象级）
- `has_object_permission`: 校验 `obj.user_id == request.user.id`

### 6.2 ViewSet 权限组合（示意）

- 管理端 ViewSet: `permission_classes = [CustomPermission]`（管理员直通）
- 商家端 ViewSet: `permission_classes = [CustomPermission, MerchantPermission]`
- 用户端 ViewSet（如地址/购物车/订单）: `permission_classes = [CustomPermission, OwnerPermission]`
- 公共只读接口（如图书列表/分类）: `permission_classes = [AllowAny]` 或 `CustomPermission`（按需）

### 6.3 菜单与 RBAC 集成策略

#### 现有菜单机制

- `dvadmin_system_menu` + `dvadmin_system_menu_button` + `dvadmin_role_menu_button_permission`
- `backEnd.ts` 通过 `menuApi.getSystemMenu()` 获取菜单 → `handleMenu()` 注册动态路由
- `dynamicViewsModules` 使用 `import.meta.glob('../views/**/*.{vue,tsx}')` 自动发现组件

#### bookshop 菜单注册方式

1. 在 `bookshop/fixtures/init_menu.json` 中定义菜单与按钮（含 `component` 字段）
2. 通过管理命令或 SQL 脚本插入 `dvadmin_system_menu`（不修改现有初始化代码）
3. `RoleMenuButtonPermission` 按角色控制菜单/按钮可见性（复用现有 RBAC）

#### 三端菜单划分

- **管理端菜单**（角色=管理员可见）  
  component 示例: `bookshop/admin/books` → 对应 `views/bookshop/admin/books/index.vue`

- **商家端菜单**（角色=商家可见）  
  component 示例: `bookshop/merchant/books/index` → `views/bookshop/merchant/books/index.vue`  
  父级菜单 component 可指向 `bookshop/merchant/layout.vue`（含 MerchantLayout）

- **用户端菜单**（角色=消费者可见，或对匿名开放）  
  component 示例: `bookshop/customer/home` → `views/bookshop/customer/home.vue`  
  父级菜单 component 可指向 `bookshop/customer/layout.vue`（含 CustomerLayout + 导航栏/页脚）

#### 前端布局切换实现要点（非实现代码）

- 管理端沿用现有布局（`layout/routerView/parent.vue`）
- 商家端与用户端页面通过菜单父级的 `component` 指定布局组件（`MerchantLayout.vue` / `CustomerLayout.vue`）
- 动态路由由后端菜单返回，前端按 `component` 字段映射到 `views/` 相应文件

### 6.4 按钮权限集成

- 商家端/管理端的敏感操作按钮（如下架、发货、审核）通过 `RoleMenuButtonPermission` 控制
- 前端使用 `v-auth="'bookshop:merchant:edit'"` 风格指令（依现有 `v-auth` 实现）
- 后端在 `perform_create`/`perform_update` 中可二次校验对象权限（如商家只能操作自己商品）

---

## 7. 关键业务规则集成点

### 7.1 库存扣减与释放

- **扣减时机**: 下单时（`Order` 创建）使用 `select_for_update()` 在事务中扣减 `Book.stock`
- **释放时机**: 订单状态 `pending` 且 `created_at` 超时 30 分钟，由 Celery beat 任务 `cancel_timeout_orders` 扫描并释放库存
- **事务要求**: 所有库存变更需在 `@transaction.atomic` 内进行，失败回滚

### 7.2 模拟支付

- 仅模拟（禁止真实第三方）
- `PaymentRecord` 记录流水，`pay_method ∈ {mock_alipay, mock_wechat}`
- 支付回调为内部状态变更接口（需幂等）

### 7.3 评价与敏感词

- `Review` 含 `is_sensitive` 与 `is_visible`
- 敏感词过滤使用 DFA 算法（`utils/sensitive_word.py`）
- 默认 `is_visible=False`，需审核通过后显示

### 7.4 地址限制

- 每用户最多 5 个地址（序列化器层校验）
- 下单时从 `Address` 复制收货信息到 `Order`（快照）

---

## 8. 前端项目集成规范（单 Vue 项目）

- **非三端独立项目**，而是单 Vue 项目通过后端菜单动态注册路由
- **目录**: `web/src/views/bookshop/{admin,merchant,customer}/...`
- **API 层**: `web/src/api/bookshop/{merchant,book,order,cart,review,payment,address,statistics}.ts`（统一使用 `service.ts`，code 2000=成功）
- **状态管理**: `web/src/stores/bookshop/{cart,user}.ts`
- **布局组件**: `web/src/views/bookshop/merchant/layout.vue`（MerchantLayout）、`web/src/views/bookshop/customer/layout.vue`（CustomerLayout）

---

## 9. 迁移与兼容性约束

- **Users 扩展**: 仅扩展 `user_type` choices 与新增 `merchant` FK，不修改已有字段
- **旧数据保护**: `user_type=0/1` 数据保持不变
- **表命名**: 全量使用 `dvadmin_bookshop_*`
- **金额**: `DecimalField(max_digits=10, decimal_places=2)`
- **API 格式**: 与 `service.ts` 一致（code 2000）
- **不修改现有 RBAC**: `CustomPermission` 与 `RoleMenuButtonPermission` 保持原样，新增权限类作为补充

---

## 10. 验收要点（本 SPEC 完成标志）

- [x] 明确 `backend/dvadmin/bookshop` 目录结构与模块职责
- [x] 定义 `/api/bookshop/` 前缀与三端 API 划分
- [x] 明确 `user_type` 扩展方案与 `role` 协同策略
- [x] 定义 `MerchantPermission` 与 `OwnerPermission` 基类及使用方式
- [x] 明确菜单/RBAC 集成方案（菜单数据 + 前端布局映射）
- [x] 列出关键业务规则（库存、支付、评价、地址）的集成要求
- [x] 明确前端单项目集成方式（目录、API、状态管理、布局）
- [x] 列出迁移与兼容性约束

---

**备注**: 本 SPEC 仅描述基础架构与集成点，**不包含**具体实现代码、接口详细参数、数据库迁移语句与测试用例。实现阶段将依据此 SPEC 产出相应模块并补充详细设计。