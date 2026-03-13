from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Address, OperationLog

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2", "email", "phone", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False},
            "phone": {"required": False},
            "role": {"required": False, "default": "customer"},
        }

    def validate_password2(self, value):
        if self.initial_data.get("password") != value:
            raise serializers.ValidationError("两次密码不一致")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_role(self, value):
        # 注册时允许任何有效角色，但后台管理会进一步控制
        if value not in ("customer", "merchant", "admin"):
            raise serializers.ValidationError(
                "角色必须为：customer, merchant, 或 admin"
            )
        return value

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        role = validated_data.get("role", "customer")

        user = User(**validated_data)
        user.set_password(password)

        # 根据角色设置 is_staff（Django后台登录需要）
        if role in ("admin", "merchant"):
            user.is_staff = True

        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""

    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "avatar",
            "role",
            "is_vip",
            "vip_level",
            "points",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "role",
            "is_vip",
            "vip_level",
            "points",
            "is_staff",
            "date_joined",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""

    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password2 = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "两次新密码不一致"})
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    """地址序列化器"""

    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "phone",
            "province",
            "city",
            "district",
            "detail",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and self.instance is None:
            if request.user.addresses.count() >= 5:
                raise serializers.ValidationError("最多只能添加5个收货地址")
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """管理员用户列表序列化器"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "is_active",
            "date_joined",
        ]


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "user",
            "username",
            "action",
            "module",
            "detail",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = fields
