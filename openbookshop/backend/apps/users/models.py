from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""

    ROLE_CHOICES = [
        ("customer", "普通用户"),
        ("merchant", "商家"),
        ("admin", "管理员"),
    ]

    phone = models.CharField("手机号", max_length=11, blank=True)
    avatar = models.ImageField("头像", upload_to="avatars/", blank=True, null=True)
    role = models.CharField(
        "角色", max_length=20, choices=ROLE_CHOICES, default="customer"
    )
    is_vip = models.BooleanField("是否VIP", default=False)
    vip_level = models.IntegerField("VIP等级", default=0)
    points = models.IntegerField("积分", default=0)
    risk_score = models.IntegerField("风险评分", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(models.Model):
    """用户收货地址"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses", verbose_name="用户"
    )
    name = models.CharField("收货人", max_length=50)
    phone = models.CharField("手机号", max_length=11)
    province = models.CharField("省份", max_length=20)
    city = models.CharField("城市", max_length=20)
    district = models.CharField("区县", max_length=20)
    detail = models.CharField("详细地址", max_length=200)
    is_default = models.BooleanField("默认地址", default=False)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.province}{self.city}{self.district}{self.detail}"


class OperationLog(models.Model):
    """操作日志"""

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="operation_logs",
        verbose_name="用户",
    )
    action = models.CharField("操作", max_length=50)
    module = models.CharField("模块", max_length=50)
    detail = models.TextField("详情", blank=True)
    ip_address = models.GenericIPAddressField("IP地址", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.module}"
