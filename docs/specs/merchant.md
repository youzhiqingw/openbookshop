# OpenBookShop 商家模块 SPEC

**版本**: 2.0  
**日期**: 2026-05-16  
**依赖**: [foundation.md](foundation.md)  
**目标**: 定义 Merchant 模型字段、状态流转、审核 API、用户绑定、权限规则、校验/错误/测试/迁移策略。**不包含**实现代码与数据库迁移语句。

---

## 1. Merchant 模型定义

### 1.1 字段清单

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField (CoreModel) | PK | 继承自 CoreModel |
| `name` | CharField(max_length=100) | NOT NULL, 全局唯一 | 店铺名称 |
| `logo` | CharField(max_length=255) | null, blank | 店铺 Logo URL（复用系统文件上传） |
| `description` | TextField | null, blank | 店铺描述 |
| `status` | CharField(max_length=20) | NOT NULL, default='pending' | 商家状态，见 1.2 |
| `contact_name` | CharField(max_length=50) | NOT NULL | 联系人姓名 |
| `contact_phone` | CharField(max_length=20) | NOT NULL, regex `^1[3-9]\d{9}$` | 联系电话 |
| `contact_email` | EmailField | NOT NULL | 联系邮箱 |
| `address` | CharField(max_length=255) | NOT NULL | 店铺地址 |
| `is_open` | BooleanField | default=True | 营业状态（商家自行切换） |
| `reject_reason` | CharField(max_length=500) | null, blank | 审核拒绝原因 |
| `creator` / `modifier` | FK(Users) (CoreModel) | null, blank | 创建/修改人 |
| `create_datetime` | DateTimeField (CoreModel) | auto_now_add | 创建时间 |
| `update_datetime` | DateTimeField (CoreModel) | auto_now | 更新时间 |

**表名**: `dvadmin_bookshop_merchant`  
**基类**: `CoreModel`  
**ordering**: `-create_datetime`  
**索引**: `status`（筛选索引）, `name`（唯一索引）

### 1.2 状态枚举与流转

```
STATUS_CHOICES = (
    ('pending',  '待审核'),
    ('approved', '已通过'),
    ('rejected', '已拒绝'),
    ('disabled', '已禁用'),
)
```

**状态流转图**:

```
  ┌─────────┐
  │ pending │ ← 初始状态（创建商家申请）
  └────┬────┘
       │
  ┌────┴────────────────┐
  │                     │
  ▼                     ▼
┌──────────┐       ┌──────────┐
│ approved │       │ rejected │
└────┬─────┘       └────┬─────┘
     │                  │
     │  管理员禁用       │  修改信息后重新提交
     ▼                  ▼
┌──────────┐       ┌─────────┐
│ disabled │──────→│ pending │
└──────────┘  解禁  └─────────┘
```

**合法转换**:

| 从 → 到 | 触发者 | 条件 |
|----------|--------|------|
| `pending` → `approved` | 管理员 | 审核通过 |
| `pending` → `rejected` | 管理员 | 审核拒绝，需填写 `reject_reason` |
| `approved` → `disabled` | 管理员 | 禁用商家（违规等） |
| `disabled` → `approved` | 管理员 | 解禁 |
| `rejected` → `pending` | 商家用户 | 修改信息后重新提交（PUT profile 自动触发） |
| 任何 → 任何（非上表） | **禁止** | — |

### 1.3 与 Users 的绑定关系

- `Users.merchant` = OneToOneField(`bookshop.Merchant`, null=True, blank=True, on_delete=SET_NULL, related_name='user')
- **绑定时机**: 管理员审核通过时，在 `@transaction.atomic` 内执行：
  1. `merchant.status = 'approved'; merchant.save()`
  2. `user.user_type = 2; user.merchant = merchant; user.save()`
