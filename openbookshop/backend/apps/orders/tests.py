from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.books.models import Book, Category
from apps.merchants.models import Merchant
from apps.users.models import Address

from .models import Cart, Order, OrderItem

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
