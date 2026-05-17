from django.core.validators import RegexValidator
from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class Address(CoreModel):
    """收货地址"""
    user = models.ForeignKey(
        to='system.Users', on_delete=models.CASCADE,
        related_name='addresses', verbose_name='消费者',
        db_constraint=False,
    )
    receiver_name = models.CharField(max_length=50, verbose_name='收货人')
    receiver_phone = models.CharField(
        max_length=20, verbose_name='联系电话',
        validators=[RegexValidator(regex=r'^1[3-9]\d{9}$', message='联系电话格式不正确')],
    )
    province = models.CharField(max_length=50, verbose_name='省份')
    city = models.CharField(max_length=50, verbose_name='城市')
    district = models.CharField(max_length=50, verbose_name='区/县')
    detail_address = models.CharField(max_length=255, verbose_name='详细地址')
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    class Meta:
        db_table = table_prefix + 'bookshop_address'
        ordering = ('-is_default', '-create_datetime')
        indexes = [
            models.Index(fields=['user_id'], name='idx_address_user'),
        ]
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
