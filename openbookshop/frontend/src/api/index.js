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
}

export const merchantApi = {
  applyMerchant: (data) => request.post('/merchants/apply/', data),
  getProfile: () => request.get('/merchants/profile/'),
  updateProfile: (data) => request.put('/merchants/profile/', data),
}
