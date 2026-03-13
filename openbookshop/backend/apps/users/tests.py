from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):
    """用户注册测试"""

    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "username": "testuser",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "email": "test@example.com",
            "phone": "13800138000",
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["code"], 201)
        self.assertIn("tokens", response.data["data"])
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username="testuser", password="SomePass123!")
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertIn(response.status_code, [400])

    def test_register_password_mismatch(self):
        data = self.valid_data.copy()
        data["password2"] = "WrongPass123!"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)


class LoginTests(APITestCase):
    """用户登录测试"""

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", email="test@example.com"
        )

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {"username": "testuser", "password": "TestPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], 200)
        self.assertIn("tokens", response.data["data"])

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {"username": "testuser", "password": "WrongPass!"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.url, {"username": "nobody", "password": "Whatever123!"}, format="json"
        )
        self.assertEqual(response.status_code, 401)


class TokenRefreshTests(APITestCase):
    """Token刷新测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!"
        )

    def test_token_refresh(self):
        login_response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "TestPass123!"},
            format="json",
        )
        refresh_token = login_response.data["data"]["tokens"]["refresh"]

        response = self.client.post(
            reverse("token_refresh"), {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)


class ProfileTests(APITestCase):
    """用户资料测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!", email="test@example.com"
        )
        self.url = reverse("user_profile")

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")

    def test_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


class AddressTests(APITestCase):
    """收货地址测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("address-list")
        self.address_data = {
            "name": "张三",
            "phone": "13800138000",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "detail": "科技园路1号",
            "is_default": True,
        }

    def test_create_address(self):
        response = self.client.post(self.list_url, self.address_data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_list_addresses(self):
        self.client.post(self.list_url, self.address_data, format="json")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_update_address(self):
        create_resp = self.client.post(self.list_url, self.address_data, format="json")
        addr_id = create_resp.data["id"]
        detail_url = reverse("address-detail", args=[addr_id])
        response = self.client.patch(detail_url, {"name": "李四"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "李四")

    def test_delete_address(self):
        create_resp = self.client.post(self.list_url, self.address_data, format="json")
        addr_id = create_resp.data["id"]
        detail_url = reverse("address-detail", args=[addr_id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)

    def test_max_5_addresses(self):
        for i in range(5):
            data = self.address_data.copy()
            data["name"] = f"用户{i}"
            data["is_default"] = False
            self.client.post(self.list_url, data, format="json")
        data = self.address_data.copy()
        data["name"] = "第六个"
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, 400)


class AdminUserListTests(APITestCase):
    """管理员用户列表测试"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", password="AdminPass123!", role="admin"
        )
        self.normal_user = User.objects.create_user(
            username="normal", password="NormalPass123!"
        )

    def test_admin_can_access(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/v1/users/admin/users/")
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_access(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get("/api/v1/users/admin/users/")
        self.assertEqual(response.status_code, 403)


class LogoutTests(APITestCase):
    """用户登出测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!"
        )
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")

    def test_logout_success(self):
        login_resp = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "TestPass123!"},
            format="json",
        )
        refresh_token = login_resp.data["data"]["tokens"]["refresh"]
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.logout_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_logout_requires_auth(self):
        response = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(response.status_code, 401)


class ChangePasswordTests(APITestCase):
    """修改密码测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("change_password")

    def test_change_password_success(self):
        response = self.client.put(
            self.url,
            {
                "old_password": "TestPass123!",
                "new_password": "NewPass456!",
                "new_password2": "NewPass456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_change_password_wrong_old(self):
        response = self.client.put(
            self.url,
            {
                "old_password": "WrongPass!",
                "new_password": "NewPass456!",
                "new_password2": "NewPass456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_change_password_mismatch(self):
        response = self.client.put(
            self.url,
            {
                "old_password": "TestPass123!",
                "new_password": "NewPass456!",
                "new_password2": "DifferentPass!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_change_password_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(
            self.url,
            {
                "old_password": "TestPass123!",
                "new_password": "NewPass456!",
                "new_password2": "NewPass456!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)


class AdminUserToggleStatusTests(APITestCase):
    """管理员切换用户状态测试"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass123!", role="admin", is_staff=True
        )
        self.target_user = User.objects.create_user(
            username="target", password="TestPass123!"
        )
        self.url = reverse("admin_user_toggle_status", args=[self.target_user.pk])

    def test_admin_can_ban_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_active)

    def test_admin_can_unban_user(self):
        self.target_user.is_active = False
        self.target_user.save()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_active)

    def test_admin_cannot_toggle_self(self):
        self.client.force_authenticate(user=self.admin)
        self_url = reverse("admin_user_toggle_status", args=[self.admin.pk])
        response = self.client.post(self_url)
        self.assertEqual(response.status_code, 400)

    def test_non_admin_cannot_toggle(self):
        normal_user = User.objects.create_user(
            username="normal", password="NormalPass123!"
        )
        self.client.force_authenticate(user=normal_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_toggle_nonexistent_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("admin_user_toggle_status", args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class AdminOperationLogTests(APITestCase):
    """管理员操作日志测试"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="AdminPass123!", role="admin", is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username="normal", password="NormalPass123!"
        )
        self.url = reverse("admin_operation_logs")

    def test_admin_can_view_logs(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_view_logs(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
