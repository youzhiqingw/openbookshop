# OpenBookShop 前端 SPEC

**版本**: 1.0
**日期**: 2026-05-16
**依赖**: [foundation.md](foundation.md), [merchant.md](merchant.md), [catalog.md](catalog.md), [order.md](order.md), [payment-review.md](payment-review.md)
**目标**: 定义 `web/src/views/bookshop/` 三端目录结构、API 模块、Pinia stores、菜单/RBAC 集成与路由注册策略、UI 状态、表单校验、i18n 需求、构建与 E2E 检查。**不包含**实现代码。

---

## 1. 前端架构事实

### 1.1 现有代码事实

- **单 Vue 项目**: 非 three 端独立项目，通过后端菜单动态注册路由
- **路由发现**: `backEnd.ts:24` 使用 `import.meta.glob('../views/**/*.{vue,tsx}')` 自动发现组件
- **路由注册**: `backEnd.ts:147` 通过 `menuApi.getSystemMenu()` 获取后端菜单 → `handleMenu()` → `backEndComponent()` 映射组件
- **请求封装双轨并存**:
  - `request.ts`: `code !== 0` 为错误，header `JWT <token>`
  - `service.ts`: `code === 2000` 为成功，header `JWT <token>`
  - **bookshop 统一使用 `service.ts`**（import from `/@/utils/service.ts`）
- **FastCrud 模式**: 管理端/商家端列表页使用 `@fast-crud/fast-crud` 的 `useFs({ createCrudOptions })` 模式
- **i18n**: 三语（zh-cn / zh-tw / en），每个模块在 `web/src/i18n/pages/` 下有对应翻译文件
- **API 风格**: 系统模块的 API 定义在视图文件夹内（如 `views/system/dictionary/api.ts`），非集中式
- **布局**: 管理端使用 `web/src/layout/` 下现有布局组件
- **权限指令**: `v-auth` 按钮权限指令（已有）
- **Pinia stores**: 在 `web/src/stores/` 下，视图局部 stores 可放在视图文件夹内

### 1.2 版本约束

- Node.js: 18.19.0
- Vue: 3.4.38
- Vite: 5.4.1
- Element Plus: 2.8.x
- FastCrud: 1.21.2
- TypeScript: 4.9.4
- 包管理器: pnpm

---

## 2. 目录结构

### 2.1 视图目录 `web/src/views/bookshop/`

```
web/src/views/bookshop/
├── admin/                          # 管理端（使用现有管理端布局）
│   ├── merchant_audit/             # 商家审核
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── books/                      # 全平台图书管理
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── category/                   # 分类管理
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── orders/                     # 订单监控
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── stock_warning/              # 库存预警
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── reviews/                    # 评价管理
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── payment_records/            # 支付记录
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   └── dashboard/                  # 统计仪表盘
│       └── index.vue
│
├── merchant/                       # 商家端（使用 MerchantLayout）
│   ├── layout.vue                  # 商家端布局组件（侧边栏+顶栏）
│   ├── profile/                    # 店铺信息
│   │   ├── index.vue
│   │   └── api.ts
│   ├── apply/                      # 入驻申请
│   │   ├── index.vue
│   │   └── api.ts
│   ├── books/                      # 自己的图书管理
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   ├── orders/                     # 自己的订单管理
│   │   ├── index.vue
│   │   ├── api.ts
│   │   └── crud.tsx
│   └── reviews/                    # 自己的评价管理
│       ├── index.vue
│       ├── api.ts
│       └── crud.tsx
│
└── customer/                       # 用户端/书城（使用 CustomerLayout）
    ├── layout.vue                  # 用户端布局组件（导航栏+页脚，参考 PRD UI 规范）
    ├── home/                       # 首页
    │   └── index.vue
    ├── category/                   # 分类浏览
    │   └── index.vue
    ├── book/                       # 图书详情
    │   └── index.vue
    ├── cart/                       # 购物车
    │   └── index.vue
    ├── checkout/                   # 结算/下单
    │   └── index.vue
    ├── orders/                     # 我的订单
    │   ├── index.vue               # 订单列表
    │   └── detail.vue              # 订单详情
    ├── reviews/                    # 我的评价
    │   └── index.vue
    ├── collections/                # 我的收藏
    │   └── index.vue
    └── user/                       # 个人中心
        ├── profile.vue             # 个人信息
        └── addresses.vue           # 收货地址管理
```

