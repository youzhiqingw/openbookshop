from django.core.validators import RegexValidator
from dvadmin.utils.models import CoreModel, table_prefix
from django.db import models


class Merchant(CoreModel):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('disabled', '已禁用'),
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="店铺名称", help_text="店铺名称")
    logo = models.CharField(max_length=255, null=True, blank=True, verbose_name="店铺Logo", help_text="店铺Logo URL")
    description = models.TextField(null=True, blank=True, verbose_name="店铺描述", help_text="店铺描述")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="审核状态",
                              help_text="审核状态", db_index=True)
    contact_name = models.CharField(max_length=50, verbose_name="联系人姓名", help_text="联系人姓名")
    contact_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^1[3-9]\d{9}$', message='联系电话格式不正确')],
        verbose_name="联系电话", help_text="联系电话",
    )
    contact_email = models.EmailField(verbose_name="联系邮箱", help_text="联系邮箱")
    address = models.CharField(max_length=255, verbose_name="店铺地址", help_text="店铺地址")
    is_open = models.BooleanField(default=True, verbose_name="营业状态", help_text="营业状态")
    reject_reason = models.CharField(max_length=500, null=True, blank=True, verbose_name="拒绝原因",
                                     help_text="拒绝原因")

    class Meta:
        db_table = table_prefix + "bookshop_merchant"
        verbose_name = "商家表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.name
