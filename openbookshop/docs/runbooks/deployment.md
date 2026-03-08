# 部署运维手册

## 开发环境

### 后端启动
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 生产环境部署

### 使用 Docker
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 执行迁移
docker-compose exec backend python manage.py migrate

# 创建管理员
docker-compose exec backend python manage.py createsuperuser
```

### 手动部署 (Linux + Nginx + Gunicorn + MySQL)

#### 1. 环境准备
```bash
# 安装依赖
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server

# 创建数据库
sudo mysql -u root -p
CREATE DATABASE bookstore CHARACTER SET utf8mb4;
```

#### 2. 后端部署
```bash
cd /var/www/bookstore/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn mysqlclient

# 修改 settings_prod.py
# - DEBUG = False
# - ALLOWED_HOSTS = ['yourdomain.com']
# - 配置 MySQL 连接

python manage.py collectstatic
python manage.py migrate

# 创建 Gunicorn 服务
sudo nano /etc/systemd/system/bookstore.service
```

```ini
[Unit]
Description=Bookstore Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/bookstore/backend
ExecStart=/var/www/bookstore/backend/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/bookstore/backend/app.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 3. Nginx 配置
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /var/www/bookstore/backend/static/;
    }

    location /media/ {
        alias /var/www/bookstore/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/bookstore/backend/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. 前端部署
```bash
cd /var/www/bookstore/frontend
npm install
npm run build

# 将 dist/ 目录复制到 Nginx 静态目录
sudo cp -r dist/* /var/www/html/
```

## 数据库迁移 (SQLite → MySQL)

```python
# 1. 导出数据
python manage.py dumpdata > data.json

# 2. 修改配置为 MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# 3. 创建表结构
python manage.py migrate

# 4. 导入数据
python manage.py loaddata data.json
```

## 备份策略

### 数据库备份
```bash
# SQLite
cp backend/db.sqlite3 backup/db_$(date +%Y%m%d).sqlite3

# MySQL
mysqldump -u root -p bookstore > backup/bookstore_$(date +%Y%m%d).sql
```

### 媒体文件备份
```bash
tar -czf backup/media_$(date +%Y%m%d).tar.gz backend/media/
```

## 监控与维护

### 日志查看
```bash
# Gunicorn 日志
sudo journalctl -u bookstore.service

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 服务管理
```bash
# 重启服务
sudo systemctl restart bookstore
sudo systemctl restart nginx

# 查看服务状态
sudo systemctl status bookstore
```

### 性能监控
```bash
# 查看系统资源
top
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

## 故障排除

### 常见问题

1. **静态文件404**
   - 检查 `python manage.py collectstatic` 是否执行
   - 检查 Nginx 静态文件路径配置

2. **数据库连接失败**
   - 检查数据库服务是否运行
   - 检查数据库连接配置

3. **权限问题**
   - 检查文件权限：`chown -R www-data:www-data /var/www/bookstore/`
   - 检查目录权限：`chmod -R 755 /var/www/bookstore/`

4. **Gunicorn 启动失败**
   - 检查虚拟环境是否正确激活
   - 检查依赖是否安装完整

### 紧急恢复
```bash
# 停止服务
sudo systemctl stop bookstore

# 恢复数据库备份
mysql -u root -p bookstore < backup/bookstore_YYYYMMDD.sql

# 恢复媒体文件
tar -xzf backup/media_YYYYMMDD.tar.gz -C /

# 重启服务
sudo systemctl start bookstore
```

## 安全建议

1. **定期更新**
   ```bash
   # 更新系统包
   sudo apt update && sudo apt upgrade

   # 更新 Python 包
   pip install --upgrade -r requirements.txt

   # 更新 Node.js 包
   npm update
   ```

2. **SSL 证书**
   ```bash
   # 使用 Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. **防火墙配置**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```