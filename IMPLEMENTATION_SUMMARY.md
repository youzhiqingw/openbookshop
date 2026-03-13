# 🎯 容器持久化方案 - 实施总结

## 📝 需求

确保容器重启后，以下数据完整保留：
- ✅ 测试账户（admin, merchant_test, customer_test）
- ✅ 商家信息（测试书店）
- ✅ 书籍数据（25本）+ 图片（PNG/png）
- ✅ 收货地址（2个）

---

## 🛠️ 实施方案

### 核心文件

#### 1. `backend/init_data_persistent.py` 【新增】
- **作用**: Django 应用启动时自动初始化所有数据
- **特性**: 
  - 使用 `get_or_create()` 确保幂等性
  - 重启无副作用、无重复创建
  - Django ORM 密码 Hash 安全
  - 详细日志输出

#### 2. `backend/entrypoint.sh` 【修改】
```bash
# 修改内容：在 migrations 之后添加
python /app/init_data_persistent.py
```

#### 3. `docker-compose.yml` 【无修改】
- SQLitedata Volume 已配置，无需改动
- 数据库 MySQL 启动后自动挂载 Volume

---

## ⚡ 快速开始

### 首次启动（5-10分钟）
```bash
cd e:\opencode\openbookshop\openbookshop
docker-compose up -d --build
```

### 日常重启（数据自动恢复）
```bash
docker-compose down
docker-compose up -d
```

### 查看初始化过程
```bash
docker logs openbookshop_backend -f
```

---

## ✅ 验证方法

### 方式1: 查看日志摘要
```bash
docker logs openbookshop_backend | grep "数据初始化完成摘要" -A 15
```
应该看到: 3个用户，25本书籍，2个地址

### 方式2: 容器内检查
```bash
# 用户总数
docker exec openbookshop_backend python manage.py shell -c "from apps.users.models import User; print(f'用户: {User.objects.count()}')"

# 书籍总数
docker exec openbookshop_backend python manage.py shell -c "from apps.books.models import Book; print(f'书籍: {Book.objects.count()}')"
```

### 方式3: 浏览器登录
```
用户端: http://127.0.0.1:8080
账户: customer_test / customer123456

商家端: http://127.0.0.1:8080
账户: merchant_test / merchant123456

管理端: http://127.0.0.1:8080
账户: admin / admin123456
```

---

## 📊 初始化数据

| 类型 | 数据 | 说明 |
|------|------|------|
| **账户** | admin | 密码: admin123456 (超级管理员) |
| | merchant_test | 密码: merchant123456 (商家) |
| | customer_test | 密码: customer123456 (普通用户) |
| **商家** | 测试书店 | 状态: 已批准，所属: merchant_test |
| **地址** | 北京朝阳 | 默认地址，所属: customer_test |
| | 上海浦东 | 备选地址，所属: customer_test |
| **分类** | 12 个 | 中国/外国文学、编程、人工智能等 |
| **书籍** | 25 本 | 所有都有正确的图片路径 |

---

## 🧪 重启后数据持久化验证

```bash
# 1. 停止容器
docker-compose down

# 2. 重启容器
docker-compose up -d

# 3. 查看初始化日志（应看到"⏭️  已存在"而不是"✅ 创建"）
docker logs openbookshop_backend | grep "⏭️"

# 4. 验证书籍数量仍为 25
curl http://127.0.0.1:8000/api/v1/books/ | jq '.data | length'

# 5. 验证账户仍存在
docker exec openbookshop_backend python manage.py shell -c "from apps.users.models import User; print(User.objects.all())"
```

---

## 🔄 工作原理

```
Docker Start
  ↓
Dockerfile COPY (复制 init_data_persistent.py)
  ↓
entrypoint.sh 执行
  ├─ migrations (创建表结构，幂等)
  ├─ init_data_persistent.py (创建/检查数据，幂等)
  │  ├─ 首次启动: ✅ 创建 admin, merchant_test, ...
  │  └─ 重启时: ⏭️  已存在, ⏭️  已存在, ... (跳过)
  └─ gunicorn (启动服务)
  ↓
应用就绪，用户可登录 ✅
```

**关键**: Volume 中的 MySQL 数据在容器间共享，无需重新创建

---

## 📁 文件清单

### 新增文件
- ✅ `backend/init_data_persistent.py` - 初始化脚本
- ✅ `PERSISTENCE_GUIDE.md` - 完整指南
- ✅ `QUICK_START_PERSISTENCE.md` - 快速开始
- ✅ `DEPLOYMENT_VERIFICATION_CHECKLIST.md` - 验证清单
- ✅ `PERSISTENCE_SOLUTION_SUMMARY.md` - 方案总结

### 修改文件
- ✏️ `backend/entrypoint.sh` - 添加初始化脚本调用

### 无需修改
- ✅ `docker-compose.yml` - Volume 已正确配置
- ✅ Django models - 表结构无变化
- ✅ 前端代码 - 无需修改

---

## ⚠️ 注意事项

### ✅ 正确做法
```bash
docker-compose down           # 停止容器（保留数据）
docker-compose up -d          # 重启（数据自动恢复）
docker-compose up -d --build  # 修改代码后重建（保留数据）
```

### ❌ 禁止操作
```bash
docker-compose down -v        # ❌ 删除 Volume，数据丢失！
docker rm openbookshop_db     # ❌ 直接删除容器！
rm -rf /var/lib/docker/volumes/openbookshop_db_data/  # ❌ 灾难！
```

---

## 📈 现在可以做什么

✅ 安心地重启容器，数据完整保留  
✅ 修改代码后重建镜像，无需重新初始化数据  
✅ 整支团队共享相同的初始数据快照  
✅ 在生产环境中放心部署  

---

## 📚 完整文档

| 文档 | 用途 |
|------|------|
| [PERSISTENCE_GUIDE.md](PERSISTENCE_GUIDE.md) | 📖 基础架构和原理 |
| [QUICK_START_PERSISTENCE.md](QUICK_START_PERSISTENCE.md) | ⚡ 快速命令和验证 |
| [DEPLOYMENT_VERIFICATION_CHECKLIST.md](DEPLOYMENT_VERIFICATION_CHECKLIST.md) | ✅ 部署前检查清单 |
| [PERSISTENCE_SOLUTION_SUMMARY.md](PERSISTENCE_SOLUTION_SUMMARY.md) | 📋 完整方案说明 |

---

## 🆘 故障排查

### 问题: 初始化脚本报错
```bash
docker logs openbookshop_backend 2>&1 | tail -50
```

### 问题: 数据重启后丢失
```bash
# 检查 Volume 是否存在
docker volume ls | grep db_data

# 检查 MySQL 数据目录
docker exec openbookshop_db ls -la /var/lib/mysql/bookstore/
```

### 问题: 登录失败
```bash
# 在容器内验证
docker exec openbookshop_backend python manage.py shell
>>> from apps.users.models import User
>>> u = User.objects.get(username='customer_test')
>>> u.check_password('customer123456')  # 应返回 True
```

---

## 🎓 总结

这个方案通过 **Python 初始化脚本 + MySQL Volume 持久化**，实现了：
- ✅ 自动化初始化
- ✅ 数据完整保留
- ✅ 幂等操作（安全重启）
- ✅ 生产就绪

**立即开始使用**:
```bash
docker-compose up -d --build
```

---

**最后更新**: 2026-03-13  
**状态**: ✅ 完全就绪
