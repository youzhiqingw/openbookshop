<template>
  <div class="log-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <div class="header-tools">
            <el-select v-model="moduleFilter" clearable placeholder="筛选模块" style="width: 120px" @change="loadLogs">
              <el-option label="auth" value="auth" />
              <el-option label="admin" value="admin" />
              <el-option label="merchants" value="merchants" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户/操作"
              clearable
              style="width: 200px"
              prefix-icon="Search"
              @input="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="logs" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="操作" width="160" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="130" />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const page = ref(1)
const moduleFilter = ref('')
const searchQuery = ref('')

let searchTimer = null

async function loadLogs() {
  loading.value = true
  try {
    const res = await adminApi.getOperationLogs({
      page: page.value,
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
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(loadLogs)
</script>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-tools {
    display: flex;
    gap: 12px;
  }
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
