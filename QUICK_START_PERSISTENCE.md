# 🚀 容器持久化方案快速启动指南

## ⚡ 快速命令 (复制粘贴即可用)

### 第一次启动

```bash
cd e:\opencode\openbookshop\openbookshop

# 1️⃣  构建并启动所有容器
docker-compose up -d --build

# 2️⃣  查看初始化日志（等待完成）
docker logs openbookshop_backend -f

# 应该看到:
# ✅ 创建: admin
# ✅ 创建: merchant_test
# ✅ 创建: customer_test
# ✅ 创建: 测试书店
# 📖 初始化书籍数据...
# ✅ 创建: 活着
# ... (25本书籍)

# Ctrl+C 退出日志查看
```

### 日常重启 (保留所有数据)

```bash
cd e:\opencode\openbookshop\openbookshop

# 停止容器
docker-compose down

# 重启容器 (数据自动恢复)
docker-compose up -d

# 验证
docker logs openbookshop_backend | grep "初始化完成摘要" -A 20
```

### 完全重置 (删除所有数据)

```bash
cd e:\opencode\openbookshop\openbookshop

# ⚠️  删除所有 Volume (会清空数据库)
docker-compose down -v

# 重新启动 (自动重新初始化)
docker-compose up -d --build

# 等待初始化完成
docker logs openbookshop_backend -f
```

---

## ✅ 验证状态

### 方式 1: 查看初始化摘要

```bash
docker logs openbookshop_backend | grep "数据初始化完成摘要" -A 15
```

**预期输出**:
```
============================================================
📊 数据初始化完成摘要
============================================================

✅ 用户总数: 3
   - admin (管理员)
   - merchant_test (商家)
   - customer_test (普通用户)

✅ 商家总数: 1
   - 测试书店

✅ 分类总数: 12

✅ 书籍总数: 25

✅ 收货地址: 2 (属于customer_test)
   - 北京朝阳区 (默认)
   - 上海浦东新区

🔗 可以立即访问:
   - 用户端: http://127.0.0.1:8080
   - 商家端: http://127.0.0.1:8080
   - 管理端: http://127.0.0.1:8080
   - Django Admin: http://127.0.0.1:8000/admin/
```

### 方式 2: 在容器内检查

```bash
# 查看用户
docker exec openbookshop_backend python manage.py shell -c "from apps.users.models import User; print(f'用户总数: {User.objects.count()}')"
# 应输出: 用户总数: 3

# 查看书籍
docker exec openbookshop_backend python manage.py shell -c "from apps.books.models import Book; print(f'书籍总数: {Book.objects.count()}')"
# 应输出: 书籍总数: 25

# 查看地址
docker exec openbookshop_backend python manage.py shell -c "from apps.users.models import Address; print(f'地址总数: {Address.objects.count()}')"
# 应输出: 地址总数: 2
```

### 方式 3: 浏览器登录测试

| 地址 | 用户名 | 密码 | 预期 |
|------|--------|------|------|
| http://127.0.0.1:8080 | customer_test | customer123456 | ✅ 用户端首页 |
| http://127.0.0.1:8080 | merchant_test | merchant123456 | ✅ 商家后台 |
| http://127.0.0.1:8080 | admin | admin123456 | ✅ 管理后台 |
| http://127.0.0.1:8000/admin/ | admin | admin123456 | ✅ Django Admin |

---

## 📁 文件列表

修改或新增的文件:

```
openbookshop/
├── backend/
│   ├── entrypoint.sh                    ← 【修改】添加初始化脚本调用
│   └── init_data_persistent.py          ← 【新增】数据持久化初始化脚本
└── PERSISTENCE_GUIDE.md                 ← 【新增】完整持久化指南
```

---

## 🔑 核心概念

### 为什么数据能持久化?

1. **MySQL Volume**: 
   - `db_data` Volume 在容器间共享
   - 即使容器删除也保存数据

2. **初始化脚本**:
   - 使用 `get_or_create()` 避免重复创建
   - 重启时自动检查并跳过已存在的数据

3. **多层验证**:
   - 数据库 Migration 确保表结构存在
   - ORM 查询确保数据完整性

### Docker Compose 中的 Volume

```yaml
volumes:
  db_data:  # 定义 Volume

db:
  volumes:
    - db_data:/var/lib/mysql  # MySQL 数据持久化到 Volume
```

---

## 📊 初始化数据内容

### 账户 3 个:
```
admin           | 密码: admin123456  | 超级管理员
merchant_test   | 密码: merchant123456 | 商家
customer_test   | 密码: customer123456 | 普通用户
```

### 商家 1 个:
```
测试书店 (OpenBook Store)
- 所有者: merchant_test
- 状态: 已批准
- 25本书籍都归属此商家
```

### 地址 2 个 (都属于 customer_test):
```
1️⃣  张三 - 北京市朝阳区望京街1号 (默认地址)
2️⃣  李四 - 上海市浦东新区陆家嘴环路100号
```

