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


# ---------------------------------------------------------------------------
# Review Views
# ---------------------------------------------------------------------------

class BookReviewListView(ListAPIView):
    """图书评论列表（已审核通过的）"""

    serializer_class = None  # set in get_serializer_class
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        from .serializers import ReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        from .models import Review
        book_id = self.kwargs['pk']
        return Review.objects.filter(
            book_id=book_id, is_approved=True
        ).select_related('user').order_by('-created_at')


class BookReviewCreateView(APIView):
    """用户提交评论（需已购买该书）"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from django.utils import timezone as tz
        from .models import Book, Review
        from .serializers import ReviewCreateSerializer, ReviewSerializer
        from utils.sensitive_filter import sensitive_filter

        try:
            book = Book.objects.get(pk=pk, is_on_sale=True)
        except Book.DoesNotExist:
            return error_response(message="图书不存在", code=404)

        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 检查是否购买过该书（订单已完成/已确认收货）
        from apps.orders.models import Order, OrderItem
        order_id = data.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(
                    pk=order_id, user=request.user,
                    status__in=['completed', 'delivered'],
                )
                if not order.items.filter(book=book).exists():
                    return error_response(message="该订单中没有此书")
            except Order.DoesNotExist:
                return error_response(message="订单不存在或状态不满足评论条件")
        else:
            # 无订单时检查是否有任意已完成订单含此书
            has_order = OrderItem.objects.filter(
                book=book, order__user=request.user,
                order__status__in=['completed', 'delivered'],
            ).exists()
            if not has_order:
                return error_response(message="请先购买并确认收货后再评论")
            order = None

        # 检查是否已评论过（同一用户+同一书+同一订单唯一）
        qs = Review.objects.filter(user=request.user, book=book)
        if order:
            qs = qs.filter(order=order)
        else:
            qs = qs.filter(order__isnull=True)
        if qs.exists():
            return error_response(message="您已对该书（订单）评论过了")

        # 敏感词检测
        content = data['content']
        is_sensitive = sensitive_filter.contains(content)
        is_approved = not is_sensitive  # 无敏感词自动通过

        review = Review.objects.create(
            user=request.user,
            book=book,
            order=order,
            rating=data['rating'],
            content=content,
            is_sensitive=is_sensitive,
            is_approved=is_approved,
        )

        # 更新图书平均评分（销量加权，简单处理）
        from apps.users.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action='create_review',
            module='books',
            detail=f'用户 {request.user.username} 评论《{book.title}》，评分 {data["rating"]}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        result = ReviewSerializer(review).data
        msg = "评论已提交，待审核" if is_sensitive else "评论发布成功"
        return success_response(data=result, message=msg, code=201)


class MerchantReviewReplyView(APIView):
    """商家回复评论"""

    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def post(self, request, pk):
        from django.utils import timezone as tz
        from .models import Review
        from .serializers import MerchantReplySerializer, ReviewSerializer

        try:
            review = Review.objects.get(pk=pk, book__merchant=request.user.merchant)
        except Review.DoesNotExist:
            return error_response(message="评论不存在", code=404)

        serializer = MerchantReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.merchant_reply = serializer.validated_data['merchant_reply']
        review.replied_at = tz.now()
        review.save(update_fields=['merchant_reply', 'replied_at', 'updated_at'])
        return success_response(data=ReviewSerializer(review).data, message="回复成功")


class AdminReviewListView(ListAPIView):
    """管理员查看所有评论（可过滤待审核）"""

    serializer_class = None
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'book__title', 'content']

    def get_serializer_class(self):
        from .serializers import ReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        from .models import Review
        queryset = Review.objects.select_related('user', 'book').order_by('-created_at')
        is_approved = self.request.query_params.get('is_approved')
        if is_approved is not None:
            queryset = queryset.filter(is_approved=is_approved in ('true', '1', 'True'))
        is_sensitive = self.request.query_params.get('is_sensitive')
        if is_sensitive is not None:
            queryset = queryset.filter(is_sensitive=is_sensitive in ('true', '1', 'True'))
        return queryset


class AdminReviewApproveView(APIView):
    """管理员审核评论"""

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        from .models import Review
        from .serializers import ReviewSerializer
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return error_response(message="评论不存在", code=404)

        action = request.data.get('action', 'approve')
        if action == 'approve':
            review.is_approved = True
        elif action == 'reject':
            review.is_approved = False
        else:
            return error_response(message="无效操作，使用 approve 或 reject")
        review.save(update_fields=['is_approved', 'updated_at'])
        return success_response(data=ReviewSerializer(review).data, message="操作成功")


class MerchantReviewListView(ListAPIView):
    """商家查看自己图书的评论"""

    serializer_class = None
    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def get_serializer_class(self):
        from .serializers import ReviewSerializer
        return ReviewSerializer

    def get_queryset(self):
        from .models import Review
        return Review.objects.filter(
            book__merchant=self.request.user.merchant
        ).select_related('user', 'book').order_by('-created_at')
