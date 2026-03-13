<template>
  <div class="log-page">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">操作日志</span>
          <div class="header-tools">
            <el-select v-model="moduleFilter" clearable placeholder="筛选模块" style="width: 130px" @change="() => { page = 1; loadLogs() }">
              <el-option label="认证模块" value="auth" />
              <el-option label="管理后台" value="admin" />
              <el-option label="商家管理" value="merchants" />
              <el-option label="订单管理" value="orders" />
              <el-option label="图书管理" value="books" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户 / 操作"
              clearable
              style="width: 200px"
              :prefix-icon="Search"
              @input="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="logs" stripe row-key="id">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column label="用户" width="110">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="24" style="background:#1890ff; font-size:11px">
                {{ row.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="moduleTagType(row.module)" size="small" effect="light">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" min-width="160" show-overflow-tooltip />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="130">
          <template #default="{ row }">
            <span class="ip-text">{{ row.ip_address || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const moduleFilter = ref('')
const searchQuery = ref('')

let searchTimer = null

async function loadLogs() {
  loading.value = true
  try {
    const res = await adminApi.getOperationLogs({
      page: page.value,
      page_size: pageSize.value,
      module: moduleFilter.value || undefined,
      search: searchQuery.value || undefined,
    })
    logs.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } catch {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadLogs()
  }, 300)
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', { hour12: false })
}

const moduleColors = { auth: '', admin: 'danger', merchants: 'warning', orders: 'success', books: 'info' }
const moduleTagType = (m) => moduleColors[m] || ''

onMounted(loadLogs)
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
  flex-wrap: wrap;
  gap: 12px;

  .card-title { font-size: 15px; font-weight: 600; color: #1a1a1a; }
  .header-tools { display: flex; gap: 10px; align-items: center; }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.ip-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
