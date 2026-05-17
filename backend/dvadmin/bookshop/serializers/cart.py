from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.bookshop.models import CartItem
from dvadmin.bookshop.serializers.book import CustomerBookSerializer


class CartItemSerializer(CustomModelSerializer):
    """购物车项序列化器"""
    book_detail = CustomerBookSerializer(source='book', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'book', 'quantity', 'book_detail', 'create_datetime']
        read_only_fields = ['user']

    def validate_quantity(self, value):
        if value < 1 or value > 99:
            raise serializers.ValidationError('数量不合法')
        return value


class CartItemCreateSerializer(serializers.Serializer):
    """加入购物车序列化器"""
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1, max_value=99)

    def validate_book_id(self, value):
        from dvadmin.bookshop.models import Book
        book = Book.objects.filter(id=value).first()
        if not book:
            raise serializers.ValidationError('图书不存在')
        if book.status != 'on_sale':
            raise serializers.ValidationError('该图书已下架')
        if book.merchant.status != 'approved' or not book.merchant.is_open:
            raise serializers.ValidationError('商家暂停营业')
        return value