- **审核拒绝**: `merchant.status = 'rejected'`，`user.merchant = None`（不保留关联），`user.user_type` 不变
- **禁用**: `merchant.status = 'disabled'`，不改变 `user_type`，`user.merchant` 保留指向
- **解禁**: `merchant.status = 'approved'`，恢复访问

**一个用户只能绑定一个商家；一个商家只能绑定一个用户。**

---

## 2. API 设计

### 2.1 管理端 — `/api/bookshop/admin/merchants/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/admin/merchants/` | 商家列表（分页、状态筛选） | 管理员 (CustomPermission) |
| GET | `/api/bookshop/admin/merchants/{id}/` | 商家详情 | 管理员 |
| POST | `/api/bookshop/admin/merchants/{id}/audit/` | 审核商家（通过/拒绝） | 管理员 + RBAC `bookshop:admin:merchant:audit` |
| POST | `/api/bookshop/admin/merchants/{id}/disable/` | 禁用商家 | 管理员 + RBAC `bookshop:admin:merchant:disable` |
| POST | `/api/bookshop/admin/merchants/{id}/enable/` | 解禁商家 | 管理员 + RBAC `bookshop:admin:merchant:disable` |

#### POST `.../audit/` 请求体

```json
{
  "action": "approve" | "reject",
  "reject_reason": "string (action=reject 时必填, max=500)"
}
```

**响应**: `{code: 2000, data: {id, status: "approved"|"rejected"}, msg: "审核成功"}`

#### POST `.../disable/` 请求体

```json
{
  "reason": "string (可选, 禁用原因)"
}
```

#### GET `.../` 查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `limit` | int | 每页数量 |
| `status` | string | 状态筛选（pending/approved/rejected/disabled） |
| `name__icontains` | string | 店铺名模糊搜索 |
| `contact_name__icontains` | string | 联系人模糊搜索 |

### 2.2 商家端 — `/api/bookshop/merchant/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/bookshop/merchant/profile/` | 获取自己的商家信息 | 商家 (MerchantPermission) |
| PUT | `/api/bookshop/merchant/profile/` | 更新商家信息 | 商家 (MerchantPermission, status=approved) |
| POST | `/api/bookshop/merchant/apply/` | 提交商家入驻申请 | 已登录用户（user_type=3 或 1，无 merchant 关联） |

#### POST `.../apply/` 请求体（入驻申请）

```json
{
  "name": "string (必填, max=100)",
  "description": "string (可选)",
  "contact_name": "string (必填, max=50)",
  "contact_phone": "string (必填, max=20, regex:^1[3-9]\\d{9}$)",
  "contact_email": "string (必填, email格式)",
  "address": "string (必填, max=255)",
  "logo": "string (可选, URL)"
}
```

**响应**: `{code: 2000, data: {id, name, status: "pending", ...}, msg: "申请提交成功"}`

#### PUT `.../profile/` 可更新字段

- `status=approved` 时可更新: `description`, `logo`, `is_open`
- `status=approved` 时**不可更新**: `name`, `contact_name`, `contact_phone`, `contact_email`, `address`
- `status=approved` 时**不可更新**: `status`, `reject_reason`（任何状态都不可通过商家端修改）
- `status=rejected` 时: PUT 更新信息后自动将 `status` 设为 `pending`（重新提交审核）

---

## 3. 权限规则

### 3.1 管理端权限

| 接口 | 权限要求 |
|------|----------|
| 商家列表/详情 | `CustomPermission`（is_superuser 直通，或 RBAC 角色含商家管理菜单） |
| 审核商家 | `CustomPermission` + RBAC 按钮权限 `bookshop:admin:merchant:audit` |
| 禁用/解禁 | `CustomPermission` + RBAC 按钮权限 `bookshop:admin:merchant:disable` |

### 3.2 商家端权限

| 接口 | 权限要求 |
|------|----------|
| 获取 profile | `MerchantPermission`（user_type=2, merchant 存在, status=approved） |
| 更新 profile | `MerchantPermission`（同上） |
| 入驻申请 | `IsAuthenticated`（任何已登录用户均可申请，排除 user_type=0 管理员） |

