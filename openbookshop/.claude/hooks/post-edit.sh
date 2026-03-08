#!/bin/bash
# 编辑后钩子: 自动格式化和检查

echo "🔧 运行编辑后钩子..."

# 检测变更文件
CHANGED_FILES=$(git diff --name-only --cached)

# Python 文件格式化
if echo "$CHANGED_FILES" | grep -q ".py$"; then
    echo "🐍 格式化 Python 代码..."
    cd backend
    black .
    isort .
    echo "🧪 运行 Python 测试..."
    python manage.py test --failfast || exit 1
fi

# Vue/JS 文件格式化
if echo "$CHANGED_FILES" | grep -q ".vue$|.js$"; then
    echo "🎨 格式化前端代码..."
    cd frontend
    npm run lint -- --fix
    echo "🧪 运行前端测试..."
    npm run test:unit || exit 1
fi

# 检查敏感文件
if echo "$CHANGED_FILES" | grep -q "settings.py|config/"; then
    echo "⚠️ 检测到配置文件变更，请确认无硬编码密钥"
fi

echo "✅ 钩子检查完成"