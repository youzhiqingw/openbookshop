<template>
  <div class="review-moderation-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>评论审核</span>
          <div class="filters">
            <el-select v-model="filterApproved" placeholder="审核状态" clearable style="width: 140px;" @change="fetchList">
              <el-option label="全部" value="" />
              <el-option label="待审核" value="false" />
              <el-option label="已通过" value="true" />
            </el-select>
            <el-select v-model="filterSensitive" placeholder="敏感词" clearable style="width: 140px; margin-left: 8px;" @change="fetchList">
              <el-option label="全部" value="" />
              <el-option label="含敏感词" value="true" />
              <el-option label="无敏感词" value="false" />
            </el-select>
            <el-input
              v-model="searchText"
              placeholder="搜索用户/书名/内容"
              clearable
              style="width: 200px; margin-left: 8px;"
              @keyup.enter="fetchList"
              @clear="fetchList"
            >
              <template #suffix>
                <el-icon @click="fetchList" style="cursor: pointer;"><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="book_title" label="图书" min-width="130" show-overflow-tooltip />
        <el-table-column prop="username" label="用户" width="90" />
        <el-table-column label="评分" width="80">
          <template #default="{ row }">
            <el-rate :model-value="row.rating" disabled show-score size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评论内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_sensitive" type="danger" size="small" style="margin-right: 4px;">含敏感词</el-tag>
            <el-tag :type="row.is_approved ? 'success' : 'warning'" size="small">
              {{ row.is_approved ? '已通过' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="150">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_approved"
              type="success" size="small"
              @click="handleApprove(row, 'approve')"
            >通过</el-button>
            <el-button
              v-if="row.is_approved"
              type="danger" size="small"
              @click="handleApprove(row, 'reject')"
            >驳回</el-button>
          </template>
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
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterApproved = ref('false')
const filterSensitive = ref('')
const searchText = ref('')

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterApproved.value !== '') params.is_approved = filterApproved.value
    if (filterSensitive.value !== '') params.is_sensitive = filterSensitive.value
    if (searchText.value) params.search = searchText.value
    const res = await adminApi.getReviewList(params)
    const data = res.data.data
    list.value = data.results
    total.value = data.total
  } catch {
    ElMessage.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

async function handleApprove(row, action) {
  try {
    await adminApi.approveReview(row.id, { action })
    ElMessage.success(action === 'approve' ? '已通过' : '已驳回')
    fetchList()
  } catch {
    ElMessage.error('操作失败')
  }
}

function formatDate(dt) {
  if (!dt) return '-'
  return new Date(dt).toLocaleString('zh-CN', { hour12: false })
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
.review-moderation-view {}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
