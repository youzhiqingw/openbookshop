# 功能开发技能

## 触发条件
用户说"开发功能"、"实现"、"添加模块"时调用

## 开发流程

### 1. 需求澄清
- 属于哪个端? (admin/merchant/user)
- 涉及哪些模型?
- 权限要求?

### 2. 数据库设计
```python
# 在 apps/<name>/models.py 定义
# 必须包含:
# - created_at, updated_at
# - 商家外键 (如果是商家端功能)
# - 注释说明用途
```

### 3. API 开发 (后端)
```python
# views.py: 使用 ModelViewSet
# serializers.py: 使用 ModelSerializer
# urls.py: 注册路由
# permissions.py: 自定义权限类
```

### 4. 界面开发 (前端)
```vue
<!-- 按端分类存放 -->
<!-- views/admin/xxx.vue -->
<!-- views/merchant/xxx.vue -->
<!-- views/user/xxx.vue -->
<!-- 必须包含: -->
<!-- - 权限检查 (v-permission) -->
<!-- - 错误处理 -->
<!-- - 加载状态 -->
```

### 5. 联调测试
- API 文档: http://localhost:8000/api/docs
- 测试数据: scripts/generate_mock_data.py

### 6. 文档更新
- 更新 docs/architecture/api.md
- 更新 docs/architecture/database.md (如有变更)
