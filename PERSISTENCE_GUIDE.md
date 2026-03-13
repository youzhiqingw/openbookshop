# 🔄 OpenBookShop 容器重启持久化方案

## 📋 概述

本方案确保每次容器重启后，测试账户、商家信息、书籍数据和用户地址都能自动恢复，无需手动重新初始化。

---

## 🏗️ 方案架构

### 工作流程

```
Docker 容器启动
    ↓
Dockerfile COPY (复制所有代码)
    ↓
entrypoint.sh 执行
    ↓
1️⃣  Python 运行 manage.py migrate (数据库迁移)
    ↓
2️⃣  Python 运行 init_data_persistent.py (数据初始化)
    ↓
3️⃣  Gunicorn 启动 (服务运行)
```

### 关键文件

| 文件 | 位置 | 功能 |
|------|------|------|
| `entrypoint.sh` | `/backend/entrypoint.sh` | 容器启动脚本（已修改） |
| `init_data_persistent.py` | `/backend/init_data_persistent.py` | 数据持久化初始化脚本（新建） |
| `Dockerfile` | `/backend/Dockerfile` | Docker 镜像构建配置 |
| `docker-compose.yml` | `/openbookshop/docker-compose.yml` | 容器编排配置 |

---

## 🔧 脚本说明

### init_data_persistent.py

**文件位置**: `backend/init_data_persistent.py`

**核心特性**:
- ✅ **幂等性**: 重复运行也不会重复创建数据
- ✅ **智能检测**: 用 `.get_or_create()` 检查数据是否已存在
- ✅ **密码安全**: 使用 Django 的 `make_password()` 进行密码 Hash
- ✅ **完整性**: 初始化用户、商家、地址、分类、书籍全套数据
- ✅ **详细日志**: 打印创建/跳过状态，便于调试

**初始化的数据**:

1. **用户账户 (3个)**
   ```
   admin / admin123456 (管理员)
   merchant_test / merchant123456 (商家)
   customer_test / customer123456 (普通用户)
   ```

2. **商家 (1个)**
   ```
   商家名: 测试书店
   状态: 已批准
   归属用户: merchant_test
   ```

3. **收货地址 (2个)**
   ```
   ✅ 张三 - 北京市朝阳区望京街1号 (默认)
   ✅ 李四 - 上海市浦东新区陆家嘴环路100号
   ```

4. **图书分类 (12个)**
   ```
   中国当代文学、外国文学、自我成长、心理学、
   科幻小说、幻想文学、历史、社科、
   职场提升、人工智能、编程、计算机
   ```

5. **书籍 (25本)**
   ```
   - 国内经典: 活着、围城、三体等
   - 国外经典: 1984、房间、人間失格等
   - 技术书籍: 算法导论、代码整洁之道等
   - 所有书籍都关联到 merchant_test 商家
   - 所有书籍都有正确的封面路径
   ```

---

## 📊 持久化原理

### 为什么数据会保留？

**MySQL 容器**:
- 使用 `docker-compose.yml` 中的 `db_data` Volume
- Volume 在容器删除后仍然保存
- 重启或重建容器时，数据库数据不丢失

```yaml
volumes:
  db_data:

db:
  volumes:
    - db_data:/var/lib/mysql
```

**Django 应用层**:
- `init_data_persistent.py` 使用 ORM 的 `get_or_create()`
- 如果数据已存在则跳过创建
- 确保重启时不会报错或重复创建

### 初始化流程

```python
# 伪代码示例
user, created = User.objects.get_or_create(
    username='merchant_test',
    defaults={...}
)

if created:
    print("✅ 创建: merchant_test")
else:
    print("⏭️  已存在: merchant_test")
```

---

## 🚀 使用方法

### 首次启动或完全重建

```bash
cd /openbookshop

# 完全清空并重建（谨慎使用）
docker-compose down -v
docker-compose up -d

# 查看初始化过程
docker logs openbookshop_backend -f
```

### 日常重启（保留数据）

```bash
# 仅停止容器，保留所有数据
docker-compose down

# 重启容器，所有数据自动恢复
docker-compose up -d

# 验证
docker logs openbookshop_backend
```

### 查看初始化日志

```bash
# 查看完整初始化日志
docker logs openbookshop_backend | grep -A 50 "数据初始化"

# 实时监看启动过程
docker logs openbookshop_backend -f
```

---

## 🔍 验证数据persistence

### 验证方式 1: 查看容器日志

```bash
docker logs openbookshop_backend

# 预期看到:
# Running database migrations...
# Initializing persistent data...
# 📝 初始化用户账户...
# ✅ 创建: admin
# ✅ 创建: merchant_test
# ✅ 创建: customer_test
# 📊 统计: 新建25本, 已存在0本
```

### 验证方式 2: 在容器内检查数据库

```bash
# 进入后端容器的 Django shell
docker exec -it openbookshop_backend python manage.py shell

# 查看用户
>>> from apps.users.models import User
>>> User.objects.all().values_list('username', 'role')
# 应显示 3 个用户

# 查看书籍
>>> from apps.books.models import Book
>>> Book.objects.count()
# 应显示 25

# 查看商家
>>> from apps.merchants.models import Merchant
>>> Merchant.objects.count()
# 应显示 1

# 退出 shell
>>> exit()
```

### 验证方式 3: 在浏览器中登录

```
用户端: http://127.0.0.1:8080
Login: customer_test / customer123456

商家端: http://127.0.0.1:8080
Login: merchant_test / merchant123456

管理端: http://127.0.0.1:8080
Login: admin / admin123456
```

