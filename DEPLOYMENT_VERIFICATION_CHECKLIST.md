# ✅ 容器持久化部署验证清单

**版本**: 2026-03-13  
**状态**: ✅ 已配置完成  
**目标**: 确保容器重启后所有数据完整保留

---

## 📋 部署前检查

### 文件完整性

- [x] `backend/entrypoint.sh` - 已修改，包含初始化脚本调用
- [x] `backend/init_data_persistent.py` - 已新增，完整的数据初始化脚本
- [x] `backend/apps/books/serializers.py` - 已配置 cover_url 字段
- [x] `backend/Dockerfile` - 自动包含所有 backend 文件
- [x] `backend/requirements.txt` - 已包含所有依赖

### 数据库配置检查

- [x] `docker-compose.yml` - Volume `db_data` 已配置
- [x] MySQL 健康检查 - 30s 启动等待，5 次重试
- [x] 字符集 - UTF8MB4 (支持中文)
- [x] 从属服务依赖 - backend 依赖 db 启动完毕

### 应用配置检查

- [x] Django settings - MEDIA_URL 和 MEDIA_ROOT 配置正确
- [x] 静态文件收集 - 执行一次后不重复
- [x] 数据库迁移 - 幂等执行（migrations 非常安全）
- [x] 初始化脚本 - 使用 get_or_create() 确保幂等性

---

## 🚀 部署步骤

### 步骤 1: 清理环境（首次部署）

```bash
cd e:\opencode\openbookshop\openbookshop

# 确保之前的容器已清理
docker-compose down
docker volume ls | grep openbookshop
```

### 步骤 2: 构建并启动容器

```bash
# 完全重建并启动（包括镜像重建）
docker-compose up -d --build

# 等待日志显示 "Starting Gunicorn..."（约 1-2 分钟）
docker logs openbookshop_backend -f
```

### 步骤 3: 验证初始化完成

在日志中应看到:
```
✅ 创建: admin
✅ 创建: merchant_test
✅ 创建: customer_test
📊 统计: 新建25本, 已存在0本
📊 数据初始化完成摘要
Starting Gunicorn...
```

### 步骤 4: 浏览器测试

访问以下 URL（3 个都应成功）:
- http://127.0.0.1:8080 (前端正常)
- http://127.0.0.1:8000/api/v1/books/ (后端正常)
- http://127.0.0.1:8000/admin/ (Django Admin 正常)

---

## 🧪 下面进行验证测试

### 测试 1: 用户登录验证

#### 1.1 超级管理员登录
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123456"
  }'
```

**预期响应** (200 OK):
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": X,
      "username": "admin",
      "role": "admin",
      "is_staff": true
    },
    "tokens": {
      "access": "eyJ0eXAiOi...",
      "refresh": "eyJ0eXAiOi..."
    }
  }
}
```

#### 1.2 商家登录
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "merchant_test",
    "password": "merchant123456"
  }'
```

**预期**: 200 OK，返回 JWT Token

#### 1.3 普通用户登录
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer_test",
    "password": "customer123456"
  }'
```

**预期**: 200 OK，返回 JWT Token

### 测试 2: 书籍数据验证

```bash
# 获取书籍列表
curl http://127.0.0.1:8000/api/v1/books/ | jq '.'

# 检查返回的数据
# - code 应该是 200
# - data 应该包含 25 本书籍
# - 每本书籍都有 cover_url 字段（完整的 HTTP URL）
```

**预期响应结构**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "活着",
      "author": "余华",
      "cover": "book_covers/Library02.png",
      "cover_url": "http://127.0.0.1:8000/media/book_covers/Library02.png",
      "price": "29.80",
      "stock": 100,
      "is_on_sale": true
    },
    ...
  ]
}
```

### 测试 3: 地址数据验证

```bash
# 先登录获取 token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"customer_test","password":"customer123456"}' | jq -r '.data.tokens.access')

