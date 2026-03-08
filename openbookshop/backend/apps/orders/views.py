from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import filters
from rest_framework.generics import (
    DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.mock_services.logistics import mock_logistics
from utils.mock_services.payment import mock_payment
from utils.permissions import IsAdmin, IsMerchantApproved
from utils.response import error_response, success_response

from .models import Cart, Order, OrderItem
from .serializers import (
    CartSerializer, CartUpdateSerializer, OrderCreateSerializer, OrderSerializer,
)


# ---------------------------------------------------------------------------
# Cart Views
# ---------------------------------------------------------------------------

class CartListView(ListAPIView):
    """查看购物车"""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related(
            'book', 'book__merchant', 'book__category'
        )


class CartAddView(APIView):
    """加入购物车 / 追加数量"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.books.models import Book
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        if not book_id:
            return error_response(message="请指定图书")
        try:
            book = Book.objects.get(pk=book_id, is_on_sale=True)
        except Book.DoesNotExist:
            return error_response(message="图书不存在或已下架", code=404)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user, book=book,
            defaults={'quantity': 0},
        )
        new_quantity = cart_item.quantity + quantity
        if book.stock < new_quantity:
            return error_response(message="库存不足")
        cart_item.quantity = new_quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)
        msg = "已加入购物车" if created else "购物车已更新"
        return success_response(data=serializer.data, message=msg)


class CartUpdateView(UpdateAPIView):
    """更新购物车商品数量"""

    serializer_class = CartUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=CartSerializer(instance).data, message="购物车已更新")


class CartDeleteView(DestroyAPIView):
    """删除购物车商品"""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return success_response(message="已移出购物车")


class CartClearView(APIView):
    """清空购物车"""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return success_response(message="购物车已清空")


# ---------------------------------------------------------------------------
# Order Views
# ---------------------------------------------------------------------------

class OrderCreateView(APIView):
    """创建订单（从购物车下单）"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data['address_id']
        cart_item_ids = serializer.validated_data['cart_item_ids']
        remark = serializer.validated_data['remark']

        from apps.users.models import Address
        address = Address.objects.get(pk=address_id, user=request.user)

        # Determine which cart items to checkout
        cart_qs = Cart.objects.filter(user=request.user).select_related('book', 'book__merchant')
        if cart_item_ids:
            cart_qs = cart_qs.filter(id__in=cart_item_ids)

        cart_items = list(cart_qs)
        if not cart_items:
            return error_response(message="购物车为空，请先添加商品")

        # Validate stock and calculate total
        total_amount = Decimal('0.00')
        for item in cart_items:
            if not item.book.is_on_sale:
                return error_response(message=f"《{item.book.title}》已下架")
            if item.book.stock < item.quantity:
                return error_response(message=f"《{item.book.title}》库存不足")
            total_amount += item.book.price * item.quantity

        # Address snapshot
        address_snapshot = {
            'name': address.name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'detail': address.detail,
        }

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            address_snapshot=address_snapshot,
            remark=remark,
        )

        # Create order items and deduct stock
        for item in cart_items:
            cover_url = ''
            if item.book.cover:
                cover_url = request.build_absolute_uri(item.book.cover.url)
            OrderItem.objects.create(
                order=order,
                book=item.book,
                merchant=item.book.merchant,
                book_title=item.book.title,
                book_cover=cover_url,
                book_author=item.book.author,
                price=item.book.price,
                quantity=item.quantity,
                subtotal=item.book.price * item.quantity,
            )
            # Deduct stock
            item.book.stock -= item.quantity
            item.book.save(update_fields=['stock'])

        # Remove purchased items from cart
        cart_qs.delete()

        # Log
        from apps.users.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action='create_order',
            module='orders',
            detail=f'用户 {request.user.username} 创建订单 {order.order_no}，金额 ¥{total_amount}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return success_response(
            data=OrderSerializer(order).data,
            message="订单创建成功",
            code=201,
        )


