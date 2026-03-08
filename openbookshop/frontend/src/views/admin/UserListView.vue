<template>
  <div class="user-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名/邮箱"
            clearable
            style="width: 240px"
            prefix-icon="Search"
            @input="handleSearch"
          />
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="120">
          <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              text
              :type="row.is_active ? 'danger' : 'success'"
              :loading="togglingId === row.id"
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
import { adminApi } from '@/api'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const togglingId = ref(null)

let searchTimer = null

async function loadUsers() {
  loading.value = true
  try {
    const res = await adminApi.getUserList({
      page: page.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
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
  await ElMessageBox.confirm(`确定要${action}用户「${row.username}」吗？`, '提示', { type: 'warning' })
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
const roleLabel = (role) => roleMap[role] || role
const roleTagType = (role) => roleTagTypeMap[role] || ''

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(loadUsers)
</script>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