### 3.3 MerchantPermission 详细规则

**has_permission(request, view)**:
1. `request.user.is_authenticated` → 否则 401
2. `request.user.is_superuser` → 直通
3. `request.user.user_type == 2` → 否则 4003
4. `request.user.merchant is not None` → 否则 4003
5. `request.user.merchant.status == 'approved'` → 否则 4003
6. 通过

**has_object_permission(request, view, obj)**:
1. `request.user.is_superuser` → 直通
2. `obj` 有 `merchant` 属性 → `obj.merchant_id == request.user.merchant_id`
3. `obj` 本身是 Merchant → `obj.pk == request.user.merchant_id`
4. 不匹配 → 4003

### 3.4 数据隔离

- 管理端 ViewSet: `get_queryset()` 返回 `Merchant.objects.all()`（全平台）
- 商家端 ViewSet: `get_queryset()` 返回 `Merchant.objects.filter(pk=request.user.merchant_id)`（仅自身）

---

## 4. 校验规则

### 4.1 创建/入驻校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 店铺名称 | 非空, max=100 | 4000 | 店铺名称不能为空 |
| 店铺名称唯一 | `name` 全平台唯一 | 4000 | 该店铺名称已存在 |
| 联系人 | 非空, max=50 | 4000 | 联系人不能为空 |
| 联系电话 | 非空, 手机号格式 `^1[3-9]\d{9}$` | 4000 | 联系电话格式不正确 |
| 联系邮箱 | 非空, email 格式 | 4000 | 联系邮箱格式不正确 |
| 店铺地址 | 非空, max=255 | 4000 | 店铺地址不能为空 |
| 用户已有商家 | `user.merchant is not None` 且 status ∈ (pending, approved) | 4000 | 已有待审核或已通过的商家申请 |
| 管理员申请 | `user.user_type == 0` | 4003 | 管理员不能申请商家 |

### 4.2 审核校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 目标商家状态 | audit 仅对 `status=pending` 生效 | 4000 | 该商家不在待审核状态 |
| reject 原因 | `action=reject` 时 `reject_reason` 非空 | 4000 | 拒绝原因不能为空 |
| 审核者身份 | 非管理员/无审核权限 | 4003 | 无审核权限 |

### 4.3 禁用/解禁校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 禁用目标 | `status=approved` | 4000 | 只能禁用已通过的商家 |
| 解禁目标 | `status=disabled` | 4000 | 只能解禁已禁用的商家 |

### 4.4 更新 profile 校验

| 校验项 | 规则 | 错误码 | 错误信息 |
|--------|------|--------|----------|
| 商家状态非 approved | `status ∉ (approved, rejected)` 时禁止修改 | 4003 | 商家未通过审核，无法修改店铺信息 |
| 审核通过后不可改核心字段 | `name/contact_name/contact_phone/contact_email/address` 不可修改 | 4000 | 审核通过后不可修改店铺名称和联系人信息 |
| 不可修改 status/reject_reason | 任何状态下商家端不可修改这两个字段 | 4000 | 无权修改此字段 |
| rejected 重新提交 | 更新信息后自动 status→pending | — | — |

---

## 5. 错误码定义

| 错误码 | 含义 | 商家模块典型场景 |
|--------|------|-----------------|
| 2000 | 成功 | — |
| 4000 | 业务错误 | 校验失败、状态不允许操作、重复申请 |
| 4001 | 未认证 | JWT 缺失/过期 |
| 4003 | 无权限 | 非管理员审核、非本人商家数据、商家未审核通过 |

**错误响应格式**（遵循 `CustomValidationError` + `CustomExceptionHandler`）:

```json
{
  "code": 4000,
  "msg": "该店铺名称已存在",
  "data": null
}
```

---

## 6. 测试策略

### 6.1 单元测试清单

