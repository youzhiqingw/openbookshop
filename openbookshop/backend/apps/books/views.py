from rest_framework import filters
from rest_framework.generics import (
    CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView,
    RetrieveUpdateDestroyAPIView, UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from utils.permissions import IsAdmin, IsMerchantApproved
from utils.response import error_response, success_response

from .models import Book, Category
from .serializers import (
    BookCreateSerializer, BookListSerializer, BookSerializer,
    CategorySerializer, CategorySimpleSerializer,
)


# ---------------------------------------------------------------------------
# Category Views
# ---------------------------------------------------------------------------

class CategoryListView(ListAPIView):
    """分类列表（树形，仅顶级分类，包含子分类）"""

    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Category.objects.filter(parent=None).prefetch_related('children')


class AdminCategoryCreateView(CreateAPIView):
    """管理员创建分类"""

    serializer_class = CategorySimpleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="分类创建成功", code=201)


class AdminCategoryUpdateView(RetrieveUpdateDestroyAPIView):
    """管理员更新/删除分类"""

    serializer_class = CategorySimpleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Category.objects.all()


# ---------------------------------------------------------------------------
# Public Book Views
# ---------------------------------------------------------------------------

class BookListView(ListAPIView):
    """图书列表（用户浏览，仅上架商品）"""

    serializer_class = BookListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'publisher']
    ordering_fields = ['price', 'sales', 'created_at']

    def get_queryset(self):
        queryset = Book.objects.filter(is_on_sale=True).select_related('merchant', 'category')
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class BookDetailView(RetrieveAPIView):
    """图书详情（用户浏览）"""

    serializer_class = BookSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Book.objects.filter(is_on_sale=True).select_related('merchant', 'category')


# ---------------------------------------------------------------------------
# Merchant Book Management Views
# ---------------------------------------------------------------------------

class MerchantBookListView(ListAPIView):
    """商家图书列表（含下架商品）"""

    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsMerchantApproved]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['price', 'stock', 'sales', 'created_at']

    def get_queryset(self):
        return Book.objects.filter(
            merchant=self.request.user.merchant
        ).select_related('category')


class MerchantBookCreateView(CreateAPIView):
    """商家创建图书"""

    serializer_class = BookCreateSerializer
    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(merchant=request.user.merchant)
        return success_response(data=serializer.data, message="图书创建成功", code=201)


class MerchantBookUpdateView(RetrieveUpdateDestroyAPIView):
    """商家更新/删除图书"""

    serializer_class = BookCreateSerializer
    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def get_queryset(self):
        return Book.objects.filter(merchant=self.request.user.merchant)

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        book.delete()
        return success_response(message="图书已删除")


# ---------------------------------------------------------------------------
# Admin Book Management Views
# ---------------------------------------------------------------------------

class AdminBookListView(ListAPIView):
    """管理员图书列表（全平台）"""

    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'merchant__store_name']
    ordering_fields = ['price', 'stock', 'sales', 'created_at']

    def get_queryset(self):
        queryset = Book.objects.select_related('merchant', 'category').order_by('-created_at')
        merchant_id = self.request.query_params.get('merchant')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
        return queryset


class AdminBookUpdateView(RetrieveUpdateDestroyAPIView):
    """管理员更新/删除任意图书"""

    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Book.objects.all()


class AdminLowStockView(ListAPIView):
    """管理员查看全平台库存预警图书"""

    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        from django.db.models import F
        return Book.objects.filter(
            stock__lte=F('warning_stock')
        ).select_related('merchant', 'category').order_by('stock')


class MerchantLowStockView(ListAPIView):
    """商家查看自己的库存预警图书"""

    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def get_queryset(self):
        from django.db.models import F
        return Book.objects.filter(
            merchant=self.request.user.merchant,
            stock__lte=F('warning_stock'),
        ).order_by('stock')
