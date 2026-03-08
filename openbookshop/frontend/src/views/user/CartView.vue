<template>
  <div class="cart-page">
    <div class="page-header">
      <h2 class="page-title">我的购物车</h2>
      <el-button
        v-if="cartStore.items.length"
        type="danger"
        text
        size="small"
        @click="clearCart"
      >
        <el-icon><Delete /></el-icon> 清空购物车
      </el-button>
    </div>

    <el-empty v-if="!cartStore.items.length" description="购物车空空如也">
      <el-button type="primary" @click="router.push('/books')">去逛逛</el-button>
    </el-empty>

    <template v-else>
      <!-- Cart Items -->
      <div class="cart-list">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <el-checkbox v-model="selectedIds" :label="item.id" class="item-check" />
          <div class="item-cover" @click="router.push(`/books/${item.book}`)">
            <img v-if="item.book_detail?.cover" :src="item.book_detail.cover" class="cover-img" />
            <div v-else class="cover-placeholder">📚</div>
          </div>
          <div class="item-info" @click="router.push(`/books/${item.book}`)">
            <div class="item-title">{{ item.book_detail?.title }}</div>
            <div class="item-author">{{ item.book_detail?.author }}</div>
            <div class="item-price">¥{{ item.book_detail?.price }}</div>
          </div>
          <div class="item-quantity">
            <el-input-number
              v-model="item.quantity"
              :min="1"
              :max="item.book_detail?.stock || 99"
              size="small"
              @change="(val) => updateQuantity(item.id, val)"
            />
          </div>
          <div class="item-subtotal">¥{{ item.subtotal }}</div>
          <el-button type="danger" link @click="removeItem(item.id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- Checkout Bar -->
      <div class="checkout-bar">
        <div class="bar-left">
          <el-checkbox v-model="selectAll" @change="toggleSelectAll">全选</el-checkbox>
          <span class="selected-info">已选 <strong>{{ selectedIds.length }}</strong> 件</span>
        </div>
        <div class="bar-right">
          <span class="total-amount">
            合计：<strong class="total-price">¥{{ selectedTotal }}</strong>
          </span>
          <el-button
            type="primary"
            size="large"
            class="checkout-btn"
            :disabled="!selectedIds.length"
            @click="checkout"
          >
            结算 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()

const selectedIds = ref([])

const selectAll = computed({
  get: () => selectedIds.value.length === cartStore.items.length && cartStore.items.length > 0,
  set: () => {},
})

const selectedTotal = computed(() => {
  const total = cartStore.items
    .filter((i) => selectedIds.value.includes(i.id))
    .reduce((sum, i) => sum + Number(i.subtotal), 0)
  return total.toFixed(2)
})

function toggleSelectAll(val) {
  selectedIds.value = val ? cartStore.items.map((i) => i.id) : []
}

async function updateQuantity(id, quantity) {
  await cartStore.updateQuantity(id, quantity)
}

async function removeItem(id) {
  await cartStore.removeItem(id)
  selectedIds.value = selectedIds.value.filter((i) => i !== id)
}

async function clearCart() {
  await ElMessageBox.confirm('确定要清空购物车吗？', '提示', { type: 'warning' })
  await cartStore.clearCart()
  selectedIds.value = []
}

function checkout() {
  router.push({
    name: 'Checkout',
    query: { cart_ids: selectedIds.value.join(',') },
  })
}

onMounted(() => cartStore.fetchCart())
</script>

<style lang="scss" scoped>
.cart-page {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .page-title {
    font-size: 22px;
    font-weight: 700;
    color: #1A1A1A;
  }
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  transition: box-shadow 0.2s;

  &:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

  .item-check { flex-shrink: 0; }

  .item-cover {
    width: 80px;
    height: 100px;
    flex-shrink: 0;
    cursor: pointer;
    background: #F5F5F5;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    overflow: hidden;

    .cover-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s;
    }

    &:hover .cover-img { transform: scale(1.05); }
    .cover-placeholder { font-size: 32px; color: #ccc; }
  }

  .item-info {
    flex: 1;
    cursor: pointer;

    .item-title {
      font-size: 14px;
      font-weight: 600;
      color: #1A1A1A;
      margin-bottom: 6px;
      line-height: 1.4;
      &:hover { color: #2C5F2D; }
    }

    .item-author { font-size: 12px; color: #999; margin-bottom: 8px; }
    .item-price { color: #C75B39; font-weight: 700; font-size: 15px; }
  }

  .item-quantity { flex-shrink: 0; }

  .item-subtotal {
    width: 90px;
    text-align: right;
    font-weight: 700;
    color: #C75B39;
    font-size: 16px;
    flex-shrink: 0;
  }
}

.checkout-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
  position: sticky;
  bottom: 20px;

  .bar-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .selected-info {
      color: #666;
      font-size: 14px;
      strong { color: #1A1A1A; }
    }
  }

  .bar-right {
    display: flex;
    align-items: center;
    gap: 24px;

    .total-amount {
      font-size: 15px;
      color: #666;
    }

    .total-price {
      font-size: 24px;
      color: #C75B39;
      font-weight: 700;
    }

    .checkout-btn {
      background: #2C5F2D;
      border-color: #2C5F2D;
      font-size: 15px;
      padding: 10px 28px;
      &:hover:not(:disabled) { background: #4A7C4B; border-color: #4A7C4B; }
    }
  }
}
</style>
