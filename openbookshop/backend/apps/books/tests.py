from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.merchants.models import Merchant
from apps.orders.models import Order, OrderItem

from .models import Book, Category, Review

User = get_user_model()


class BooksAPITestCase(APITestCase):
    """Tests for books and categories API."""

    def setUp(self):
        # Merchant user with approved status
        self.merchant_user = User.objects.create_user(
            username="merchant_test", password="pass123", role="merchant"
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user, store_name="Test Shop", status="approved"
        )
        # Admin user
        self.admin_user = User.objects.create_user(
            username="admin_test", password="pass123", role="admin", is_staff=True
        )
        # Regular customer
        self.customer = User.objects.create_user(
            username="customer_test", password="pass123", role="customer"
        )
        self.category = Category.objects.create(name="文学")
        self.book = Book.objects.create(
            merchant=self.merchant,
            category=self.category,
            title="Django 实战",
            author="测试作者",
            price=Decimal("49.90"),
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
        resp = self.client.get("/api/v1/books/")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["data"]["results"]
        self.assertTrue(any(b["title"] == "Django 实战" for b in results))

    def test_public_book_detail(self):
        resp = self.client.get(f"/api/v1/books/{self.book.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "Django 实战")

    def test_offline_book_not_visible(self):
        self.book.is_on_sale = False
        self.book.save()
        resp = self.client.get(f"/api/v1/books/{self.book.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_category_list(self):
        resp = self.client.get("/api/v1/books/categories/")
        self.assertEqual(resp.status_code, 200)

    # ------------------------------------------------------------------
    # Merchant endpoints
    # ------------------------------------------------------------------

    def test_merchant_create_book(self):
        self._auth(self.merchant_user)
        resp = self.client.post(
            "/api/v1/books/merchant/create/",
            {
                "title": "新书",
                "author": "作者",
                "price": "29.00",
                "stock": 10,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(
            Book.objects.filter(title="新书", merchant=self.merchant).exists()
        )

    def test_merchant_update_own_book(self):
        self._auth(self.merchant_user)
        resp = self.client.patch(
            f"/api/v1/books/merchant/{self.book.id}/", {"price": "39.00"}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.price, Decimal("39.00"))

    def test_merchant_cannot_update_others_book(self):
        other_user = User.objects.create_user(
            "other_merchant", password="pass", role="merchant"
        )
        Merchant.objects.create(user=other_user, store_name="Other", status="approved")
        self._auth(other_user)
        resp = self.client.patch(
            f"/api/v1/books/merchant/{self.book.id}/", {"price": "1.00"}, format="json"
        )
        self.assertEqual(resp.status_code, 404)

    def test_merchant_low_stock_view(self):
        # Set stock below warning threshold
        self.book.stock = 5
        self.book.warning_stock = 10
        self.book.save()
        self._auth(self.merchant_user)
        resp = self.client.get("/api/v1/books/merchant/low-stock/")
        self.assertEqual(resp.status_code, 200)

    # ------------------------------------------------------------------
    # Admin endpoints
    # ------------------------------------------------------------------

    def test_admin_book_list(self):
        self._auth(self.admin_user)
        resp = self.client.get("/api/v1/books/admin/")
        self.assertEqual(resp.status_code, 200)

    def test_admin_create_category(self):
        self._auth(self.admin_user)
        resp = self.client.post(
            "/api/v1/books/admin/categories/",
            {"name": "科技", "sort_order": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Category.objects.filter(name="科技").exists())

    def test_non_admin_cannot_access_admin_books(self):
        self._auth(self.customer)
        resp = self.client.get("/api/v1/books/admin/")
        self.assertEqual(resp.status_code, 403)


class ReviewAPITestCase(APITestCase):
    """Tests for the review system."""

    def setUp(self):
        self.merchant_user = User.objects.create_user(
            username="rev_merchant", password="pass123", role="merchant"
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user, store_name="Rev Shop", status="approved"
        )
        self.admin_user = User.objects.create_user(
            username="rev_admin", password="pass123", role="admin", is_staff=True
        )
        self.customer = User.objects.create_user(
            username="rev_customer", password="pass123", role="customer"
        )
        self.category = Category.objects.create(name="评论分类")
        self.book = Book.objects.create(
            merchant=self.merchant,
            category=self.category,
            title="Review Test Book",
            author="Author",
            price=Decimal("30.00"),
            stock=10,
            is_on_sale=True,
        )
        # Create a completed order for the customer
        self.order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal("30.00"),
            address_snapshot={
                "name": "测试用户",
                "phone": "13800000000",
                "province": "广东",
                "city": "深圳",
                "district": "南山",
                "detail": "某处",
            },
            status="completed",
        )
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            merchant=self.merchant,
            book_title=self.book.title,
            book_author=self.book.author,
            price=self.book.price,
            quantity=1,
            subtotal=self.book.price,
        )

    # ------------------------------------------------------------------
    # Public review list
    # ------------------------------------------------------------------

    def test_public_can_list_approved_reviews(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=5,
            content="非常好读的一本书！",
            is_approved=True,
        )
        resp = self.client.get(f"/api/v1/books/{self.book.id}/reviews/")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["data"]["results"]
        self.assertEqual(len(results), 1)

    def test_unapproved_reviews_not_visible_publicly(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=2,
            content="垃圾书籍差评！",
            is_approved=False,
        )
        resp = self.client.get(f"/api/v1/books/{self.book.id}/reviews/")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["data"]["results"]
        self.assertEqual(len(results), 0)

    # ------------------------------------------------------------------
    # Create review
    # ------------------------------------------------------------------

    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.post(
            f"/api/v1/books/{self.book.id}/reviews/create/",
            {
                "rating": 5,
                "content": "非常好的图书，推荐购买！",
                "order_id": self.order.id,
            },
            format="json",
        )
        self.assertIn(resp.status_code, [200, 201])
        self.assertTrue(
            Review.objects.filter(user=self.customer, book=self.book).exists()
        )

    def test_sensitive_content_not_auto_approved(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.post(
            f"/api/v1/books/{self.book.id}/reviews/create/",
            {"rating": 1, "content": "这是垃圾书，骗子！", "order_id": self.order.id},
            format="json",
        )
        self.assertIn(resp.status_code, [200, 201])
        review = Review.objects.get(user=self.customer, book=self.book)
        self.assertTrue(review.is_sensitive)
        self.assertFalse(review.is_approved)

    def test_unauthenticated_cannot_create_review(self):
        resp = self.client.post(
            f"/api/v1/books/{self.book.id}/reviews/create/",
            {"rating": 5, "content": "好书推荐购买！", "order_id": self.order.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_cannot_review_without_purchase(self):
        no_order_user = User.objects.create_user(
            username="no_order_user", password="pass123", role="customer"
        )
        self.client.force_authenticate(user=no_order_user)
        resp = self.client.post(
            f"/api/v1/books/{self.book.id}/reviews/create/",
            {"rating": 4, "content": "感觉还不错的一本书！"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_cannot_review_twice_same_order(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=5,
            content="很好的书推荐阅读！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.customer)
        resp = self.client.post(
            f"/api/v1/books/{self.book.id}/reviews/create/",
            {"rating": 4, "content": "又评一次这本好书！", "order_id": self.order.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # Merchant review management
    # ------------------------------------------------------------------

    def test_merchant_can_list_own_book_reviews(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=5,
            content="好书值得购买！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.get("/api/v1/books/merchant/reviews/")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["data"]["results"]
        self.assertEqual(len(results), 1)

    def test_merchant_can_reply_review(self):
        review = Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=4,
            content="还不错的书籍！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.post(
            f"/api/v1/books/merchant/reviews/{review.id}/reply/",
            {"merchant_reply": "感谢您的评论，欢迎再次光临！"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.merchant_reply, "感谢您的评论，欢迎再次光临！")

    def test_merchant_cannot_reply_other_book_review(self):
        other_user = User.objects.create_user(
            "other_m", password="pass", role="merchant"
        )
        other_merchant = Merchant.objects.create(
            user=other_user, store_name="Other", status="approved"
        )
        other_book = Book.objects.create(
            merchant=other_merchant,
            category=self.category,
            title="Other Book",
            author="X",
            price=Decimal("10.00"),
            stock=5,
            is_on_sale=True,
        )
        other_order = Order.objects.create(
            user=self.customer,
            total_amount=Decimal("10.00"),
            address_snapshot={
                "name": "测试",
                "phone": "13800000001",
                "province": "北京",
                "city": "北京",
                "district": "海淀",
                "detail": "某处",
            },
            status="completed",
        )
        OrderItem.objects.create(
            order=other_order,
            book=other_book,
            merchant=other_merchant,
            book_title=other_book.title,
            book_author=other_book.author,
            price=other_book.price,
            quantity=1,
            subtotal=other_book.price,
        )
        other_review = Review.objects.create(
            user=self.customer,
            book=other_book,
            order=other_order,
            rating=3,
            content="还可以的书籍！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.merchant_user)
        resp = self.client.post(
            f"/api/v1/books/merchant/reviews/{other_review.id}/reply/",
            {"merchant_reply": "感谢评论！"},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    # ------------------------------------------------------------------
    # Admin review management
    # ------------------------------------------------------------------

    def test_admin_can_list_all_reviews(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=5,
            content="非常推荐这本好书！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get("/api/v1/books/admin/reviews/")
        self.assertEqual(resp.status_code, 200)

    def test_admin_can_approve_review(self):
        review = Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=2,
            content="垃圾骗子差评！",
            is_sensitive=True,
            is_approved=False,
        )
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.post(
            f"/api/v1/books/admin/reviews/{review.id}/approve/",
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        review.refresh_from_db()
        self.assertTrue(review.is_approved)

    def test_admin_can_reject_review(self):
        review = Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=5,
            content="好书推荐！",
            is_approved=True,
        )
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.post(
            f"/api/v1/books/admin/reviews/{review.id}/approve/",
            {"action": "reject"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        review.refresh_from_db()
        self.assertFalse(review.is_approved)

    def test_admin_filter_by_sensitive(self):
        Review.objects.create(
            user=self.customer,
            book=self.book,
            order=self.order,
            rating=1,
            content="垃圾骗子！",
            is_sensitive=True,
            is_approved=False,
        )
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get("/api/v1/books/admin/reviews/", {"is_sensitive": "true"})
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["data"]["results"]
        self.assertTrue(all(r["is_sensitive"] for r in results))

    def test_non_admin_cannot_access_admin_reviews(self):
        self.client.force_authenticate(user=self.customer)
        resp = self.client.get("/api/v1/books/admin/reviews/")
        self.assertEqual(resp.status_code, 403)
