import json
from datetime import timedelta

from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from dvadmin.bookshop.models import Book, Order, OrderItem, Merchant, Category
from dvadmin.bookshop.serializers.statistics import WarningBookSerializer, WarningThresholdSerializer
from dvadmin.bookshop.permissions import MerchantPermission
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.filters import CoreModelFilterBankend
from dvadmin.utils.permission import CustomPermission


def get_global_threshold():
    from dvadmin.system.models import SystemConfig
    config = SystemConfig.objects.filter(key='bookshop_warning_stock_threshold').first()
    if config and config.value:
        try:
            return int(config.value)
        except (ValueError, TypeError):
            pass
    return 10


def compute_warning_level(stock, threshold):
    if stock == 0:
        return 'critical'
    elif stock <= threshold * 0.5:
        return 'warning'
    elif stock <= threshold:
        return 'info'
    return None


def get_warning_queryset(merchant=None):
    """返回所有触发预警的图书 QuerySet"""
    global_threshold = get_global_threshold()
    books = Book.objects.select_related('merchant', 'category').all()
    if merchant:
        books = books.filter(merchant=merchant)

    warning_books = []
    for book in books:
        effective = book.warning_stock if (book.warning_stock and book.warning_stock > 0) else global_threshold
        level = compute_warning_level(book.stock, effective)
        if level:
            warning_books.append(book.id)

    return Book.objects.select_related('merchant', 'category').filter(id__in=warning_books)


class AdminWarningViewSet(CustomModelViewSet):
    """管理端-库存预警"""
    queryset = Book.objects.select_related('merchant', 'category').all()
    serializer_class = WarningBookSerializer
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def list(self, request, *args, **kwargs):
        """全平台预警图书列表"""
        qs = get_warning_queryset()

        # 筛选参数
        level = request.query_params.get('level')
        merchant_id = request.query_params.get('merchant_id')
        category_id = request.query_params.get('category_id')

        if merchant_id:
            qs = qs.filter(merchant_id=merchant_id)
        if category_id:
            qs = qs.filter(category_id=category_id)

        if level:
            global_threshold = get_global_threshold()
            filtered_ids = []
            for book in qs:
                effective = book.warning_stock if (book.warning_stock and book.warning_stock > 0) else global_threshold
                book_level = compute_warning_level(book.stock, effective)
                if book_level == level:
                    filtered_ids.append(book.id)
            qs = qs.filter(id__in=filtered_ids)

        # 分页
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = WarningBookSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = WarningBookSerializer(qs, many=True, context={'request': request})
        return DetailResponse(data=serializer.data, msg="success")

    @action(methods=['get'], detail=False, permission_classes=[CustomPermission])
    def threshold(self, request):
        """获取全局预警阈值"""
        threshold = get_global_threshold()
        return DetailResponse(data={'threshold': threshold}, msg="success")

    @threshold.mapping.put
    def set_threshold(self, request):
        """设置全局预警阈值"""
        serializer = WarningThresholdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        threshold = serializer.validated_data['threshold']

        from dvadmin.system.models import SystemConfig
        config, _ = SystemConfig.objects.get_or_create(
            key='bookshop_warning_stock_threshold',
            defaults={'value': str(threshold)}
        )
        config.value = str(threshold)
        config.save(update_fields=['value'])
        return DetailResponse(data={'threshold': threshold}, msg="设置成功")


class MerchantWarningViewSet(CustomModelViewSet):
    """商家端-库存预警"""
    queryset = Book.objects.select_related('merchant', 'category').all()
    serializer_class = WarningBookSerializer
    permission_classes = [MerchantPermission]
    extra_filter_class = [CoreModelFilterBankend]

    def list(self, request, *args, **kwargs):
        """自己店铺预警图书列表"""
        merchant = request.user.merchant
        qs = get_warning_queryset(merchant=merchant)

        level = request.query_params.get('level')
        category_id = request.query_params.get('category_id')

        if category_id:
            qs = qs.filter(category_id=category_id)

        if level:
            global_threshold = get_global_threshold()
            filtered_ids = []
            for book in qs:
                effective = book.warning_stock if (book.warning_stock and book.warning_stock > 0) else global_threshold
                book_level = compute_warning_level(book.stock, effective)
                if book_level == level:
                    filtered_ids.append(book.id)
            qs = qs.filter(id__in=filtered_ids)

        serializer = WarningBookSerializer(qs, many=True, context={'request': request})
        return DetailResponse(data=serializer.data, msg="success")


