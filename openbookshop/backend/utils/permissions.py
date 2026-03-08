from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """允许管理员访问"""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_staff)
        )


class IsMerchant(BasePermission):
    """允许商家访问"""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'merchant'
        )


class IsCustomer(BasePermission):
    """允许普通用户访问"""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'customer'
        )


class IsMerchantApproved(BasePermission):
    """允许已审核通过的商家访问"""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role != 'merchant':
            return False
        return (
            hasattr(request.user, 'merchant')
            and request.user.merchant.status == 'approved'
        )
