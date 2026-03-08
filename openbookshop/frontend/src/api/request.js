import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach JWT token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor: handle token refresh & errors
request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post('/api/v1/auth/refresh/', { refresh: refreshToken })
          const newAccess = res.data.access
          localStorage.setItem('access_token', newAccess)
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return request(originalRequest)
        } catch {
          // Refresh failed: logout
          const authStore = useAuthStore()
          authStore.logout()
          router.push('/auth/login')
        }
      } else {
        router.push('/auth/login')
      }
    }
    return Promise.reject(error)
  },
)

export default request
