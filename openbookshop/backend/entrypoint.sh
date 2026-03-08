#!/bin/sh
set -e

# 收集静态文件（仅在 STATIC_ROOT 目录为空时执行，避免每次重启都运行）
if [ ! -f /app/static/.collected ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    touch /app/static/.collected
fi

# 执行数据库迁移（幂等，可安全重复执行）
echo "Running database migrations..."
python manage.py migrate --noinput

# 启动 Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