# 获取用户的收货地址
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/v1/users/addresses/
```

**预期**: 返回 2 个地址
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "张三",
      "phone": "13800138000",
      "province": "北京市",
      "city": "朝阳区",
      "is_default": true
    },
    {
      "id": 2,
      "name": "李四",
      "phone": "13900139000",
      "province": "上海市",
      "city": "浦东新区",
      "is_default": false
    }
  ]
}
```

### 测试 4: 购物功能验证

```bash
# 使用之前获取的 token

# 1. 加入购物车
curl -X POST http://127.0.0.1:8000/api/v1/orders/cart/add/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "quantity": 2}'

# 2. 查看购物车
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/v1/orders/cart/

# 3. 创建订单
curl -X POST http://127.0.0.1:8000/api/v1/orders/create/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address_id": 1,
    "cart_item_ids": [1],
    "remark": "测试订单"
  }'
```

**预期**: 所有请求都返回 200 OK，订单成功创建

### 测试 5: 容器重启数据持久化验证

```bash
# 1. 停止容器（不删除 volume）
docker-compose down

# 2. 重启容器
docker-compose up -d

# 3. 等待初始化完成（查看日志中的"已存在"状态）
docker logs openbookshop_backend | grep "⏭️"

# 4. 重新登录验证
curl -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"customer_test","password":"customer123456"}'

# 5. 验证书籍数据
curl http://127.0.0.1:8000/api/v1/books/ | jq '.data | length'
# 应该返回: 25
```

**预期日志输出** (重启时):
```
📝 初始化用户账户...
   ⏭️  已存在: admin
   ⏭️  已存在: merchant_test
   ⏭️  已存在: customer_test

🏪 初始化商家...
   ⏭️  已存在: 测试书店

📍 初始化收货地址...
   ⏭️  已存在: 张三 - 北京市朝阳区

📖 初始化书籍数据...
   📊 统计: 新建0本, 已存在25本

✨ 所有数据初始化完成！
```

---

## 🌐 前端 UI 验证

### 用户端验证

```
URL: http://127.0.0.1:8080
账户: customer_test / customer123456

验证项：
✅ 登录成功
✅ 首页显示 25 本书籍的封面图片
✅ 点击书籍可查看详情
✅ 加入购物车功能正常
✅ 购物车显示正确数量
✅ 能看到 2 个收货地址
✅ 能成功创建订单
```

### 商家端验证

```
URL: http://127.0.0.1:8080/merchant/login
账户: merchant_test / merchant123456

验证项：
✅ 登录成功进入商家后台
✅ 店铺名显示为 "测试书店"
✅ 商品列表显示 25 本书籍
✅ 能查看销售统计
✅ 能查看订单列表
```

### 管理端验证

```
URL: http://127.0.0.1:8080/admin/login
账户: admin / admin123456

验证项：
✅ 登录成功进入管理后台
✅ 用户管理显示 3 个账户
✅ 商家管理显示 1 个商家
✅ 书籍管理显示 25 本书
✅ 订单管理显示创建的订单
```

### Django Admin 验证

```
URL: http://127.0.0.1:8000/admin/
账户: admin / admin123456

验证项：
✅ 登录成功进入 Django Admin
✅ Users 显示 3 个用户
✅ Merchants 显示 1 个商家
✅ Books 显示 25 本书籍
✅ Categories 显示 12 个分类
```

---

## 📊 性能检查

### 响应时间验证

```bash
# 书籍列表响应时间（应 < 200ms）
time curl -s http://127.0.0.1:8000/api/v1/books/ > /dev/null

# 登录响应时间（应 < 300ms）
time curl -s -X POST http://127.0.0.1:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}' > /dev/null

# 数据库连接检查（应 < 10ms）
docker exec openbookshop_backend python manage.py dbshell -c "SELECT 1;" 2>&1 | tail -1
```

### 容器资源检查

```bash
# 检查容器资源使用情况
docker stats openbookshop_backend openbookshop_frontend openbookshop_db --no-stream

# 预期：
# - 内存使用: backend < 200MB, frontend < 50MB, db < 150MB
# - CPU 使用: < 10% (启动时可能高一些)
```

