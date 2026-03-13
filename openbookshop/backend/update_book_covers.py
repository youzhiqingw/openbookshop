#!/usr/bin/env python
"""
更新数据库中所有书籍的封面文件名
将旧的 Library*.jpeg/png 格式更新为新的数字.png格式
"""
import os
import sys
import django

# 配置Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from apps.books.models import Book

# 新旧文件名映射
COVER_MAPPING = {
    'book_covers/Library02.jpeg': 'book_covers/496.png',
    'book_covers/Library11.jpeg': 'book_covers/564.png',
    'book_covers/Library12.jpeg': 'book_covers/637.png',
    'book_covers/Library21.jpeg': 'book_covers/701.png',
    'book_covers/Library23.jpeg': 'book_covers/841.png',
    'book_covers/Library24.jpeg': 'book_covers/958.png',
    'book_covers/Library28.jpeg': 'book_covers/1013.png',
    'book_covers/Library31.jpeg': 'book_covers/1135.png',
    'book_covers/Library32.jpeg': 'book_covers/1291.png',
    'book_covers/Library33.jpeg': 'book_covers/1388.png',
    'book_covers/Library34.jpeg': 'book_covers/1415.png',
    'book_covers/Library37.jpeg': 'book_covers/1506.png',
    'book_covers/Library41.jpeg': 'book_covers/1684.png',
    'book_covers/Library44.jpeg': 'book_covers/1775.png',
    'book_covers/Library47.jpeg': 'book_covers/1808.png',
    'book_covers/Library49.jpeg': 'book_covers/1973.png',
    'book_covers/Library50.jpeg': 'book_covers/2038.png',
    'book_covers/Library51.jpeg': 'book_covers/2195.png',
    'book_covers/Library52.jpeg': 'book_covers/2216.png',
    'book_covers/Library55.jpeg': 'book_covers/2389.png',
    'book_covers/Library58.jpeg': 'book_covers/2457.png',
    'book_covers/Library59.jpeg': 'book_covers/2510.png',
    'book_covers/Library62.jpeg': 'book_covers/2643.png',
    'book_covers/Library63.jpeg': 'book_covers/2797.png',
    'book_covers/Library73.jpeg': 'book_covers/2809.png',
    # PNG文件映射
    'book_covers/Library02.png': 'book_covers/496.png',
    'book_covers/Library11.png': 'book_covers/564.png',
    'book_covers/Library12.png': 'book_covers/637.png',
    'book_covers/Library21.png': 'book_covers/701.png',
    'book_covers/Library23.png': 'book_covers/841.png',
    'book_covers/Library24.png': 'book_covers/958.png',
    'book_covers/Library28.png': 'book_covers/1013.png',
    'book_covers/Library31.png': 'book_covers/1135.png',
    'book_covers/Library32.png': 'book_covers/1291.png',
    'book_covers/Library33.png': 'book_covers/1388.png',
    'book_covers/Library34.png': 'book_covers/1415.png',
    'book_covers/Library37.png': 'book_covers/1506.png',
    'book_covers/Library41.png': 'book_covers/1684.png',
    'book_covers/Library44.png': 'book_covers/1775.png',
    'book_covers/Library47.png': 'book_covers/1808.png',
    'book_covers/Library49.png': 'book_covers/1973.png',
    'book_covers/Library50.png': 'book_covers/2038.png',
    'book_covers/Library51.png': 'book_covers/2195.png',
    'book_covers/Library52.png': 'book_covers/2216.png',
    'book_covers/Library55.png': 'book_covers/2389.png',
    'book_covers/Library58.png': 'book_covers/2457.png',
    'book_covers/Library59.png': 'book_covers/2510.png',
    'book_covers/Library62.png': 'book_covers/2643.png',
    'book_covers/Library63.png': 'book_covers/2797.png',
    'book_covers/Library73.png': 'book_covers/2809.png',
}

def update_book_covers():
    """更新数据库中所有书籍的封面"""
    print('╔════════════════════════════════════════════╗')
    print('║       OpenBookShop 书籍封面更新            ║')
    print('╚════════════════════════════════════════════╝')
    print()
    
    updated_count = 0
    not_updated_count = 0
    
    # 获取所有包含旧格式封面的书籍
    for old_cover, new_cover in COVER_MAPPING.items():
        books = Book.objects.filter(cover=old_cover)
        
        for book in books:
            try:
                book.cover = new_cover
                book.save()
                updated_count += 1
                print(f'✅ 更新: {book.title} ({old_cover} → {new_cover})')
            except Exception as e:
                not_updated_count += 1
                print(f'❌ 失败: {book.title} - {str(e)}')
    
    print()
    print('📊 统计信息:')
    print(f'   成功更新: {updated_count} 本')
    print(f'   更新失败: {not_updated_count} 本')
    
    # 显示当前数据库中使用的所有cover值
    print()
    print('📋 当前数据库中的封面统计:')
    cover_stats = {}
    for book in Book.objects.all():
        cover = book.cover if book.cover else 'None'
        cover_stats[cover] = cover_stats.get(cover, 0) + 1
    
    for cover, count in sorted(cover_stats.items()):
        print(f'   {cover}: {count} 本')
    
    print()
    if updated_count > 0:
        print('✅ 更新完成！')
    else:
        print('ℹ️  没有找到需要更新的书籍记录。')

if __name__ == '__main__':
    update_book_covers()
