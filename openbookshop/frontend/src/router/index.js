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
      { path: '', redirect: '/profile' },
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
      { path: '', redirect: '/admin/users' },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/UserListView.vue') },
      { path: 'merchants', name: 'AdminMerchants', component: () => import('@/views/admin/MerchantListView.vue') },
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
