from dvadmin.bookshop.models import CartItem
from dvadmin.bookshop.serializers.cart import CartItemSerializer, CartItemCreateSerializer
from dvadmin.bookshop.permissions import OwnerPermission
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend


class CustomerCartViewSet(CustomModelViewSet):
    """消费者端-购物车"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    create_serializer_class = CartItemCreateSerializer
    permission_classes = [OwnerPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """加入购物车（合并逻辑）"""
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']

        existing = CartItem.objects.filter(user=request.user, book_id=book_id).first()
        if existing:
            new_qty = existing.quantity + quantity
            if new_qty > 99:
                return ErrorResponse(code=4000, msg='购物车数量超出上限')
            existing.quantity = new_qty
            existing.save(update_fields=['quantity', 'update_datetime'])
            return DetailResponse(data=CartItemSerializer(existing, context={'request': request}).data, msg='添加成功')
        else:
            cart_item = CartItem.objects.create(
                user=request.user, book_id=book_id, quantity=quantity
            )
            return DetailResponse(data=CartItemSerializer(cart_item, context={'request': request}).data, msg='添加成功')

    def update(self, request, *args, **kwargs):
        """更新数量"""
        instance = self.get_object()
        quantity = request.data.get('quantity')
        if quantity is None or quantity < 1 or quantity > 99:
            return ErrorResponse(code=4000, msg='数量不合法')
        instance.quantity = quantity
        instance.save(update_fields=['quantity', 'update_datetime'])
        return DetailResponse(data=CartItemSerializer(instance, context={'request': request}).data, msg='更新成功')
