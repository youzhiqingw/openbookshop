#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.users.models import User
from apps.users.serializers import UserProfileSerializer

# Check admin user data
print('=== Admin user in database ===')
admin = User.objects.get(username='admin')
print(f'id: {admin.id}')
print(f'username: {admin.username}')
print(f'role: {admin.role}')
print(f'is_staff: {admin.is_staff}')
print(f'is_superuser: {admin.is_superuser}')

# Test serializer
print('\n=== UserProfileSerializer output for admin ===')
serializer = UserProfileSerializer(admin)
print('Data fields:')
for key, value in serializer.data.items():
    print(f'  {key}: {value}')
