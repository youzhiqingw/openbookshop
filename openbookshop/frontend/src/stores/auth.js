import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.is_staff)
  const isMerchant = computed(() => user.value?.role === 'merchant')
  const isCustomer = computed(() => user.value?.role === 'customer')

  function setAuth(userData, tokens) {
    user.value = userData
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
  }

  function updateUser(userData) {
    user.value = { ...user.value, ...userData }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function login(username, password) {
    const res = await authApi.login({ username, password })
    if (res.code === 200) {
      setAuth(res.data.user, res.data.tokens)
    }
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    if (res.code === 201) {
      setAuth(res.data.user, res.data.tokens)
    }
    return res
  }

  async function logout() {
    try {
      await authApi.logout({ refresh: refreshToken.value })
    } catch {
      // ignore errors on logout
    } finally {
      user.value = null
      accessToken.value = ''
      refreshToken.value = ''
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    isAdmin,
    isMerchant,
    isCustomer,
    setAuth,
    updateUser,
    login,
    register,
    logout,
  }
})
