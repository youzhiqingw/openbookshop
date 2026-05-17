from decimal import Decimal
from rest_framework import serializers
from dvadmin.bookshop.models import Category, Book
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator


class CategorySerializer(CustomModelSerializer):
    """分类管理-序列化器"""
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id"]

    def get_children(self, instance):
        if instance.parent is None:
            children = instance.children.all().order_by('sort', 'id')
            return CategoryTreeSerializer(children, many=True, request=self.context.get('request')).data
        return []

    def validate_parent(self, value):
        if value is not None and value.parent is not None:
            raise serializers.ValidationError("仅允许两级分类")
        return value


class CategoryTreeSerializer(CustomModelSerializer):
    """分类树-序列化器（扁平二级）"""

    class Meta:
        model = Category
        fields = ["id", "name", "sort", "parent", "create_datetime"]
        read_only_fields = ["id"]


class BookSerializer(CustomModelSerializer):
    """图书管理-序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "sales_count"]


class BookCreateSerializer(CustomModelSerializer):
    """图书创建-序列化器"""
    isbn = serializers.CharField(
        max_length=20,
        validators=[CustomUniqueValidator(queryset=Book.objects.all(), message="ISBN已存在")],
    )

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "sales_count"]

    def validate_category(self, value):
        if value.parent is None:
            raise serializers.ValidationError("仅允许二级分类")
        return value

    def validate(self, attrs):
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        if price is not None and original_price is not None:
            if Decimal(str(original_price)) < Decimal(str(price)):
                raise serializers.ValidationError({"original_price": "原价不能低于售价"})
        return attrs


class BookUpdateSerializer(CustomModelSerializer):
    """图书更新-序列化器"""

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "isbn", "merchant", "sales_count"]

    def validate_category(self, value):
        if value.parent is None:
            raise serializers.ValidationError("仅允许二级分类")
        return value

    def validate(self, attrs):
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        if price is not None and original_price is not None:
            if Decimal(str(original_price)) < Decimal(str(price)):
                raise serializers.ValidationError({"original_price": "原价不能低于售价"})
        return attrs


class CustomerBookSerializer(CustomModelSerializer):
    """用户端图书-序列化器（仅公开字段）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "isbn", "title", "author", "publisher", "publish_date",
            "category", "category_name", "merchant_name",
            "price", "original_price", "stock", "cover_image", "images",
            "description", "content", "status", "sales_count", "create_datetime",
        ]
        read_only_fields = fields


class MerchantBookCreateSerializer(CustomModelSerializer):
    """商家端图书创建-序列化器（merchant自动设置）"""
    isbn = serializers.CharField(
        max_length=20,
        validators=[CustomUniqueValidator(queryset=Book.objects.all(), message="ISBN已存在")],
    )

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "merchant", "sales_count"]

    def validate_category(self, value):
        if value.parent is None:
            raise serializers.ValidationError("仅允许二级分类")
        return value

    def validate(self, attrs):
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        if price is not None and original_price is not None:
            if Decimal(str(original_price)) < Decimal(str(price)):
                raise serializers.ValidationError({"original_price": "原价不能低于售价"})
        return attrs


class MerchantBookUpdateSerializer(CustomModelSerializer):
    """商家端图书更新-序列化器（merchant不可改）"""

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "isbn", "merchant", "sales_count"]

    def validate_category(self, value):
        if value.parent is None:
            raise serializers.ValidationError("仅允许二级分类")
        return value

    def validate(self, attrs):
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        if price is not None and original_price is not None:
            if Decimal(str(original_price)) < Decimal(str(price)):
                raise serializers.ValidationError({"original_price": "原价不能低于售价"})
        return attrs
