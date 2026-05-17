from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class Order(CoreModel):
    """订单主表"""
    STATUS_CHOICES = (
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('received', '已收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
    )

    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单号')
    user = models.ForeignKey(
        to='system.Users', on_delete=models.PROTECT,
        related_name='orders', verbose_name='下单用户', db_constraint=False,
    )
    merchant = models.ForeignKey(
        to='bookshop.Merchant', on_delete=models.PROTECT,
        related_name='orders', verbose_name='所属商家', db_constraint=False,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态', db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单金额')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='优惠金额')
    freight_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='运费')
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实付金额')
    receiver_name = models.CharField(max_length=50, verbose_name='收货人')
    receiver_phone = models.CharField(max_length=20, verbose_name='联系电话')
    receiver_address = models.CharField(max_length=255, verbose_name='收货地址')
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    pay_method = models.CharField(max_length=50, null=True, blank=True, verbose_name='支付方式')
    ship_time = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    express_company = models.CharField(max_length=50, null=True, blank=True, verbose_name='快递公司')
    express_no = models.CharField(max_length=50, null=True, blank=True, verbose_name='快递单号')
    cancel_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name='取消/退款原因')

    class Meta:
        db_table = table_prefix + 'bookshop_order'
        ordering = ('-create_datetime',)
        indexes = [
            models.Index(fields=['user_id', 'status'], name='idx_order_user_status'),
            models.Index(fields=['merchant_id', 'status'], name='idx_order_merchant_status'),
        ]
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderItem(CoreModel):
    """订单项"""
    order = models.ForeignKey(
        to='Order', on_delete=models.CASCADE,
        related_name='items', verbose_name='关联订单', db_constraint=False,
    )
    book = models.ForeignKey(
        to='bookshop.Book', on_delete=models.PROTECT,
        verbose_name='图书', db_constraint=False,
    )
    book_title = models.CharField(max_length=200, verbose_name='书名快照')
    book_cover = models.CharField(max_length=255, default='', verbose_name='封面快照')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价快照')
    quantity = models.IntegerField(verbose_name='数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='小计')

    class Meta:
        db_table = table_prefix + 'bookshop_order_item'
        ordering = ('id',)
        indexes = [
            models.Index(fields=['order_id'], name='idx_orderitem_order'),
            models.Index(fields=['book_id'], name='idx_orderitem_book'),
        ]
        verbose_name = '订单项'
        verbose_name_plural = verbose_name
