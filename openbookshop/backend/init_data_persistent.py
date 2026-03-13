#!/usr/bin/env python
"""
持久化数据初始化脚本
在容器重启时保持测试账户和书籍数据不丢失
"""

import os
import sys
import django

# 配置工作目录
os.chdir('/app')
sys.path.insert(0, '/app')

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    exit(1)

from django.contrib.auth.hashers import make_password
from apps.users.models import User, Address
from apps.merchants.models import Merchant
from apps.books.models import Category, Book


def init_users():
    """初始化测试用户"""
    print("📝 初始化用户账户...")
    
    users_data = [
        {
            'username': 'admin',
            'password': 'admin123456',
            'email': 'admin@example.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'merchant_test',
            'password': 'merchant123456',
            'email': 'merchant@example.com',
            'role': 'merchant',
            'is_staff': True,
        },
        {
            'username': 'customer_test',
            'password': 'customer123456',
            'email': 'customer@example.com',
            'role': 'customer',
        },
    ]
    
    for user_data in users_data:
        username = user_data.pop('username')
        password = user_data.pop('password')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={**user_data, 'password': make_password(password)}
        )
        
        status = "✅ 创建" if created else "⏭️  已存在"
        print(f"   {status}: {username} (role={user_data['role']})")
    
    print()


def init_merchant():
    """初始化商家"""
    print("🏪 初始化商家...")
    
    merchant_test_user = User.objects.get(username='merchant_test')
    
    merchant, created = Merchant.objects.get_or_create(
        user=merchant_test_user,
        defaults={
            'store_name': '测试书店',
            'status': 'approved',
            'description': '这是一个测试书店',
        }
    )
    
    status = "✅ 创建" if created else "⏭️  已存在"
    print(f"   {status}: {merchant.store_name}")
    print()


def init_addresses():
    """初始化收货地址"""
    print("📍 初始化收货地址...")
    
    customer = User.objects.get(username='customer_test')
    
    addresses_data = [
        {
            'name': '张三',
            'phone': '13800138000',
            'province': '北京市',
            'city': '朝阳区',
            'district': '望京',
            'detail': '望京街1号',
            'is_default': True,
        },
        {
            'name': '李四',
            'phone': '13900139000',
            'province': '上海市',
            'city': '浦东新区',
            'district': '陆家嘴',
            'detail': '陆家嘴环路100号',
            'is_default': False,
        },
    ]
    
    for addr_data in addresses_data:
        addr, created = Address.objects.get_or_create(
            user=customer,
            name=addr_data['name'],
            defaults={k: v for k, v in addr_data.items() if k != 'name'}
        )
        
        status = "✅ 创建" if created else "⏭️  已存在"
        print(f"   {status}: {addr_data['name']} - {addr_data['province']}")
    
    print()


def init_categories():
    """初始化图书分类"""
    print("📚 初始化图书分类...")
    
    categories_data = [
        '中国当代文学',
        '外国文学',
        '自我成长',
        '心理学',
        '科幻小说',
        '幻想文学',
        '历史',
        '社科',
        '职场提升',
        '人工智能',
        '编程',
        '计算机',
    ]
    
    for idx, cat_name in enumerate(categories_data, 1):
        cat, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'sort_order': idx}
        )
        
        status = "✅ 创建" if created else "⏭️  已存在"
        print(f"   {status}: {cat_name}")
    
    print()


