from rest_framework import serializers

from .models import Book, Category


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器（含子分类）"""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'sort_order', 'children']

    def get_children(self, obj):
        if obj.parent is None:
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class CategorySimpleSerializer(serializers.ModelSerializer):
    """简洁分类序列化器（不嵌套）"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'sort_order']


class BookSerializer(serializers.ModelSerializer):
    """图书完整序列化器（商家/管理员用）"""

    merchant_name = serializers.CharField(source='merchant.store_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'merchant', 'merchant_name', 'category', 'category_name',
            'title', 'author', 'isbn', 'publisher', 'publish_date',
            'description', 'cover', 'price', 'stock', 'warning_stock',
            'sales', 'is_on_sale', 'is_low_stock', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'merchant', 'sales', 'created_at', 'updated_at']


class BookCreateSerializer(serializers.ModelSerializer):
    """图书创建/更新序列化器（商家写入用）"""

    class Meta:
        model = Book
        fields = [
            'category', 'title', 'author', 'isbn', 'publisher', 'publish_date',
            'description', 'cover', 'price', 'stock', 'warning_stock', 'is_on_sale',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("价格必须大于0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("库存不能为负数")
        return value


class BookListSerializer(serializers.ModelSerializer):
    """图书列表序列化器（用户浏览用）"""

    merchant_name = serializers.CharField(source='merchant.store_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default='')

    class Meta:
        model = Book
        fields = [
            'id', 'merchant', 'merchant_name', 'category', 'category_name',
            'title', 'author', 'cover', 'price', 'stock', 'sales', 'is_on_sale',
        ]
