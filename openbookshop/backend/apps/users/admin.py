from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, OperationLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'is_vip', 'is_active', 'date_joined']
    list_filter = ['role', 'is_vip', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('phone', 'avatar', 'role', 'is_vip', 'vip_level', 'points', 'risk_score')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone', 'province', 'city', 'district', 'is_default']
    list_filter = ['is_default']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'module', 'ip_address', 'created_at']
    list_filter = ['action', 'module']
    readonly_fields = ['user', 'action', 'module', 'detail', 'ip_address', 'user_agent', 'created_at']