---

## 📁 文件清单

所有文件都应该存在且正确：

```
✅ e:\opencode\openbookshop\openbookshop\
   ├── backend/
   │   ├── entrypoint.sh                 (修改: 添加初始化脚本)
   │   ├── init_data_persistent.py       (新增: 核心初始化脚本)
   │   ├── Dockerfile                    (无修改: COPY . 自动包含)
   │   ├── apps/books/serializers.py     (无修改: 已有 cover_url)
   │   └── media/book_covers/            (已有: 34 张图片)
   │
   ├── docker-compose.yml                (无修改: Volume 已配置)
   └── PERSISTENCE_GUIDE.md              (新增: 完整指南)
   └── QUICK_START_PERSISTENCE.md        (新增: 快速启动指南)
```

---

## 🎯 验证检查清单

### 初始化完成（首次启动）
- [ ] 查看日志中的"✅ 创建: admin"
- [ ] 查看日志中的"✅ 创建: merchant_test"
- [ ] 查看日志中的"✅ 创建: customer_test"
- [ ] 查看日志中的"📊 统计: 新建25本"
- [ ] Gunicorn 成功启动

### 数据完整性（首次启动）
- [ ] `curl http://127.0.0.1:8000/api/v1/books/ | jq '.data | length'` → 25
- [ ] `SELECT COUNT(*) FROM users_user;` → 3
- [ ] `SELECT COUNT(*) FROM books_book;` → 25
- [ ] `SELECT COUNT(*) FROM merchants_merchant;` → 1
- [ ] `SELECT COUNT(*) FROM users_address;` → 2

### 登录功能
- [ ] admin 登录成功
- [ ] merchant_test 登录成功
- [ ] customer_test 登录成功

### 图片显示
- [ ] 首页书籍封面图片全部显示
- [ ] API 返回 cover_url 为完整 URL
- [ ] 图片通过 nginx 正确代理

### 容器持久化
- [ ] `docker-compose down`
- [ ] `docker-compose up -d`
- [ ] 查看日志中的"⏭️ 已存在: merchant_test"
- [ ] 重新登录成功
- [ ] 书籍数据仍为 25 本

### 浏览器测试
- [ ] 用户端能登录并浏览书籍
- [ ] 商家端能登录进入后台
- [ ] 管理端能登录进入后台
- [ ] 购物车功能正常
- [ ] 能成功创建订单

---

## 🐛 问题排查

### 如果初始化脚本报错

```bash
# 查看完整错误日志
docker logs openbookshop_backend 2>&1 | tail -100

# 进入容器手动运行脚本
docker exec -it openbookshop_backend bash
python init_data_persistent.py

# 检查 Django 环境
python manage.py shell -c "from apps.users.models import User; print(User.objects.count())"
```

### 如果数据重启后丢失

```bash
# 检查 Volume 是否仍存在
docker volume ls | grep db_data

# 查看 Volume 详情
docker volume inspect openbookshop_db_data

# 检查 MySQL 数据目录
ls -la /var/lib/docker/volumes/openbookshop_db_data/_data/bookstore/
```

### 如果登录失败

```bash
# 检查用户是否存在
docker exec openbookshop_backend python manage.py shell
>>> from apps.users.models import User
>>> User.objects.all()

# 验证密码
>>> u = User.objects.get(username='customer_test')
>>> u.check_password('customer123456')
# 应返回 True
```

---

## 📞 支持

- 查看完整文档: [PERSISTENCE_GUIDE.md](PERSISTENCE_GUIDE.md)
- 快速启动指南: [QUICK_START_PERSISTENCE.md](QUICK_START_PERSISTENCE.md)
- 查看初始化脚本: [backend/init_data_persistent.py](backend/init_data_persistent.py)

---

**最后更新**: 2026-03-13  
**状态**: ✅ 验证清单完成  
**下一步**: 执行部署并运行所有验证测试
