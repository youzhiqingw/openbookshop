from django.contrib.auth import authenticate, get_user_model
from rest_framework import filters, status
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from utils.permissions import IsAdmin
from utils.response import error_response, success_response

from .models import Address, OperationLog
from .serializers import (
    AddressSerializer, ChangePasswordSerializer, LoginSerializer,
    RegisterSerializer, UserListSerializer, UserProfileSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    """用户注册"""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = {
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }
        return success_response(data=data, message="注册成功", code=201)


class LoginView(APIView):
    """用户登录"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if user is None:
            return error_response(message="用户名或密码错误", code=401)

        if not user.is_active:
            return error_response(message="账号已被禁用", code=403)

        refresh = RefreshToken.for_user(user)
        data = {
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }

        # 记录登录日志
        OperationLog.objects.create(
            user=user,
            action='login',
            module='auth',
            detail=f'用户 {user.username} 登录',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        return success_response(data=data, message="登录成功")


class LogoutView(APIView):
    """用户登出"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return success_response(message="登出成功")
        except Exception:
            return success_response(message="登出成功")


class UserProfileView(RetrieveUpdateAPIView):
    """用户资料查看与更新"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(UpdateAPIView):
    """修改密码"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        if not user.check_password(serializer.validated_data['old_password']):
            return error_response(message="原密码错误")

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return success_response(message="密码修改成功")


class AddressViewSet(ModelViewSet):
    """收货地址CRUD"""

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user)
        if address.is_default:
            Address.objects.filter(user=self.request.user).exclude(pk=address.pk).update(is_default=False)

    def perform_update(self, serializer):
        address = serializer.save()
        if address.is_default:
            Address.objects.filter(user=self.request.user).exclude(pk=address.pk).update(is_default=False)


class AdminUserListView(ListAPIView):
    """管理员用户列表"""

    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
