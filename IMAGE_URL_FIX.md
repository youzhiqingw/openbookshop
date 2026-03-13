# 图片加载500/ERR_CONNECTION_REFUSED 修复方案

## 问题分析

用户遇到图片加载失败的两个错误：
1. **500 (Internal Server Error)** - 后端处理图片请求时发生异常
2. **net::ERR_CONNECTION_REFUSED** - 前端无法连接到服务器

**根本原因**：
- 后端序列化器使用 `request.build_absolute_uri()` 生成绝对URL
- 在反向代理(Nginx)环境中，Django接收到的是代理内部的请求信息，而非原始浏览器请求
- 导致生成的图片URL格式错误或指向错误的端口/主机

## 修复实施

### 修改1：BookSerializer (backend/apps/books/serializers.py)

**改动**：`get_cover_url()` 方法
```python
# ❌ 旧方式（在反向代理环境中不稳定）
def get_cover_url(self, obj):
    if obj.cover:
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.cover.url)  # 生成绝对URL
        return obj.cover.url
    return None

# ✅ 新方式（相对路径更稳定）
def get_cover_url(self, obj):
    if obj.cover:
        # 使用相对路径，让前端/Nginx正确处理
        # 相比 request.build_absolute_uri() 更稳定，适用于反向代理环境
        return obj.cover.url  # 例如 /media/book_covers/2809.png
    return None
```

**影响范围**：
- `BookSerializer` (第47-54行)
- `BookListSerializer` (第91-98行)

### 修改2：OrderItem创建 (backend/apps/orders/views.py)

**改动**：订单项创建时的图片URL生成
```python
# ❌ 旧方式
if book.cover:
    cover_url = request.build_absolute_uri(book.cover.url)

# ✅ 新方式
if book.cover:
    # 使用相对路径，让前端/Nginx正确处理
    cover_url = book.cover.url
```

**位置**：第187-189行

## 工作流程（修复后）

### 开发环境 (Vite 5173端口)
```
浏览器
  ↓
Vite Dev Server (localhost:5173)
  ├─ /api → 代理到 http://127.0.0.1:8000
  └─ /media → 代理到 http://127.0.0.1:8000
  ↓
Django Backend (127.0.0.1:8000)
  ├─ API 返回: { cover_url: "/media/book_covers/2809.png" }
  └─ 静态文件: /media/book_covers/2809.png
  ↓
浏览器加载 http://127.0.0.1:5173/media/book_covers/2809.png
  ↓ (Vite 代理)
http://127.0.0.1:8000/media/book_covers/2809.png ✅
```

### Docker容器环境 (Nginx 8080端口)
```
浏览器 (主机)
  ↓
Nginx (容器 127.0.0.1:8080 ← 映射自容器80)
  ├─ /api/ → proxy_pass http://backend:8000
  └─ /media/ → proxy_pass http://backend:8000
  ↓
Django Backend (容器内部 http://backend:8000)
  ├─ API 返回: { cover_url: "/media/book_covers/2809.png" }
  └─ 静态文件: /media/book_covers/2809.png
  ↓
浏览器加载 http://127.0.0.1:8080/media/book_covers/2809.png
  ↓ (Nginx 代理)
http://backend:8000/media/book_covers/2809.png ✅
```

## 验证步骤

### 1. 本地开发环境测试

```bash
# 确保后端运行
cd backend
python manage.py runserver 8000

# 在新终端启动前端
cd frontend
npm run dev

# 打开浏览器访问
http://127.0.0.1:5173
```

**检查项**：
- 浏览器开发者工具 →  Network 标签
- 搜索 `media/book_covers` 请求
- 验证图片返回 200 状态码

### 2. Docker容器环境测试

```bash
# 重建并启动容器
cd openbookshop
docker-compose down
docker-compose up -d --build

# 检查容器日志
docker logs openbookshop_backend

# 在浏览器访问
http://127.0.0.1:8080

# 检查图片请求状态
# 浏览器开发者工具 → Network → 过滤 media
```

### 3. 直接API调用测试

```bash
# 获取书籍列表，查看 cover_url 字段
curl -s http://127.0.0.1:8000/api/v1/books/ | python -m json.tool | grep -A2 "cover_url"

# 预期输出
"cover_url": "/media/book_covers/2809.png",

# 直接访问图片 URL（应该返回200且有图片内容）
curl -I http://127.0.0.1:8000/media/book_covers/2809.png
```

## 关键点总结

| 项目 | 说明 |
|-----|------|
| **使用相对路径** | `/media/book_covers/xxx.png` 而非 `http://...` |
| **让Nginx处理** | 前端无需关心后端真实地址，由Nginx代理解决 |
| **兼容所有环境** | 本地开发、Docker、生产环境均适用 |
| **前端无需修改** | 前端已正确配置代理，只需后端修复 |

## 备选方案（如需完整绝对URL）

如果后续需要返回绝对URL（如生成分享链接、发送邮件等），可在Django settings中添加：

```python
# settings.py
TRUSTED_PROXIES = ['*']  # 或指定具体IP如 ['127.0.0.1']

# nginx.conf
proxy_set_header X-Forwarded-Host $server_name:$server_port;
proxy_set_header X-Forwarded-Proto $scheme;
```

但对于当前的图片加载场景，相对路径已足够。

