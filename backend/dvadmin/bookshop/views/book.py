from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from dvadmin.bookshop.models import Category, Book
from dvadmin.bookshop.serializers.book import (
    CategorySerializer, CategoryTreeSerializer,
    BookSerializer, BookCreateSerializer, BookUpdateSerializer,
    CustomerBookSerializer, MerchantBookCreateSerializer, MerchantBookUpdateSerializer,
)
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend
from dvadmin.utils.permission import CustomPermission
from dvadmin.bookshop.permissions import MerchantPermission


# ====== 管理端 — 分类 ======

class AdminCategoryViewSet(CustomModelViewSet):
    """管理端-分类管理"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_fields = ["parent", "name"]
    search_fields = ["name"]
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['get'], detail=False)
    def tree(self, request):
        """两级分类树"""
        top_categories = Category.objects.filter(parent__isnull=True).order_by('sort', 'id')
        data = []
        for cat in top_categories:
            children = Category.objects.filter(parent=cat).order_by('sort', 'id')
            cat_data = CategoryTreeSerializer(cat, request=request).data
            cat_data['children'] = CategoryTreeSerializer(children, many=True, request=request).data
            data.append(cat_data)
        return DetailResponse(data=data, msg="success")


# ====== 管理端 — 图书 ======

class AdminBookViewSet(CustomModelViewSet):
    """管理端-图书管理"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    create_serializer_class = BookCreateSerializer
    update_serializer_class = BookUpdateSerializer
    filter_fields = ["status", "merchant", "category", "isbn"]
    search_fields = ["title", "author", "isbn"]
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['patch'], detail=True, permission_classes=[CustomPermission])
    def status(self, request, pk=None):
        """上下架"""
        book = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ('on_sale', 'off_sale'):
            return ErrorResponse(code=4000, msg="status 参数不合法，须为 on_sale 或 off_sale")
        # 上架条件校验
        if new_status == 'on_sale':
            if not book.cover_image:
                return ErrorResponse(code=4000, msg="上架图书必须有封面图")
            if not book.price or not book.original_price:
                return ErrorResponse(code=4000, msg="价格信息不完整")
            if book.merchant.status != 'approved':
                return ErrorResponse(code=4000, msg="商家未通过审核，不可上架")
        book.status = new_status
        book.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=BookSerializer(book, request=request).data, msg="操作成功")


# ====== 用户端 — 分类（公开） ======

class CustomerCategoryViewSet(CustomModelViewSet):
    """用户端-分类树（公开）"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        return Category.objects.all()

    @action(methods=['get'], detail=False, permission_classes=[AllowAny])
    def tree(self, request):
        """两级分类树"""
        top_categories = Category.objects.filter(parent__isnull=True).order_by('sort', 'id')
        data = []
        for cat in top_categories:
            children = Category.objects.filter(parent=cat).order_by('sort', 'id')
            cat_data = CategoryTreeSerializer(cat, request=request).data
            cat_data['children'] = CategoryTreeSerializer(children, many=True, request=request).data
            data.append(cat_data)
        return DetailResponse(data=data, msg="success")


# ====== 用户端 — 图书（公开） ======

class CustomerBookViewSet(CustomModelViewSet):
    """用户端-图书浏览（公开）"""
    queryset = Book.objects.filter(status='on_sale', merchant__status='approved', merchant__is_open=True)
    serializer_class = CustomerBookSerializer
    filter_fields = ["category"]
    search_fields = ["title", "author", "isbn"]
    permission_classes = [AllowAny]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        qs = Book.objects.filter(status='on_sale', merchant__status='approved', merchant__is_open=True)
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'query_params'):
            category_id = request.query_params.get('category')
            if category_id:
                qs = qs.filter(category_id=category_id)
            ordering = request.query_params.get('ordering', '-create_datetime')
            allowed_ordering = ['-sales_count', '-publish_date', 'price', '-price', '-create_datetime']
            if ordering not in allowed_ordering:
                ordering = '-create_datetime'
            return qs.order_by(ordering)
        return qs.order_by('-create_datetime')


# ====== 商家端 — 分类（只读） ======

class MerchantCategoryViewSet(CustomModelViewSet):
    """商家端-分类树（只读）"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [MerchantPermission]
    http_method_names = ['get']
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['get'], detail=False, permission_classes=[MerchantPermission])
    def tree(self, request):
        """两级分类树"""
        top_categories = Category.objects.filter(parent__isnull=True).order_by('sort', 'id')
        data = []
        for cat in top_categories:
            children = Category.objects.filter(parent=cat).order_by('sort', 'id')
            cat_data = CategoryTreeSerializer(cat, request=request).data
            cat_data['children'] = CategoryTreeSerializer(children, many=True, request=request).data
            data.append(cat_data)
        return DetailResponse(data=data, msg="success")


# ====== 商家端 — 图书（数据隔离） ======

class MerchantBookViewSet(CustomModelViewSet):
    """商家端-图书管理（数据隔离）"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    create_serializer_class = MerchantBookCreateSerializer
    update_serializer_class = MerchantBookUpdateSerializer
    filter_fields = ["status", "category", "isbn"]
    search_fields = ["title", "author", "isbn"]
    permission_classes = [MerchantPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(merchant=user.merchant)

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant)

    @action(methods=['patch'], detail=True, permission_classes=[MerchantPermission])
    def status(self, request, pk=None):
        """上下架"""
        book = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ('on_sale', 'off_sale'):
            return ErrorResponse(code=4000, msg="status 参数不合法，须为 on_sale 或 off_sale")
        if new_status == 'on_sale':
            if not book.cover_image:
                return ErrorResponse(code=4000, msg="上架图书必须有封面图")
            if not book.price or not book.original_price:
                return ErrorResponse(code=4000, msg="价格信息不完整")
            if request.user.merchant.status != 'approved':
                return ErrorResponse(code=4000, msg="商家未通过审核，不可上架")
        book.status = new_status
        book.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=BookSerializer(book, request=request).data, msg="操作成功")

    @action(methods=['post'], detail=True, permission_classes=[MerchantPermission])
    def restock(self, request, pk=None):
        """补货"""
        book = self.get_object()
        quantity = request.data.get('quantity', 0)
        if not isinstance(quantity, int) or quantity <= 0:
            return ErrorResponse(code=4000, msg="补货数量必须为正整数")
        book.stock += quantity
        book.save(update_fields=['stock', 'update_datetime'])
        return DetailResponse(data=BookSerializer(book, request=request).data, msg=f"补货成功，当前库存: {book.stock}")

    @action(methods=['post'], detail=True, permission_classes=[MerchantPermission])
    def warning_stock(self, request, pk=None):
        """设置单品预警阈值"""
        book = self.get_object()
        threshold = request.data.get('warning_stock')
        if threshold is None or not isinstance(threshold, int) or threshold < 0:
            return ErrorResponse(code=4000, msg="预警阈值必须为非负整数")
        book.warning_stock = threshold
        book.save(update_fields=['warning_stock', 'update_datetime'])
        return DetailResponse(data=BookSerializer(book, request=request).data, msg=f"预警阈值已设置为 {threshold}")
