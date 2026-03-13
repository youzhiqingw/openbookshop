#!/usr/bin/env python
"""
快速验证图片URL修复
用法: python verify_image_fix.py
"""

import os
import sys
import django
import json

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from apps.books.models import Book
from apps.books.serializers import BookSerializer, BookListSerializer


def test_serializers():
    print("=" * 60)
    print("📸 图片URL修复验证")
    print("=" * 60)
    
    # 获取第一本书
    book = Book.objects.first()
    
    if not book:
        print("❌ 数据库中没有书籍，请先初始化数据")
        return False
    
    print(f"\n📖 测试书籍: {book.title}")
    print(f"📁 物理文件: {book.cover}")
    
    # 测试 BookListSerializer
    print("\n🔍 BookListSerializer:")
    serializer = BookListSerializer(book)
    data = serializer.data
    cover_url = data.get('cover_url')
    cover = data.get('cover')
    
    print(f"  - cover: {cover}")
    print(f"  - cover_url: {cover_url}")
    
    # 验证URL格式
    if cover_url and not cover_url.startswith('/media/'):
        print(f"  ❌ cover_url 格式错误，应该以 /media/ 开头")
        return False
    
    if cover_url:
        print(f"  ✅ cover_url 格式正确 (相对路径)")
    
    # 测试 BookSerializer
    print("\n🔍 BookSerializer:")
    serializer = BookSerializer(book)
    data = serializer.data
    cover_url = data.get('cover_url')
    cover = data.get('cover')
    
    print(f"  - cover: {cover}")
    print(f"  - cover_url: {cover_url}")
    
    if cover_url and not cover_url.startswith('/media/'):
        print(f"  ❌ cover_url 格式错误，应该以 /media/ 开头")
        return False
    
    if cover_url:
        print(f"  ✅ cover_url 格式正确 (相对路径)")
    
    print("\n" + "=" * 60)
    print("✅ 所有验证通过！")
    print("=" * 60)
    print("\n📝 下一步:")
    print("  1. 重启后端: docker-compose restart openbookshop_backend")
    print("  2. 访问: http://127.0.0.1:8080")
    print("  3. 打开浏览器开发者工具 (F12)")
    print("  4. 检查 Network 标签中 /media/book_covers/* 请求状态为 200")
    
    return True


if __name__ == '__main__':
    try:
        success = test_serializers()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