class OrderListView(ListAPIView):
    """用户订单列表"""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).prefetch_related('items')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class OrderDetailView(RetrieveAPIView):
    """用户订单详情"""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderCancelView(APIView):
    """用户取消订单"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if order.status not in ('pending_payment', 'paid'):
            return error_response(message="当前状态不允许取消订单")

        # Restore stock
        for item in order.items.select_related('book').all():
            if item.book:
                item.book.stock += item.quantity
                item.book.save(update_fields=['stock'])

        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
        return success_response(message="订单已取消")


# ---------------------------------------------------------------------------
# Payment Views
# ---------------------------------------------------------------------------

class OrderPayView(APIView):
    """发起支付"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if order.status != 'pending_payment':
            return error_response(message="订单状态不允许支付")

        payment_method = request.data.get('payment_method', 'mock')
        result = mock_payment.create_order(order.id, order.total_amount, payment_method)

        order.payment_method = payment_method
        order.mock_payment_id = result['mock_order_id']
        order.pay_url = result['pay_url']
        order.save(update_fields=['payment_method', 'mock_payment_id', 'pay_url', 'updated_at'])

        return success_response(data={
            'order_no': order.order_no,
            'mock_payment_id': result['mock_order_id'],
            'pay_url': result['pay_url'],
            'amount': str(order.total_amount),
        }, message="支付信息已生成")


class OrderPayCallbackView(APIView):
    """模拟支付回调（轮询确认支付结果）"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if order.status != 'pending_payment':
            return error_response(message="订单状态异常")

        if not order.mock_payment_id:
            return error_response(message="请先发起支付")

        payment_status = mock_payment.query_status(order.mock_payment_id)

        if payment_status == 'success':
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save(update_fields=['status', 'paid_at', 'updated_at'])

            # Update sales count
            for item in order.items.select_related('book').all():
                if item.book:
                    item.book.sales += item.quantity
                    item.book.save(update_fields=['sales'])

            # Log
            from apps.users.models import OperationLog
            OperationLog.objects.create(
                user=request.user,
                action='pay_order',
                module='orders',
                detail=f'订单 {order.order_no} 支付成功，金额 ¥{order.total_amount}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            return success_response(data={'status': 'success', 'order_no': order.order_no}, message="支付成功")
        elif payment_status == 'pending':
            return success_response(data={'status': 'pending'}, message="支付处理中，请稍候")
        else:
            return error_response(message="支付失败，请重试", code=402)


# ---------------------------------------------------------------------------
# Merchant Order Views
# ---------------------------------------------------------------------------

class MerchantOrderListView(ListAPIView):
    """商家订单列表（仅显示包含自己商品的订单）"""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsMerchantApproved]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        merchant = self.request.user.merchant
        order_ids = OrderItem.objects.filter(
            merchant=merchant
        ).values_list('order_id', flat=True).distinct()
        queryset = Order.objects.filter(id__in=order_ids).prefetch_related('items')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class MerchantOrderShipView(APIView):
    """商家发货"""

    permission_classes = [IsAuthenticated, IsMerchantApproved]

    def post(self, request, pk):
        merchant = request.user.merchant
        order_ids = OrderItem.objects.filter(
            merchant=merchant
        ).values_list('order_id', flat=True)
        try:
            order = Order.objects.get(pk=pk, id__in=order_ids)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if order.status != 'paid':
            return error_response(message="只有已支付的订单才能发货")

        # Build address string for logistics
        addr = order.address_snapshot
        address_str = f"{addr.get('province', '')}{addr.get('city', '')}{addr.get('district', '')}{addr.get('detail', '')}"

        shipment = mock_logistics.create_shipment(order.id, address_str)

        order.status = 'shipped'
        order.tracking_number = shipment['tracking_number']
        order.carrier = shipment['carrier']
        order.shipped_at = timezone.now()
        order.save(update_fields=['status', 'tracking_number', 'carrier', 'shipped_at', 'updated_at'])

        from apps.users.models import OperationLog
        OperationLog.objects.create(
            user=request.user,
            action='ship_order',
            module='orders',
            detail=f'商家 {merchant.store_name} 发货订单 {order.order_no}，快递单号 {order.tracking_number}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return success_response(data={
            'tracking_number': order.tracking_number,
            'carrier': order.carrier,
        }, message="发货成功")


# ---------------------------------------------------------------------------
# Admin Order Views
# ---------------------------------------------------------------------------

class AdminOrderListView(ListAPIView):
    """管理员查看所有订单"""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_no', 'user__username']
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items').order_by('-created_at')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class OrderTrackingView(RetrieveAPIView):
    """查询物流信息"""

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if not order.tracking_number:
            return error_response(message="订单尚未发货")

        tracking_data = mock_logistics.query_tracking(order.tracking_number)
        return success_response(data=tracking_data)


class OrderConfirmView(APIView):
    """用户确认收货"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return error_response(message="订单不存在", code=404)

        if order.status != 'shipped':
            return error_response(message="订单尚未发货，无法确认收货")

        order.status = 'completed'
        order.delivered_at = timezone.now()
        order.save(update_fields=['status', 'delivered_at', 'updated_at'])
        return success_response(message="确认收货成功")
