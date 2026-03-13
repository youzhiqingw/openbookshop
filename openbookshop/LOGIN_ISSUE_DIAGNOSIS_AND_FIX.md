# 🔧 登录问题诊断与修复报告

## 📋 问题描述

用户报告：商家账号 (`merchant_test`) 和普通用户账号 (`customer_test`) 无法登录，需检查数据库中是否存储了这些账户。

---

## 🔍 诊断结果

### 问题根源 ✅ 已确认
**数据库中只有 admin 账户，merchant_test 和 customer_test 根本不存在！**

| 状态 | 用户名 | 存在于DB | 能否认证 |
|------|--------|---------|--------|
| ✗ 问题 | merchant_test | ❌ | ❌ |
| ✗ 问题 | customer_test | ❌ | ❌ |
| ✓ 正常 | admin | ✅ | ✅ |

### 根本原因
在之前的操作中，虽然我们**说**创建了这两个账户，但实际上：
- 代码逻辑中创建了这些账户
- 但在后续 docker-compose 的清推和重建过程中 (`docker-compose down -v`)，**数据库被完全清空**
- 只有最后通过 shell 命令创建的 `admin` 账户保存下来

---

## ✅ 修复方案 (已执行)

### 步骤1: 重新创建 merchant_test 账户
```
✓ 用户名: merchant_test
✓ 密码: merchant123456
✓ 角色: merchant
✓ is_active: True (已激活)
✓ is_staff: True (允许访问Django admin)
```

### 步骤2: 重新创建 customer_test 账户
```
✓ 用户名: customer_test
✓ 密码: customer123456
✓ 角色: customer
✓ is_active: True (已激活)
✓ is_staff: False (不允许访问Django admin)
```

### 步骤3: 验证认证成功
```
✓ merchant_test 认证成功 (可以登录前端Admin系统)
✓ customer_test 认证成功 (可以登录前端用户系统)
✓ admin 认证成功 (可以登录Django原生admin)
```

---

## 📊 修复后数据库状态

| 用户名 | 密码 | 角色 | is_active | is_staff | 用途 |
|--------|------|------|-----------|---------|------|
| admin | admin123456 | admin | ✓ | ✓ | Django原生admin系统 |
| merchant_test | merchant123456 | merchant | ✓ | ✓ | Vue商家管理系统 |
| customer_test | customer123456 | customer | ✓ | ✗ | Vue用户端系统 |

---

## 🚀 现在可以登录的 URL

### 1. Django 原生 Admin 系统
```
http://127.0.0.1:8000/admin/
用户名: admin
密码: admin123456
```

### 2. Vue Admin 商家系统
```
http://127.0.0.1:8080/merchant/login
用户名: merchant_test
密码: merchant123456
```

### 3. Vue 用户系统
```
http://127.0.0.1:8080 (用户端首页)
用户名: customer_test
密码: customer123456
```

### 4. Vue Admin 管理系统 (仅admin可访问)
```
http://127.0.0.1:8080/admin/login
用户名: admin
密码: admin123456
```

---

## 🔐 API 登录端点

所有前端页面通过 REST API 登录：

```
POST /api/users/login/
Content-Type: application/json

{
  "username": "merchant_test",
  "password": "merchant123456"
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 2,
      "username": "merchant_test",
      "email": "merchant@example.com",
      "role": "merchant",
      "is_staff": true,
      "is_active": true
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

---

## 🎯 验证清单

- [x] merchant_test 已创建于数据库
- [x] customer_test 已创建于数据库
- [x] 两个账户密码正确设置
- [x] 两个账户 is_active 为 True
- [x] merchant_test is_staff = True
- [x] customer_test is_staff = False
- [x] 所有账户认证成功通过
- [x] API 序列化成功返回token

---

## 📌 关键要点

### 为什么 merchant_test 的 is_staff=True?
因为商家需要访问 Django admin 进行调试和数据检查（虽然在生产环境中通常不需要，但在开发/测试阶段有用）

### 为什么 customer_test 的 is_staff=False?  
因为普通用户不应该有任何 Django admin 权限，只能通过 Vue 前端系统使用平台功能

### 下次如何避免此问题?
```bash
# 不要使用 -v 清空volume同时清空数据库
docker-compose down -v    # ❌ 这会删除所有数据

# 改为只停止容器而保留数据
docker-compose down       # ✅ 保留数据，只停止容器
docker-compose up -d      # 重启时数据不丢失
```

---

## 🧪 立即测试

### 在浏览器中验证

**测试1: 商家登录**
1. 打开 http://127.0.0.1:8080/merchant/login
2. 输入用户名: `merchant_test`
3. 输入密码: `merchant123456`
4. 点击登录 → **应该成功进入商家后台**

**测试2: 用户登录**
1. 打开 http://127.0.0.1:8080
2. 点击"登录"
3. 输入用户名: `customer_test`
4. 输入密码: `customer123456`
5. 点击登录 → **应该成功进入用户首页**

**测试3: Admin登录**
1. 打开 http://127.0.0.1:8000/admin/
2. 输入用户名: `admin`
3. 输入密码: `admin123456`
4. 点击登录 → **应该进入Django原生admin系统**

---

## 📞 故障排查

**如果仍然无法登录，请检查：**

1. **Docker 容器是否正在运行?**
   ```bash
   docker-compose ps
   # 应该显示 3 个 running 的容器: backend, frontend, db
   ```

2. **后端是否正常？**
   ```bash
   docker exec openbookshop_backend python manage.py migrate
   # 应该输出 "No migrations to apply"
   ```

3. **用户是否真的在数据库中？**
   ```bash
   docker exec openbookshop_backend python manage.py shell
   >>> from apps.users.models import User
   >>> User.objects.all()
   # 应该显示 3 个用户: admin, merchant_test, customer_test
   ```

4. **数据库连接是否正常？**
   ```bash
   docker exec openbookshop_db mysql -u bookshop -pbookshop123 bookshop -e "SELECT * FROM users_user;"
   # 应该返回 3 行用户数据
   ```

---

## 📄 相关文件

| 文件 | 说明 |
|------|------|
| `backend/apps/users/models.py` | User 模型定义 |
| `backend/apps/users/views.py` | LoginView 实现 |
| `backend/apps/users/serializers.py` | LoginSerializer 数据序列化 |
| `backend/config/settings.py` | Django 配置 |
| `frontend/src/stores/auth.js` | Vue auth 状态管理 |

---

## 🎓 总结

✅ **问题原因**: 数据库数据丢失  
✅ **解决方案**: 重新创建账户  
✅ **验证状态**: 所有账户已创建且认证成功  
✅ **现在可以**: 前端各系统正常登录  

**建议**: 在生产环境中使用数据库管理工具（如 phpMyAdmin）或 Django dump/load fixtures 来持久化初始数据。

---

**修复时间**: 2026年3月13日  
**修复状态**: ✅ 已完成
