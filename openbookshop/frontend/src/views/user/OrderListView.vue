<template>
  <div class="order-list-page">
    <el-card>
      <template #header><span>我的订单</span></template>

      <!-- Status Tabs -->
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="待支付" name="pending_payment" />
        <el-tab-pane label="已支付" name="paid" />
        <el-tab-pane label="已发货" name="shipped" />
        <el-tab-pane label="已完成" name="completed" />
        <el-tab-pane label="已取消" name="cancelled" />
      </el-tabs>

      <div v-loading="loading">
        <el-empty v-if="!loading && !orders.length" description="暂无订单" />
        <div v-else class="order-list">
          <div v-for="order in orders" :key="order.id" class="order-card">
            <div class="order-header">
              <span class="order-no">订单号：{{ order.order_no }}</span>
              <el-tag :type="statusTag(order.status)">{{ order.status_display }}</el-tag>
              <span class="order-time">{{ formatTime(order.created_at) }}</span>
            </div>
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
                <div class="item-price">¥{{ item.price }} × {{ item.quantity }}</div>
              </div>
            </div>
            <div class="order-footer">
              <span class="order-total">
                实付：<strong>¥{{ order.total_amount }}</strong>
              </span>
              <div class="order-actions">
                <el-button
                  v-if="order.status === 'pending_payment'"
                  type="primary"
                  size="small"
                  @click="router.push(`/orders/${order.id}/pay`)"
                >
                  去支付
                </el-button>
                <el-button
                  v-if="order.status === 'shipped'"
                  type="success"
                  size="small"
                  @click="confirmReceived(order)"
                >
                  确认收货
                </el-button>
                <el-button
                  v-if="order.status === 'shipped'"
                  size="small"
                  @click="viewTracking(order)"
                >
                  查看物流
                </el-button>
                <el-button
                  v-if="['pending_payment', 'paid'].includes(order.status)"
                  type="danger"
                  plain
                  size="small"
                  @click="cancelOrder(order)"
                >
                  取消订单
                </el-button>
                <el-button size="small" @click="router.push(`/orders/${order.id}`)">
                  订单详情
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="fetchOrders"
          />
        </div>
      </div>
    </el-card>

    <!-- Tracking Dialog -->
    <el-dialog v-model="trackingVisible" title="物流信息" width="500px">
      <div v-if="tracking">
        <p><strong>快递公司：</strong>{{ tracking.carrier }}</p>
        <p><strong>运单号：</strong>{{ tracking.tracking_number }}</p>
        <el-timeline class="track-timeline">
          <el-timeline-item
            v-for="(event, i) in tracking.events"
            :key="i"
            :timestamp="event.time"
            placement="top"
          >
            {{ event.description }}（{{ event.location }}）
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无物流信息" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const router = useRouter()

const orders = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref('')
const trackingVisible = ref(false)
const tracking = ref(null)

async function fetchOrders(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    const params = { page: currentPage.value }
    if (activeTab.value) params.status = activeTab.value
    const res = await orderApi.getOrderList(params)
    orders.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  fetchOrders(1)
}

async function cancelOrder(order) {
  try {
    await ElMessageBox.confirm('确定要取消此订单吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await orderApi.cancelOrder(order.id)
    ElMessage.success('订单已取消')
    fetchOrders(currentPage.value)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '取消失败')
  }
}

async function confirmReceived(order) {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await orderApi.confirmReceived(order.id)
    ElMessage.success('确认收货成功')
    fetchOrders(currentPage.value)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  }
}

async function viewTracking(order) {
  tracking.value = null
  trackingVisible.value = true
  try {
    const res = await orderApi.getTracking(order.id)
    tracking.value = res.data || res
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '获取物流信息失败')
  }
}

function statusTag(status) {
  const map = {
    pending_payment: 'warning',
    paid: '',
    processing: 'info',
    shipped: '',
    delivered: 'success',
    completed: 'success',
    cancelled: 'danger',
    refunding: 'warning',
    refunded: 'info',
  }
  return map[status] || 'info'
}

function formatTime(ts) {
  return ts ? new Date(ts).toLocaleString('zh-CN') : ''
}

onMounted(fetchOrders)
</script>

<style lang="scss" scoped>
.order-list-page {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 20px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.order-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  font-size: 13px;

  .order-no { font-weight: 500; flex: 1; }
  .order-time { color: #999; margin-left: auto; }
}

.order-items {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;

  .item-cover {
    width: 50px;
    height: 63px;
    flex-shrink: 0;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    overflow: hidden;

    .cover-img { width: 100%; height: 100%; object-fit: cover; }
    .cover-placeholder { font-size: 20px; color: #ccc; }
  }

  .item-info { flex: 1; }
  .item-title { font-size: 13px; font-weight: 500; }
  .item-author { font-size: 12px; color: #999; }
  .item-price { color: #666; font-size: 13px; }
}

.order-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid #eee;

  .order-total {
    font-size: 14px;
    strong { font-size: 18px; color: #e6a23c; }
  }

  .order-actions { display: flex; gap: 8px; }
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.track-timeline {
  margin-top: 12px;
}
</style>
