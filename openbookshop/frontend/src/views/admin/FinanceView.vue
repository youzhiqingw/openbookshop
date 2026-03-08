<template>
  <div class="finance-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>财务流水</span>
          <div class="filters">
            <el-select v-model="filterType" placeholder="收支类型" clearable style="width: 140px;" @change="fetchList">
              <el-option label="全部" value="" />
              <el-option label="订单收入" value="income" />
              <el-option label="退款支出" value="refund" />
            </el-select>
          </div>
        </div>
      </template>

      <!-- 汇总信息 -->
      <el-row :gutter="16" class="summary-row">
        <el-col :span="8">
          <el-statistic title="总收入" :value="totalIncome" prefix="¥" :precision="2" value-style="color: #67c23a" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="总退款" :value="totalRefund" prefix="¥" :precision="2" value-style="color: #f56c6c" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="流水笔数" :value="total" value-style="color: #409eff" />
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
        <el-table-column prop="merchant_name" label="商家" min-width="120" />
        <el-table-column prop="username" label="用户" width="100" />
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
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterType = ref('')

const totalIncome = computed(() => {
  // We show this based on current page data; ideally from backend summary
  // For now compute from all loaded records
  return list.value.filter(r => r.type === 'income').reduce((s, r) => s + Number(r.amount), 0)
})
const totalRefund = computed(() =>
  list.value.filter(r => r.type === 'refund').reduce((s, r) => s + Number(r.amount), 0)
)

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterType.value) params.type = filterType.value
    const res = await adminApi.getFinanceList(params)
    const data = res.data.data
    list.value = data.results
    total.value = data.total
  } catch {
    ElMessage.error('获取财务数据失败')
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
.finance-view {}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.summary-row {
  margin-bottom: 20px;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}
.income-amount { color: #67c23a; font-weight: bold; }
.refund-amount { color: #f56c6c; font-weight: bold; }
.order-no { font-family: monospace; font-size: 12px; }
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
