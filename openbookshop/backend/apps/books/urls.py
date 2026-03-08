from django.urls import path

from .views import (
    AdminBookListView, AdminBookUpdateView, AdminCategoryCreateView,
    AdminCategoryUpdateView, AdminLowStockView, AdminReviewApproveView,
    AdminReviewListView, BookDetailView, BookListView, BookReviewCreateView,
    BookReviewListView, CategoryListView, MerchantBookCreateView,
    MerchantBookListView, MerchantBookUpdateView, MerchantLowStockView,
    MerchantReviewListView, MerchantReviewReplyView,
)

urlpatterns = [
    # Public
    path('', BookListView.as_view(), name='book-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('<int:pk>/reviews/', BookReviewListView.as_view(), name='book-review-list'),
    path('<int:pk>/reviews/create/', BookReviewCreateView.as_view(), name='book-review-create'),

    # Merchant (string patterns first, then int)
    path('merchant/', MerchantBookListView.as_view(), name='merchant-book-list'),
    path('merchant/create/', MerchantBookCreateView.as_view(), name='merchant-book-create'),
    path('merchant/low-stock/', MerchantLowStockView.as_view(), name='merchant-low-stock'),
    path('merchant/reviews/', MerchantReviewListView.as_view(), name='merchant-review-list'),
    path('merchant/reviews/<int:pk>/reply/', MerchantReviewReplyView.as_view(), name='merchant-review-reply'),
    path('merchant/<int:pk>/', MerchantBookUpdateView.as_view(), name='merchant-book-update'),

    # Admin (string patterns first, then int)
    path('admin/', AdminBookListView.as_view(), name='admin-book-list'),
    path('admin/low-stock/', AdminLowStockView.as_view(), name='admin-low-stock'),
    path('admin/categories/', AdminCategoryCreateView.as_view(), name='admin-category-create'),
    path('admin/categories/<int:pk>/', AdminCategoryUpdateView.as_view(), name='admin-category-update'),
    path('admin/reviews/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('admin/reviews/<int:pk>/approve/', AdminReviewApproveView.as_view(), name='admin-review-approve'),
    path('admin/<int:pk>/', AdminBookUpdateView.as_view(), name='admin-book-update'),
]
