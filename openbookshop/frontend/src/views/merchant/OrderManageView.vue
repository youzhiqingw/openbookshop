<template>
  <div class="merchant-orders-page">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">订单管理</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索订单号 / 买家"
            clearable
            style="width: 220px"
            :prefix-icon="Search"
            @input="handleSearch"
          />
        </div>
      </template>

      <!-- Status Tabs -->
      <el-tabs v-model="activeTab" class="order-tabs" @tab-change="() => { currentPage = 1; fetchOrders() }">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="待支付" name="pending_payment" />
        <el-tab-pane name="paid">
          <template #label>
            <span>待发货</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已发货" name="shipped" />
        <el-tab-pane label="已完成" name="completed" />
        <el-tab-pane label="已取消" name="cancelled" />
      </el-tabs>

      <el-table v-loading="loading" :data="orders" stripe row-key="id">
        <el-table-column prop="order_no" label="订单号" min-width="150">
          <template #default="{ row }">
            <span class="order-no">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品" min-width="180">
          <template #default="{ row }">
            <div v-for="item in row.items" :key="item.id" class="order-item-row">
              <span class="item-title">{{ item.book_title }}</span>
              <el-tag size="small" type="info" effect="plain">×{{ item.quantity }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="买家 / 收货" min-width="200">
          <template #default="{ row }">
            <div class="buyer-cell">
              <span class="buyer-name">{{ row.username }}</span>
              <div v-if="row.address_snapshot" class="buyer-addr">
                {{ row.address_snapshot.province }}{{ row.address_snapshot.city }}
                {{ row.address_snapshot.district }}
                {{ row.address_snapshot.detail }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="95" align="right">
          <template #default="{ row }">
            <span class="amount">¥{{ row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" effect="light" round>
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下单时间" width="150">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paid'"
              type="primary"
              size="small"
              :icon="Van"
              @click="openShipDialog(row)"
            >发货</el-button>
            <div v-else-if="row.tracking_number" class="tracking-info">
              <el-tag size="small" type="success" effect="plain">{{ row.carrier }}</el-tag>
              <div class="tracking-no">{{ row.tracking_number }}</div>
            </div>
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

    <!-- Ship Dialog -->
    <el-dialog v-model="shipDialogVisible" title="确认发货" width="460px" align-center>
      <div class="ship-dialog-body">
        <el-descriptions :column="1" border size="small" class="order-desc">
          <el-descriptions-item label="订单号">
            <span class="order-no">{{ shipTarget?.order_no }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="买家">{{ shipTarget?.username }}</el-descriptions-item>
          <el-descriptions-item label="商品">
            <div v-for="item in shipTarget?.items" :key="item.id">
              {{ item.book_title }} × {{ item.quantity }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="收货地址" v-if="shipTarget?.address_snapshot">
            {{ shipTarget.address_snapshot.name }}
            {{ shipTarget.address_snapshot.province }}{{ shipTarget.address_snapshot.city }}
            {{ shipTarget.address_snapshot.district }}{{ shipTarget.address_snapshot.detail }}
            （{{ shipTarget.address_snapshot.phone }}）
          </el-descriptions-item>
        </el-descriptions>
        <el-alert
          title="点击确认后系统将自动分配快递单号"
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 14px;"
        />
      </div>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" :icon="Van" :loading="shipping" @click="doShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Van, Search } from '@element-plus/icons-vue'
import { merchantApi } from '@/api'

const orders = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref('')
const searchQuery = ref('')

// Ship dialog
const shipDialogVisible = ref(false)
const shipTarget = ref(null)
const shipping = ref(false)

let searchTimer = null

async function fetchOrders(page = currentPage.value) {
  loading.value = true
  currentPage.value = page
  try {
    const params = { page: currentPage.value }
    if (activeTab.value) params.status = activeTab.value
    if (searchQuery.value) params.search = searchQuery.value
    const res = await merchantApi.getOrderList(params)
    orders.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchOrders()
  }, 300)
}

function openShipDialog(order) {
  shipTarget.value = order
  shipDialogVisible.value = true
}

async function doShip() {
  shipping.value = true
  try {
    const res = await merchantApi.shipOrder(shipTarget.value.id)
    const data = res.data || res
    ElMessage.success(`发货成功！快递：${data.carrier}，单号：${data.tracking_number}`)
    shipDialogVisible.value = false
    fetchOrders()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发货失败')
  } finally {
    shipping.value = false
  }
}

function statusTag(status) {
  const map = {
    pending_payment: 'warning',
    paid: '',
    shipped: 'success',
    completed: 'success',
    cancelled: 'danger',
    refunding: 'warning',
    refunded: 'info',
  }
  return map[status] || 'info'
}

function formatTime(ts) {
  return ts ? new Date(ts).toLocaleString('zh-CN', { hour12: false }) : ''
}

onMounted(() => fetchOrders())
</script>

<style lang="scss" scoped>
.merchant-orders-page { }

.main-card {
  border-radius: 12px !important;

  :deep(.el-card__header) {
    padding: 14px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;

  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a1a;
  }
}

.order-tabs {
  margin-bottom: 8px;

  :deep(.el-tabs__item) {
    font-size: 13px;
  }
}

.order-no {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #555;
}

.order-item-row {
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.8;

  .item-title {
    font-size: 13px;
    color: #333;
  }
}

.buyer-cell {
  .buyer-name {
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
  }
  .buyer-addr {
    font-size: 12px;
    color: #999;
    margin-top: 2px;
    line-height: 1.4;
  }
}

.amount {
  font-weight: 600;
  color: #c75b39;
}

.tracking-info {
  text-align: center;
  .tracking-no {
    font-size: 11px;
    color: #999;
    margin-top: 4px;
    font-family: monospace;
  }
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

// Dialog
.ship-dialog-body {
  .order-desc {
    :deep(.el-descriptions__label) {
      width: 80px;
    }
  }
}
</style>
