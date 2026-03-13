# CLAUDE.md

## 项目记忆与指令

### 项目概述

这是一个基于Django + Vue3的在线图书销售系统毕业设计项目，采用前后端分离的B/S架构，支持管理端、用户端、商家端三端功能。

### 技术栈规范

- **后端**: Python 3.11+, Django 4.x, Django REST Framework, SQLite/MySQL
- **前端**: Vue 3, Vite, Element Plus, Pinia, Vue Router
- **架构**: RESTful API, JWT认证, 前后端分离
- **模拟服务**: 支付、物流、邮件均在本地模拟，无真实第三方接入

### 角色权限体系

1. **超级管理员**: 全平台数据管理、风控分析、财务结算、系统配置
2. **商家**: 需审核通过，仅管理自己店铺的商品、订单、数据
3. **普通用户**: 浏览购买、订单管理、会员积分、客服咨询

### 开发约束

- ✅ 必须实现: 数据隔离（商家只能看自己的数据）、敏感词过滤、操作日志
- ❌ 禁止实现: 真实支付接口、短信验证、IP封禁验证、邮件真实发送
- 🔄 模拟实现: 支付流程（本地模拟）、物流追踪（模拟数据）、邮件（控制台输出）

### 数据库设计原则

- 使用Django ORM，支持SQLite开发/MySQL生产
- 关键表: User(扩展AbstractUser), Book, Order, OrderItem, Cart, Review, Merchant, Category
- 商家数据严格隔离: 所有查询必须过滤 `merchant_id`
- 库存预警: 支持商品级自定义阈值

### 代码规范

- **后端**: PEP8, 类型提示, CBV/ViewSets, ModelSerializer, 自定义Permission
- **前端**: Composition API + `&lt;script setup&gt;`, 大驼峰组件名, Pinia状态管理, API拦截器

### 开发阶段

1. Week1: 基础架构、认证体系、权限控制
2. Week2-3: 图书/订单/购物车核心流程、模拟支付
3. Week4: 三端功能完善（管理端/商家端/用户端）
4. Week5: 数据统计(ECharts)、库存预警、日志财务
5. Week6: 测试优化、论文撰写

### 关键实现细节

#### 敏感词过滤

- 使用DFA算法，评论提交时自动检测
- 命中敏感词标记 `is_sensitive=True`，需审核后展示

#### 模拟支付服务

```python
class MockPaymentService:
    def create_order(self, order_id, amount) -> dict:
        # 返回模拟支付URL，不调用真实API
        pass
    def query_status(self, mock_order_id) -> str:
        # 返回模拟状态: success/pending
        pass
```

#### 商家数据隔离

所有商家端查询必须添加

```python
queryset = Book.objects.filter(merchant=request.user.merchant)
```

#### 库存预警逻辑

- 超级管理员: 可查看全平台预警，设置全局阈值
- 商家: 仅查看/设置自己商品的预警值
- 触发条件: `current_stock <= warning_stock`#### 常用命令

```
# 后端
cd backend && python manage.py runserver
cd backend && python manage.py makemigrations
cd backend && python manage.py migrate

# 前端
cd frontend && npm run dev
cd frontend && npm run build
```

### 注意事项


# ❌ 永远不要这么做（会删除所有数据库数据）

docker-compose down -v

# ✅ 正确做法（只停止容器，保留数据）

docker-compose down
docker-compose up -d

- 所有资金操作记录财务流水(FinanceRecord)
- 所有操作记录日志(OperationLog)
- 用户地址最多5条，数据库层限制
- 分类支持两级，使用 `parent`自关联
- 评论需审核后公开，商家可回复
