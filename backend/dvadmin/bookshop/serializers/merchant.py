from rest_framework import serializers
from dvadmin.bookshop.models import Merchant
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator


class MerchantSerializer(CustomModelSerializer):
    """商家管理-序列化器"""

    class Meta:
        model = Merchant
        fields = "__all__"
        read_only_fields = ["id", "status", "reject_reason"]


class MerchantCreateSerializer(CustomModelSerializer):
    """商家入驻申请-序列化器"""
    name = serializers.CharField(
        max_length=100,
        validators=[CustomUniqueValidator(queryset=Merchant.objects.all(), message="该店铺名称已存在")],
    )

    class Meta:
        model = Merchant
        fields = "__all__"
        read_only_fields = ["id", "status", "reject_reason"]


class MerchantApplySerializer(CustomModelSerializer):
    """商家入驻申请-前端提交序列化器"""
    name = serializers.CharField(
        max_length=100,
        validators=[CustomUniqueValidator(queryset=Merchant.objects.all(), message="该店铺名称已存在")],
    )

    class Meta:
        model = Merchant
        fields = ["name", "logo", "description", "contact_name", "contact_phone", "contact_email", "address"]
        read_only_fields = []


class MerchantProfileUpdateSerializer(CustomModelSerializer):
    """商家店铺信息更新-序列化器"""

    class Meta:
        model = Merchant
        fields = ["name", "logo", "description", "contact_name", "contact_phone", "contact_email", "address", "is_open"]
