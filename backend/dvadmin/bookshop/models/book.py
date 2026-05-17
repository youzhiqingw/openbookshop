from django.core.validators import RegexValidator, MinValueValidator
from dvadmin.utils.models import CoreModel, table_prefix
from django.db import models


class Category(CoreModel):
    """两级图书分类"""
    name = models.CharField(max_length=50, verbose_name="分类名称", help_text="分类名称")
    parent = models.ForeignKey(
        to='self', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="父分类", help_text="父分类（null=一级）", related_name='children',
    )
    sort = models.IntegerField(default=0, verbose_name="排序", help_text="排序")

    class Meta:
        db_table = table_prefix + "bookshop_category"
        verbose_name = "图书分类表"
        verbose_name_plural = verbose_name
        ordering = ("sort", "id")

    def __str__(self):
        return self.name


class Book(CoreModel):
    """图书"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('on_sale', '在售'),
        ('off_sale', '已下架'),
    )
    isbn = models.CharField(
        max_length=20, unique=True,
        validators=[RegexValidator(regex=r'^[0-9-]{10,20}$', message='ISBN格式不正确')],
        verbose_name="ISBN", help_text="ISBN",
    )
    title = models.CharField(max_length=200, verbose_name="书名", help_text="书名")
    author = models.CharField(max_length=100, verbose_name="作者", help_text="作者")
    publisher = models.CharField(max_length=100, verbose_name="出版社", help_text="出版社")
    publish_date = models.DateField(verbose_name="出版日期", help_text="出版日期")
    category = models.ForeignKey(
        to=Category, on_delete=models.PROTECT,
        verbose_name="分类", help_text="分类（必须二级分类）", related_name='books',
    )
    merchant = models.ForeignKey(
        to='bookshop.Merchant', on_delete=models.CASCADE,
        verbose_name="商家", help_text="商家", related_name='books',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="售价", help_text="售价")
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="原价", help_text="原价",
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                verbose_name="库存", help_text="库存")
    warning_stock = models.IntegerField(default=10, validators=[MinValueValidator(0)],
                                        verbose_name="预警阈值", help_text="单品预警阈值")
    cover_image = models.CharField(max_length=255, verbose_name="封面图", help_text="封面图URL")
    images = models.JSONField(default=list, verbose_name="详情图", help_text="详情图URL列表，最多10张")
    description = models.TextField(verbose_name="图书简介", help_text="图书简介")
    content = models.TextField(null=True, blank=True, verbose_name="目录/试读", help_text="目录/试读")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft',
                              verbose_name="上架状态", help_text="上架状态", db_index=True)
    sales_count = models.IntegerField(default=0, verbose_name="销量", help_text="销量")

    class Meta:
        db_table = table_prefix + "bookshop_book"
        verbose_name = "图书表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        indexes = [
            models.Index(fields=['merchant_id', 'status'], name='idx_book_merchant_status'),
            models.Index(fields=['category_id', 'status'], name='idx_book_category_status'),
        ]

    def __str__(self):
        return self.title
