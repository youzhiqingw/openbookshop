import pytest
from django.contrib.auth import get_user_model
from dvadmin.bookshop.models import Merchant
from dvadmin.bookshop.permissions import MerchantPermission, OwnerPermission

User = get_user_model()


@pytest.fixture
def merchant_perm():
    return MerchantPermission()


@pytest.fixture
def owner_perm():
    return OwnerPermission()


@pytest.fixture
def superuser(db):
    u = User.objects.create_user(username='superadmin_test', password='test123456', name='super',
                                  is_superuser=True, user_type=0)
    return u


@pytest.fixture
def merchant_approved(db):
    m = Merchant.objects.create(name='审核通过商家', contact_name='张三', contact_phone='13800138001',
                                contact_email='zhang@test.com', address='北京市', status='approved')
    return m


@pytest.fixture
def merchant_pending(db):
    m = Merchant.objects.create(name='待审核商家', contact_name='李四', contact_phone='13800138002',
                                contact_email='li@test.com', address='上海市', status='pending')
    return m


@pytest.fixture
def merchant_disabled(db):
    m = Merchant.objects.create(name='已禁用商家', contact_name='王五', contact_phone='13800138003',
                                contact_email='wang@test.com', address='广州市', status='disabled',
                                is_open=False)
    return m


@pytest.fixture
def merchant_rejected(db):
    m = Merchant.objects.create(name='已拒绝商家', contact_name='赵六', contact_phone='13800138004',
                                contact_email='zhao@test.com', address='深圳市', status='rejected',
                                reject_reason='资质不符')
    return m


@pytest.fixture
def merchant_user_approved(db, merchant_approved):
    u = User.objects.create_user(username='merchant_a', password='test123456', name='商家A',
                                  user_type=2, merchant=merchant_approved)
    return u


@pytest.fixture
def merchant_user_pending(db, merchant_pending):
    u = User.objects.create_user(username='merchant_pending', password='test123456', name='待审核商家用户',
                                  user_type=2, merchant=merchant_pending)
    return u


@pytest.fixture
def merchant_user_disabled(db, merchant_disabled):
    u = User.objects.create_user(username='merchant_disabled', password='test123456', name='已禁用商家用户',
                                  user_type=2, merchant=merchant_disabled)
    return u


@pytest.fixture
def merchant_user_no_merchant(db):
    u = User.objects.create_user(username='merchant_no_fk', password='test123456', name='无商家FK用户',
                                  user_type=2)
    return u


@pytest.fixture
def customer_a(db):
    return User.objects.create_user(username='customer_a', password='test123456', name='消费者A', user_type=3)


@pytest.fixture
def customer_b(db):
    return User.objects.create_user(username='customer_b', password='test123456', name='消费者B', user_type=3)


class FakeRequest:
    """模拟 DRF Request 对象"""
    def __init__(self, user):
        self.user = user


class FakeObjWithMerchantId:
    """有 merchant_id 属性的模拟对象（如 Book, Order）"""
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id


class FakeObjWithUserId:
    """有 user_id 属性的模拟对象（如 CartItem, Address, Order）"""
    def __init__(self, user_id):
        self.user_id = user_id


# ====== MerchantPermission Tests ======

class TestMerchantPermissionHasPermission:

    def test_superuser_passes(self, merchant_perm, superuser):
        req = FakeRequest(superuser)
        assert merchant_perm.has_permission(req, None) is True

    def test_approved_merchant_passes(self, merchant_perm, merchant_user_approved):
        req = FakeRequest(merchant_user_approved)
        assert merchant_perm.has_permission(req, None) is True

    def test_pending_merchant_denied(self, merchant_perm, merchant_user_pending):
        req = FakeRequest(merchant_user_pending)
        assert merchant_perm.has_permission(req, None) is False

    def test_disabled_merchant_denied(self, merchant_perm, merchant_user_disabled):
        req = FakeRequest(merchant_user_disabled)
        assert merchant_perm.has_permission(req, None) is False

    def test_merchant_no_fk_denied(self, merchant_perm, merchant_user_no_merchant):
        req = FakeRequest(merchant_user_no_merchant)
        assert merchant_perm.has_permission(req, None) is False

    def test_customer_denied(self, merchant_perm, customer_a):
        req = FakeRequest(customer_a)
        assert merchant_perm.has_permission(req, None) is False

    def test_anonymous_denied(self, merchant_perm):
        req = FakeRequest(None)
        assert merchant_perm.has_permission(req, None) is False

    def test_non_merchant_user_type_denied(self, merchant_perm, db):
        user = User.objects.create_user(username='admin_user', password='test123456', name='管理员', user_type=0)
        req = FakeRequest(user)
        assert merchant_perm.has_permission(req, None) is False


class TestMerchantPermissionHasObjectPermission:

    def test_superuser_passes(self, merchant_perm, superuser, merchant_approved):
        req = FakeRequest(superuser)
        assert merchant_perm.has_object_permission(req, None, merchant_approved) is True

    def test_own_merchant_passes(self, merchant_perm, merchant_user_approved, merchant_approved):
        req = FakeRequest(merchant_user_approved)
        assert merchant_perm.has_object_permission(req, None, merchant_approved) is True

    def test_other_merchant_denied(self, merchant_perm, merchant_user_approved, merchant_pending):
        req = FakeRequest(merchant_user_approved)
        assert merchant_perm.has_object_permission(req, None, merchant_pending) is False

    def test_own_obj_with_merchant_id(self, merchant_perm, merchant_user_approved):
        req = FakeRequest(merchant_user_approved)
        obj = FakeObjWithMerchantId(merchant_user_approved.merchant_id)
        assert merchant_perm.has_object_permission(req, None, obj) is True

    def test_other_obj_with_merchant_id_denied(self, merchant_perm, merchant_user_approved, merchant_pending):
        req = FakeRequest(merchant_user_approved)
        obj = FakeObjWithMerchantId(merchant_pending.id)
        assert merchant_perm.has_object_permission(req, None, obj) is False


# ====== OwnerPermission Tests ======

class TestOwnerPermissionHasPermission:

    def test_superuser_passes(self, owner_perm, superuser):
        req = FakeRequest(superuser)
        assert owner_perm.has_permission(req, None) is True

    def test_customer_passes(self, owner_perm, customer_a):
        req = FakeRequest(customer_a)
        assert owner_perm.has_permission(req, None) is True

    def test_anonymous_denied(self, owner_perm):
        req = FakeRequest(None)
        assert owner_perm.has_permission(req, None) is False


class TestOwnerPermissionHasObjectPermission:

    def test_superuser_passes(self, owner_perm, superuser, customer_a):
        req = FakeRequest(superuser)
        obj = FakeObjWithUserId(customer_a.id)
        assert owner_perm.has_object_permission(req, None, obj) is True

    def test_own_obj_passes(self, owner_perm, customer_a):
        req = FakeRequest(customer_a)
        obj = FakeObjWithUserId(customer_a.id)
        assert owner_perm.has_object_permission(req, None, obj) is True

    def test_other_user_obj_denied(self, owner_perm, customer_a, customer_b):
        req = FakeRequest(customer_a)
        obj = FakeObjWithUserId(customer_b.id)
        assert owner_perm.has_object_permission(req, None, obj) is False

    def test_anonymous_denied(self, owner_perm, customer_a):
        req = FakeRequest(None)
        obj = FakeObjWithUserId(customer_a.id)
        assert owner_perm.has_object_permission(req, None, obj) is False