### 2.2 API 目录 `web/src/api/bookshop/`

> **策略**: bookshop 模块采用**集中式 API 目录**（区别于系统模块的视图内嵌式），因为同一后端接口可能被多个端复用（如 book API 被管理端/商家端/用户端共用）。

```
web/src/api/bookshop/
├── merchant.ts         # 商家相关 API（入驻申请、profile、审核）
├── book.ts             # 图书相关 API（分类、图书 CRUD、上下架、补货、预警）
├── order.ts            # 订单相关 API（创建、支付、取消、发货、退款、强制退款）
├── cart.ts             # 购物车 API（CRUD）
├── address.ts          # 收货地址 API（CRUD、设默认）
├── review.ts           # 评价 API（提交、列表、回复、可见性）
├── payment.ts          # 支付记录 API（查询）
├── collection.ts       # 收藏 API（收藏/取消/列表）
└── statistics.ts       # 统计数据 API（仪表盘）
```

**统一规范**:
- 所有 API 函数使用 `request` from `/@/utils/service.ts`（code 2000 = 成功）
- 函数命名: `GetList`, `GetObj`, `AddObj`, `UpdateObj`, `DelObj`（与 FastCrud 模式一致）
- 自定义操作: `ShipOrder`, `CancelOrder`, `PayOrder`, `ApproveRefund` 等
- 返回类型: 使用 TypeScript interface 定义

### 2.3 Pinia Stores `web/src/stores/bookshop/`

```
web/src/stores/bookshop/
├── cart.ts             # 购物车状态（items、total、addToCart、removeFromCart、clearCart）
└── user.ts             # 用户端状态（userInfo、addresses、collections count）
```

**cart.ts 职责**:
- `items`: CartItem[] — 购物车列表
- `totalCount`: computed — 购物车总数量
- `totalAmount`: computed — 购物车总金额
- `fetchCart()`: 从后端拉取购物车
- `addToCart(bookId, quantity)`: 加购（调用 API 后刷新）
- `updateQuantity(cartItemId, quantity)`: 更新数量
- `removeItem(cartItemId)`: 删除项
- **持久化**: 不持久化（每次登录从后端获取）

**user.ts 职责**:
- `collectionCount`: number — 收藏数量（用于徽章显示）
- `fetchCollectionCount()`: 从后端获取
- **不持久化**

---

## 3. 布局策略

### 3.1 管理端布局

- **复用现有布局**: `web/src/layout/` 下的管理端布局组件
- **菜单**: 后端菜单 API 返回管理员可见菜单集，侧边栏展示
- **无需新建布局组件**

### 3.2 商家端布局 — MerchantLayout

- **文件**: `web/src/views/bookshop/merchant/layout.vue`
- **结构**: 侧边栏 + 顶栏 + 内容区（参考现有管理端布局简化版）
- **菜单来源**: 后端菜单 API 返回商家角色可见菜单集
- **布局切换**: 菜单父级 `component` 字段指向 `bookshop/merchant/layout`
- **样式**: 与管理端风格一致，侧边栏可折叠

### 3.3 用户端布局 — CustomerLayout

- **文件**: `web/src/views/bookshop/customer/layout.vue`
- **结构**: 顶部导航栏 + 内容区 + 页脚（参考 PRD §2-5 UI 规范）
- **菜单来源**: 后端菜单 API 返回消费者角色可见菜单集
- **布局切换**: 菜单父级 `component` 字段指向 `bookshop/customer/layout`
- **导航栏组件**:
  - Logo + 品牌名"阅享书城"
  - 主导航: 首页 | 分类 | 畅销榜 | 新书
  - 搜索框（380px 宽，圆角 21px）
  - 右侧: 购物车(带徽章) | 收藏 | 我的账户下拉
