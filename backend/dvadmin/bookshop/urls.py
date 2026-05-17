from django.urls import path, include
from rest_framework import routers

from dvadmin.bookshop.views.merchant import AdminMerchantViewSet, MerchantApplyViewSet, MerchantProfileViewSet
from dvadmin.bookshop.views.book import (
    AdminCategoryViewSet, AdminBookViewSet,
    CustomerCategoryViewSet, CustomerBookViewSet,
    MerchantCategoryViewSet, MerchantBookViewSet,
)
from dvadmin.bookshop.views.cart import CustomerCartViewSet
from dvadmin.bookshop.views.address import CustomerAddressViewSet

from dvadmin.bookshop.views.order import AdminOrderViewSet, MerchantOrderViewSet
from dvadmin.bookshop.views.statistics import AdminWarningViewSet, MerchantWarningViewSet, AdminStatisticsViewSet

bookshop_url = routers.SimpleRouter()

# 管理端
bookshop_url.register(r'admin/merchants', AdminMerchantViewSet, basename='admin-merchant')
bookshop_url.register(r'admin/categories', AdminCategoryViewSet, basename='admin-category')
bookshop_url.register(r'admin/books', AdminBookViewSet, basename='admin-book')
bookshop_url.register(r'admin/orders', AdminOrderViewSet, basename='admin-order')
bookshop_url.register(r'admin/warnings', AdminWarningViewSet, basename='admin-warning')
bookshop_url.register(r'admin/statistics', AdminStatisticsViewSet, basename='admin-statistics')

# 商家端
bookshop_url.register(r'merchant/apply', MerchantApplyViewSet, basename='merchant-apply')
bookshop_url.register(r'merchant/profile', MerchantProfileViewSet, basename='merchant-profile')
bookshop_url.register(r'merchant/categories', MerchantCategoryViewSet, basename='merchant-category')
bookshop_url.register(r'merchant/books', MerchantBookViewSet, basename='merchant-book')
bookshop_url.register(r'merchant/orders', MerchantOrderViewSet, basename='merchant-order')
bookshop_url.register(r'merchant/warnings', MerchantWarningViewSet, basename='merchant-warning')

# 用户端
bookshop_url.register(r'customer/categories', CustomerCategoryViewSet, basename='customer-category')
bookshop_url.register(r'customer/books', CustomerBookViewSet, basename='customer-book')
bookshop_url.register(r'customer/cart', CustomerCartViewSet, basename='customer-cart')
bookshop_url.register(r'customer/addresses', CustomerAddressViewSet, basename='customer-address')

urlpatterns = [
    path('', include(bookshop_url.urls)),
]
