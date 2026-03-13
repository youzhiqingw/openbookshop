<template>
  <div class="cart-page">
    <div class="cart-head">
      <div>
        <p class="head-kicker">YOUR SHELF</p>
        <h1>购物车</h1>
      </div>
      <div class="cart-summary">共 {{ cartStore.totalCount }} 件商品</div>
    </div>

    <el-card class="cart-card">
      <template #header>
        <div class="card-header">
          <span>已添加商品</span>
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
  try {
    await ElMessageBox.confirm('确定要清空购物车吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
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
  margin: 0 auto;
  padding: 0 12px 28px;
}

.cart-head {
  margin-bottom: 16px;
  padding: 20px 22px;
  border-radius: 20px;
  border: 1px solid #dde8d7;
  background:
    radial-gradient(circle at 18% 16%, rgba(230, 249, 224, 0.9) 0%, rgba(230, 249, 224, 0) 40%),
    linear-gradient(130deg, #f2f8ef 0%, #fbfdf8 100%);
  box-shadow: 0 20px 36px -34px rgba(42, 56, 35, 0.95);
  display: flex;
  justify-content: space-between;
  align-items: end;

  .head-kicker {
    margin: 0 0 6px;
    font-size: 12px;
    letter-spacing: 2px;
    color: #5e775f;
  }

  h1 {
    margin: 0;
    font-size: 32px;
    font-family: 'STZhongsong', 'KaiTi', serif;
    color: #203427;
  }

  .cart-summary {
    border-radius: 999px;
    border: 1px solid #d4e0ce;
    background: rgba(255, 255, 255, 0.85);
    color: #2d5c39;
    font-size: 13px;
    font-weight: 600;
    padding: 7px 12px;
  }
}

.cart-card {
  border-radius: 16px;
  border: 1px solid #e0e8db;
  box-shadow: 0 26px 40px -36px rgba(35, 44, 30, 0.95);

  :deep(.el-card__header) {
    border-bottom: 1px solid #e8eee2;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  span {
    font-weight: 600;
    color: #273929;
  }
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
  border: 1px solid #e5ebdf;
  border-radius: 12px;
  background: #fff;
  transition: border-color 0.25s, box-shadow 0.25s;

  &:hover {
    border-color: #cddbc8;
    box-shadow: 0 14px 24px -26px rgba(34, 47, 30, 0.95);
  }

  .item-check { flex-shrink: 0; }

  .item-cover {
    width: 80px;
    height: 100px;
    flex-shrink: 0;
    cursor: pointer;
    background: linear-gradient(140deg, #edf4ea, #f7faf4);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    overflow: hidden;

    .cover-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .cover-placeholder { font-size: 32px; color: #b9c7b7; }
  }

  .item-info {
    flex: 1;
    cursor: pointer;

    .item-title {
      font-size: 15px;
      font-weight: 600;
      margin-bottom: 4px;
      color: #243726;
    }

    .item-author { font-size: 12px; color: #6d7f6f; margin-bottom: 8px; }
    .item-price { color: #2f6440; font-weight: 700; }
  }

  .item-quantity {
    flex-shrink: 0;

    :deep(.el-input-number) {
      border-radius: 10px;
    }
  }

  .item-subtotal {
    width: 80px;
    text-align: right;
    font-weight: 700;
    color: #c96845;
    flex-shrink: 0;
  }
}

.checkout-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(120deg, #f2f7ed, #f8fbf4);
  border-radius: 12px;
  border: 1px solid #dde8d6;
  position: sticky;
  bottom: 12px;
  z-index: 5;

  .bar-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .selected-info { color: #607261; font-size: 14px; }
  }

  .bar-right {
    display: flex;
    align-items: center;
    gap: 20px;

    .total-amount {
      font-size: 16px;
      color: #4a5d4d;

      strong {
        font-size: 24px;
        color: #cc6947;
      }
    }

    :deep(.el-button) {
      border-radius: 999px;
      border: none;
      background: linear-gradient(130deg, #2f6d45, #205438);
      padding: 12px 26px;
    }
  }
}

@media (max-width: 900px) {
  .cart-item {
    flex-wrap: wrap;

    .item-info {
      min-width: 180px;
    }

    .item-subtotal {
      width: auto;
      margin-left: auto;
    }
  }

  .checkout-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;

    .bar-right {
      justify-content: space-between;
    }
  }
}

@media (max-width: 640px) {
  .cart-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;

    h1 {
      font-size: 28px;
    }
  }
}
</style>