### 分类 12 个:
```
中国当代文学  | 外国文学    | 自我成长   | 心理学
科幻小说      | 幻想文学    | 历史       | 社科
职场提升      | 人工智能    | 编程       | 计算机
```

### 书籍 25 本:
```
活着、三体、1984、围城、算法导论...等经典书籍
- 所有书籍都有正确的 cover 图片路径
- 库存充足（30-120本）
- 价格合理（28-178元）
```

---

## 🐛 常见问题

### Q: 容器重启后数据是否会丢失?
**A**: 不会。MySQL Volume 保存数据，初始化脚本会检查并跳过已存在的数据。

### Q: 如何修改初始化的账户密码?
**A**: 编辑 `backend/init_data_persistent.py`，修改 `users_data` 字典中的 `password` 字段，然后:
```bash
docker-compose down -v
docker-compose up -d --build
```

### Q: 如何添加更多初始化书籍?
**A**: 编辑 `backend/init_data_persistent.py` 中 `init_books()` 函数内的 `books_data` 列表。

### Q: 为什么初始化很慢?
**A**: MySQL 容器启动需要时间。查看日志:
```bash
docker logs openbookshop_db | grep ready
```

### Q: 如何完全清空数据重新开始?
**A**: 
```bash
docker-compose down -v  # 删除 Volume
docker-compose up -d --build  # 重新初始化
```

---

## 🛠️ 调试命令

### 进入容器交互式 Shell

```bash
docker exec -it openbookshop_backend bash

# 在容器内执行命令
python manage.py shell
python init_data_persistent.py
ls -la /app/media/book_covers/
```

### 查看 MySQL 数据

```bash
# 进入 MySQL 容器
docker exec -it openbookshop_db mysql -u bookshop -pbookshop123 bookstore

# 查看表
SHOW TABLES;

# 查看用户
SELECT id, username, role FROM users_user;

# 查看书籍
SELECT id, title, price FROM books_book;

# 退出
EXIT;
```

### 查看 Volume 信息

```bash
# 列出所有 Volume
docker volume ls

# 查看具体 Volume 信息
docker volume inspect openbookshop_db_data

# 查看 Volume 磁盘大小
du -sh /var/lib/docker/volumes/openbookshop_db_data/_data
```

---

## 📈 监控初始化进度

### 实时查看启动日志

```bash
docker logs openbookshop_backend -f

# 等待看到这些日志:
# 1️⃣  "Collecting static files..." - 10s
# 2️⃣  "Running database migrations..." - 5s
# 3️⃣  "Initializing persistent data..." - 10-20s
# 4️⃣  "🚀 OpenBookShop 数据初始化" - 开始初始化
# 5️⃣  "📊 数据初始化完成摘要" - 完成!
# 6️⃣  "Starting Gunicorn..." - 服务启动
```

### 检查容器是否正常运行

```bash
docker-compose ps

# 应显示 3 个服务都在运行:
# NAME                 STATUS
# openbookshop_backend Up 2 minutes
# openbookshop_frontend Up 2 minutes
# openbookshop_db      Up 2 minutes
```

### API 健康检查

```bash
# 检查后端是否响应
curl -s http://127.0.0.1:8000/api/v1/books/ | jq '.code'
# 应返回: 200

# 检查书籍是否加载
curl -s http://127.0.0.1:8000/api/v1/books/ | jq '.data | length'
# 应返回: 25
```

---

## 🎯 最佳实践

### ✅ DO (应该做)

```bash
# ✅ 日常使用时，用这个停止
docker-compose down
docker-compose up -d

# ✅ 修改代码后，用这个重建
docker-compose up -d --build

# ✅ 查看关键日志时，用这个
docker logs openbookshop_backend -f

# ✅ 需要调试时，用这个
docker exec -it openbookshop_backend bash
```

### ❌ DON'T (不应该做)

```bash
# ❌ 不要用 -v，会删除所有 Volume 和数据
docker-compose down -v  # 只在完全重置时用

# ❌ 不要直接删除容器
docker rm openbookshop_db  # 会很麻烦

# ❌ 不要 kill Volume
docker volume rm openbookshop_db_data  # 数据丢失

# ❌ 不要修改 MySQL 数据目录
rm -rf /var/lib/docker/volumes/openbookshop_db_data/  # 灾难
```

---

## 📞 需要帮助?

1. **查看完整指南**: [PERSISTENCE_GUIDE.md](PERSISTENCE_GUIDE.md)
2. **查看初始化日志**: `docker logs openbookshop_backend`
3. **进入容器调试**: `docker exec -it openbookshop_backend bash`
4. **重置所有数据**: `docker-compose down -v && docker-compose up -d --build`

---

⏰ **最后更新**: 2026-03-13  
✅ **状态**: 生产就绪
