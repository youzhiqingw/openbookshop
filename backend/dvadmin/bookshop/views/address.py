from rest_framework.decorators import action
from dvadmin.bookshop.models import Address
from dvadmin.bookshop.serializers.address import AddressSerializer
from dvadmin.bookshop.permissions import OwnerPermission
from dvadmin.utils.json_response import DetailResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend


class CustomerAddressViewSet(CustomModelViewSet):
    """消费者端-收货地址"""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [OwnerPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    @action(methods=['patch'], detail=True, permission_classes=[OwnerPermission])
    def default(self, request, pk=None):
        """设为默认地址"""
        address = self.get_object()
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save(update_fields=['is_default', 'update_datetime'])
        return DetailResponse(data=AddressSerializer(address, request=request).data, msg='设置成功')
