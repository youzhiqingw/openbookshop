from rest_framework import serializers

from apps.books.serializers import BookListSerializer

from .models import Cart, FinanceRecord, Order, OrderItem


class CartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""

    book_detail = BookListSerializer(source='book', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'book', 'book_detail', 'quantity', 'subtotal', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_subtotal(self, obj):
        return str(obj.book.price * obj.quantity)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("数量至少为1")
        return value

    def validate(self, attrs):
        book = attrs.get('book') or (self.instance.book if self.instance else None)
        quantity = attrs.get('quantity', 1)
        if book and book.stock < quantity:
            raise serializers.ValidationError({"quantity": "库存不足"})
        return attrs


class CartUpdateSerializer(serializers.ModelSerializer):
    """购物车数量更新序列化器"""

    class Meta:
        model = Cart
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("数量至少为1")
        return value

    def validate(self, attrs):
        if self.instance and self.instance.book.stock < attrs.get('quantity', 1):
            raise serializers.ValidationError({"quantity": "库存不足"})
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""

    class Meta:
        model = OrderItem
        fields = [
            'id', 'book', 'merchant', 'book_title', 'book_cover',
            'book_author', 'price', 'quantity', 'subtotal',
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""

    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'user', 'username', 'status', 'status_display',
            'total_amount', 'address_snapshot', 'remark',
            'payment_method', 'payment_method_display', 'mock_payment_id',
            'pay_url', 'paid_at',
            'tracking_number', 'carrier', 'shipped_at', 'delivered_at',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """创建订单序列化器"""

    address_id = serializers.IntegerField(help_text='收货地址ID')
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='购物车条目ID列表（为空则购买全部）',
        required=False,
        default=list,
    )
    remark = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')

    def validate_address_id(self, value):
        from apps.users.models import Address
        request = self.context['request']
        try:
            Address.objects.get(pk=value, user=request.user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("地址不存在或不属于当前用户")
        return value


class FinanceRecordSerializer(serializers.ModelSerializer):
    """财务流水序列化器"""

    type_display = serializers.CharField(source='get_type_display', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True, default='')
    merchant_name = serializers.CharField(source='merchant.store_name', read_only=True, default='')
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = FinanceRecord
        fields = [
            'id', 'order', 'order_no', 'merchant', 'merchant_name',
            'user', 'username', 'type', 'type_display',
            'amount', 'description', 'created_at',
        ]
        read_only_fields = fields
