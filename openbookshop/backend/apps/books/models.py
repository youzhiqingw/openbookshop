from django.conf import settings
from django.db import models


class Category(models.Model):
    """图书分类（支持两级：一级分类/二级分类）"""

    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name='父分类',
    )
    sort_order = models.IntegerField('排序权重', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Book(models.Model):
    """图书"""

    merchant = models.ForeignKey(
        'merchants.Merchant', on_delete=models.CASCADE,
        related_name='books', verbose_name='所属商家',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='books', verbose_name='分类',
    )
    title = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100)
    isbn = models.CharField('ISBN', max_length=20, blank=True)
    publisher = models.CharField('出版社', max_length=100, blank=True)
    publish_date = models.DateField('出版日期', null=True, blank=True)
    description = models.TextField('图书简介', blank=True)
    cover = models.ImageField('封面图片', upload_to='book_covers/', blank=True, null=True)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    stock = models.IntegerField('库存', default=0)
    warning_stock = models.IntegerField('预警库存', default=10)
    sales = models.IntegerField('销售量', default=0)
    is_on_sale = models.BooleanField('是否上架', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_low_stock(self):
        return self.stock <= self.warning_stock