- **页脚**: 服务保障 + 链接分组 + 版权信息
- **配色**: 主色 #2c3e50，强调色 #f1c40f（参考 PRD §3）

---

## 4. 菜单/RBAC 集成与路由注册

### 4.1 路由注册机制

**现有机制**（不修改）:
1. `backEnd.ts:147` — `menuApi.getSystemMenu()` 获取菜单
2. `backEnd.ts:174` — `backEndComponent()` 将 `component` 字符串映射到 Vue 文件
3. `backEnd.ts:24` — `import.meta.glob('../views/**/*.{vue,tsx}')` 自动发现组件

**bookshop 路由注册**:
- Vue 文件放在 `views/bookshop/` 下 → 自动被 `import.meta.glob` 发现
- 后端菜单 `component` 字段值 → `backEndComponent()` 自动映射
- **无需修改 `backEnd.ts`**

### 4.2 菜单数据定义（后端 init_menu.json）

```
书店管理 (目录级, 管理员可见)
├── 商家审核     component=bookshop/admin/merchant_audit/index
├── 图书管理     component=bookshop/admin/books/index
├── 分类管理     component=bookshop/admin/category/index
├── 订单监控     component=bookshop/admin/orders/index
├── 库存预警     component=bookshop/admin/stock_warning/index
├── 评价管理     component=bookshop/admin/reviews/index
├── 支付记录     component=bookshop/admin/payment_records/index
└── 数据统计     component=bookshop/admin/dashboard/index

我的店铺 (目录级, 商家可见, component=bookshop/merchant/layout)
├── 店铺信息     component=bookshop/merchant/profile/index
├── 图书管理     component=bookshop/merchant/books/index
├── 订单管理     component=bookshop/merchant/orders/index
└── 评价管理     component=bookshop/merchant/reviews/index

书城 (目录级, 消费者可见, component=bookshop/customer/layout)
├── 首页         component=bookshop/customer/home/index
├── 分类浏览     component=bookshop/customer/category/index
├── 购物车       component=bookshop/customer/cart/index
├── 我的订单     component=bookshop/customer/orders/index
├── 我的收藏     component=bookshop/customer/collections/index
├── 我的评价     component=bookshop/customer/reviews/index
└── 个人中心     component=bookshop/customer/user/profile
```

### 4.3 按钮权限（MenuButton 注册）

| 按钮权限 key | 所属菜单 | 说明 |
|-------------|---------|------|
| `bookshop:admin:merchant:audit` | 商家审核 | 审核通过/拒绝 |
| `bookshop:admin:merchant:disable` | 商家审核 | 禁用/解禁 |
| `bookshop:admin:book:status` | 图书管理 | 上下架 |
| `bookshop:admin:order:force_refund` | 订单监控 | 强制退款 |
| `bookshop:admin:review:visibility` | 评价管理 | 设置可见性 |
| `bookshop:merchant:book:status` | 商家图书管理 | 上下架 |
| `bookshop:merchant:book:restock` | 商家图书管理 | 补货 |
| `bookshop:merchant:order:ship` | 商家订单管理 | 发货 |
| `bookshop:merchant:order:refund` | 商家订单管理 | 退款审核 |
| `bookshop:merchant:review:reply` | 商家评价管理 | 回复评价 |

**前端使用**: `v-auth="'bookshop:admin:merchant:audit'"`

### 4.4 角色可见性

| 角色 | 可见菜单集 |
|------|-----------|
| 管理员（is_superuser 或 user_type=0） | 书店管理 + 我的店铺(可选) + 书城(可选) |
| 商家（user_type=2, merchant.status=approved） | 我的店铺 + 书城 |
| 消费者（user_type=3） | 书城 |
| 匿名 | 书城（首页/分类/详情，只读） |