class AdminStatisticsViewSet(CustomModelViewSet):
    """管理端-统计仪表盘"""
    queryset = Book.objects.none()
    permission_classes = [CustomPermission]
    extra_filter_class = [CoreModelFilterBankend]

    @action(methods=['get'], detail=False, permission_classes=[CustomPermission])
    def overview(self, request):
        """总览数据"""
        from dvadmin.system.models import Users
        paid_statuses = ['paid', 'shipped', 'received', 'completed']
        sales_agg = Order.objects.filter(status__in=paid_statuses).aggregate(total=Sum('pay_amount'))
        total_sales = sales_agg['total'] or 0

        data = {
            'total_books': Book.objects.count(),
            'on_sale_books': Book.objects.filter(status='on_sale').count(),
            'total_merchants': Merchant.objects.count(),
            'approved_merchants': Merchant.objects.filter(status='approved').count(),
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_sales_amount': str(total_sales),
            'total_users': Users.objects.filter(user_type=3).count(),
            'warning_count': get_warning_queryset().count(),
        }
        return DetailResponse(data=data, msg="success")

    @action(methods=['get'], detail=False, permission_classes=[CustomPermission])
    def trend(self, request):
        """趋势数据"""
        days = request.query_params.get('days', '30')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            try:
                start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                if start > end:
                    return ErrorResponse(code=4000, msg="起始日期不能晚于结束日期")
            except ValueError:
                return ErrorResponse(code=4000, msg="日期格式不正确")
        else:
            try:
                days_int = int(days)
                if days_int < 1 or days_int > 90:
                    return ErrorResponse(code=4000, msg="天数必须在1-90之间")
            except (ValueError, TypeError):
                return ErrorResponse(code=4000, msg="天数必须在1-90之间")
            end = timezone.now().date()
            start = end - timedelta(days=days_int - 1)

        from dvadmin.system.models import Users

        order_trend = (
            Order.objects.filter(create_datetime__date__gte=start, create_datetime__date__lte=end)
            .annotate(date=TruncDate('create_datetime'))
            .values('date')
            .annotate(count=Count('id'), amount=Sum('pay_amount'))
            .order_by('date')
        )
        user_trend = (
            Users.objects.filter(date_joined__date__gte=start, date_joined__date__lte=end)
            .annotate(date=TruncDate('date_joined'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        order_map = {item['date']: item for item in order_trend}
        user_map = {item['date']: item['count'] for item in user_trend}

        dates, order_counts, sales_amounts, new_users = [], [], [], []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            item = order_map.get(current)
            order_counts.append(item['count'] if item else 0)
            sales_amounts.append(str(item['amount'] or 0) if item else '0')
            new_users.append(user_map.get(current, 0))
            current += timedelta(days=1)

        return DetailResponse(data={
            'dates': dates,
            'order_count': order_counts,
            'sales_amount': sales_amounts,
            'new_users': new_users,
        }, msg="success")

    @action(methods=['get'], detail=False, permission_classes=[CustomPermission])
    def category_distribution(self, request):
        """分类分布"""
        book_dist = (
            Book.objects.values('category_id', 'category__name')
            .annotate(book_count=Count('id'))
            .order_by('-book_count')
        )
        sales_dist = (
            OrderItem.objects.filter(order__status__in=['paid', 'shipped', 'received', 'completed'])
            .values('book__category_id')
            .annotate(sales_count=Sum('quantity'))
        )
        sales_map = {item['book__category_id']: item['sales_count'] for item in sales_dist}

        data = []
        for item in book_dist:
            data.append({
                'category_id': item['category_id'],
                'category_name': item['category__name'] or '',
                'book_count': item['book_count'],
                'sales_count': sales_map.get(item['category_id'], 0),
            })
        return DetailResponse(data=data, msg="success")

    @action(methods=['get'], detail=False, permission_classes=[CustomPermission])
    def merchant_ranking(self, request):
        """商家排行"""
        limit = request.query_params.get('limit', '10')
        order_by = request.query_params.get('order_by', 'sales_amount')

        try:
            limit_int = int(limit)
            if limit_int < 1 or limit_int > 50:
                return ErrorResponse(code=4000, msg="排行数量必须在1-50之间")
        except (ValueError, TypeError):
            return ErrorResponse(code=4000, msg="排行数量必须在1-50之间")

        if order_by not in ('sales_amount', 'order_count', 'book_count'):
            return ErrorResponse(code=4000, msg="排序字段不合法")

        if order_by == 'book_count':
            merchants = Merchant.objects.annotate(
                book_count=Count('books'),
            ).order_by('-book_count')[:limit_int]
            data = []
            for m in merchants:
                data.append({
                    'merchant_id': m.id,
                    'merchant_name': m.name,
                    'book_count': m.book_count,
                    'order_count': 0,
                    'sales_amount': '0',
                })
            return DetailResponse(data=data, msg="success")

        paid_statuses = ['paid', 'shipped', 'received', 'completed']
        order_items = (
            OrderItem.objects.filter(order__status__in=paid_statuses)
            .values('book__merchant_id', 'book__merchant__name')
            .annotate(
                order_count=Count('order_id', distinct=True),
                sales_amount=Sum(F('price') * F('quantity')),
            )
        )

        if order_by == 'sales_amount':
            order_items = order_items.order_by('-sales_amount')[:limit_int]
        else:
            order_items = order_items.order_by('-order_count')[:limit_int]

        book_count_map = dict(
            Book.objects.values('merchant_id').annotate(cnt=Count('id')).values_list('merchant_id', 'cnt')
        )

        data = []
        for item in order_items:
            data.append({
                'merchant_id': item['book__merchant_id'],
                'merchant_name': item['book__merchant__name'],
                'book_count': book_count_map.get(item['book__merchant_id'], 0),
                'order_count': item['order_count'],
                'sales_amount': str(item['sales_amount'] or 0),
            })
        return DetailResponse(data=data, msg="success")
