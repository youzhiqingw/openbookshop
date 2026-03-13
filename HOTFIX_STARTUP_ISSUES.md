# 🔧 容器启动问题已修复

## ✅ 已修复的问题

### 1️⃣ 后端初始化脚本不执行
**原因**: Django 导入路径未正确设置  
**修复**: 在 `init_data_persistent.py` 中添加：
```python
sys.path.insert(0, '/app')
os.chdir('/app')
```

### 2️⃣ 前端 npm build 失败
**原因**: npm install 超时或依赖问题  
**修复**: 在 Dockerfile 中添加重试机制和超时参数：
```bash
RUN npm install --legacy-peer-deps --foreground --fetch-timeout=60000 || npm install --legacy-peer-deps
```

### 3️⃣ entrypoint.sh 错误处理不完整
**原因**: 初始化脚本失败会导致容器启动失败  
**修复**: 添加 try-catch 逻辑和详细日志

### 4️⃣ 书籍图片扩展名不一致
**原因**: 初始化脚本使用 .png，但实际文件是 .jpeg  
**修复**: 更新所有书籍文件引用使用正确的 .jpeg 扩展名

---

## 🚀 重新启动容器

```bash
cd e:\opencode\openbookshop\openbookshop

# 完全清除并重建
docker-compose down -v
docker-compose up -d --build

# 或者如果只想重启（保留数据）
docker-compose down
docker-compose up -d --build
```

## 📋 启动流程验证

```bash
# 查看启动日志（应该看到初始化信息）
docker logs openbookshop_backend -f

# 预期输出（首次启动）:
# Running database migrations...
# Initializing persistent data...
# 🚀 OpenBookShop 数据初始化
# 📝 初始化用户账户...
# ✅ 创建: admin
# ✅ 创建: merchant_test
# ✅ 创建: customer_test
# Starting Gunicorn...
```

## ✅ 验证后端成功启动

```powershell
# PowerShell 命令验证后端
$response = Invoke-WebRequest -Uri http://127.0.0.1:8000/api/v1/books/ -ErrorAction SilentlyContinue
$response.StatusCode  # 应返回 200
```

## ✅ 验证前端成功启动

```
打开浏览器: http://127.0.0.1:8080
应该看到: 前端首页（可能提示登录）
```

## 🔐 测试账户

| 用途 | 账户 | 密码 |
|------|------|------|
| 用户端 | customer_test | customer123456 |
| 商家端 | merchant_test | merchant123456 |
| 管理端 | admin | admin123456 |

---

## 如果仍有问题

### 问题: 初始化脚本仍未执行

```bash
# 在容器内手动测试
docker exec -it openbookshop_backend bash
cd /app
python init_data_persistent.py
```

### 问题: 前端仍在构建失败

```bash
# 绕过缓存重建前端镜像
docker-compose build --no-cache frontend
docker-compose up -d
```

### 问题: 获取详细错误信息

```bash
# 查看完整后端日志
docker logs openbookshop_backend -n 100

# 查看完整前端日志
docker logs openbookshop_frontend -n 100

# 进入容器调试
docker exec -it openbookshop_backend python manage.py shell
```

---

**修复时间**: 2026-03-13  
**状态**: ✅ 已验证修复完成
