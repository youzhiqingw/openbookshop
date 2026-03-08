import uuid

from django.conf import settings
from django.db import models


def generate_order_no():
    """生成唯一订单号"""
    return uuid.uuid4().hex.upper()[:20]


class Cart(models.Model):
    """购物车"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cart_items', verbose_name='用户',
    )
    book = models.ForeignKey(
        'books.Book', on_delete=models.CASCADE,
        related_name='cart_items', verbose_name='图书',
    )
    quantity = models.IntegerField('数量', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} x{self.quantity}"


class Order(models.Model):
    """订单"""

    STATUS_CHOICES = [
        ('pending_payment', '待支付'),
        ('paid', '已支付'),
        ('processing', '备货中'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('mock', '模拟支付'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='orders', verbose_name='用户',
    )
    order_no = models.CharField('订单号', max_length=50, unique=True, default=generate_order_no)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    # 地址快照（下单时记录，防止地址修改影响历史订单）
    address_snapshot = models.JSONField('收货地址快照')
    remark = models.CharField('备注', max_length=200, blank=True)
    # 支付信息
    payment_method = models.CharField('支付方式', max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    mock_payment_id = models.CharField('模拟支付ID', max_length=200, blank=True)
    pay_url = models.CharField('支付链接', max_length=500, blank=True)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)
    # 物流信息
    tracking_number = models.CharField('物流单号', max_length=100, blank=True)
    carrier = models.CharField('快递公司', max_length=50, blank=True)
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('签收时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    """订单商品"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='订单',
    )
    book = models.ForeignKey(
        'books.Book', on_delete=models.SET_NULL, null=True,
        related_name='order_items', verbose_name='图书',
    )
    merchant = models.ForeignKey(
        'merchants.Merchant', on_delete=models.SET_NULL, null=True,
        related_name='order_items', verbose_name='商家',
    )
    # 商品快照（下单时记录）
    book_title = models.CharField('书名快照', max_length=200)
    book_cover = models.CharField('封面URL快照', max_length=500, blank=True)
    book_author = models.CharField('作者快照', max_length=100, blank=True)
    price = models.DecimalField('单价快照', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('数量')
    subtotal = models.DecimalField('小计', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.order.order_no} - {self.book_title}"
