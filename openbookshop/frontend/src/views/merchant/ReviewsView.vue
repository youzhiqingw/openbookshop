<template>
  <div class="merchant-reviews-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>图书评论</span>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="book_title" label="图书" min-width="130" show-overflow-tooltip />
        <el-table-column prop="username" label="用户" width="90" />
        <el-table-column label="评分" width="140">
          <template #default="{ row }">
            <el-rate :model-value="row.rating" disabled show-score size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评论内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="我的回复" min-width="160">
          <template #default="{ row }">
            <span v-if="row.merchant_reply" class="reply-text">{{ row.merchant_reply }}</span>
            <el-tag v-else type="info" size="small">未回复</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openReplyDialog(row)">
              {{ row.merchant_reply ? '修改回复' : '回复' }}
            </el-button>
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

    <!-- 回复对话框 -->
    <el-dialog v-model="dialogVisible" title="回复评论" width="500px">
      <div class="review-preview" v-if="currentReview">
        <p><strong>书名：</strong>{{ currentReview.book_title }}</p>
        <p><strong>用户：</strong>{{ currentReview.username }}</p>
        <p><strong>评分：</strong><el-rate :model-value="currentReview.rating" disabled show-score size="small" /></p>
        <p><strong>内容：</strong>{{ currentReview.content }}</p>
      </div>
      <el-divider />
      <el-form>
        <el-form-item label="回复内容">
          <el-input
            v-model="replyText"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容（5-500字）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { merchantApi } from '@/api'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const currentReview = ref(null)
const replyText = ref('')
const submitting = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await merchantApi.getReviewList(params)
    const data = res.data.data
    list.value = data.results
    total.value = data.total
  } catch {
    ElMessage.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

function openReplyDialog(review) {
  currentReview.value = review
  replyText.value = review.merchant_reply || ''
  dialogVisible.value = true
}

async function submitReply() {
  if (!replyText.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  submitting.value = true
  try {
    await merchantApi.replyReview(currentReview.value.id, { merchant_reply: replyText.value })
    ElMessage.success('回复成功')
    dialogVisible.value = false
    fetchList()
  } catch {
    ElMessage.error('回复失败')
  } finally {
    submitting.value = false
  }
}

function formatDate(dt) {
  if (!dt) return '-'
  return new Date(dt).toLocaleString('zh-CN', { hour12: false })
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
.merchant-reviews-view {}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.reply-text {
  color: #606266;
  font-size: 13px;
}
.review-preview {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  p { margin: 6px 0; font-size: 14px; }
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
