<template>
  <div v-loading="loading" class="order-detail-page">
    <el-button class="back-btn" @click="router.back()">← 返回</el-button>

    <template v-if="order">
      <el-card class="section-card">
        <template #header>
          <div class="card-header-row">
            <span>订单详情 - {{ order.order_no }}</span>
            <el-tag :type="statusTag(order.status)">{{ order.status_display }}</el-tag>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="下单时间">{{ formatTime(order.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">
            <strong class="price">¥{{ order.total_amount }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ order.payment_method_display || '—' }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ order.paid_at ? formatTime(order.paid_at) : '—' }}</el-descriptions-item>
          <el-descriptions-item label="快递公司">{{ order.carrier || '—' }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ order.tracking_number || '—' }}</el-descriptions-item>
          <el-descriptions-item label="发货时间">{{ order.shipped_at ? formatTime(order.shipped_at) : '—' }}</el-descriptions-item>
          <el-descriptions-item label="签收时间">{{ order.delivered_at ? formatTime(order.delivered_at) : '—' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ order.remark || '—' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Address -->
      <el-card class="section-card">
        <template #header>收货地址</template>
        <div v-if="order.address_snapshot" class="address-snapshot">
          <span class="addr-name">{{ order.address_snapshot.name }}</span>
          <span class="addr-phone">{{ order.address_snapshot.phone }}</span>
          <span>
            {{ order.address_snapshot.province }}{{ order.address_snapshot.city }}{{ order.address_snapshot.district }}{{ order.address_snapshot.detail }}
          </span>
        </div>
      </el-card>

      <!-- Items -->
      <el-card class="section-card">
        <template #header>商品清单</template>
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <div class="item-cover">
              <img v-if="item.book_cover" :src="item.book_cover" class="cover-img" />
              <div v-else class="cover-placeholder">📚</div>
            </div>
            <div class="item-info">
              <div class="item-title">{{ item.book_title }}</div>
              <div class="item-author">{{ item.book_author }}</div>
            </div>
            <div class="item-price">¥{{ item.price }}</div>
            <div class="item-quantity">× {{ item.quantity }}</div>
            <div class="item-subtotal">¥{{ item.subtotal }}</div>
          </div>
        </div>
        <div class="total-row">
          合计：<strong class="price">¥{{ order.total_amount }}</strong>
        </div>
      </el-card>

      <!-- Actions -->
      <div class="action-row">
        <el-button
          v-if="order.status === 'pending_payment'"
          type="primary"
          @click="router.push(`/orders/${order.id}/pay`)"
        >
          去支付
        </el-button>
        <el-button
          v-if="order.status === 'shipped'"
          type="success"
          @click="confirmReceived"
        >
          确认收货
        </el-button>
        <el-button
          v-if="['pending_payment', 'paid'].includes(order.status)"
          type="danger"
          plain
          @click="cancelOrder"
        >
          取消订单
        </el-button>
      </div>
    </template>

    <el-empty v-else-if="!loading" description="订单不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const loading = ref(false)

async function fetchOrder() {
  loading.value = true
  try {
    const res = await orderApi.getOrderDetail(route.params.id)
    order.value = res.data || res
  } finally {
    loading.value = false
  }
}

async function cancelOrder() {
  await ElMessageBox.confirm('确定要取消此订单吗？', '提示', { type: 'warning' })
  try {
    await orderApi.cancelOrder(order.value.id)
    ElMessage.success('订单已取消')
    await fetchOrder()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '取消失败')
  }
}

async function confirmReceived() {
  await ElMessageBox.confirm('确认已收到商品？', '提示', { type: 'warning' })
  try {
    await orderApi.confirmReceived(order.value.id)
    ElMessage.success('确认收货成功')
    await fetchOrder()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  }
}

function statusTag(status) {
  const map = {
    pending_payment: 'warning',
    paid: '',
    shipped: '',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

function formatTime(ts) {
  return ts ? new Date(ts).toLocaleString('zh-CN') : ''
}

onMounted(fetchOrder)
</script>

<style lang="scss" scoped>
.order-detail-page {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px;
}

.back-btn {
  margin-bottom: 16px;
  color: #666;
  font-size: 14px;
  &:hover { color: #2C5F2D; }
}

.section-card {
  margin-bottom: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.card-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: #1A1A1A;
}

.price {
  color: #C75B39;
  font-size: 18px;
  font-weight: 700;
}

.address-snapshot {
  display: flex;
  gap: 12px;
  font-size: 14px;
  align-items: center;
  flex-wrap: wrap;

  .addr-name { font-weight: 600; color: #1A1A1A; }
  .addr-phone { color: #666; }
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
  padding: 10px 0;
  border-bottom: 1px solid #F5F5F5;

  &:last-child { border-bottom: none; }

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

  .item-info { flex: 1; }
  .item-title { font-size: 14px; font-weight: 500; color: #1A1A1A; margin-bottom: 4px; }
  .item-author { font-size: 12px; color: #999; }
  .item-price { color: #666; }
  .item-quantity { color: #999; }
  .item-subtotal { font-weight: 700; color: #C75B39; width: 80px; text-align: right; font-size: 15px; }
}

.total-row {
  text-align: right;
  margin-top: 16px;
  font-size: 15px;
  color: #666;
  padding-top: 12px;
  border-top: 1px solid #E5E5E5;
}

.action-row {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 4px;
}
</style>
