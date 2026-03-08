from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView
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

    def update(self, request, *args, **kwargs):
        from apps.users.models import OperationLog
        response = super().update(request, *args, **kwargs)
        merchant = self.get_object()
        OperationLog.objects.create(
            user=request.user,
            action='audit_merchant',
            module='merchants',
            detail=f'管理员 {request.user.username} 审核商家 {merchant.store_name}: {merchant.status}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        return response


class AdminMerchantListView(ListAPIView):
    """管理员商家列表"""

    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['store_name', 'user__username', 'business_license']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        queryset = Merchant.objects.select_related('user').order_by('-created_at')
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
