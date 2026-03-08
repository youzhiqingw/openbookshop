# API 规范文档

## 基础信息

- **基础URL**: http://localhost:8000/api/v1/
- **认证方式**: JWT Token (Header: `Authorization: Bearer <token>`)
- **数据格式**: JSON

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 分页响应
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 10,
    "results": [ ... ]
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

## 接口模块

### 认证 (auth/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | /auth/login/ | 公开 | 登录 |
| POST | /auth/register/ | 公开 | 注册 |
| POST | /auth/refresh/ | 公开 | 刷新 Token |
| POST | /auth/logout/ | 公开 | 登出 |

### 用户 (users/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /users/profile/ | 登录 | 获取个人信息 |
| PUT | /users/profile/ | 登录 | 更新个人信息 |
| GET | /users/addresses/ | 登录 | 地址列表 |
| POST | /users/addresses/ | 登录 | 新增地址 (最多5个) |

### 图书 (books/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /books/ | 公开 | 图书列表 (筛选/搜索/排序) |
| GET | /books/<id>/ | 公开 | 图书详情 |
| POST | /books/ | 商家 | 创建图书 |
| PUT | /books/<id>/ | 商家 | 更新图书 (仅自己) |
| DELETE | /books/<id>/ | 商家/管理员 | 删除图书 |

### 订单 (orders/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | /orders/ | 登录 | 创建订单 |
| GET | /orders/ | 登录 | 订单列表 |
| GET | /orders/<id>/ | 登录 | 订单详情 |
| PUT | /orders/<id>/status/ | 商家/管理员 | 更新状态 |

### 购物车 (cart/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /cart/ | 登录 | 购物车列表 |
| POST | /cart/ | 登录 | 添加商品 |
| PUT | /cart/<id>/ | 登录 | 修改数量 |
| DELETE | /cart/<id>/ | 登录 | 删除商品 |

### 评价 (reviews/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /reviews/?book_id= | 公开 | 图书评价列表 |
| POST | /reviews/ | 登录 | 发表评价 (需购买) |
| PUT | /reviews/<id>/reply/ | 商家 | 回复评价 |

### 管理端 (admin/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /admin/users/ | 管理员 | 用户列表 |
| GET | /admin/merchants/ | 管理员 | 商家审核列表 |
| PUT | /admin/merchants/<id>/audit/ | 管理员 | 审核商家 |
| GET | /admin/analytics/ | 管理员 | 统计数据 |
| GET | /admin/logs/ | 管理员 | 操作日志 |

### 商家端 (merchant/)

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | /merchant/dashboard/ | 商家 | 仪表盘数据 |
| GET | /merchant/orders/ | 商家 | 本店订单 |
| GET | /merchant/books/ | 商家 | 本店图书 |
| GET | /merchant/finance/ | 商家 | 财务记录 |

## WebSocket 接口

### 客服聊天

- **URL**: ws://localhost:8000/ws/chat/<session_id>/
- **认证**: Token 作为 query param `?token=<jwt>`

## 错误码

| 码 | 含义 |
|----|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 1001 | 库存不足 |
| 1002 | 敏感词命中 |
| 1003 | 商家未审核 |