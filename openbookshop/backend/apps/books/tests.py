from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.merchants.models import Merchant

from .models import Book, Category

User = get_user_model()


class BooksAPITestCase(APITestCase):
    """Tests for books and categories API."""

    def setUp(self):
        # Merchant user with approved status
        self.merchant_user = User.objects.create_user(
            username='merchant_test', password='pass123', role='merchant'
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user, store_name='Test Shop', status='approved'
        )
        # Admin user
        self.admin_user = User.objects.create_user(
            username='admin_test', password='pass123', role='admin', is_staff=True
        )
        # Regular customer
        self.customer = User.objects.create_user(
            username='customer_test', password='pass123', role='customer'
        )
        self.category = Category.objects.create(name='文学')
        self.book = Book.objects.create(
            merchant=self.merchant,
            category=self.category,
            title='Django 实战',
            author='测试作者',
            price=Decimal('49.90'),
            stock=50,
            is_on_sale=True,
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    def test_public_book_list(self):
        """Unauthenticated users can browse books."""
        resp = self.client.get('/api/v1/books/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['data']['results']
        self.assertTrue(any(b['title'] == 'Django 实战' for b in results))

    def test_public_book_detail(self):
        resp = self.client.get(f'/api/v1/books/{self.book.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['title'], 'Django 实战')

    def test_offline_book_not_visible(self):
        self.book.is_on_sale = False
        self.book.save()
        resp = self.client.get(f'/api/v1/books/{self.book.id}/')
        self.assertEqual(resp.status_code, 404)

    def test_category_list(self):
        resp = self.client.get('/api/v1/books/categories/')
        self.assertEqual(resp.status_code, 200)

    # ------------------------------------------------------------------
    # Merchant endpoints
    # ------------------------------------------------------------------

    def test_merchant_create_book(self):
        self._auth(self.merchant_user)
        resp = self.client.post('/api/v1/books/merchant/create/', {
            'title': '新书', 'author': '作者', 'price': '29.00', 'stock': 10,
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Book.objects.filter(title='新书', merchant=self.merchant).exists())

    def test_merchant_update_own_book(self):
        self._auth(self.merchant_user)
        resp = self.client.patch(f'/api/v1/books/merchant/{self.book.id}/', {
            'price': '39.00'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.price, Decimal('39.00'))

    def test_merchant_cannot_update_others_book(self):
        other_user = User.objects.create_user('other_merchant', password='pass', role='merchant')
        Merchant.objects.create(user=other_user, store_name='Other', status='approved')
        self._auth(other_user)
        resp = self.client.patch(f'/api/v1/books/merchant/{self.book.id}/', {
            'price': '1.00'
        }, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_merchant_low_stock_view(self):
        # Set stock below warning threshold
        self.book.stock = 5
        self.book.warning_stock = 10
        self.book.save()
        self._auth(self.merchant_user)
        resp = self.client.get('/api/v1/books/merchant/low-stock/')
        self.assertEqual(resp.status_code, 200)

    # ------------------------------------------------------------------
    # Admin endpoints
    # ------------------------------------------------------------------

    def test_admin_book_list(self):
        self._auth(self.admin_user)
        resp = self.client.get('/api/v1/books/admin/')
        self.assertEqual(resp.status_code, 200)

    def test_admin_create_category(self):
        self._auth(self.admin_user)
        resp = self.client.post('/api/v1/books/admin/categories/', {
            'name': '科技', 'sort_order': 1
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Category.objects.filter(name='科技').exists())

    def test_non_admin_cannot_access_admin_books(self):
        self._auth(self.customer)
        resp = self.client.get('/api/v1/books/admin/')
        self.assertEqual(resp.status_code, 403)
