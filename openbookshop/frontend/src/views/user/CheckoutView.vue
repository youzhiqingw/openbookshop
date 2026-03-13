<template>
  <div v-loading="loading" class="checkout-page">
    <el-card class="checkout-card">
      <template #header><span>确认订单</span></template>

      <!-- Address Selection -->
      <div class="section">
        <h3>收货地址</h3>
        <el-radio-group v-model="selectedAddressId" class="address-list">
          <el-radio
            v-for="addr in addresses"
            :key="addr.id"
            :label="addr.id"
            class="address-item"
          >
            <span class="addr-name">{{ addr.name }}</span>
            <span class="addr-phone">{{ addr.phone }}</span>
            <el-tag v-if="addr.is_default" size="small" type="success">默认</el-tag>
            <span class="addr-detail">
              {{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.detail }}
            </span>
          </el-radio>
        </el-radio-group>
        <el-button text type="primary" @click="router.push('/addresses')">
          管理收货地址
        </el-button>
      </div>

      <!-- Order Items -->
      <div class="section">
        <h3>商品清单</h3>
        <div class="order-items">
          <div v-for="item in checkoutItems" :key="item.id" class="order-item">
            <div class="item-cover">
              <img v-if="item.book_detail?.cover_url || item.book_detail?.cover" :src="item.book_detail?.cover_url || item.book_detail?.cover" class="cover-img" @error="(e) => (e.target.style.display = 'none')" />
              <div v-else class="cover-placeholder">📚</div>
            </div>
            <div class="item-title">{{ item.book_detail?.title }}</div>
            <div class="item-price">¥{{ item.book_detail?.price }} × {{ item.quantity }}</div>
            <div class="item-subtotal">¥{{ item.subtotal }}</div>
          </div>
        </div>
      </div>

      <!-- Remark -->
      <div class="section">
        <h3>备注</h3>
        <el-input v-model="remark" type="textarea" placeholder="选填，对本次交易的说明" maxlength="200" show-word-limit />
      </div>

      <!-- Summary -->
      <div class="order-summary">
        <span>共 {{ checkoutItems.length }} 种商品，合计：</span>
        <span class="total">¥{{ totalAmount }}</span>
      </div>

      <div class="submit-row">
        <el-button @click="router.back()">返回购物车</el-button>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          :disabled="!selectedAddressId"
          @click="submitOrder"
        >
          提交订单
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userApi, orderApi } from '@/api'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const loading = ref(false)
const submitting = ref(false)
const addresses = ref([])
const selectedAddressId = ref(null)
const remark = ref('')

const cartIds = computed(() => {
  const ids = route.query.cart_ids
  return ids ? ids.split(',').map(Number) : []
})

const checkoutItems = computed(() =>
  cartStore.items.filter((i) => cartIds.value.includes(i.id))
)

const totalAmount = computed(() =>
  checkoutItems.value.reduce((sum, i) => sum + Number(i.subtotal), 0).toFixed(2)
)

async function fetchAddresses() {
  loading.value = true
  try {
    const res = await userApi.getAddresses()
    addresses.value = res.results || res || []
    const defaultAddr = addresses.value.find((a) => a.is_default)
    selectedAddressId.value = defaultAddr?.id || addresses.value[0]?.id || null
  } finally {
    loading.value = false
  }
}

async function submitOrder() {
  if (!selectedAddressId.value) {
    return ElMessage.warning('请选择收货地址')
  }
  if (!checkoutItems.value.length) {
    return ElMessage.warning('请先选择商品')
  }
  submitting.value = true
  try {
    const res = await orderApi.createOrder({
      address_id: selectedAddressId.value,
      cart_item_ids: cartIds.value,
      remark: remark.value,
    })
    const order = res.data || res
    if (!order?.id) {
      ElMessage.error('订单创建失败，请重试')
      return
    }
    ElMessage.success('订单创建成功，请完成支付')
    await cartStore.fetchCart()
    router.push(`/orders/${order.id}/pay`)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '下单失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await cartStore.fetchCart()
  await fetchAddresses()
})
</script>

<style lang="scss" scoped>
.checkout-page {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.section {
  margin-bottom: 24px;
  h3 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
  }
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}

.address-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  width: 100%;

  .addr-name { font-weight: 500; margin-right: 8px; }
  .addr-phone { color: #666; margin-right: 8px; }
  .addr-detail { color: #999; font-size: 13px; }
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;

  .item-cover {
    width: 60px;
    height: 75px;
    flex-shrink: 0;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    overflow: hidden;

    .cover-img { width: 100%; height: 100%; object-fit: cover; }
    .cover-placeholder { font-size: 24px; color: #ccc; }
  }

  .item-title { flex: 1; font-size: 14px; }
  .item-price { color: #666; font-size: 13px; }
  .item-subtotal { font-weight: bold; color: #e6a23c; width: 70px; text-align: right; }
}

.order-summary {
  text-align: right;
  font-size: 16px;
  margin: 20px 0;
  padding-top: 16px;
  border-top: 1px solid #eee;

  .total {
    font-size: 24px;
    font-weight: bold;
    color: #e6a23c;
    margin-left: 8px;
  }
}

.submit-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
