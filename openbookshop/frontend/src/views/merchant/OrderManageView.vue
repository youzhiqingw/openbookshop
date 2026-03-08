<template>
  <div class="merchant-orders-page">
    <el-card>
      <template #header><span>订单管理</span></template>

      <!-- Status Tabs -->
      <el-tabs v-model="activeTab" @tab-change="fetchOrders(1)">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="待支付" name="pending_payment" />
        <el-tab-pane label="已支付（待发货）" name="paid" />
        <el-tab-pane label="已发货" name="shipped" />
        <el-tab-pane label="已完成" name="completed" />
      </el-tabs>

      <el-table v-loading="loading" :data="orders" stripe>
        <el-table-column prop="order_no" label="订单号" min-width="160" />
        <el-table-column prop="username" label="买家" width="100" />
        <el-table-column label="商品" min-width="200">
          <template #default="{ row }">
            <div v-for="item in row.items" :key="item.id" class="order-item-row">
              {{ item.book_title }} × {{ item.quantity }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="收货地址" min-width="200">
          <template #default="{ row }">
            <span v-if="row.address_snapshot">
              {{ row.address_snapshot.name }}
              {{ row.address_snapshot.province }}{{ row.address_snapshot.city }}{{ row.address_snapshot.district }}{{ row.address_snapshot.detail }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下单时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paid'"
              type="primary"
              size="small"
              @click="shipOrder(row)"
            >
              发货
            </el-button>
            <span v-else-if="row.tracking_number" style="font-size:12px;color:#999">
              {{ row.carrier }}<br />{{ row.tracking_number }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="fetchOrders"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { merchantApi } from '@/api'

const orders = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref('')

async function fetchOrders(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    const params = { page: currentPage.value }
    if (activeTab.value) params.status = activeTab.value
    const res = await merchantApi.getOrderList(params)
    orders.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

async function shipOrder(order) {
  await ElMessageBox.confirm(`确认为订单 ${order.order_no} 发货？`, '发货确认', { type: 'warning' })
  try {
    const res = await merchantApi.shipOrder(order.id)
    const data = res.data || res
    ElMessage.success(`发货成功！快递单号：${data.tracking_number}（${data.carrier}）`)
    fetchOrders(currentPage.value)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发货失败')
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

function formatTime(ts) {
  return ts ? new Date(ts).toLocaleString('zh-CN') : ''
}

onMounted(() => fetchOrders())
</script>

<style lang="scss" scoped>
.merchant-orders-page { padding: 20px; }

.order-item-row {
  font-size: 12px;
  color: #666;
  line-height: 1.6;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
