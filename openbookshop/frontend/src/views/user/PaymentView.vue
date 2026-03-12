<template>
  <div class="payment-page">
    <el-card class="payment-card">
      <template #header><span>订单支付</span></template>

      <template v-if="order">
        <el-descriptions :column="1" border class="order-info">
          <el-descriptions-item label="订单号">{{ order.order_no }}</el-descriptions-item>
          <el-descriptions-item label="应付金额">
            <span class="amount">¥{{ order.total_amount }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="statusTag(order.status)">{{ order.status_display }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <template v-if="order.status === 'pending_payment'">
          <div class="payment-method">
            <h3>选择支付方式</h3>
            <el-radio-group v-model="paymentMethod" class="method-group">
              <el-radio-button label="wechat">微信支付</el-radio-button>
              <el-radio-button label="alipay">支付宝</el-radio-button>
              <el-radio-button label="mock">模拟支付</el-radio-button>
            </el-radio-group>
          </div>

          <div v-if="payUrl" class="pay-url-box">
            <el-alert type="success" :closable="false" title="支付信息已生成">
              <p>模拟支付链接（真实环境将跳转到支付页面）：</p>
              <el-link :href="payUrl" target="_blank" type="primary">{{ payUrl }}</el-link>
            </el-alert>
          </div>

          <div class="pay-actions">
            <el-button
              v-if="!payUrl"
              type="primary"
              size="large"
              :loading="payLoading"
              @click="initPay"
            >
              发起支付
            </el-button>
            <el-button
              v-if="payUrl"
              type="success"
              size="large"
              :loading="confirmLoading"
              @click="confirmPay"
            >
              确认已支付
            </el-button>
            <el-button @click="cancelOrder">取消订单</el-button>
          </div>
        </template>

        <template v-else-if="order.status === 'paid'">
          <el-result icon="success" title="支付成功" sub-title="商家正在备货，请耐心等待">
            <template #extra>
              <el-button type="primary" @click="router.push('/orders')">查看我的订单</el-button>
            </template>
          </el-result>
        </template>

        <template v-else>
          <el-result icon="info" :title="order.status_display" sub-title="订单状态已变更">
            <template #extra>
              <el-button type="primary" @click="router.push('/orders')">查看我的订单</el-button>
            </template>
          </el-result>
        </template>
      </template>

      <el-empty v-else-if="!loading" description="订单不存在" />
    </el-card>
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
const payLoading = ref(false)
const confirmLoading = ref(false)
const paymentMethod = ref('mock')
const payUrl = ref('')

async function fetchOrder() {
  loading.value = true
  try {
    const res = await orderApi.getOrderDetail(route.params.id)
    order.value = res.data || res
    if (order.value.pay_url) {
      payUrl.value = order.value.pay_url
    }
  } finally {
    loading.value = false
  }
}

async function initPay() {
  payLoading.value = true
  try {
    const res = await orderApi.payOrder(route.params.id, { payment_method: paymentMethod.value })
    const data = res.data || res
    payUrl.value = data.pay_url
    ElMessage.success('支付信息已生成')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发起支付失败')
  } finally {
    payLoading.value = false
  }
}

async function confirmPay() {
  confirmLoading.value = true
  try {
    const res = await orderApi.confirmPayment(route.params.id)
    const data = res.data || res
    if (data.status === 'success') {
      ElMessage.success('支付成功！')
      await fetchOrder()
    } else {
      ElMessage.info(res.message || '支付处理中，请稍后再试')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '支付确认失败')
  } finally {
    confirmLoading.value = false
  }
}

async function cancelOrder() {
  try {
    await ElMessageBox.confirm('确定要取消此订单吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await orderApi.cancelOrder(route.params.id)
    ElMessage.success('订单已取消')
    router.push('/orders')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '取消失败')
  }
}

function statusTag(status) {
  const map = {
    pending_payment: 'warning',
    paid: 'success',
    shipped: '',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

onMounted(fetchOrder)
</script>

<style lang="scss" scoped>
.payment-page {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
}

.order-info {
  margin-bottom: 24px;
}

.amount {
  font-size: 24px;
  font-weight: bold;
  color: #e6a23c;
}

.payment-method {
  margin-bottom: 20px;

  h3 { margin-bottom: 12px; font-size: 16px; }

  .method-group { display: flex; gap: 8px; }
}

.pay-url-box {
  margin-bottom: 20px;
}

.pay-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