| 测试类 | 测试用例 | 验证点 |
|--------|----------|--------|
| `TestMerchantModel` | 创建 Merchant 验证默认值 | status=pending, is_open=True |
| `TestMerchantModel` | name 唯一约束 | 重复 name 抛异常 |
| `TestMerchantApply` | 已登录用户申请商家 | Merchant 创建成功; status=pending; user.merchant 关联 |
| `TestMerchantApply` | 重复申请（已有 pending） | 返回 4000 |
| `TestMerchantApply` | 重复申请（已有 approved） | 返回 4000 |
| `TestMerchantApply` | 管理员申请商家 | 返回 4003 |
| `TestMerchantApply` | 名称重复 | 返回 4000 |
| `TestMerchantApply` | 必填字段缺失 | 返回 4000 |
| `TestMerchantApply` | 手机号格式错误 | 返回 4000 |
| `TestMerchantAudit` | 管理员审核通过 | status=approved; user.user_type=2; user.merchant 绑定 |
| `TestMerchantAudit` | 管理员审核拒绝 | status=rejected; reject_reason 非空; user_type 不变; user.merchant=None |
| `TestMerchantAudit` | 审核拒绝无原因 | 返回 4000 |
| `TestMerchantAudit` | 非管理员审核 | 返回 4003 |
| `TestMerchantAudit` | 审核非 pending 状态 | 返回 4000 |
| `TestMerchantAudit` | 审核通过事务原子性 | 模拟异常，merchant.status 与 user.user_type 同时回滚 |
| `TestMerchantDisable` | 禁用已通过商家 | status=disabled |
| `TestMerchantDisable` | 禁用非 approved 状态 | 返回 4000 |
| `TestMerchantEnable` | 解禁已禁用商家 | status=approved |
| `TestMerchantEnable` | 解禁非 disabled 状态 | 返回 4000 |
| `TestMerchantProfile` | 商家获取自己 profile | 返回正确数据 |
| `TestMerchantProfile` | 未审核商家获取 profile | 返回 4003（MerchantPermission 拦截） |
| `TestMerchantProfile` | 商家更新 profile（description, logo, is_open） | 字段更新成功 |
| `TestMerchantProfile` | approved 商家更新 name | 返回 4000 |
| `TestMerchantProfile` | 被拒绝商家更新后重新提交 | status 变为 pending |
| `TestMerchantPermission` | 商家 A 访问商家 B 数据 | 返回 4003 |
| `TestMerchantPermission` | status=disabled 时访问商家端接口 | 返回 4003 |
| `TestMerchantPermission` | status=rejected 时访问商家端接口 | 返回 4003 |
| `TestMerchantPermission` | status=pending 时访问商家端接口 | 返回 4003 |

### 6.2 集成测试场景

| 场景 | 步骤 | 验证 |
|------|------|------|
| 完整入驻流程 | 注册 → 申请 → 管理员审核通过 | user_type=2; merchant 绑定; 可访问商家端 |
| 拒绝后重新申请 | 申请 → 拒绝 → 修改信息 → 重新 pending → 通过 | status 流转正确; 第二次审核后 user_type=2 |
| 禁用后解禁 | 通过 → 禁用 → 禁用期间访问失败 → 解禁 → 访问恢复 | disabled 时 4003; 解禁后正常 |
| 审核原子性 | 审核通过时 DB 异常 | merchant.status 与 user.user_type/merchant 要么同时更新要么回滚 |

### 6.3 API 集成测试

| 测试 | 验证 |
|------|------|
| GET `/api/bookshop/admin/merchants` — 管理员 | 返回 2000 + 分页数据 |
| GET `/api/bookshop/admin/merchants` — 商家 | 返回 403 |
| POST `.../audit` approve | 返回 2000 |
| POST `.../audit` reject | 返回 2000 |
| POST `/api/bookshop/merchant/apply` — 新用户 | 返回 2000 |
| POST `/api/bookshop/merchant/apply` — 已有 merchant | 返回 4000 |
| GET `/api/bookshop/merchant/profile` | 自己的 merchant 返回 2000 |
| PUT `/api/bookshop/merchant/profile` | approved 商家修改 description 返回 2000; 修改 name 返回 4000 |

