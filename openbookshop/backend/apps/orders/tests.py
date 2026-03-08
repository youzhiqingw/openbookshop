from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.books.models import Book, Category
from apps.merchants.models import Merchant
from apps.users.models import Address

from .models import Cart, FinanceRecord, Order, OrderItem

User = get_user_model()


class CartAPITestCase(APITestCase):
    """Tests for shopping cart API."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='cart_customer', password='pass123', role='customer'
        )
        merchant_user = User.objects.create_user(
            username='cart_merchant', password='pass123', role='merchant'
        )
        self.merchant = Merchant.objects.create(
            user=merchant_user, store_name='Cart Shop', status='approved'
        )
        cat = Category.objects.create(name='分类')
        self.book = Book.objects.create(
            merchant=self.merchant, category=cat,
            title='Cart Test Book', author='Author',
            price=Decimal('25.00'), stock=10, is_on_sale=True,
        )

    def _auth(self):
        self.client.force_authenticate(user=self.customer)

    def test_add_to_cart(self):
        self._auth()
        resp = self.client.post('/api/v1/orders/cart/add/', {
            'book_id': self.book.id, 'quantity': 2
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Cart.objects.filter(user=self.customer, book=self.book).exists())

    def test_add_exceeds_stock(self):
        self._auth()
        resp = self.client.post('/api/v1/orders/cart/add/', {
            'book_id': self.book.id, 'quantity': 100
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_cart_list(self):
        self._auth()
        Cart.objects.create(user=self.customer, book=self.book, quantity=1)
        resp = self.client.get('/api/v1/orders/cart/')
        self.assertEqual(resp.status_code, 200)

    def test_remove_cart_item(self):
        self._auth()
        item = Cart.objects.create(user=self.customer, book=self.book, quantity=1)
        resp = self.client.delete(f'/api/v1/orders/cart/{item.id}/remove/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Cart.objects.filter(id=item.id).exists())

    def test_clear_cart(self):
        self._auth()
        Cart.objects.create(user=self.customer, book=self.book, quantity=1)
        resp = self.client.delete('/api/v1/orders/cart/clear/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Cart.objects.filter(user=self.customer).count(), 0)


class OrderAPITestCase(APITestCase):
    """Tests for order creation, payment, and status flow."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='order_customer', password='pass123', role='customer'
        )
        merchant_user = User.objects.create_user(
            username='order_merchant', password='pass123', role='merchant'
        )
        self.merchant = Merchant.objects.create(
            user=merchant_user, store_name='Order Shop', status='approved'
        )
        cat = Category.objects.create(name='订单分类')
        self.book = Book.objects.create(
            merchant=self.merchant, category=cat,
            title='Order Test Book', author='Author',
            price=Decimal('50.00'), stock=10, is_on_sale=True,
        )
        self.address = Address.objects.create(
            user=self.customer,
            name='Test User', phone='13800138000',
            province='广东', city='深圳', district='南山', detail='科技园1号',
        )
        # Add book to cart
        self.cart_item = Cart.objects.create(user=self.customer, book=self.book, quantity=2)

    def _auth(self):
        self.client.force_authenticate(user=self.customer)

    def test_create_order(self):
        self._auth()
        resp = self.client.post('/api/v1/orders/create/', {
            'address_id': self.address.id,
            'cart_item_ids': [self.cart_item.id],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()['data']
        self.assertEqual(data['status'], 'pending_payment')
        self.assertEqual(Decimal(data['total_amount']), Decimal('100.00'))
        # Stock should be deducted
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 8)
        # Cart should be cleared
        self.assertFalse(Cart.objects.filter(id=self.cart_item.id).exists())

    def test_create_order_insufficient_stock(self):
        self._auth()
        self.book.stock = 0
        self.book.save()
        resp = self.client.post('/api/v1/orders/create/', {
            'address_id': self.address.id,
            'cart_item_ids': [self.cart_item.id],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_pay_order(self):
        self._auth()
        # Create order first
        order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal('50.00'),
            address_snapshot={'name': 'T', 'phone': '13800138000', 'province': '广东', 'city': '深圳', 'district': '南山', 'detail': '1号'},
        )
        resp = self.client.post(f'/api/v1/orders/{order.id}/pay/', {
            'payment_method': 'mock'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        order.refresh_from_db()
        self.assertNotEqual(order.mock_payment_id, '')

    def test_cancel_pending_order_restores_stock(self):
        self._auth()
        # Create order
        resp = self.client.post('/api/v1/orders/create/', {
            'address_id': self.address.id,
            'cart_item_ids': [self.cart_item.id],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        order_id = resp.json()['data']['id']
        self.book.refresh_from_db()
        stock_after_order = self.book.stock

        # Cancel order
        cancel_resp = self.client.post(f'/api/v1/orders/{order_id}/cancel/')
        self.assertEqual(cancel_resp.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, stock_after_order + 2)

    def test_order_list_only_shows_own_orders(self):
        self._auth()
        other = User.objects.create_user('other_ord', password='pass')
        Order.objects.create(
            user=other, total_amount=Decimal('10'),
            address_snapshot={'name': 'X', 'phone': '13000000000', 'province': '北京', 'city': '北京', 'district': '海淀', 'detail': '某地'}
        )
        resp = self.client.get('/api/v1/orders/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(all(o['user'] == self.customer.id for o in results))


class OrderFlowAPITestCase(APITestCase):
    """Tests for order shipping, tracking, confirmation and admin/merchant views."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='flow_customer', password='pass123', role='customer'
        )
        self.merchant_user = User.objects.create_user(
            username='flow_merchant', password='pass123', role='merchant'
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user, store_name='Flow Shop', status='approved'
        )
        self.admin_user = User.objects.create_user(
            username='flow_admin', password='pass123', role='admin', is_staff=True
        )
        cat = Category.objects.create(name='流程分类')
        self.book = Book.objects.create(
            merchant=self.merchant, category=cat,
            title='Flow Test Book', author='Author',
            price=Decimal('40.00'), stock=10, is_on_sale=True,
        )
        addr_snapshot = {
            'name': 'Test', 'phone': '13800138001',
            'province': '广东', 'city': '深圳', 'district': '南山', 'detail': '测试路1号',
        }
        self.order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal('40.00'),
            address_snapshot=addr_snapshot,
            status='paid',
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, book=self.book, merchant=self.merchant,
            book_title=self.book.title, book_author=self.book.author,
            price=self.book.price, quantity=1, subtotal=self.book.price,
        )

    # ------------------------------------------------------------------
    # Merchant order ship
    # ------------------------------------------------------------------

    def test_merchant_can_ship_paid_order(self):
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.post(f'/api/v1/orders/merchant/{self.order.id}/ship/')
        self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'shipped')
        self.assertNotEqual(self.order.tracking_number, '')

    def test_merchant_cannot_ship_unrelated_order(self):
        other_customer = User.objects.create_user('other_ship_cust', password='pass')
        other_order = Order.objects.create(
            user=other_customer,
            total_amount=Decimal('10.00'),
            address_snapshot={
                'name': 'X', 'phone': '13000000000',
                'province': '北京', 'city': '北京', 'district': '海淀', 'detail': '某处',
            },
            status='paid',
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.post(f'/api/v1/orders/merchant/{other_order.id}/ship/')
        self.assertEqual(resp.status_code, 404)

    def test_merchant_cannot_ship_non_paid_order(self):
        self.order.status = 'pending_payment'
        self.order.save()
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.post(f'/api/v1/orders/merchant/{self.order.id}/ship/')
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # Order tracking
    # ------------------------------------------------------------------

    def test_tracking_requires_shipment(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get(f'/api/v1/orders/{self.order.id}/tracking/')
        self.assertEqual(resp.status_code, 400)

    def test_tracking_after_shipment(self):
        self.order.status = 'shipped'
        self.order.tracking_number = 'SF123456789012'
        self.order.carrier = '顺丰速运'
        self.order.save()
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get(f'/api/v1/orders/{self.order.id}/tracking/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertIn('tracking_number', data)
        self.assertIn('events', data)

    # ------------------------------------------------------------------
    # Order confirm received
    # ------------------------------------------------------------------

    def test_customer_can_confirm_shipped_order(self):
        self.order.status = 'shipped'
        self.order.save()
        self.client.force_authenticate(user=self.customer)
        resp = self.client.post(f'/api/v1/orders/{self.order.id}/confirm/')
        self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_confirm_fails_for_non_shipped_order(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.post(f'/api/v1/orders/{self.order.id}/confirm/')
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # Merchant order list
    # ------------------------------------------------------------------

    def test_merchant_can_list_own_orders(self):
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get('/api/v1/orders/merchant/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(any(o['id'] == self.order.id for o in results))

    def test_merchant_order_list_excludes_unrelated(self):
        other_customer = User.objects.create_user('mer_list_other', password='pass')
        other_order = Order.objects.create(
            user=other_customer,
            total_amount=Decimal('5.00'),
            address_snapshot={
                'name': 'Y', 'phone': '13000000001',
                'province': '上海', 'city': '上海', 'district': '浦东', 'detail': '某处',
            },
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get('/api/v1/orders/merchant/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertFalse(any(o['id'] == other_order.id for o in results))

    # ------------------------------------------------------------------
    # Admin order list
    # ------------------------------------------------------------------

    def test_admin_can_list_all_orders(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get('/api/v1/orders/admin/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(any(o['id'] == self.order.id for o in results))

    def test_non_admin_cannot_list_admin_orders(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get('/api/v1/orders/admin/')
        self.assertEqual(resp.status_code, 403)

    def test_admin_order_filter_by_status(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get('/api/v1/orders/admin/', {'status': 'paid'})
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(all(o['status'] == 'paid' for o in results))


class FinanceStatisticsAPITestCase(APITestCase):
    """Tests for finance records and statistics views."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='fin_customer', password='pass123', role='customer'
        )
        self.merchant_user = User.objects.create_user(
            username='fin_merchant', password='pass123', role='merchant'
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user, store_name='Finance Shop', status='approved'
        )
        self.admin_user = User.objects.create_user(
            username='fin_admin', password='pass123', role='admin', is_staff=True
        )
        cat = Category.objects.create(name='财务分类')
        self.book = Book.objects.create(
            merchant=self.merchant, category=cat,
            title='Finance Book', author='Author',
            price=Decimal('60.00'), stock=20, is_on_sale=True,
        )
        addr_snapshot = {
            'name': 'Fin User', 'phone': '13800138002',
            'province': '广东', 'city': '广州', 'district': '天河', 'detail': '天河路1号',
        }
        self.order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal('60.00'),
            address_snapshot=addr_snapshot,
            status='paid',
        )

        self.finance_record = FinanceRecord.objects.create(
            order=self.order,
            merchant=self.merchant,
            user=self.customer,
            type='income',
            amount=Decimal('60.00'),
            description=f'订单 {self.order.order_no} 收入',
        )

    # ------------------------------------------------------------------
    # Finance records
    # ------------------------------------------------------------------

    def test_admin_can_list_finance_records(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get('/api/v1/orders/admin/finance/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(any(r['id'] == self.finance_record.id for r in results))

    def test_merchant_can_list_own_finance_records(self):
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get('/api/v1/orders/merchant/finance/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(any(r['id'] == self.finance_record.id for r in results))

    def test_merchant_finance_excludes_other_merchants(self):
        other_user = User.objects.create_user('fin_other_m', password='pass', role='merchant')
        other_merchant = Merchant.objects.create(
            user=other_user, store_name='Other Finance Shop', status='approved'
        )
        other_order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal('20.00'),
            address_snapshot={
                'name': 'X', 'phone': '13000000002',
                'province': '北京', 'city': '北京', 'district': '朝阳', 'detail': '某处',
            },
            status='paid',
        )

        other_record = FinanceRecord.objects.create(
            order=other_order, merchant=other_merchant, user=self.customer,
            type='income', amount=Decimal('20.00'),
            description=f'订单 {other_order.order_no} 收入',
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get('/api/v1/orders/merchant/finance/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        record_ids = [r['id'] for r in results]
        self.assertNotIn(other_record.id, record_ids)

    def test_non_admin_cannot_access_admin_finance(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get('/api/v1/orders/admin/finance/')
        self.assertEqual(resp.status_code, 403)

    # ------------------------------------------------------------------
    # Statistics & Analytics
    # ------------------------------------------------------------------

    def test_admin_statistics_view(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get('/api/v1/orders/admin/statistics/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertIn('overview', data)
        self.assertIn('daily_data', data)
        self.assertIn('status_distribution', data)
        self.assertIn('top_books', data)
        overview = data['overview']
        self.assertIn('total_users', overview)
        self.assertIn('total_revenue', overview)

    def test_non_admin_cannot_access_statistics(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get('/api/v1/orders/admin/statistics/')
        self.assertEqual(resp.status_code, 403)

    def test_merchant_analytics_view(self):
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get('/api/v1/orders/merchant/analytics/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertIn('overview', data)
        self.assertIn('daily_data', data)
        self.assertIn('top_books', data)
        overview = data['overview']
        self.assertIn('total_revenue', overview)

    def test_non_merchant_cannot_access_analytics(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get('/api/v1/orders/merchant/analytics/')
        self.assertEqual(resp.status_code, 403)

    def test_admin_finance_filter_by_type(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get('/api/v1/orders/admin/finance/', {'type': 'income'})
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(all(r['type'] == 'income' for r in results))
