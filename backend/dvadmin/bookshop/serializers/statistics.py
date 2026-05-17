from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.bookshop.models import Book


class WarningBookSerializer(serializers.Serializer):
    """预警图书序列化器"""
    book_id = serializers.IntegerField(source='id')
    book_name = serializers.CharField(source='title')
    isbn = serializers.CharField()
    cover = serializers.CharField(source='cover_image', default='')
    stock = serializers.IntegerField()
    warning_stock = serializers.IntegerField()
    effective_warning_stock = serializers.SerializerMethodField()
    warning_level = serializers.SerializerMethodField()
    merchant_id = serializers.IntegerField(source='merchant.id')
    merchant_name = serializers.CharField(source='merchant.name')
    category_name = serializers.CharField(source='category.name', default='')

    def _get_global_threshold(self):
        from dvadmin.system.models import SystemConfig
        config = SystemConfig.objects.filter(key='bookshop_warning_stock_threshold').first()
        if config and config.value:
            try:
                return int(config.value)
            except (ValueError, TypeError):
                pass
        return 10

    def get_effective_warning_stock(self, obj):
        if obj.warning_stock and obj.warning_stock > 0:
            return obj.warning_stock
        return self._get_global_threshold()

    def get_warning_level(self, obj):
        threshold = self.get_effective_warning_stock(obj)
        if obj.stock == 0:
            return 'critical'
        elif obj.stock <= threshold * 0.5:
            return 'warning'
        elif obj.stock <= threshold:
            return 'info'
        return None


class WarningThresholdSerializer(serializers.Serializer):
    """全局预警阈值序列化器"""
    threshold = serializers.IntegerField(min_value=1, max_value=99999)