---

## 7. 迁移与回滚

### 7.1 迁移批次

**执行顺序**: 批次 002（创建 Merchant 表）→ 批次 001（Users 添加 merchant FK），避免 FK 指向不存在的表。

| 批次 | 内容 | 依赖 |
|------|------|------|
| 002 | 创建 `dvadmin_bookshop_merchant` 表 | 无 |
| 001 | 扩展 `Users.user_type` choices + 新增 `Users.merchant` OneToOneField | 002（FK 指向 bookshop_merchant） |

### 7.2 回滚策略

| 批次 | 回滚操作 |
|------|----------|
| 001 (Users FK) | `ALTER TABLE dvadmin_system_users DROP COLUMN merchant_id;` user_type choices 回退不影响数据 |
| 002 (Merchant 表) | `DROP TABLE dvadmin_bookshop_merchant;` |

**回滚安全**: Users 旧数据不受影响（user_type=0/1 值不变）；Merchant 表独立，除 Users.merchant FK 外无其他表 FK 依赖。

### 7.3 数据兼容性

- 现有 `user_type=0/1` 数据不受影响
- 新注册消费者默认 `user_type=3`（与旧 `user_type=1` 共存）
- `merchant` FK 为 `null=True`，不强制所有用户关联

---

## 8. 前端集成要点

### 8.1 管理端页面

- **商家审核页**: `web/src/views/bookshop/admin/merchant_audit.vue`
  - 列表展示（状态筛选、搜索）
  - 审核操作（通过/拒绝，拒绝需填原因）
  - 禁用/解禁操作
- **API**: `web/src/api/bookshop/merchant.ts`（使用 `service.ts`）

### 8.2 商家端页面

- **入驻申请页**: `web/src/views/bookshop/merchant/apply.vue`（无商家关联时可访问）
- **店铺信息页**: `web/src/views/bookshop/merchant/profile.vue`（审核通过后可访问）
- **API**: 同 `merchant.ts`

### 8.3 菜单注册

| 菜单 | component | 可见角色 |
|------|-----------|----------|
| 书店管理 > 商家审核 | `bookshop/admin/merchant_audit` | 管理员 |
| 我的店铺 > 店铺信息 | `bookshop/merchant/profile` | 商家 |
| 商家入驻 | `bookshop/merchant/apply` | 已登录无商家用户 |

---

## 9. Settings 变更

| 变更 | 文件 | 说明 |
|------|------|------|
| INSTALLED_APPS 添加 `"dvadmin.bookshop"` | `backend/application/settings.py` | 注册 bookshop app |
| URL 路由添加 `path("api/bookshop/", include("dvadmin.bookshop.urls"))` | `backend/application/urls.py` | 注册 bookshop 路由 |

**无新增环境变量**。merchant 模块使用现有 MySQL/Redis 配置和 JWT 配置。

---

## 10. 验收要点

- [x] Merchant 模型字段、状态枚举、合法转换已定义
- [x] 与 Users 的绑定关系与时机已定义（审核通过时原子操作）
- [x] 管理端/商家端 API 路径、请求/响应格式已定义（8 个端点）
- [x] 管理员审核权限与商家自访问权限规则已定义
- [x] MerchantPermission 详细判定逻辑已定义（has_permission + has_object_permission）
- [x] 校验规则已定义（4 类 14 条规则）
- [x] 错误码已定义（2000/4000/4001/4003）
- [x] 单元测试（28 用例）与集成测试（4 场景）已定义
- [x] 迁移批次、执行顺序、回滚策略已定义
- [x] 前端页面与菜单集成已定义