### 验证方式 4: API 测试

```bash
# 获取书籍列表（验证 25 本书籍已加载）
curl http://127.0.0.1:8000/api/v1/books/ | jq '.data | length'
# 应返回 25

# 用户登录（验证账户存在）
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"customer_test","password":"customer123456"}'
# 应返回 200 + JWT Token
```

---

## ⚠️ 重要注意事项

### 不要做这些操作（会导致数据丢失）

```bash
# ❌ 删除 volume (会删除所有数据)
docker-compose down -v

# ❌ 删除 MySQL 容器过程中的 volume
docker volume rm openbookshop_db_data

# ❌ 直接删除 MySQL 容器
docker rm openbookshop_db
```

### 正确的操作方式

```bash
# ✅ 只停止容器，保留数据
docker-compose down

# ✅ 重启时数据自动恢复
docker-compose up -d

# ✅ 重建镜像但保留数据
docker-compose up -d --build

# ✅ 完全清空（仅在需要重置时）
docker-compose down -v
# 然后重新设置所有数据
```

---

## 🐛 故障排查

### 问题 1: 重启后数据还是丢失

**症状**: 容器重启后找不到书籍或账户

**排查步骤**:
```bash
# 1. 检查 Volume 是否存在
docker volume ls | grep db_data

# 2. 检查启动日志
docker logs openbookshop_backend | grep -i "error\|migrat"

# 3. 检查数据库连接
docker exec openbookshop_backend python manage.py migrate --noinput

# 4. 手动执行初始化脚本
docker exec openbookshop_backend python /app/init_data_persistent.py
```

### 问题 2: 初始化脚本报错

**症状**: 容器启动时 init_data_persistent.py 执行失败

**排查步骤**:
```bash
# 1. 查看完整错误日志
docker logs openbookshop_backend 2>&1 | tail -50

# 2. 进入容器调试
docker exec -it openbookshop_backend bash

# 3. 手动运行脚本
python /app/init_data_persistent.py

# 4. 如果有 Django 问题
python manage.py shell -c "from apps.users.models import User; print(User.objects.all())"
```

### 问题 3: 账户无法登录

**症状**: 用户能看到登录页面，但无法登录

**排查步骤**:
```bash
# 1. 验证密码是否正确（使用 Django auth）
docker exec openbookshop_backend python manage.py shell
>>> from django.contrib.auth import authenticate
>>> result = authenticate(username='customer_test', password='customer123456')
>>> print(result)  # 应该返回 User object

# 2. 验证用户是否激活
>>> from apps.users.models import User
>>> u = User.objects.get(username='customer_test')
>>> print(f"is_active: {u.is_active}, role: {u.role}")

# 3. 直接验证密码 Hash
>>> u.check_password('customer123456')
# 应返回 True
```

---

## 📈 性能优化建议

### 1. 数据库连接优化

当前 `docker-compose.yml` 中 MySQL 配置:
```yaml
healthcheck:
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

这确保数据库完全启动后再执行迁移和初始化。

### 2. 初始化脚本优化

如果初始化很慢，可以考虑:
- 批量插入: using `bulk_create()`
- 异步初始化: 使用 Celery
- 预生成数据: 使用 Django 的 fixtures

### 3. 书籍数据优化

当前 25 本书籍由 `init_data_persistent.py` 初始化，可以升级为:
```python
# 方案 1: 使用 Django fixtures
python manage.py dumpdata > fixtures/initial_books.json
python manage.py loaddata fixtures/initial_books.json

# 方案 2: 使用 CSV 导入
# 编写管理命令 import_books_from_csv
```

---

## 📝 修改说明

### 哪些文件被修改了?

| 文件 | 修改 | 原因 |
|------|------|------|
| `entrypoint.sh` | 添加初始化脚本调用 | 在迁移后执行 init_data_persistent.py |
| `init_data_persistent.py` | 新建文件 | 处理用户、商家、地址、书籍的持久化初始化 |

### 哪些文件没有修改？

- ✅ `Dockerfile` - 已有 `COPY . .`，会自动包含新脚本
- ✅ `docker-compose.yml` - Volume 配置已正确
- ✅ Django models - 无需修改
- ✅ 前端代码 - 无需修改

---

## 🎓 工作原理总结

```
容器启动流程:

1. Docker 构建镜像
   └─ COPY backend/ 所有文件（包括 init_data_persistent.py）

2. Docker 启动容器
   └─ MySQL Volume 自动挂载（持久化存储）

3. entrypoint.sh 执行
   ├─ 步骤 A: python manage.py migrate
   │  └─ 应用所有数据库 Migration
   │
   └─ 步骤 B: python init_data_persistent.py
      ├─ 检查 admin 用户是否存在
      ├─ 如果不存在则创建（第一次启动）
      ├─ 如果存在则跳过（重启或重建时）
      ├─ 创建商家、地址、分类、书籍
      └─ 打印完成摘要

4. Gunicorn 启动
   └─ Django 应用就绪

5. 用户可以登录
   └─ 所有数据已恢复，系统正常工作
```

---

## ✨ 总结

✅ **自动初始化**: 容器启动时自动创建测试账户和书籍  
✅ **数据持久化**: MySQL Volume 保证数据不丢失  
✅ **幂等脚本**: 重启无副作用，不会重复创建  
✅ **完整恢复**: 每次启动都验证所有数据完整性  
✅ **易于维护**: 修改初始化数据只需编辑 Python 脚本  

--

**最后更新**: 2026-03-13  
**状态**: ✅ 生产就绪
