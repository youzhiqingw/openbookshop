from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Merchant

User = get_user_model()


class MerchantApplyTests(APITestCase):
    """商家申请测试"""

    def setUp(self):
        self.url = reverse("merchant_apply")
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!"
        )
        self.valid_data = {
            "store_name": "测试书店",
            "description": "专业图书零售",
            "business_license": "91440300XXXXXXXX",
            "address": "广东省深圳市南山区",
        }

    def test_apply_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["code"], 201)
        self.assertTrue(Merchant.objects.filter(user=self.user).exists())
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "merchant")

    def test_apply_unauthenticated(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_apply_duplicate(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, self.valid_data, format="json")
        # Apply again
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_apply_missing_store_name(self):
        self.client.force_authenticate(user=self.user)
        data = self.valid_data.copy()
        del data["store_name"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)


class MerchantProfileTests(APITestCase):
    """商家资料测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="merchant", password="TestPass123!", role="merchant"
        )
        self.merchant = Merchant.objects.create(
            user=self.user,
            store_name="测试书店",
            status="approved",
        )
        self.url = reverse("merchant_profile")

    def test_profile_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["store_name"], "测试书店")

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {"description": "新描述"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.description, "新描述")

    def test_profile_requires_merchant_role(self):
        normal_user = User.objects.create_user(
            username="normal", password="TestPass123!"
        )
        self.client.force_authenticate(user=normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class MerchantAuditTests(APITestCase):
    """商家审核测试"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass123!", role="admin", is_staff=True
        )
        self.merchant_user = User.objects.create_user(
            username="merchant", password="TestPass123!", role="merchant"
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            store_name="待审书店",
            status="pending",
        )
        self.url = reverse("merchant_audit", args=[self.merchant.pk])

    def test_admin_can_approve(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url, {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.status, "approved")

    def test_admin_can_reject(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url, {"status": "rejected"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.merchant.refresh_from_db()
        self.assertEqual(self.merchant.status, "rejected")

    def test_non_admin_cannot_audit(self):
        self.client.force_authenticate(user=self.merchant_user)
        response = self.client.put(self.url, {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_invalid_audit_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url, {"status": "pending"}, format="json")
        self.assertEqual(response.status_code, 400)


class AdminMerchantListTests(APITestCase):
    """管理员商家列表测试"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass123!", role="admin", is_staff=True
        )
        self.url = reverse("admin_merchant_list")

        # Create some merchants
        for i in range(3):
            u = User.objects.create_user(
                username=f"merchant{i}", password="TestPass123!", role="merchant"
            )
            Merchant.objects.create(
                user=u,
                store_name=f"书店{i}",
                status="pending" if i < 2 else "approved",
            )

    def test_admin_can_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_filter_by_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"status": "pending"})
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_list(self):
        normal_user = User.objects.create_user(
            username="normal", password="TestPass123!"
        )
        self.client.force_authenticate(user=normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
