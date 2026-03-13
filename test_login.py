#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.users.models import User
from apps.users.serializers import LoginSerializer

# Test admin login
serializer = LoginSerializer(data={'username': 'admin', 'password': 'admin123456'})
if serializer.is_valid():
    user_data = serializer.validated_data
    print('Admin Login Success:')
    print('  username:', user_data['username'])
    print('  role:', user_data['role'])
    print('  is_staff:', user_data['is_staff'])
else:
    print('Admin Login Failed:', serializer.errors)

# Test merchant login
print()
serializer = LoginSerializer(data={'username': 'merchant_test', 'password': 'merchant123456'})
if serializer.is_valid():
    user_data = serializer.validated_data
    print('Merchant Login Success:')
    print('  username:', user_data['username'])
    print('  role:', user_data['role'])
    print('  is_staff:', user_data['is_staff'])
else:
    print('Merchant Login Failed:', serializer.errors)

# Test customer login
print()
serializer = LoginSerializer(data={'username': 'customer_test', 'password': 'customer123456'})
if serializer.is_valid():
    user_data = serializer.validated_data
    print('Customer Login Success:')
    print('  username:', user_data['username'])
    print('  role:', user_data['role'])
    print('  is_staff:', user_data['is_staff'])
else:
    print('Customer Login Failed:', serializer.errors)
