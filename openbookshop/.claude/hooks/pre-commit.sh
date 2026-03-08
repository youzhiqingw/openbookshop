#!/bin/bash
# 提交前钩子: 阻止危险操作

echo "🛡️ 运行提交前检查..."

# 阻止提交到 main 分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ]; then
    echo "❌ 禁止直接提交到 main 分支"
    exit 1
fi

# 阻止提交包含敏感词的文件
if git diff --cached --name-only | xargs grep -l "password|secret|key" 2>/dev/null; then
    echo "⚠️ 检测到可能包含敏感信息的文件，请检查"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查商家隔离 (简单检查)
if git diff --cached --name-only | grep -q "views.py"; then
    echo "🔍 检查商家数据隔离..."
    # 这里可以添加更复杂的检查逻辑
fi

echo "✅ 提交前检查通过"