### 4.5 登录后路由重定向

- 管理员登录 → `/home`（现有管理端首页）
- 商家登录 → `/bookshop/merchant/profile`（商家端首页）
- 消费者登录 → `/bookshop/customer/home`（书城首页）

**实现**: 在 `backEnd.ts` 的路由初始化中根据 `user_type` 设置默认跳转

---

## 5. UI 状态定义

### 5.1 管理端页面状态

| 页面 | 主要 UI 状态 | 说明 |
|------|-------------|------|
| 商家审核 | 列表态、审核弹窗（通过/拒绝）、禁用/解禁确认 | FastCrud 表格 + 自定义 action |
| 图书管理 | 列表态、新增/编辑表单、上下架确认 | FastCrud CRUD |
| 分类管理 | 树形列表态、新增/编辑弹窗 | FastCrud 树形表格 |
| 订单监控 | 列表态、详情抽屉、强制退款确认 | FastCrud 表格 + 详情 |
| 库存预警 | 列表态、全局阈值设置弹窗 | FastCrud 表格 + 设置 |
| 评价管理 | 列表态、可见性切换、内容查看 | FastCrud 表格 |
| 支付记录 | 只读列表态 | FastCrud 表格（仅 GET） |
| 统计仪表盘 | 图表展示态 | ECharts 组件 |

### 5.2 商家端页面状态

| 页面 | 主要 UI 状态 | 说明 |
|------|-------------|------|
| 入驻申请 | 表单态（待审核）、结果态（已提交/已通过/已拒绝） | 多步表单 |
| 店铺信息 | 展示态、编辑态（description/logo/is_open） | 表单 |
| 图书管理 | 列表态、新增/编辑表单、上下架/补货/预警值弹窗 | FastCrud CRUD |
| 订单管理 | 列表态、详情抽屉、发货弹窗、退款审核弹窗 | FastCrud + 自定义 action |
| 评价管理 | 列表态、回复弹窗 | FastCrud 表格 + 回复 |

### 5.3 用户端页面状态

| 页面 | 主要 UI 状态 | 说明 |
|------|-------------|------|
| 首页 | 轮播图、畅销榜、新书上架 | 自定义布局（非 FastCrud） |
| 分类浏览 | 左侧分类树、右侧图书网格 | 自定义布局 |
| 图书详情 | 图书信息、评价列表、相关推荐 | 自定义布局 |
| 购物车 | 列表态（全选/数量修改/删除）、空状态 | 自定义布局 |
| 结算下单 | 地址选择、商品确认、提交 | 自定义表单 |
| 订单列表 | Tab 切换（全部/待付款/待发货/待收货/已完成） | 自定义列表 |
| 订单详情 | 状态时间线、商品信息、操作按钮 | 自定义布局 |
| 收货地址 | 列表态、新增/编辑弹窗、删除确认 | 自定义 CRUD |
| 我的收藏 | 图书网格、取消收藏 | 自定义布局 |
| 我的评价 | 列表态、评价弹窗（星级+文本+图片上传） | 自定义布局 |
| 个人中心 | 展示态、编辑态 | 表单 |

### 5.4 通用 UI 状态

| 状态 | 处理 |
|------|------|
| 加载中 | Element Plus `v-loading` 指令或 `el-skeleton` 骨架屏 |
| 空数据 | `el-empty` 组件 + 提示文案 |
| 网络错误 | `ElMessage.error` + 重试按钮 |
| 权限不足 | 403 页面或 `ElMessage.warning` |
| 表单提交中 | 按钮 `loading` 状态，防重复提交 |
| 操作成功 | `ElMessage.success` |
| 操作失败 | `ElMessage.error`（显示后端返回 msg） |

---

## 6. 表单校验规则

### 6.1 管理端/商家端（FastCrud 模式）

