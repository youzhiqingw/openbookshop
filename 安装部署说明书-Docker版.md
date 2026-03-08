# 📦 OpenBookShop 安装部署说明书 — Docker 版

> **适用读者**：有一定 Linux/命令行基础，希望快速在服务器或本地以容器化方式部署本项目的用户。  
> **适用系统**：Linux（推荐 Ubuntu 22.04 / CentOS 7+）、macOS、Windows 10/11（需开启 WSL2 或直接使用 Docker Desktop）。  
> **中国用户提示**：本指南已在关键步骤配置国内镜像（清华大学/阿里云），可大幅提升下载速度。

---

## 目录

1. [环境要求](#1-环境要求)
2. [安装 Docker 与 Docker Compose](#2-安装-docker-与-docker-compose)
3. [获取项目源码](#3-获取项目源码)
4. [配置环境变量](#4-配置环境变量)
5. [构建并启动容器](#5-构建并启动容器)
6. [初始化数据库](#6-初始化数据库)
7. [创建超级管理员](#7-创建超级管理员)
8. [访问系统](#8-访问系统)
9. [日常运维命令](#9-日常运维命令)
10. [使用 MySQL 替换 SQLite（生产推荐）](#10-使用-mysql-替换-sqlite生产推荐)
11. [常见问题排查](#11-常见问题排查)

---

## 1. 环境要求

| 软件 | 最低版本 | 说明 |
|------|---------|------|
| Docker | 20.10+ | 容器运行时 |
| Docker Compose | 2.0+（V2） | 多容器编排 |
| 硬盘空间 | 2 GB+ | 镜像 + 代码 + 数据 |
| 内存 | 1 GB+ | 建议 2 GB 以上 |

> **说明**：Docker Desktop（Windows/macOS）已内置 Docker Compose V2，无需单独安装。

---

## 2. 安装 Docker 与 Docker Compose

### 2.1 Ubuntu / Debian（推荐使用阿里云镜像加速）

```bash
# 卸载旧版本（如有）
sudo apt remove docker docker-engine docker.io containerd runc

# 安装依赖工具
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加阿里云 Docker 软件源（国内加速）
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 将当前用户加入 docker 组（避免每次使用 sudo）
sudo usermod -aG docker $USER
# ⚠️ 执行后需重新登录或运行 newgrp docker 使设置生效

# 验证安装
docker --version
docker compose version
```

### 2.2 CentOS 7 / RHEL 7

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加阿里云 Docker 软件源
sudo yum-config-manager --add-repo \
  https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户加入 docker 组
sudo usermod -aG docker $USER
```

### 2.3 配置 Docker 国内镜像加速（强烈推荐）

编辑或创建 `/etc/docker/daemon.json`：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 2.4 Windows 10/11 安装 Docker Desktop

1. 打开 [Docker Desktop 官网](https://www.docker.com/products/docker-desktop/)，下载 Windows 安装包  
   （国内用户也可在 [阿里云镜像站](https://developer.aliyun.com/mirror/) 搜索 Docker Desktop）
2. 双击安装包，按向导完成安装
3. 安装完毕后，在系统托盘打开 Docker Desktop 界面
4. 进入 **Settings → Docker Engine**，在 JSON 配置中加入镜像加速：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

5. 点击 **Apply & Restart** 使配置生效

---

## 3. 获取项目源码

```bash
# 方法一：使用 Git 克隆（推荐）
git clone https://github.com/youzhiqingw/openbookshop.git
cd openbookshop/openbookshop

# 方法二：下载 ZIP 压缩包
# 访问 https://github.com/youzhiqingw/openbookshop 点击 "Code" → "Download ZIP"
# 解压后进入 openbookshop/openbookshop 目录
```

> **国内用户提示**：若 GitHub 访问缓慢，可尝试使用 Gitee 镜像或配置代理后再克隆。

---

## 4. 配置环境变量

```bash
# 从示例文件复制出实际配置文件
cp .env.example .env

# 用任意文本编辑器打开 .env 并修改以下关键项
nano .env        # Linux / macOS
notepad .env     # Windows（在 PowerShell 中执行）
```

**最少需要修改的配置项：**

| 配置项 | 说明 | 示例值 |
|-------|------|--------|
| `SECRET_KEY` | Django 密钥，**生产环境必须修改** | 见下方生成命令 |
| `DJANGO_DEBUG` | 调试模式，生产环境设 `False` | `False` |
| `ALLOWED_HOSTS` | 允许访问的域名或 IP | `yourdomain.com,127.0.0.1` |

**生成安全随机密钥：**

```bash
# 如果本机已安装 Python
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 5. 构建并启动容器

```bash
# 进入项目目录（包含 docker-compose.yml 的目录）
cd openbookshop/openbookshop

# 构建镜像（首次执行，耗时约 3~10 分钟，取决于网速）
docker compose build

# 在后台启动所有服务
docker compose up -d

# 查看服务运行状态
docker compose ps
```

预期输出示例：

```
NAME                        STATUS          PORTS
openbookshop_backend        running         0.0.0.0:8000->8000/tcp
openbookshop_frontend       running         0.0.0.0:80->80/tcp
openbookshop_db             running         3306/tcp
```

---

## 6. 初始化数据库

```bash
# 执行数据库迁移（首次部署必须运行）
docker compose exec backend python manage.py migrate

# 预期输出：Running migrations: ... OK
```

---

## 7. 创建超级管理员

```bash
docker compose exec backend python manage.py createsuperuser
```

按提示依次输入：
- 用户名（Username）
- 邮箱（Email address）
- 密码（Password，至少 8 位，包含数字）
- 确认密码（Password again）

---

## 8. 访问系统

| 端口/路径 | 说明 |
|-----------|------|
| `http://localhost` 或 `http://服务器IP` | 用户端首页 |
| `http://localhost/admin/login` | 管理端登录 |
| `http://localhost/merchant/login` | 商家端登录 |
| `http://localhost:8000/admin/` | Django 后台（调试用） |

---

## 9. 日常运维命令

```bash
# 查看所有服务日志（实时）
docker compose logs -f

# 只查看后端日志
docker compose logs -f backend

# 停止所有服务
docker compose down

# 停止并删除数据卷（⚠️ 会清空数据库数据，谨慎使用）
docker compose down -v

# 重启某个服务
docker compose restart backend

# 更新代码后重新构建并启动
git pull
docker compose build
docker compose up -d

# 进入后端容器执行命令
docker compose exec backend bash

# 在容器内执行 Django 管理命令
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py showmigrations
```

---

## 10. 使用 MySQL 替换 SQLite（生产推荐）

默认配置使用 SQLite，生产环境建议切换为 MySQL 以获得更好性能。

### 10.1 安装 MySQL 驱动

在 `backend/requirements.txt` 中添加：

```
mysqlclient>=2.2.0
```

### 10.2 修改 Django 数据库配置

编辑 `backend/config/settings.py`，将数据库配置改为：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'bookstore'),
        'USER': os.environ.get('MYSQL_USER', 'bookshop'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'bookshop123'),
        'HOST': os.environ.get('MYSQL_HOST', 'db'),  # Docker 服务名
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### 10.3 重新构建并迁移

```bash
docker compose build backend
docker compose up -d
docker compose exec backend python manage.py migrate
```

---

## 11. 常见问题排查

### Q1：构建镜像时下载速度极慢

**原因**：Docker Hub 在国内访问受限。  
**解决**：确保已按第 2.3/2.4 步配置了国内镜像加速，然后重新执行 `docker compose build`。

---

### Q2：`docker compose` 命令不存在

**原因**：安装的是旧版 Docker Compose V1（`docker-compose`，带连字符）。  
**解决**：

```bash
# V1 用法（兼容）
docker-compose up -d

# 或升级到 V2
sudo apt install docker-compose-plugin
```

---

### Q3：端口 80 或 8000 被占用

**错误信息**：`Bind for 0.0.0.0:80 failed: port is already allocated`  
**解决**：修改 `docker-compose.yml` 中的端口映射，例如将 `"80:80"` 改为 `"8080:80"`：

```yaml
frontend:
  ports:
    - "8080:80"
```

然后访问 `http://localhost:8080`。

---

### Q4：数据库迁移失败

```bash
# 查看详细错误
docker compose exec backend python manage.py migrate --verbosity=2

# 如果报 "table already exists"，可尝试
docker compose exec backend python manage.py migrate --fake-initial
```

---

### Q5：前端页面空白或 API 请求失败

1. 检查后端是否正常运行：`docker compose ps`
2. 查看后端日志：`docker compose logs backend`
3. 在浏览器访问 `http://localhost:8000/api/v1/` 测试后端是否可达
4. 检查 `nginx.conf` 中的 `proxy_pass` 是否与 docker-compose 服务名一致（默认 `backend`）

---

### Q6：Windows 上 Docker Desktop 无法启动

1. 确认已在 BIOS 中开启虚拟化（Intel VT-x / AMD-V）
2. 确认已开启 Windows 功能：**Hyper-V** 和 **适用于 Linux 的 Windows 子系统（WSL2）**
3. 以管理员身份运行 PowerShell 执行：
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```
4. 重启电脑后重试

---

## 附录：项目目录结构（Docker 相关文件）

```
openbookshop/
├── docker-compose.yml          # 多服务编排配置
├── .env.example                # 环境变量示例（复制为 .env 后修改）
├── .env                        # 实际环境变量（不提交到 Git）
├── backend/
│   ├── Dockerfile              # 后端镜像构建文件
│   ├── entrypoint.sh           # 容器启动脚本（migrate + collectstatic + gunicorn）
│   └── ...                     # Django 后端代码
└── frontend/
    ├── Dockerfile              # 前端镜像构建文件（多阶段构建 + Nginx）
    ├── nginx.conf              # Nginx 反向代理配置
    └── ...                     # Vue3 前端代码
```
