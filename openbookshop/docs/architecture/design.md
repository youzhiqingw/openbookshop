# 架构设计文档

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  前端 (Vue3)    │ ←→ │ 后端 (Django)   │ ←→ │   数据库        │
│                 │ JWT│                 │ ORM│ (SQLite/MySQL)  │
│ - 管理端        │    │ - RESTful API   │    │                 │
│ - 商家端        │    │ - 权限控制      │    │                 │
│ - 用户端        │    │ - 业务逻辑      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 技术选型理由

| 技术 | 选择理由 |
|------|----------|
| Django | 快速开发、ORM强大、生态完善 |
| DRF | 快速构建 RESTful API |
| Vue3 | 组合式API、性能优秀、生态成熟 |
| Element Plus | 组件丰富、适合后台系统 |
| Pinia | 类型友好、Vue官方推荐 |
| JWT | 无状态认证、适合前后端分离 |

## 安全设计

### 认证流程

1. 用户登录 → 返回 JWT (access + refresh)
2. 前端存储于 localStorage
3. 每次请求携带 `Authorization: Bearer <token>`
4. 后端验证 JWT 并解析用户角色

### 权限控制

- 使用 Django 自定义 Permission 类
- 商家端所有接口检查 `request.user.merchant`
- 管理端检查 `request.user.is_staff`

### 数据隔离

```python
# 商家端视图基类
class MerchantViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.model.objects.filter(
            merchant=self.request.user.merchant
        )
```

## 模块划分

### 后端应用

| 应用 | 职责 |
|------|------|
| users | 用户认证、角色管理、风控 |
| merchants | 商家资质、店铺设置 |
| books | 图书信息、分类、库存 |
| orders | 订单生命周期、状态流转 |
| cart | 购物车逻辑 |
| reviews | 评价系统、敏感词过滤 |
| payments | 支付记录、模拟支付 |
| logistics | 物流记录、模拟物流 |
| promotions | 优惠券、满减、秒杀 |
| analytics | 数据统计、图表接口 |
| chat | 客服会话、WebSocket |
| finance | 财务流水、结算、提现 |

### 前端模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 管理端 | `views/admin/` | 全平台管理 |
| 商家端 | `views/merchant/` | 店铺管理 |
| 用户端 | `views/user/` | 个人中心 |
| 公共组件 | `components/common/` | 通用组件 |

## 扩展性考虑

1. **支持 MySQL 切换** (仅改配置)
2. **支持真实支付接入** (保留接口)
3. **支持微服务拆分** (按应用独立)