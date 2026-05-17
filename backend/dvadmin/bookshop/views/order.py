from django.db import transaction, models
from rest_framework.decorators import action
from dvadmin.bookshop.models import Order, OrderItem, Book
from dvadmin.bookshop.serializers.order import OrderSerializer
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend
from dvadmin.utils.permission import CustomPermission
from dvadmin.bookshop.permissions import MerchantPermission
from django.utils import timezone


class AdminOrderViewSet(CustomModelViewSet):
    """管理端-订单监控"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_fields = ["status", "merchant", "user"]
    search_fields = ["order_no", "receiver_name"]
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['post'], detail=True, permission_classes=[CustomPermission])
    @transaction.atomic
    def force_refund(self, request, pk=None):
        """强制退款"""
        order = self.get_object()
        if order.status in ('cancelled', 'refunded', 'completed'):
            return ErrorResponse(code=4000, msg='该订单状态不允许强制退款')

        # 锁定订单
        order = Order.objects.select_for_update().get(id=order.id)

        # 释放库存
        for item in order.items.all():
            Book.objects.filter(id=item.book_id).update(
                stock=models.F('stock') + item.quantity
            )

        order.status = 'refunded'
        order.cancel_reason = request.data.get('reason', '管理员强制退款')
        order.save(update_fields=['status', 'cancel_reason', 'update_datetime'])
        return DetailResponse(data=OrderSerializer(order, context={'request': request}).data, msg='强制退款成功')


class MerchantOrderViewSet(CustomModelViewSet):
    """商家端-订单管理（数据隔离）"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_fields = ["status"]
    search_fields = ["order_no", "receiver_name"]
    permission_classes = [MerchantPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(merchant=user.merchant)

    # 禁止商家直接创建/更新/删除订单，只能通过action操作
    def create(self, request, *args, **kwargs):
        return ErrorResponse(code=4000, msg="商家不能直接创建订单")

    def update(self, request, *args, **kwargs):
        return ErrorResponse(code=4000, msg="商家不能直接修改订单")

    def destroy(self, request, *args, **kwargs):
        return ErrorResponse(code=4000, msg="商家不能删除订单")

    @action(methods=['post'], detail=True, permission_classes=[MerchantPermission])
    @transaction.atomic
    def ship(self, request, pk=None):
        """发货"""
        order = self.get_object()
        if order.status != 'paid':
            return ErrorResponse(code=4000, msg='仅已付款订单可发货')

        express_company = request.data.get('express_company', '').strip()
        express_no = request.data.get('express_no', '').strip()
        if not express_company or not express_no:
            return ErrorResponse(code=4000, msg='快递公司和快递单号不能为空')

        order = Order.objects.select_for_update().get(id=order.id)
        order.status = 'shipped'
        order.express_company = express_company
        order.express_no = express_no
        order.ship_time = timezone.now()
        order.save(update_fields=['status', 'express_company', 'express_no', 'ship_time', 'update_datetime'])
        return DetailResponse(data=OrderSerializer(order, context={'request': request}).data, msg='发货成功')

    @action(methods=['post'], detail=True, permission_classes=[MerchantPermission])
    @transaction.atomic
    def refund_approve(self, request, pk=None):
        """同意退款"""
        order = self.get_object()
        if order.status != 'refunding':
            return ErrorResponse(code=4000, msg='仅退款中的订单可操作')

        order = Order.objects.select_for_update().get(id=order.id)

        # 释放库存
        for item in order.items.all():
            Book.objects.filter(id=item.book_id).update(
                stock=models.F('stock') + item.quantity
            )

        order.status = 'refunded'
        order.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=OrderSerializer(order, context={'request': request}).data, msg='退款已同意，库存已释放')

    @action(methods=['post'], detail=True, permission_classes=[MerchantPermission])
    @transaction.atomic
    def refund_reject(self, request, pk=None):
        """拒绝退款"""
        order = self.get_object()
        if order.status != 'refunding':
            return ErrorResponse(code=4000, msg='仅退款中的订单可操作')

        order = Order.objects.select_for_update().get(id=order.id)
        # 回退到已发货或已付款状态（根据是否有物流信息判断）
        if order.express_no:
            order.status = 'shipped'
        else:
            order.status = 'paid'
        order.save(update_fields=['status', 'update_datetime'])
        return DetailResponse(data=OrderSerializer(order, context={'request': request}).data, msg='退款已拒绝')
