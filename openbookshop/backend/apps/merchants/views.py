from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from utils.permissions import IsAdmin, IsMerchant
from utils.response import error_response, success_response

from .models import Merchant
from .serializers import MerchantApplySerializer, MerchantAuditSerializer, MerchantSerializer


class MerchantApplyView(CreateAPIView):
    """商家入驻申请"""

    serializer_class = MerchantApplySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, 'merchant'):
            return error_response(message="您已提交过商家申请")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        # Update user role
        request.user.role = 'merchant'
        request.user.save(update_fields=['role'])

        return success_response(data=serializer.data, message="商家申请已提交", code=201)


class MerchantProfileView(RetrieveUpdateAPIView):
    """商家资料查看与更新"""

    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated, IsMerchant]

    def get_object(self):
        return self.request.user.merchant


class MerchantAuditView(UpdateAPIView):
    """管理员审核商家"""

    serializer_class = MerchantAuditSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Merchant.objects.all()
