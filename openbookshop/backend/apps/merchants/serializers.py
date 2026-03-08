from rest_framework import serializers

from .models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    """商家完整序列化器"""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Merchant
        fields = ['id', 'user', 'username', 'store_name', 'logo', 'description',
                  'status', 'business_license', 'address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class MerchantApplySerializer(serializers.ModelSerializer):
    """商家申请序列化器"""

    class Meta:
        model = Merchant
        fields = ['store_name', 'description', 'business_license', 'address']


class MerchantAuditSerializer(serializers.ModelSerializer):
    """商家审核序列化器"""

    class Meta:
        model = Merchant
        fields = ['status']

    def validate_status(self, value):
        if value not in ('approved', 'rejected'):
            raise serializers.ValidationError("审核状态只能为通过或拒绝")
        return value
