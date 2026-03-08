import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { orderApi } from '@/api'
import { ElMessage } from 'element-plus'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const loading = ref(false)

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const totalAmount = computed(() =>
    items.value.reduce((sum, item) => sum + Number(item.subtotal), 0).toFixed(2)
  )

  async function fetchCart() {
    loading.value = true
    try {
      const res = await orderApi.getCart()
      items.value = res.results || res || []
    } catch {
      // silent fail
    } finally {
      loading.value = false
    }
  }

  async function addToCart(bookId, quantity = 1) {
    try {
      await orderApi.addToCart({ book_id: bookId, quantity })
      ElMessage.success('已加入购物车')
      await fetchCart()
    } catch (err) {
      ElMessage.error(err.response?.data?.message || '加入购物车失败')
    }
  }

  async function updateQuantity(cartItemId, quantity) {
    try {
      await orderApi.updateCartItem(cartItemId, { quantity })
      const item = items.value.find((i) => i.id === cartItemId)
      if (item) item.quantity = quantity
      await fetchCart()
    } catch (err) {
      ElMessage.error(err.response?.data?.message || '更新失败')
    }
  }

  async function removeItem(cartItemId) {
    try {
      await orderApi.removeCartItem(cartItemId)
      items.value = items.value.filter((i) => i.id !== cartItemId)
      ElMessage.success('已移出购物车')
    } catch {
      ElMessage.error('移除失败')
    }
  }

  async function clearCart() {
    try {
      await orderApi.clearCart()
      items.value = []
    } catch {
      // silent
    }
  }

  return {
    items,
    loading,
    totalCount,
    totalAmount,
    fetchCart,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
  }
})
