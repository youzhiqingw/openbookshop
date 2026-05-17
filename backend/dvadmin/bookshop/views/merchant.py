from django.db import transaction
from rest_framework.decorators import action
from dvadmin.bookshop.models import Merchant
from dvadmin.bookshop.serializers.merchant import (
    MerchantSerializer, MerchantApplySerializer, MerchantProfileUpdateSerializer,
)
from dvadmin.system.models import Users
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend
from dvadmin.utils.permission import CustomPermission


class AdminMerchantViewSet(CustomModelViewSet):
    """管理端-商家审核接口"""
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    filter_fields = ["status", "name"]
    search_fields = ["name", "contact_name"]
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['post'], detail=True, permission_classes=[CustomPermission])
    @transaction.atomic
    def audit(self, request, pk=None):
        """审核商家（通过/拒绝）"""
        merchant = self.get_object()
        action_type = request.data.get('action')

        if merchant.status != 'pending':
            return ErrorResponse(code=4000, msg="该商家不在待审核状态")

        if action_type == 'approve':
            merchant.status = 'approved'
            merchant.reject_reason = None
            merchant.save(update_fields=['status', 'reject_reason', 'update_datetime'])
            user = merchant.creator
            if user:
                user.user_type = 2
                user.merchant = merchant
                user.save(update_fields=['user_type', 'merchant_id', 'update_datetime'])
            return DetailResponse(data=MerchantSerializer(merchant).data, msg="审核通过")

        elif action_type == 'reject':
            reject_reason = request.data.get('reject_reason', '').strip()
            if not reject_reason:
                return ErrorResponse(code=4000, msg="拒绝原因不能为空")
            merchant.status = 'rejected'
            merchant.reject_reason = reject_reason
            merchant.save(update_fields=['status', 'reject_reason', 'update_datetime'])
            user = merchant.creator
            if user and user.merchant_id == merchant.pk:
                user.merchant = None
                user.save(update_fields=['merchant_id', 'update_datetime'])
            return DetailResponse(data=MerchantSerializer(merchant).data, msg="审核拒绝")

        else:
            return ErrorResponse(code=4000, msg="action 参数不合法，须为 approve 或 reject")

    @action(methods=['post'], detail=True, permission_classes=[CustomPermission])
    def disable(self, request, pk=None):
        """禁用商家"""
        merchant = self.get_object()
        if merchant.status != 'approved':
            return ErrorResponse(code=4000, msg="只能禁用已通过的商家")
        merchant.status = 'disabled'
        merchant.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=MerchantSerializer(merchant).data, msg="禁用成功")

    @action(methods=['post'], detail=True, permission_classes=[CustomPermission])
    def enable(self, request, pk=None):
        """解禁商家"""
        merchant = self.get_object()
        if merchant.status != 'disabled':
            return ErrorResponse(code=4000, msg="只能解禁已禁用的商家")
        merchant.status = 'approved'
        merchant.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=MerchantSerializer(merchant).data, msg="解禁成功")


class MerchantApplyViewSet(CustomModelViewSet):
    """商家端-入驻申请"""
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomPermission]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create':
            return MerchantApplySerializer
        return MerchantSerializer

    def create(self, request, *args, **kwargs):
        """提交入驻申请"""
        user = request.user
        if hasattr(user, 'merchant') and user.merchant and user.merchant.status != 'rejected':
            return ErrorResponse(code=4000, msg="您已提交过入驻申请，请勿重复提交")

        serializer = MerchantApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant = serializer.save(creator=user, status='pending')
        user.merchant = merchant
        user.save(update_fields=['merchant_id', 'update_datetime'])
        return DetailResponse(data=MerchantSerializer(merchant).data, msg="入驻申请已提交，请等待审核")

    def list(self, request, *args, **kwargs):
        """获取当前用户的入驻申请状态"""
        user = request.user
        if hasattr(user, 'merchant') and user.merchant:
            return DetailResponse(data=MerchantSerializer(user.merchant).data, msg="获取成功")
        return DetailResponse(data=None, msg="尚未提交入驻申请")


class MerchantProfileViewSet(CustomModelViewSet):
    """商家端-店铺信息管理"""
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [CustomPermission]
    http_method_names = ['get', 'put']

    def get_serializer_class(self):
        if self.action == 'update_profile':
            return MerchantProfileUpdateSerializer
        return MerchantSerializer

    def list(self, request, *args, **kwargs):
        """获取当前用户的店铺信息"""
        user = request.user
        if not hasattr(user, 'merchant') or not user.merchant:
            return ErrorResponse(code=4000, msg="您尚未入驻")
        merchant = user.merchant
        if merchant.status != 'approved':
            return ErrorResponse(code=4000, msg="店铺尚未通过审核")
        return DetailResponse(data=MerchantSerializer(merchant).data, msg="获取成功")

    @action(methods=['put'], detail=False, permission_classes=[CustomPermission])
    def update_profile(self, request, pk=None):
        """更新当前用户的店铺信息"""
        user = request.user
        if not hasattr(user, 'merchant') or not user.merchant:
            return ErrorResponse(code=4000, msg="您尚未入驻")
        merchant = user.merchant
        if merchant.status != 'approved':
            return ErrorResponse(code=4000, msg="店铺尚未通过审核，无法修改信息")
        serializer = MerchantProfileUpdateSerializer(merchant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DetailResponse(data=MerchantSerializer(merchant).data, msg="更新成功")

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'merchant') or not user.merchant:
            return ErrorResponse(code=4000, msg="您尚未入驻")
        return DetailResponse(data=MerchantSerializer(user.merchant).data, msg="获取成功")
