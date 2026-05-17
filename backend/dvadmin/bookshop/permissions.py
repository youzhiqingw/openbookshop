from rest_framework.permissions import BasePermission


class MerchantPermission(BasePermission):
    """商家权限类 — 仅审核通过的商家可访问，is_superuser 直通"""

    def has_permission(self, request, view):
        user = request.user
        # 未认证
        if not user or not user.is_authenticated:
            return False
        # 超级管理员直通
        if user.is_superuser:
            return True
        # 必须是商家
        if user.user_type != 2:
            return False
        # 必须有关联商家
        if not hasattr(user, 'merchant') or user.merchant is None:
            return False
        # 商家必须审核通过
        if user.merchant.status != 'approved':
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # obj 本身是 Merchant
        if hasattr(obj, 'pk') and obj.__class__.__name__ == 'Merchant':
            return obj.pk == user.merchant_id
        # obj 有 merchant 属性
        if hasattr(obj, 'merchant_id'):
            return obj.merchant_id == user.merchant_id
        return False


class OwnerPermission(BasePermission):
    """消费者权限类 — 仅操作自己的数据，is_superuser 直通"""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # 消费者或其他已认证用户均可（user_type=3 或 user_type=1）
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # obj 有 user_id 属性
        if hasattr(obj, 'user_id'):
            return obj.user_id == user.id
        # obj 有 user 属性（FK）
        if hasattr(obj, 'user') and obj.user:
            return obj.user.id == user.id
        return False
