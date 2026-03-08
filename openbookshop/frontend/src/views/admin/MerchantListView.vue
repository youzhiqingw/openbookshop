<template>
  <div class="merchant-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商家管理</span>
          <div class="header-tools">
            <el-select v-model="statusFilter" clearable placeholder="筛选状态" style="width: 120px" @change="loadMerchants">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索店铺名/用户名"
              clearable
              style="width: 220px"
              prefix-icon="Search"
              @input="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="merchants" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="store_name" label="店铺名称" />
        <el-table-column prop="username" label="店主" width="100" />
        <el-table-column prop="business_license" label="营业执照" />
        <el-table-column prop="address" label="经营地址" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="120">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button text type="success" :loading="auditingId === row.id" @click="audit(row, 'approved')">通过</el-button>
              <el-button text type="danger" :loading="auditingId === row.id" @click="audit(row, 'rejected')">拒绝</el-button>
            </template>
            <span v-else class="audit-done">已处理</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadMerchants"
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
const merchants = ref([])
const total = ref(0)
const page = ref(1)
const statusFilter = ref('')
const searchQuery = ref('')
const auditingId = ref(null)

let searchTimer = null

async function loadMerchants() {
  loading.value = true
  try {
    const res = await adminApi.getMerchantList({
      page: page.value,
      status: statusFilter.value || undefined,
      search: searchQuery.value || undefined,
    })
    merchants.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } catch {
    ElMessage.error('获取商家列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadMerchants()
  }, 300)
}

async function audit(row, status) {
  const label = status === 'approved' ? '通过' : '拒绝'
  await ElMessageBox.confirm(`确定要${label}店铺「${row.store_name}」的申请吗？`, '确认审核', { type: 'warning' })
  auditingId.value = row.id
  try {
    await adminApi.auditMerchant(row.id, { status })
    ElMessage.success(`审核操作成功：${label}`)
    await loadMerchants()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '审核失败')
  } finally {
    auditingId.value = null
  }
}

const statusMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
const statusTagTypeMap = { pending: 'warning', approved: 'success', rejected: 'danger' }
const statusLabel = (s) => statusMap[s] || s
const statusTagType = (s) => statusTagTypeMap[s] || ''

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(loadMerchants)
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

.audit-done {
  color: #999;
  font-size: 13px;
}
</style>
