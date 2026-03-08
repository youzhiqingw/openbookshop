<template>
  <div class="cart-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>购物车（{{ cartStore.totalCount }} 件商品）</span>
          <el-button type="danger" text @click="clearCart" :disabled="!cartStore.items.length">
            清空购物车
          </el-button>
        </div>
      </template>

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
            <el-button type="danger" text @click="removeItem(item.id)">删除</el-button>
          </div>
        </div>

        <!-- Checkout Bar -->
        <div class="checkout-bar">
          <div class="bar-left">
            <el-checkbox v-model="selectAll" @change="toggleSelectAll">全选</el-checkbox>
            <span class="selected-info">已选 {{ selectedIds.length }} 件</span>
          </div>
          <div class="bar-right">
            <span class="total-amount">合计：<strong>¥{{ selectedTotal }}</strong></span>
            <el-button type="primary" size="large" :disabled="!selectedIds.length" @click="checkout">
              结算 ({{ selectedIds.length }})
            </el-button>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;

  .item-check { flex-shrink: 0; }

  .item-cover {
    width: 80px;
    height: 100px;
    flex-shrink: 0;
    cursor: pointer;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    overflow: hidden;

    .cover-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .cover-placeholder { font-size: 32px; color: #ccc; }
  }

  .item-info {
    flex: 1;
    cursor: pointer;

    .item-title {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 4px;
    }

    .item-author { font-size: 12px; color: #999; margin-bottom: 8px; }
    .item-price { color: #e6a23c; font-weight: bold; }
  }

  .item-quantity { flex-shrink: 0; }

  .item-subtotal {
    width: 80px;
    text-align: right;
    font-weight: bold;
    color: #e6a23c;
    flex-shrink: 0;
  }
}

.checkout-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;

  .bar-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .selected-info { color: #666; font-size: 14px; }
  }

  .bar-right {
    display: flex;
    align-items: center;
    gap: 20px;

    .total-amount {
      font-size: 16px;
      strong { font-size: 22px; color: #e6a23c; }
    }
  }
}
</style>