FastCrud 表单校验在 `crud.tsx` 的 `columns` 定义中通过 `form.rules` 配置，使用 Element Plus 的 async-validator 规则。

**通用规则**:
- 必填: `{ required: true, message: 'xxx不能为空', trigger: 'blur' }`
- 最大长度: `{ max: N, message: '不能超过N个字符', trigger: 'blur' }`
- 数值范围: `{ type: 'number', min: 0, message: '不能为负', trigger: 'blur' }`
- 手机号: `{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }`
- ISBN: `{ pattern: /^[0-9-]{10,20}$/, message: 'ISBN格式不正确', trigger: 'blur' }`

### 6.2 用户端（自定义表单）

用户端页面使用 Element Plus 的 `el-form` + `rules` 进行前端校验，规则与后端校验一致。

**关键校验**:
- 收货地址: 所有字段必填 + 手机号格式 + 详细地址 max=255
- 评价: 评分必选 1-5 + 内容必填 max=500 + 图片最多 9 张
- 购物车数量: 1-99 整数

### 6.3 前端校验与后端校验关系

- 前端校验: 即时反馈，提升用户体验
- 后端校验: 最终安全保障，前端校验不能替代后端校验
- 前后端校验规则必须一致（字段、长度、格式、范围）

---

## 7. i18n 需求

### 7.1 翻译文件

每个 bookshop 子模块需要三个翻译文件:

```
web/src/i18n/pages/bookshop/
├── admin/
│   ├── en.ts
│   ├── zh-cn.ts
│   └── zh-tw.ts
├── merchant/
│   ├── en.ts
│   ├── zh-cn.ts
│   └── zh-tw.ts
└── customer/
    ├── en.ts
    ├── zh-cn.ts
    └── zh-tw.ts
```

### 7.2 翻译 key 命名规范

```
bookshop.admin.merchantAudit.title       # 页面标题
bookshop.admin.merchantAudit.audit       # 审核按钮
bookshop.admin.books.status.onSale       # 状态文本
bookshop.customer.cart.empty             # 空状态文案
bookshop.customer.orders.status.pending  # 订单状态
```

### 7.3 翻译优先级

- **P0（必须）**: zh-cn（中文简体，开发默认语言）
- **P1（应做）**: en（英文）
- **P2（可选）**: zh-tw（繁体）

MVP 阶段优先完成 zh-cn，en/zh-tw 可后续补充。

---

## 8. 构建与 E2E 检查

### 8.1 构建验证

每次前端变更后必须通过:

```bash
cd web
pnpm run build    # 生产构建，无 TypeScript/ESLint 编译错误
```

**检查点**:
- 无 TypeScript 编译错误
- 无未解析的 import
- 无循环依赖警告
- 构建产物大小合理（bookshop 模块不应使构建产物超过 5MB）

### 8.2 ESLint 检查

```bash
cd web
pnpm run lint-fix  # 自动修复
```

### 8.3 E2E 测试（Playwright）

| 测试场景 | 步骤 | 验证 |
|---------|------|------|
| 管理员审核商家 | 登录管理端→商家审核页→审核通过 | 商家状态更新 |
| 商家管理图书 | 登录商家端→图书管理→创建图书→上架 | 图书创建成功 |
| 用户浏览购物 | 登录用户端→首页→图书详情→加购→下单→支付 | 订单创建/支付成功 |
| 用户地址管理 | 登录→个人中心→地址管理→新增→设默认→删除 | 地址 CRUD |
| 数据隔离 | 商家 A 登录→仅见自己图书/订单 | 无其他商家数据 |
| 角色菜单隔离 | 管理员/商家/消费者登录→侧边栏菜单 | 各角色仅见自己菜单 |

### 8.4 开发服务器验证

```bash
cd web
pnpm run dev      # 开发服务器启动无错误
```

