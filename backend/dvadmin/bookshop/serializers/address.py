from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.bookshop.models import Address


class AddressSerializer(CustomModelSerializer):
    """收货地址序列化器"""

    class Meta:
        model = Address
        fields = [
            'id', 'receiver_name', 'receiver_phone',
            'province', 'city', 'district', 'detail_address',
            'is_default', 'create_datetime',
        ]
        read_only_fields = ['user']

    def validate(self, attrs):
        user = self.context['request'].user
        # 创建时校验上限
        if not self.instance:
            count = Address.objects.filter(user=user).count()
            if count >= 5:
                raise serializers.ValidationError('最多添加5个收货地址')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        # 如果设为默认，先取消其他默认
        if validated_data.get('is_default'):
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 如果设为默认，先取消其他默认
        if validated_data.get('is_default'):
            Address.objects.filter(user=instance.user, is_default=True).exclude(id=instance.id).update(is_default=False)
        return super().update(instance, validated_data)
