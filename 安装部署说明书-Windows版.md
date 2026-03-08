# 💻 OpenBookShop 安装部署说明书 — Windows 版

> **适用读者**：在 Windows 10/11 系统上进行本地开发或演示的用户。  
> **适用系统**：Windows 10 21H2 及以上版本，Windows 11 所有版本。  
> **中国用户提示**：本指南已在关键步骤配置国内镜像（清华大学/阿里云），可大幅提升下载速度。

---

## 目录

1. [环境要求](#1-环境要求)
2. [安装基础软件](#2-安装基础软件)
3. [获取项目源码](#3-获取项目源码)
4. [后端部署（Django）](#4-后端部署django)
5. [前端部署（Vue3）](#5-前端部署vue3)
6. [访问系统](#6-访问系统)
7. [一键启动脚本](#7-一键启动脚本)
8. [常见问题排查](#8-常见问题排查)

---

## 1. 环境要求

| 软件 | 最低版本 | 用途 |
|------|---------|------|
| Python | 3.11+ | 运行 Django 后端 |
| Node.js | 18 LTS+ | 编译/运行 Vue3 前端 |
| Git | 任意版本 | 克隆代码仓库 |
| 操作系统 | Windows 10 21H2+ | - |

> **推荐**：安装 Windows Terminal，获得更好的命令行体验。

---

## 2. 安装基础软件

### 2.1 安装 Python 3.11+

**方法一：官网下载（推荐）**

1. 访问 [Python 官网](https://www.python.org/downloads/windows/)，下载最新 Python 3.11.x 安装包  
   国内备用下载：[华为镜像站](https://mirrors.huaweicloud.com/python/) 或 [淘宝镜像站](https://registry.npmmirror.com/binary.html?path=python/)
2. 双击安装包，**务必勾选 "Add Python to PATH"**（添加到系统路径）
3. 选择 "Customize installation"，建议勾选 "pip" 和 "for all users"
4. 点击 "Install Now" 完成安装

**验证安装：**

```powershell
# 打开 PowerShell 或命令提示符（Win + R → 输入 cmd）
python --version
# 预期输出：Python 3.11.x

pip --version
# 预期输出：pip xx.x.x from ...
```

### 2.2 配置 pip 国内镜像（强烈推荐）

```powershell
# 设置清华大学 pip 镜像（一次配置，永久生效）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 验证配置
pip config list
```

### 2.3 安装 Node.js 18 LTS

**方法一：直接下载安装包**

1. 访问 [Node.js 官网](https://nodejs.org/zh-cn/)，下载 **LTS（长期支持）** 版本  
   国内备用下载：[阿里云镜像](https://registry.npmmirror.com/binary.html?path=node/)
2. 双击 `.msi` 安装包，按向导完成安装（默认选项即可）
3. 安装完成后打开新的 PowerShell 窗口验证：

```powershell
node --version
# 预期输出：v18.x.x 或 v20.x.x

npm --version
# 预期输出：9.x.x 或 10.x.x
```

**方法二：使用 nvm-windows（推荐，方便管理多版本）**

1. 下载 [nvm-windows](https://github.com/coreybutler/nvm-windows/releases)，安装 `nvm-setup.exe`
2. 安装完成后在 PowerShell 中执行：

```powershell
nvm install 18
nvm use 18
node --version
```

### 2.4 配置 npm 国内镜像（强烈推荐）

```powershell
# 设置阿里云 npm 镜像（一次配置，永久生效）
npm config set registry https://registry.npmmirror.com

# 验证配置
npm config get registry
# 预期输出：https://registry.npmmirror.com
```

### 2.5 安装 Git

1. 访问 [Git 官网](https://git-scm.com/download/win) 下载安装包  
   国内备用：[腾讯云镜像](https://mirrors.cloud.tencent.com/git-for-windows/)
2. 按默认选项安装（推荐选择 "Git Bash Here" 右键菜单选项）
3. 验证安装：

```powershell
git --version
# 预期输出：git version 2.x.x.windows.x
```

---

## 3. 获取项目源码

打开 **PowerShell** 或 **命令提示符**，执行：

```powershell
# 克隆项目到本地
git clone https://github.com/youzhiqingw/openbookshop.git

# 进入项目目录
cd openbookshop\openbookshop
```

> **国内用户提示**：若 GitHub 访问缓慢，可尝试：  
> - 使用 Gitee 导入的镜像仓库克隆  
> - 直接在 GitHub 页面下载 ZIP 压缩包后解压

项目目录结构如下：

```
openbookshop\openbookshop\
├── backend\        # Django 后端
├── frontend\       # Vue3 前端
├── docs\           # 项目文档
└── README.md
```

---

## 4. 后端部署（Django）

### 4.1 进入后端目录

```powershell
cd backend
```

### 4.2 创建 Python 虚拟环境

```powershell
# 创建虚拟环境（隔离项目依赖，避免影响系统 Python）
python -m venv venv

# 激活虚拟环境（Windows 专用命令）
venv\Scripts\activate
```

激活成功后，命令提示符前会出现 `(venv)` 前缀，例如：

```
(venv) PS C:\...\backend>
```

> **常见错误**：若出现 "无法加载文件，因为在此系统上禁止运行脚本" 错误，  
> 请以管理员身份运行 PowerShell 并执行：  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 4.3 安装后端依赖

```powershell
# 确保已激活虚拟环境（前面有 (venv)）
pip install -r requirements.txt
```

依赖安装完成后，主要包含：

| 包名 | 说明 |
|------|------|
| Django 4.x | Web 框架 |
| djangorestframework | RESTful API 支持 |
| djangorestframework-simplejwt | JWT 认证 |
| django-cors-headers | 跨域请求支持 |
| Pillow | 图片处理 |
| python-dotenv | 环境变量管理 |

### 4.4 配置环境变量（可选，开发环境可跳过）

在 `backend` 目录下创建 `.env` 文件（可直接新建文本文件并重命名）：

```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-dev-key-only-for-local
DJANGO_ALLOWED_HOSTS=*
```

### 4.5 执行数据库迁移

```powershell
# 生成迁移文件（如有新模型修改时使用）
python manage.py makemigrations

# 执行迁移，创建数据库表（首次部署必须运行）
python manage.py migrate
```

预期输出（截取）：

```
Operations to perform:
  Apply all migrations: admin, auth, books, contenttypes, merchants, orders, sessions, token_blacklist, users
Running migrations:
  Applying contenttypes.0001_initial... OK
  ...
  Applying users.0001_initial... OK
```

### 4.6 创建超级管理员账户

```powershell
python manage.py createsuperuser
```

按提示输入：

```
用户名 (leave blank to use 'xxx'): admin
邮件地址: admin@example.com
Password: (至少 8 位，包含数字，不会显示输入内容)
Password (again): 
Superuser created successfully.
```

### 4.7 启动后端开发服务器

```powershell
python manage.py runserver
```

成功后输出：

```
Django version 4.2.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

> ✅ 后端服务已运行在 **http://127.0.0.1:8000**

---

## 5. 前端部署（Vue3）

**新开一个 PowerShell 窗口**（保持后端服务在另一个窗口中运行），执行以下命令：

### 5.1 进入前端目录

```powershell
# 从项目根目录进入前端目录
cd openbookshop\openbookshop\frontend
```

### 5.2 安装前端依赖

```powershell
npm install
```

安装的主要依赖：

| 包名 | 说明 |
|------|------|
| vue 3.x | 前端框架 |
| vue-router 4.x | 路由管理 |
| pinia 2.x | 状态管理 |
| element-plus | UI 组件库 |
| axios | HTTP 客户端 |
| echarts | 数据可视化图表 |
| vite | 构建工具 |

### 5.3 启动前端开发服务器

```powershell
npm run dev
```

成功后输出：

```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://x.x.x.x:5173/
```

> ✅ 前端服务已运行在 **http://localhost:5173**  
> Vite 已自动将 `/api` 请求代理到后端 `http://127.0.0.1:8000`

### 5.4 编译前端（生产构建）

如需将前端编译为静态文件（部署到服务器时使用）：

```powershell
npm run build
```

构建产物位于 `frontend\dist\` 目录，可将该目录下所有文件部署到任意 Web 服务器（Nginx、IIS 等）。

---

## 6. 访问系统

确保后端和前端服务均已启动后，在浏览器中访问：

| 地址 | 说明 |
|------|------|
| [http://localhost:5173](http://localhost:5173) | 用户端首页 |
| [http://localhost:5173/admin/login](http://localhost:5173/admin/login) | 管理端登录 |
| [http://localhost:5173/merchant/login](http://localhost:5173/merchant/login) | 商家端登录 |
| [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Django 后台（调试用） |

**默认管理员账户**：您在第 4.6 步自行创建的用户名和密码。

---

## 7. 一键启动脚本

在 `openbookshop\openbookshop` 目录下创建如下两个脚本，方便日后快速启动。

### 启动后端（start-backend.bat）

在该目录新建文件 `start-backend.bat`，内容如下：

```bat
@echo off
chcp 65001 >nul
title OpenBookShop 后端服务

cd /d "%~dp0backend"

if not exist venv\Scripts\activate (
    echo 正在创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate
echo 后端服务启动中，访问地址：http://127.0.0.1:8000
python manage.py runserver
pause
```

### 启动前端（start-frontend.bat）

在该目录新建文件 `start-frontend.bat`，内容如下：

```bat
@echo off
chcp 65001 >nul
title OpenBookShop 前端服务

cd /d "%~dp0frontend"

echo 前端服务启动中，访问地址：http://localhost:5173
npm run dev
pause
```

双击对应 `.bat` 文件即可启动对应服务。

---

## 8. 常见问题排查

### Q1：`python` 命令未找到

**原因**：Python 安装时未勾选 "Add Python to PATH"。  
**解决**：

1. 重新安装 Python，并在安装界面勾选 "Add Python to PATH"
2. 或手动添加环境变量：  
   右键"此电脑" → 属性 → 高级系统设置 → 环境变量 → 在 Path 中添加 Python 安装目录（如 `C:\Python311\` 和 `C:\Python311\Scripts\`）

---

### Q2：`pip install` 超时或失败

**原因**：默认从 pypi.org 下载，国内访问较慢。  
**解决**：确保已按 2.2 步配置了清华镜像，或临时指定镜像：

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Q3：虚拟环境激活失败（脚本执行策略）

**错误信息**：`venv\Scripts\activate : 无法加载文件，因为在此系统上禁止运行脚本`  
**解决**：

```powershell
# 以管理员身份运行 PowerShell，然后执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Q4：`npm install` 速度慢或失败

**原因**：默认从 npm 官方源下载，国内访问较慢。  
**解决**：确保已按 2.4 步配置了阿里云镜像，或临时指定：

```powershell
npm install --registry https://registry.npmmirror.com
```

---

### Q5：端口 8000 已被占用

**错误信息**：`Error: That port is already in use.`  
**解决**：使用其他端口启动后端：

```powershell
python manage.py runserver 8001
```

同时修改 `frontend\vite.config.js` 中的代理目标：

```javascript
proxy: {
  '/api': { target: 'http://127.0.0.1:8001', changeOrigin: true },
  '/media': { target: 'http://127.0.0.1:8001', changeOrigin: true },
}
```

---

### Q6：前端访问出现跨域错误（CORS）

**错误信息**：浏览器控制台显示 `CORS policy` 相关错误  
**原因**：开发环境已开启 CORS 全部放行（`CORS_ALLOW_ALL_ORIGINS = True`），出现此错误通常是后端未启动或地址配置错误。  
**解决**：
1. 确认后端正在 `127.0.0.1:8000` 运行
2. 确认 Vite 代理配置正确
3. 检查浏览器请求地址是否走了 Vite 代理（通过 `localhost:5173` 访问，而非直接访问 `8000`）

---

### Q7：数据库迁移报错

```
django.db.utils.OperationalError: no such table: ...
```

**解决**：

```powershell
# 重新执行迁移
python manage.py makemigrations
python manage.py migrate
```

---

### Q8：静态文件/图片无法显示

**原因**：开发环境下 Django 自动处理静态文件，若图片路径无法访问，检查 `media` 目录权限。  
**解决**：确保 `backend\media\` 目录存在，若不存在手动创建：

```powershell
mkdir backend\media
```

---

## 附录 A：完整命令速查表

### 后端命令（在 `backend` 目录，激活虚拟环境后执行）

```powershell
# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver

# 收集静态文件（部署前）
python manage.py collectstatic

# 进入 Django Shell
python manage.py shell

# 运行测试
python manage.py test
```

### 前端命令（在 `frontend` 目录执行）

```powershell
# 安装依赖
npm install

# 启动开发服务器（含热重载）
npm run dev

# 生产环境构建
npm run build

# 预览生产构建结果
npm run preview
```

---

## 附录 B：推荐开发工具

| 工具 | 用途 | 下载地址 |
|------|------|---------|
| Visual Studio Code | 代码编辑器 | https://code.visualstudio.com/ |
| VS Code Python 扩展 | Python 语法高亮、调试 | VS Code 扩展市场搜索 "Python" |
| VS Code Volar 扩展 | Vue3 语法支持 | VS Code 扩展市场搜索 "Vue - Official" |
| Windows Terminal | 更好的命令行体验 | 微软应用商店搜索 "Windows Terminal" |
| Postman / Apifox | API 接口测试 | https://www.apifox.com/（国内推荐） |
| DBeaver | 数据库可视化管理 | https://dbeaver.io/ |

---

## 附录 C：系统三端登录说明

| 端 | 访问路径 | 账号创建方式 |
|----|---------|------------|
| **管理端** | `/admin/login` | 通过 `createsuperuser` 命令创建，或在 Django 后台设置 `is_staff=True` |
| **商家端** | `/merchant/login` | 普通用户注册后，由管理员在管理端审核通过商家申请 |
| **用户端** | `/` (首页) | 通过注册页面正常注册 |
