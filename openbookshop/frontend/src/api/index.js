import request from './request'

export const authApi = {
  login: (data) => request.post('/auth/login/', data),
  register: (data) => request.post('/auth/register/', data),
  logout: (data) => request.post('/auth/logout/', data),
  refreshToken: (data) => request.post('/auth/refresh/', data),
}

export const userApi = {
  getProfile: () => request.get('/users/profile/'),
  updateProfile: (data) => request.put('/users/profile/', data),
  changePassword: (data) => request.put('/users/change-password/', data),
  getAddresses: () => request.get('/users/addresses/'),
  createAddress: (data) => request.post('/users/addresses/', data),
  updateAddress: (id, data) => request.patch(`/users/addresses/${id}/`, data),
  deleteAddress: (id) => request.delete(`/users/addresses/${id}/`),
}

export const adminApi = {
  getUserList: (params) => request.get('/users/admin/users/', { params }),
  toggleUserStatus: (id) => request.post(`/users/admin/users/${id}/toggle-status/`),
  getOperationLogs: (params) => request.get('/users/admin/logs/', { params }),
  getMerchantList: (params) => request.get('/merchants/admin/', { params }),
  auditMerchant: (id, data) => request.put(`/merchants/${id}/audit/`, data),
  // Books
  getBookList: (params) => request.get('/books/admin/', { params }),
  updateBook: (id, data) => request.patch(`/books/admin/${id}/`, data),
  deleteBook: (id) => request.delete(`/books/admin/${id}/`),
  getLowStock: (params) => request.get('/books/admin/low-stock/', { params }),
  // Categories
  getCategories: () => request.get('/books/categories/'),
  createCategory: (data) => request.post('/books/admin/categories/', data),
  updateCategory: (id, data) => request.patch(`/books/admin/categories/${id}/`, data),
  deleteCategory: (id) => request.delete(`/books/admin/categories/${id}/`),
  // Orders
  getOrderList: (params) => request.get('/orders/admin/', { params }),
  // Statistics & Finance
  getStatistics: () => request.get('/orders/admin/statistics/'),
  getFinanceList: (params) => request.get('/orders/admin/finance/', { params }),
  // Reviews
  getReviewList: (params) => request.get('/books/admin/reviews/', { params }),
  approveReview: (id, data) => request.post(`/books/admin/reviews/${id}/approve/`, data),
}

export const merchantApi = {
  applyMerchant: (data) => request.post('/merchants/apply/', data),
  getProfile: () => request.get('/merchants/profile/'),
  updateProfile: (data) => request.put('/merchants/profile/', data),
  // Books
  getBookList: (params) => request.get('/books/merchant/', { params }),
  createBook: (data) => request.post('/books/merchant/create/', data),
  updateBook: (id, data) => request.patch(`/books/merchant/${id}/`, data),
  deleteBook: (id) => request.delete(`/books/merchant/${id}/`),
  getLowStock: (params) => request.get('/books/merchant/low-stock/', { params }),
  // Orders
  getOrderList: (params) => request.get('/orders/merchant/', { params }),
  shipOrder: (id) => request.post(`/orders/merchant/${id}/ship/`),
  // Finance & Analytics
  getFinanceList: (params) => request.get('/orders/merchant/finance/', { params }),
  getAnalytics: () => request.get('/orders/merchant/analytics/'),
  // Reviews
  getReviewList: (params) => request.get('/books/merchant/reviews/', { params }),
  replyReview: (id, data) => request.post(`/books/merchant/reviews/${id}/reply/`, data),
}

export const bookApi = {
  getList: (params) => request.get('/books/', { params }),
  getDetail: (id) => request.get(`/books/${id}/`),
  getCategories: () => request.get('/books/categories/'),
  // Reviews
  getReviews: (id, params) => request.get(`/books/${id}/reviews/`, { params }),
  createReview: (id, data) => request.post(`/books/${id}/reviews/create/`, data),
}

export const orderApi = {
  // Cart
  getCart: () => request.get('/orders/cart/'),
  addToCart: (data) => request.post('/orders/cart/add/', data),
  updateCartItem: (id, data) => request.patch(`/orders/cart/${id}/`, data),
  removeCartItem: (id) => request.delete(`/orders/cart/${id}/remove/`),
  clearCart: () => request.delete('/orders/cart/clear/'),
  // Orders
  createOrder: (data) => request.post('/orders/create/', data),
  getOrderList: (params) => request.get('/orders/', { params }),
  getOrderDetail: (id) => request.get(`/orders/${id}/`),
  cancelOrder: (id) => request.post(`/orders/${id}/cancel/`),
  payOrder: (id, data) => request.post(`/orders/${id}/pay/`, data),
  confirmPayment: (id) => request.post(`/orders/${id}/pay/callback/`),
  getTracking: (id) => request.get(`/orders/${id}/tracking/`),
  confirmReceived: (id) => request.post(`/orders/${id}/confirm/`),
}

