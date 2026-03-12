import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // Auth routes
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'Login', component: () => import('@/views/auth/LoginView.vue') },
      { path: 'register', name: 'Register', component: () => import('@/views/auth/RegisterView.vue') },
    ],
  },
  // User routes
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Home', component: () => import('@/views/user/HomeView.vue') },
      { path: 'books', name: 'BookList', component: () => import('@/views/user/BookListView.vue') },
      { path: 'books/:id', name: 'BookDetail', component: () => import('@/views/user/BookDetailView.vue') },
      { path: 'cart', name: 'Cart', component: () => import('@/views/user/CartView.vue') },
      { path: 'checkout', name: 'Checkout', component: () => import('@/views/user/CheckoutView.vue') },
      { path: 'orders', name: 'OrderList', component: () => import('@/views/user/OrderListView.vue') },
      { path: 'orders/:id', name: 'OrderDetail', component: () => import('@/views/user/OrderDetailView.vue') },
      { path: 'orders/:id/pay', name: 'Payment', component: () => import('@/views/user/PaymentView.vue') },
      { path: 'profile', name: 'UserProfile', component: () => import('@/views/user/ProfileView.vue') },
      { path: 'addresses', name: 'Addresses', component: () => import('@/views/user/AddressView.vue') },
    ],
  },
  // Admin routes
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/DashboardView.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/UserListView.vue') },
      { path: 'merchants', name: 'AdminMerchants', component: () => import('@/views/admin/MerchantListView.vue') },
      { path: 'books', name: 'AdminBooks', component: () => import('@/views/admin/BookManageView.vue') },
      { path: 'reviews', name: 'AdminReviews', component: () => import('@/views/admin/ReviewModerationView.vue') },
      { path: 'finance', name: 'AdminFinance', component: () => import('@/views/admin/FinanceView.vue') },
      { path: 'stock-warning', name: 'AdminStockWarning', component: () => import('@/views/admin/StockWarningView.vue') },
      { path: 'logs', name: 'AdminLogs', component: () => import('@/views/admin/OperationLogView.vue') },
    ],
  },
  // Merchant routes
  {
    path: '/merchant',
    component: () => import('@/layouts/MerchantLayout.vue'),
    meta: { requiresAuth: true, requiresMerchant: true },
    children: [
      { path: '', redirect: '/merchant/profile' },
      { path: 'profile', name: 'MerchantProfile', component: () => import('@/views/merchant/ProfileView.vue') },
      { path: 'books', name: 'MerchantBooks', component: () => import('@/views/merchant/BookManageView.vue') },
      { path: 'orders', name: 'MerchantOrders', component: () => import('@/views/merchant/OrderManageView.vue') },
      { path: 'analytics', name: 'MerchantAnalytics', component: () => import('@/views/merchant/AnalyticsView.vue') },
      { path: 'finance', name: 'MerchantFinance', component: () => import('@/views/merchant/FinanceView.vue') },
      { path: 'stock-warning', name: 'MerchantStockWarning', component: () => import('@/views/merchant/StockWarningView.vue') },
      { path: 'reviews', name: 'MerchantReviews', component: () => import('@/views/merchant/ReviewsView.vue') },
      { path: 'apply', name: 'MerchantApply', component: () => import('@/views/merchant/ApplyView.vue'), meta: { requiresMerchant: false } },
    ],
  },
  // 404
  { path: '/:pathMatch(.*)*', redirect: '/auth/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'Login' })
  }

  if (to.meta.requiresMerchant && !authStore.isMerchant) {
    return next({ name: 'MerchantApply' })
  }

  next()
})

export default router
