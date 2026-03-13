#!/usr/bin/env python
"""
初始化测试账户脚本
创建admin、merchant_test、customer_test用户，并为customer_test添加收货地址
"""

import os
import sys
import django

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'openbookshop', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from apps.users.models import User, Address
from apps.merchants.models import Merchant

def init_users():
    """创建测试用户"""
    print("=" * 80)
    print("📝 初始化测试账户")
    print("=" * 80)

    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@openbookshop.local',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'merchant_test',
            'password': 'merchant123',
            'email': 'merchant@openbookshop.local',
            'role': 'merchant',
            'is_staff': False,
        },
        {
            'username': 'customer_test',
            'password': 'customer123',
            'email': 'customer@openbookshop.local',
            'role': 'customer',
            'is_staff': False,
        },
    ]

    for user_data in users_data:
        username = user_data.pop('username')
        password = user_data.pop('password')
        
        # 删除旧用户(如果存在)
        User.objects.filter(username=username).delete()
        
        # 创建新用户
        user = User.objects.create_user(username=username, password=password, **user_data)
        print(f"✓ 创建用户: {username} (role={user.role})")

    print("\n✅ 用户初始化完成!\n")

def init_merchant():
    """为merchant_test创建商家信息"""
    print("=" * 80)
    print("🏪 初始化商家信息")
    print("=" * 80)

    merchant_user = User.objects.get(username='merchant_test')
    
    # 删除旧的商家信息(如果存在)
    Merchant.objects.filter(user=merchant_user).delete()
    
    merchant = Merchant.objects.create(
        user=merchant_user,
        store_name='测试书店',
        description='这是一家测试书店，用于演示和测试功能',
        status='approved',
    )
    print(f"✓ 创建商家: {merchant.store_name}")
    print(f"✅ 商家初始化完成!\n")

def init_addresses():
    """为customer_test创建默认收货地址"""
    print("=" * 80)
    print("📮 初始化收货地址")
    print("=" * 80)

    customer_user = User.objects.get(username='customer_test')
    
    # 删除旧地址(如果存在)
    Address.objects.filter(user=customer_user).delete()
    
    addresses = [
        {
            'name': '张三',
            'phone': '13800138000',
            'province': '北京市',
            'city': '朝阳区',
            'district': '望京',
            'detail': '望京SOHO T1座1层',
            'is_default': True,
        },
        {
            'name': '李四',
            'phone': '13900139000',
            'province': '上海市',
            'city': '浦东新区',
            'district': '陆家嘴',
            'detail': '世纪大道1号',
            'is_default': False,
        },
    ]

    for addr_data in addresses:
        address = Address.objects.create(user=customer_user, **addr_data)
        default_tag = " [默认]" if address.is_default else ""
        print(f"✓ 创建地址: {address.name} - {address.province}{address.city}{address.district}{default_tag}")

    print(f"\n✅ 地址初始化完成!\n")

def main():
    """主函数"""
    try:
        # 1. 初始化用户
        init_users()
        
        # 2. 初始化商家
        init_merchant()
        
        # 3. 初始化地址
        init_addresses()
        
        print("=" * 80)
        print("✨ 所有初始化任务完成！")
        print("=" * 80)
        print("\n📌 测试账户信息:")
        print("  管理员:    admin     / admin123")
        print("  商家:      merchant_test / merchant123")
        print("  用户:      customer_test / customer123")
        print("\n💡 快速测试步骤:")
        print("  1. 访问 http://127.0.0.1:8080 "  )
        print("  2. 用customer_test登录")
        print("  3. 浏览图书 → 加入购物车 → 结算 → 下单")
        print("\n")

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
