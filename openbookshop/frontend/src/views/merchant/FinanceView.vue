<template>
  <div class="merchant-finance-view">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span>收支记录</span>
          <div class="filters">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              clearable
              style="width: 240px;"
              @change="handleFilter"
            />
          </div>
        </div>
      </template>

      <!-- 汇总 -->
      <el-row :gutter="16" class="summary-row">
        <el-col :span="8">
          <el-statistic title="本页收入合计" :value="totalIncome" prefix="¥" :precision="2" value-style="color: #67c23a" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="本页退款合计" :value="totalRefund" prefix="¥" :precision="2" value-style="color: #f56c6c" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="流水总笔数" :value="total" value-style="color: #409eff" />
        </el-col>
      </el-row>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="order_no" label="订单号" min-width="160">
          <template #default="{ row }">
            <span class="order-no">{{ row.order_no || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type_display" label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'" size="small">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="110">
          <template #default="{ row }">
            <span :class="row.type === 'income' ? 'income-amount' : 'refund-amount'">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ Number(row.amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="买家" width="100" />
        <el-table-column prop="description" label="描述" min-width="160" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchList"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { merchantApi } from '@/api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dateRange = ref(null)

const totalIncome = computed(() =>
  list.value.filter(r => r.type === 'income').reduce((s, r) => s + Number(r.amount), 0)
)
const totalRefund = computed(() =>
  list.value.filter(r => r.type === 'refund').reduce((s, r) => s + Number(r.amount), 0)
)

function handleFilter() {
  page.value = 1
  fetchList()
}

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (dateRange.value && dateRange.value[0]) params.date_from = dateRange.value[0]
    if (dateRange.value && dateRange.value[1]) params.date_to = dateRange.value[1]
    const res = await merchantApi.getFinanceList(params)
    const data = res.data
    list.value = data.results
    total.value = data.total
  } catch {
    ElMessage.error('获取收支记录失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dt) {
  if (!dt) return '-'
  return new Date(dt).toLocaleString('zh-CN', { hour12: false })
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
.main-card {
  border-radius: 12px !important;
  :deep(.el-card__header) { padding: 14px 20px; }
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .filters {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}
.summary-row {
  margin-bottom: 20px;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}
.income-amount { color: #52c41a; font-weight: bold; }
.refund-amount { color: #ff4d4f; font-weight: bold; }
.order-no { font-family: monospace; font-size: 12px; }
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
