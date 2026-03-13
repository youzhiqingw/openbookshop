from django.urls import path

from . import views

urlpatterns = [
    path("apply/", views.MerchantApplyView.as_view(), name="merchant_apply"),
    path("profile/", views.MerchantProfileView.as_view(), name="merchant_profile"),
    path("admin/", views.AdminMerchantListView.as_view(), name="admin_merchant_list"),
    path("<int:pk>/audit/", views.MerchantAuditView.as_view(), name="merchant_audit"),
]
