from django.urls import path

from .views import (
    AdminFinanceListView,
    AdminOrderListView,
    AdminStatisticsView,
    CartAddView,
    CartClearView,
    CartDeleteView,
    CartListView,
    CartUpdateView,
    MerchantAnalyticsView,
    MerchantFinanceListView,
    MerchantOrderListView,
    MerchantOrderShipView,
    OrderCancelView,
    OrderConfirmView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderPayCallbackView,
    OrderPayView,
    OrderTrackingView,
)

urlpatterns = [
    # Cart
    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/add/", CartAddView.as_view(), name="cart-add"),
    path("cart/<int:pk>/", CartUpdateView.as_view(), name="cart-update"),
    path("cart/<int:pk>/remove/", CartDeleteView.as_view(), name="cart-delete"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),
    # Orders (user)
    path("", OrderListView.as_view(), name="order-list"),
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<int:pk>/pay/", OrderPayView.as_view(), name="order-pay"),
    path(
        "<int:pk>/pay/callback/",
        OrderPayCallbackView.as_view(),
        name="order-pay-callback",
    ),
    path("<int:pk>/tracking/", OrderTrackingView.as_view(), name="order-tracking"),
    path("<int:pk>/confirm/", OrderConfirmView.as_view(), name="order-confirm"),
    # Merchant
    path("merchant/", MerchantOrderListView.as_view(), name="merchant-order-list"),
    path(
        "merchant/finance/",
        MerchantFinanceListView.as_view(),
        name="merchant-finance-list",
    ),
    path(
        "merchant/analytics/",
        MerchantAnalyticsView.as_view(),
        name="merchant-analytics",
    ),
    path(
        "merchant/<int:pk>/ship/",
        MerchantOrderShipView.as_view(),
        name="merchant-order-ship",
    ),
    # Admin
    path("admin/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/finance/", AdminFinanceListView.as_view(), name="admin-finance-list"),
    path("admin/statistics/", AdminStatisticsView.as_view(), name="admin-statistics"),
]
