<template>
  <div class="user-list-page">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">用户管理</span>
          <div class="header-tools">
            <el-select v-model="roleFilter" clearable placeholder="角色筛选" style="width: 120px" @change="() => { page = 1; loadUsers() }">
              <el-option label="管理员" value="admin" />
              <el-option label="商家" value="merchant" />
              <el-option label="普通用户" value="customer" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户名 / 邮箱"
              clearable
              style="width: 240px"
              :prefix-icon="Search"
              @input="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe row-key="id">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column label="用户" min-width="160">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="32" :style="{ background: avatarColor(row.role) }">
                {{ row.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div>
                <div class="user-name">{{ row.username }}</div>
                <div class="user-email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" effect="light" round>
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" effect="light" round>
              {{ row.is_active ? '正常' : '封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="120">
          <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.is_active ? 'danger' : 'success'"
              plain
              :loading="togglingId === row.id"
              :disabled="row.role === 'admin'"
              @click="toggleStatus(row)"
            >
              {{ row.is_active ? '封禁' : '解封' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @change="loadUsers"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const roleFilter = ref('')
const togglingId = ref(null)

let searchTimer = null

async function loadUsers() {
  loading.value = true
  try {
    const res = await adminApi.getUserList({
      page: page.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      role: roleFilter.value || undefined,
    })
    users.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } catch {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadUsers()
  }, 300)
}

async function toggleStatus(row) {
  const action = row.is_active ? '封禁' : '解封'
  await ElMessageBox.confirm(
    `确定要${action}用户「${row.username}」吗？`,
    '操作确认',
    { type: 'warning', confirmButtonText: action, confirmButtonClass: row.is_active ? 'el-button--danger' : '' },
  )
  togglingId.value = row.id
  try {
    await adminApi.toggleUserStatus(row.id)
    ElMessage.success(`${action}成功`)
    await loadUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    togglingId.value = null
  }
}

const roleMap = { admin: '管理员', merchant: '商家', customer: '普通用户' }
const roleTagTypeMap = { admin: 'danger', merchant: 'warning', customer: '' }
const avatarColorMap = { admin: '#ff4d4f', merchant: '#fa8c16', customer: '#1890ff' }
const roleLabel = (role) => roleMap[role] || role
const roleTagType = (role) => roleTagTypeMap[role] || ''
const avatarColor = (role) => avatarColorMap[role] || '#1890ff'

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(loadUsers)
</script>

<style lang="scss" scoped>
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
  flex-wrap: wrap;
  gap: 12px;

  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a1a;
  }

  .header-tools {
    display: flex;
    gap: 10px;
    align-items: center;
  }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;

  .user-name {
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
  }
  .user-email {
    font-size: 12px;
    color: #999;
  }
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