**手动验证清单**:
- [ ] 管理端: 商家审核页加载、图书 CRUD、订单列表
- [ ] 商家端: 布局渲染、图书管理、订单发货
- [ ] 用户端: 导航栏渲染、首页加载、购物车操作、下单流程
- [ ] 登录/登出: 三种角色登录后重定向正确
- [ ] 权限: 按钮权限 `v-auth` 正确显示/隐藏

---

## 9. 与后端 API 契约同步

### 9.1 响应格式

所有 bookshop API 返回格式（与 `service.ts` 兼容）:

```typescript
// 列表（分页）
interface PageResponse<T> {
  code: 2000;
  data: T[];
  total: number;
  page: number;
  limit: number;
  msg: string;
}

// 详情/操作成功
interface DetailResponse<T> {
  code: 2000;
  data: T;
  msg: string;
}

// 错误
interface ErrorResponse {
  code: 4000 | 4001 | 4003;
  data: null;
  msg: string;
}
```

### 9.2 同步检查点

| 变更类型 | 后端操作 | 前端操作 | 验证 |
|---------|---------|---------|------|
| 新增 API | 新增 ViewSet + URL | 新增 api.ts 函数 + 页面调用 | 请求路径一致 |
| 修改字段 | 修改 Serializer | 修改 TypeScript interface + 表单 | 字段名/类型一致 |
| 修改状态枚举 | 修改 choices | 修改前端状态映射 | 枚举值一致 |
| 修改错误码 | 修改异常处理 | 修改前端错误处理 | 错误码匹配 |

### 9.3 TypeScript Interface 定义位置

每个视图文件夹内可定义 `types.ts`（与系统模块一致），或在 `api.ts` 中内联定义。推荐在 `api.ts` 中定义，减少文件数量。

---

## 10. 依赖与注意事项

### 10.1 新增依赖

**无新增 npm 依赖**。所有功能使用现有依赖实现:
- Element Plus: UI 组件
- FastCrud: 管理端/商家端 CRUD 表格
- ECharts: 统计仪表盘（已在 package.json 中）
- Pinia: 状态管理

### 10.2 环境变量

**无新增环境变量**。bookshop 使用现有 `VITE_API_URL` 配置。

### 10.3 注意事项

| 项目 | 说明 |
|------|------|
| service.ts vs request.ts | bookshop API 统一用 `service.ts`；系统管理页面继续用 `request.ts`，不混用 |
| FastCrud 模式 | 仅管理端/商家端列表页使用；用户端使用自定义组件 |
| 图片上传 | 复用系统上传接口 `/api/system/file/upload/`，返回 URL 存入字段 |
| 金额显示 | 所有金额显示为 `¥XX.XX` 格式，前端不做金额计算（以后端为准） |
| 分页 | 所有列表接口必须分页，前端不一次拉取全量数据 |
| 购物车徽章 | 顶部导航栏购物车图标显示数量徽章，从 Pinia cart store 读取 |

---

## 11. 验收要点

- [x] `web/src/views/bookshop/` 三端目录结构已定义（admin 8 + merchant 5 + customer 12 = 25 个页面）
- [x] `web/src/api/bookshop/` 集中式 API 模块已定义（9 个文件）
- [x] `web/src/stores/bookshop/` Pinia stores 已定义（cart.ts + user.ts）
- [x] 三端布局策略已定义（复用管理端 + MerchantLayout + CustomerLayout）
- [x] 菜单/RBAC 集成与路由注册策略已定义（后端菜单驱动 + 自动发现）
- [x] 按钮权限 key 已定义（10 个）
- [x] 角色可见性与登录后重定向已定义
- [x] UI 状态定义（管理端 8 + 商家端 5 + 用户端 11 + 通用 6）
- [x] 前端表单校验规则已定义（FastCrud + 自定义表单）
- [x] i18n 需求与文件结构已定义（3 端 × 3 语）
- [x] 构建验证、ESLint、E2E 测试场景已定义（6 场景）
- [x] 后端 API 契约同步检查点已定义
- [x] 依赖/环境变量/注意事项已定义
