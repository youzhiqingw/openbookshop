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
  getLowStock: () => request.get('/books/admin/low-stock/'),
  // Categories
  getCategories: () => request.get('/books/categories/'),
  createCategory: (data) => request.post('/books/admin/categories/', data),
  updateCategory: (id, data) => request.patch(`/books/admin/categories/${id}/`, data),
  deleteCategory: (id) => request.delete(`/books/admin/categories/${id}/`),
  // Orders
  getOrderList: (params) => request.get('/orders/admin/', { params }),
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
  getLowStock: () => request.get('/books/merchant/low-stock/'),
  // Orders
  getOrderList: (params) => request.get('/orders/merchant/', { params }),
  shipOrder: (id) => request.post(`/orders/merchant/${id}/ship/`),
}

export const bookApi = {
  getList: (params) => request.get('/books/', { params }),
  getDetail: (id) => request.get(`/books/${id}/`),
  getCategories: () => request.get('/books/categories/'),
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

