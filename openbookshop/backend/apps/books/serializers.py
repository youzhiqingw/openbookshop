from rest_framework import serializers

from .models import Book, Category, Review


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器（含子分类）"""

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "sort_order", "children"]

    def get_children(self, obj):
        if obj.parent is None:
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class CategorySimpleSerializer(serializers.ModelSerializer):
    """简洁分类序列化器（不嵌套）"""

    class Meta:
        model = Category
        fields = ["id", "name", "parent", "sort_order"]


class BookSerializer(serializers.ModelSerializer):
    """图书完整序列化器（商家/管理员用）"""

    merchant_name = serializers.CharField(source="merchant.store_name", read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=""
    )
    is_low_stock = serializers.BooleanField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "merchant",
            "merchant_name",
            "category",
            "category_name",
            "title",
            "author",
            "isbn",
            "publisher",
            "publish_date",
            "description",
            "cover",
            "cover_url",
            "price",
            "stock",
            "warning_stock",
            "sales",
            "is_on_sale",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "merchant", "sales", "created_at", "updated_at"]

    def get_cover_url(self, obj):
        """生成图片URL（相对路径）"""
        if obj.cover:
            # 使用相对路径，让前端/Nginx正确处理
            # 相比 request.build_absolute_uri() 更稳定，适用于反向代理环境
            return obj.cover.url
        return None


class BookCreateSerializer(serializers.ModelSerializer):
    """图书创建/更新序列化器（商家写入用）"""

    class Meta:
        model = Book
        fields = [
            "category",
            "title",
            "author",
            "isbn",
            "publisher",
            "publish_date",
            "description",
            "cover",
            "price",
            "stock",
            "warning_stock",
            "is_on_sale",
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

    merchant_name = serializers.CharField(source="merchant.store_name", read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=""
    )
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "merchant",
            "merchant_name",
            "category",
            "category_name",
            "title",
            "author",
            "cover",
            "cover_url",
            "price",
            "stock",
            "sales",
            "is_on_sale",
        ]

    def get_cover_url(self, obj):
        """生成图片URL（相对路径）"""
        if obj.cover:
            # 使用相对路径，让前端/Nginx正确处理
            # 相比 request.build_absolute_uri() 更稳定，适用于反向代理环境
            return obj.cover.url
        return None


class ReviewSerializer(serializers.ModelSerializer):
    """评论序列化器"""

    username = serializers.CharField(source="user.username", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    rating_display = serializers.CharField(source="get_rating_display", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "username",
            "book",
            "book_title",
            "order",
            "rating",
            "rating_display",
            "content",
            "is_sensitive",
            "is_approved",
            "merchant_reply",
            "replied_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "is_sensitive",
            "is_approved",
            "replied_at",
            "created_at",
            "updated_at",
        ]


class ReviewCreateSerializer(serializers.Serializer):
    """创建评论序列化器"""

    order_id = serializers.IntegerField(required=False, allow_null=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(min_length=5, max_length=500)


class MerchantReplySerializer(serializers.Serializer):
    """商家回复评论序列化器"""

    merchant_reply = serializers.CharField(min_length=1, max_length=500)
