"""URL configuration for openbookshop project."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/users/', include('apps.users.urls_users')),
    path('api/v1/merchants/', include('apps.merchants.urls')),
    path('api/v1/books/', include('apps.books.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
]

# ✅ 提供媒体/静态文件（当前 Docker 部署启用）
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
