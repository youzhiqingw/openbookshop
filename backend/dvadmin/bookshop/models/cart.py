from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class CartItem(CoreModel):
    """购物车项"""
    user = models.ForeignKey(
        to='system.Users', on_delete=models.CASCADE,
        related_name='cart_items', verbose_name='消费者',
        db_constraint=False,
    )
    book = models.ForeignKey(
        to='bookshop.Book', on_delete=models.CASCADE,
        verbose_name='图书', db_constraint=False,
    )
    quantity = models.IntegerField(default=1, verbose_name='数量')

    class Meta:
        db_table = table_prefix + 'bookshop_cart_item'
        ordering = ('-create_datetime',)
        unique_together = ['user', 'book']
        indexes = [
            models.Index(fields=['user_id'], name='idx_cart_user'),
        ]
        verbose_name = '购物车项'
        verbose_name_plural = verbose_name
