<template>
  <div class="merchant-list-page">
    <!-- Summary Chips -->
    <el-row :gutter="12" class="status-summary" v-if="summary.total">
      <el-col :span="6" v-for="s in summaryItems" :key="s.label">
        <div class="summary-chip" :style="{ '--chip-color': s.color, '--chip-bg': s.bg }">
          <span class="chip-count">{{ s.count }}</span>
          <span class="chip-label">{{ s.label }}</span>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">商家管理</span>
          <div class="header-tools">
            <el-radio-group v-model="statusFilter" size="small" @change="() => { page = 1; loadMerchants() }">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="pending">
                <el-badge :value="summary.pending || 0" :hidden="!summary.pending" :max="99">待审核</el-badge>
              </el-radio-button>
              <el-radio-button value="approved">已通过</el-radio-button>
              <el-radio-button value="rejected">已拒绝</el-radio-button>
            </el-radio-group>
            <el-input
              v-model="searchQuery"
              placeholder="搜索店铺名/用户名"
              clearable
              style="width: 220px"
              :prefix-icon="Search"
              @input="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="merchants" stripe row-key="id" class="merchant-table">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="store_name" label="店铺名称" min-width="140">
          <template #default="{ row }">
            <div class="store-name-cell">
              <el-avatar :size="30" shape="square" style="background:#e8f5e9; color:#2C5F2D; font-size:13px; flex-shrink:0">
                {{ row.store_name?.charAt(0) }}
              </el-avatar>
              <div>
                <div class="store-name">{{ row.store_name }}</div>
                <div class="store-user">@{{ row.username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="business_license" label="营业执照" min-width="140" show-overflow-tooltip />
        <el-table-column prop="address" label="经营地址" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light" round>
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reject_reason" label="拒绝原因" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.reject_reason" class="reject-reason-text">{{ row.reject_reason }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button
                size="small"
                type="success"
                :loading="auditingId === row.id"
                @click="audit(row, 'approved')"
              >通过</el-button>
              <el-button
                size="small"
                type="danger"
                plain
                :loading="auditingId === row.id"
                @click="openRejectDialog(row)"
              >拒绝</el-button>
            </template>
            <el-tag v-else size="small" :type="statusTagType(row.status)" effect="plain">已处理</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :total="total"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          @current-change="loadMerchants"
        />
      </div>
    </el-card>

    <!-- Reject Reason Dialog -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝申请" width="440px" align-center>
      <el-form label-width="80px">
        <el-form-item label="店铺名称">
          <span class="dialog-store-name">{{ rejectTarget?.store_name }}</span>
        </el-form-item>
        <el-form-item label="拒绝原因" required>
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="3"
            placeholder="请填写拒绝原因（将通知商家）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="auditingId === rejectTarget?.id" @click="confirmReject">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const merchants = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const statusFilter = ref('')
const searchQuery = ref('')
const auditingId = ref(null)
const summary = ref({ total: 0, pending: 0, approved: 0, rejected: 0 })

// Reject dialog state
const rejectDialogVisible = ref(false)
const rejectTarget = ref(null)
const rejectReason = ref('')

let searchTimer = null

const summaryItems = computed(() => [
  { label: '全部商家', count: summary.value.total, color: '#1890ff', bg: '#e6f4ff' },
  { label: '待审核', count: summary.value.pending, color: '#fa8c16', bg: '#fff7e6' },
  { label: '已通过', count: summary.value.approved, color: '#52c41a', bg: '#f6ffed' },
  { label: '已拒绝', count: summary.value.rejected, color: '#ff4d4f', bg: '#fff2f0' },
])

async function loadMerchants() {
  loading.value = true
  try {
    const res = await adminApi.getMerchantList({
      page: page.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined,
      search: searchQuery.value || undefined,
    })
    const data = res.data || res
    merchants.value = data?.results || []
    total.value = data?.total || 0
    // Build summary from unfiltered counts if available
    if (!statusFilter.value && !searchQuery.value) {
      summary.value.total = data?.total || 0
    }
    // Count from current list when no filter
    const all = data?.results || []
    const pending = all.filter(m => m.status === 'pending').length
    if (!statusFilter.value) {
      summary.value.pending = data?.pending_count ?? pending
      summary.value.approved = data?.approved_count ?? 0
      summary.value.rejected = data?.rejected_count ?? 0
    }
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

async function audit(row, status, reason = '') {
  auditingId.value = row.id
  try {
    const payload = { status }
    if (reason) payload.reject_reason = reason
    await adminApi.auditMerchant(row.id, payload)
    const label = status === 'approved' ? '通过' : '拒绝'
    ElMessage.success(`审核操作成功：${label}`)
    await loadMerchants()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '审核失败')
  } finally {
    auditingId.value = null
  }
}

function openRejectDialog(row) {
  rejectTarget.value = row
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

async function confirmReject() {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请填写拒绝原因')
    return
  }
  await audit(rejectTarget.value, 'rejected', rejectReason.value.trim())
  rejectDialogVisible.value = false
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
.merchant-list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

// ── Summary Chips ─────────────────────────────────────
.status-summary {
  .summary-chip {
    background: var(--chip-bg);
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);

    .chip-count {
      font-size: 22px;
      font-weight: 700;
      color: var(--chip-color);
    }
    .chip-label {
      font-size: 13px;
      color: #888;
    }
  }
}

// ── Main Card ─────────────────────────────────────────
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
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }
}

// ── Table ─────────────────────────────────────────────
.store-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;

  .store-name {
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
  }
  .store-user {
    font-size: 12px;
    color: #999;
  }
}

.reject-reason-text {
  font-size: 12px;
  color: #ff4d4f;
}

.text-muted {
  color: #ccc;
  font-size: 13px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

// ── Dialog ────────────────────────────────────────────
.dialog-store-name {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 14px;
}
</style>
