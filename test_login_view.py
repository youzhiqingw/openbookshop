#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from rest_framework.test import APIRequestFactory
from apps.users.views import LoginView
import json

factory = APIRequestFactory()

# Test admin login
print('=== Admin Login Response ===')
request = factory.post('/api/users/login/', {'username': 'admin', 'password': 'admin123456'}, format='json')
view = LoginView.as_view()
response = view(request)
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test merchant login
print('\n=== Merchant Login Response ===')
request = factory.post('/api/users/login/', {'username': 'merchant_test', 'password': 'merchant123456'}, format='json')
response = view(request)
print(json.dumps(response.data, indent=2, ensure_ascii=False))

# Test customer login
print('\n=== Customer Login Response ===')
request = factory.post('/api/users/login/', {'username': 'customer_test', 'password': 'customer123456'}, format='json')
response = view(request)
print(json.dumps(response.data, indent=2, ensure_ascii=False))
