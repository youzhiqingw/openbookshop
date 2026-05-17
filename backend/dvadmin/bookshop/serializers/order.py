from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.bookshop.models import Order, OrderItem


class OrderItemSerializer(CustomModelSerializer):
    """订单项序列化器"""

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_title', 'book_cover', 'price', 'quantity', 'total_price']


class OrderSerializer(CustomModelSerializer):
    """订单序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'user', 'user_name', 'merchant', 'merchant_name',
            'status', 'status_display',
            'total_amount', 'discount_amount', 'freight_amount', 'pay_amount',
            'receiver_name', 'receiver_phone', 'receiver_address',
            'pay_time', 'pay_method', 'ship_time', 'express_company', 'express_no',
            'cancel_reason', 'items', 'create_datetime',
        ]
        read_only_fields = [
            'id', 'order_no', 'user', 'merchant', 'status',
            'total_amount', 'discount_amount', 'freight_amount', 'pay_amount',
            'receiver_name', 'receiver_phone', 'receiver_address',
            'pay_time', 'pay_method', 'ship_time', 'express_company', 'express_no',
            'cancel_reason', 'items',
        ]


class AdminOrderSerializer(OrderSerializer):
    """管理端订单序列化器"""
    class Meta(OrderSerializer.Meta):
        pass
