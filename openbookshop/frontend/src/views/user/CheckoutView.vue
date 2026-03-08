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
            :class="['address-item', { 'is-selected': selectedAddressId === addr.id }]"
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
              <img v-if="item.book_detail?.cover" :src="item.book_detail.cover" class="cover-img" />
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
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1A1A1A;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #E8F5E9;
    display: flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: '';
      display: inline-block;
      width: 4px;
      height: 16px;
      background: #2C5F2D;
      border-radius: 2px;
    }
  }
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.address-item {
  padding: 14px 16px;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  width: 100%;
  transition: border-color 0.2s;

  &.is-selected {
    border-color: #2C5F2D;
    background: #F0F9F0;
  }

  .addr-name { font-weight: 600; color: #1A1A1A; margin-right: 8px; }
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
  border: 1px solid #F0F0F0;
  border-radius: 6px;
  background: #FAFAFA;

  .item-cover {
    width: 60px;
    height: 75px;
    flex-shrink: 0;
    background: #F5F5F5;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    overflow: hidden;

    .cover-img { width: 100%; height: 100%; object-fit: cover; }
    .cover-placeholder { font-size: 24px; color: #ccc; }
  }

  .item-title { flex: 1; font-size: 14px; font-weight: 500; color: #1A1A1A; }
  .item-price { color: #666; font-size: 13px; }
  .item-subtotal { font-weight: 700; color: #C75B39; width: 70px; text-align: right; }
}

.order-summary {
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  text-align: right;
  font-size: 15px;
  color: #666;
  margin-bottom: 20px;

  .total {
    font-size: 28px;
    font-weight: 700;
    color: #C75B39;
    margin-left: 8px;
  }
}

.submit-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .el-button--primary {
    background: #2C5F2D;
    border-color: #2C5F2D;
    &:hover { background: #4A7C4B; border-color: #4A7C4B; }
  }
}
</style>
