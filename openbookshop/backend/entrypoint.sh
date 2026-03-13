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

# 初始化持久化数据（用户、商家、书籍等）
echo "Initializing persistent data..."
if [ -f /app/init_data_persistent.py ]; then
    python /app/init_data_persistent.py || {
        echo "⚠️  Warning: persistent data initialization failed, but continuing..."
    }
else
    echo "⚠️  Warning: init_data_persistent.py not found, skipping data initialization"
fi

# 启动 Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