def init_books():
    """初始化图书数据"""
    print("📖 初始化书籍数据...")
    
    merchant = Merchant.objects.get(user__username='merchant_test')
    
    # 书籍数据：(标题, 作者, ISBN, 出版社, 分类名, 价格, 库存, 封面文件)
    books_data = [
        ('活着', '余华', '978-7-5326-0419-4', '北京十月文艺出版社', '中国当代文学', '29.80', 100, '496.png'),
        ('三体', '刘慈欣', '978-7-5649-5940-5', '重庆出版集团', '科幻小说', '39.50', 95, '564.png'),
        ('1984', '乔治·奥威尔', '978-7-5095-9761-4', '江苏人民出版社', '外国文学', '42.00', 88, '637.png'),
        ('人性中的善良天使', '史蒂芬·平克', '978-7-5095-8614-4', '江苏人民出版社', '心理学', '58.00', 72, '701.png'),
        ('我与世界只差一个你', '大冰', '978-7-5086-5751-2', '湖南文艺出版社', '自我成长', '45.00', 110, '841.png'),
        ('活出心花怒放', '张德芬', '978-7-5086-5544-0', '湖南文艺出版社', '自我成长', '38.00', 85, '958.png'),
        ('房间', '艾玛·多诺霍', '978-7-5095-5629-0', '江苏人民出版社', '外国文学', '35.00', 92, '1013.png'),
        ('莫失莫忘', '北上', '978-7-5086-7962-0', '湖南文艺出版社', '中国当代文学', '48.00', 78, '1135.png'),
        ('雪中悍刀行', '烽火戏诸侯', '978-7-5086-5951-6', '湖南文艺出版社', '幻想文学', '42.00', 105, '1291.png'),
        ('人間失格', '太宰治', '978-7-5014-4868-9', '上海文艺出版社', '外国文学', '32.00', 89, '1388.png'),
        ('巨人的陨落', '肯·福莱特', '978-7-5325-8959-9', '北京十月文艺出版社', '历史', '88.00', 60, '1415.png'),
        ('飙速宅男', '渡边航', '978-7-5567-1234-5', '南方出版社', '幻想文学', '28.00', 120, '1506.png'),
        ('三十而立', '刘同', '978-7-5086-4897-8', '湖南文艺出版社', '职场提升', '32.00', 95, '1684.png'),
        ('重新定义公司', '埃里克·施密特', '978-7-5086-6892-2', '湖南文艺出版社', '职场提升', '76.00', 52, '1775.png'),
        ('人工智能基础', '李开复', '978-7-5086-8234-7', '湖南文艺出版社', '人工智能', '68.00', 80, '1808.png'),
        ('Python深度学习', '弗朗索瓦·肖莱', '978-7-5086-7123-5', '湖南文艺出版社', '编程', '99.00', 45, '1973.png'),
        ('代码整洁之道', '罗伯特·马丁', '978-7-5086-6988-2', '湖南文艺出版社', '编程', '57.00', 78, '2038.png'),
        ('设计模式', '四人帮', '978-7-5086-5234-6', '湖南文艺出版社', '计算机', '78.00', 63, '2195.png'),
        ('计算机网络', '谢希仁', '978-7-5086-4123-1', '湖南文艺出版社', '计算机', '65.00', 90, '2216.png'),
        ('数据库系统概论', '王珊', '978-7-5086-3456-2', '湖南文艺出版社', '计算机', '59.00', 75, '2389.png'),
        ('时间简史', '霍金', '978-7-5086-2789-1', '湖南文艺出版社', '心理学', '46.00', 87, '2457.png'),
        ('人类简史', '尤瓦尔', '978-7-5086-1234-7', '湖南文艺出版社', '历史', '68.00', 70, '2510.png'),
        ('活过100岁', '弗兰克', '978-7-5086-9999-9', '湖南文艺出版社', '心理学', '39.00', 55, '2643.png'),
        ('围城', '钱钟书', '978-7-5086-8888-8', '湖南文艺出版社', '中国当代文学', '38.00', 95, '2797.png'),
        ('算法导论', '托马斯·科尔曼', '978-7-5086-7777-7', '湖南文艺出版社', '编程', '178.00', 30, '2809.png'),
    ]
    
    category_map = {cat.name: cat for cat in Category.objects.all()}
    created_count = 0
    exists_count = 0
    
    for title, author, isbn, publisher, category_name, price, stock, cover in books_data:
        category = category_map.get(category_name)
        if not category:
            print(f"   ⚠️  分类不存在: {category_name}，跳过 {title}")
            continue
        
        book, created = Book.objects.get_or_create(
            merchant=merchant,
            isbn=isbn,
            defaults={
                'title': title,
                'author': author,
                'publisher': publisher,
                'category': category,
                'price': price,
                'stock': stock,
                'warning_stock': 10,
                'cover': f'book_covers/{cover}',
                'is_on_sale': True,
            }
        )
        
        if created:
            created_count += 1
            print(f"   ✅ 创建: {title}")
        else:
            exists_count += 1
    
    print(f"   📊 统计: 新建{created_count}本, 已存在{exists_count}本")
    print()


def print_summary():
    """打印数据统计摘要"""
    print("\n" + "="*60)
    print("📊 数据初始化完成摘要")
    print("="*60)
    
    user_count = User.objects.count()
    merchant_count = Merchant.objects.count()
    category_count = Category.objects.count()
    book_count = Book.objects.count()
    address_count = Address.objects.count()
    
    print(f"""
✅ 用户总数: {user_count}
   - admin (管理员)
   - merchant_test (商家)
   - customer_test (普通用户)

✅ 商家总数: {merchant_count}
   - 测试书店

✅ 分类总数: {category_count}

✅ 书籍总数: {book_count}

✅ 收货地址: {address_count} (属于customer_test)
   - 北京朝阳区 (默认)
   - 上海浦东新区

🔗 可以立即访问:
   - 用户端: http://127.0.0.1:8080 (customer_test/customer123456)
   - 商家端: http://127.0.0.1:8080 (merchant_test/merchant123456)
   - 管理端: http://127.0.0.1:8080 (admin/admin123456)
   - Django Admin: http://127.0.0.1:8000/admin/ (admin/admin123456)
""")
    print("="*60 + "\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 OpenBookShop 数据初始化 (持久化版)")
    print("="*60 + "\n")
    
    try:
        init_users()
        init_merchant()
        init_addresses()
        init_categories()
        init_books()
        print_summary()
        print("✨ 所有数据初始化完成！")
        
    except Exception as e:
        print(f"\n❌ 初始化过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
