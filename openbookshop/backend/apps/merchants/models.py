from django.conf import settings
from django.db import models


class Merchant(models.Model):
    """商家模型"""

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='merchant', verbose_name='用户'
    )
    store_name = models.CharField('店铺名称', max_length=100)
    logo = models.ImageField('店铺Logo', upload_to='merchant_logos/', blank=True, null=True)
    description = models.TextField('店铺描述', blank=True)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    business_license = models.CharField('营业执照号', max_length=50, blank=True)
    address = models.CharField('经营地址', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商家'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.store_name

    @property
    def is_approved(self):
        return self.status == 'approved'
