<template>
  <div v-loading="loading" class="book-detail-page">
    <el-button class="back-btn" @click="router.back()">← 返回</el-button>

    <template v-if="book">
      <el-row :gutter="40">
        <!-- Cover -->
        <el-col :span="8">
          <div class="cover-wrap">
            <img v-if="book.cover_url || book.cover" :src="book.cover_url || book.cover" :alt="book.title" class="cover-img" @error="(e) => (e.target.style.display = 'none')" />
            <div v-else class="cover-placeholder">📚</div>
          </div>
        </el-col>

        <!-- Info -->
        <el-col :span="16">
          <h1 class="book-title">{{ book.title }}</h1>
          <div class="book-meta">
            <el-tag v-if="book.category_name">{{ book.category_name }}</el-tag>
            <span class="author">作者：{{ book.author }}</span>
          </div>
          <el-descriptions :column="2" border class="book-desc">
            <el-descriptions-item v-if="book.publisher" label="出版社">{{ book.publisher }}</el-descriptions-item>
            <el-descriptions-item v-if="book.publish_date" label="出版日期">{{ book.publish_date }}</el-descriptions-item>
            <el-descriptions-item v-if="book.isbn" label="ISBN">{{ book.isbn }}</el-descriptions-item>
            <el-descriptions-item label="销量">{{ book.sales }}</el-descriptions-item>
            <el-descriptions-item label="商家">{{ book.merchant_name }}</el-descriptions-item>
          </el-descriptions>

          <div class="price-row">
            <span class="price">¥{{ book.price }}</span>
            <span :class="['stock-info', { 'out': book.stock === 0 }]">
              {{ book.stock === 0 ? '缺货' : `库存 ${book.stock} 件` }}
            </span>
          </div>

          <div class="quantity-row">
            <span>数量：</span>
            <el-input-number v-model="quantity" :min="1" :max="book.stock" :disabled="book.stock === 0" />
          </div>

          <div class="action-row">
            <el-button
              type="primary"
              size="large"
              :disabled="book.stock === 0"
              @click="addToCart"
            >
              加入购物车
            </el-button>
            <el-button
              type="warning"
              size="large"
              :disabled="book.stock === 0"
              @click="buyNow"
            >
              立即购买
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Description -->
      <el-card v-if="book.description" class="desc-card">
        <template #header>图书简介</template>
        <p class="description">{{ book.description }}</p>
      </el-card>

      <!-- Reviews -->
      <el-card class="reviews-card">
        <template #header>
          <div class="reviews-header">
            <span>读者评论（{{ total }}条）</span>
            <el-button
              v-if="authStore.isLoggedIn && !authStore.isAdmin && !authStore.isMerchant"
              type="primary"
              size="small"
              @click="openReviewDialog"
            >写评论</el-button>
          </div>
        </template>

        <div v-if="reviews.length === 0" class="no-reviews">
          <el-empty description="暂无评论" />
        </div>
        <div v-else>
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-top">
              <span class="reviewer">{{ review.username }}</span>
              <el-rate :model-value="review.rating" disabled show-score size="small" />
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
            </div>
            <p class="review-content">{{ review.content }}</p>
            <div v-if="review.merchant_reply" class="merchant-reply">
              <el-icon><ChatDotRound /></el-icon>
              <span class="reply-label">商家回复：</span>
              <span>{{ review.merchant_reply }}</span>
            </div>
          </div>
        </div>

        <div class="pagination" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="reviewPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="fetchReviews"
          />
        </div>
      </el-card>
    </template>

    <!-- Review Dialog -->
    <el-dialog v-model="reviewDialogVisible" title="写评论" width="500px">
      <el-form label-width="80px">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.rating" show-text />
        </el-form-item>
        <el-form-item label="评论内容">
          <el-input
            v-model="reviewForm.content"
            type="textarea"
            :rows="5"
            placeholder="请分享您的阅读体验（至少5个字）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingReview" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import { bookApi } from '@/api'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const book = ref(null)
const loading = ref(false)
const quantity = ref(1)

// Reviews
const reviews = ref([])
const reviewPage = ref(1)
const pageSize = 5
const total = ref(0)
const reviewDialogVisible = ref(false)
const submittingReview = ref(false)
const reviewForm = ref({ rating: 5, content: '' })

async function fetchBook() {
  loading.value = true
  try {
    const res = await bookApi.getDetail(route.params.id)
    book.value = res.data || res
    fetchReviews()
  } catch {
    book.value = null
  } finally {
    loading.value = false
  }
}

async function fetchReviews() {
  try {
    const res = await bookApi.getReviews(route.params.id, { page: reviewPage.value, page_size: pageSize })
    const data = res.data
    reviews.value = data.results
    total.value = data.total
  } catch {
    // silent
  }
}

function openReviewDialog() {
  reviewForm.value = { rating: 5, content: '' }
  reviewDialogVisible.value = true
}

async function submitReview() {
  if (!reviewForm.value.content || reviewForm.value.content.length < 5) {
    ElMessage.warning('评论内容至少5个字')
    return
  }
  submittingReview.value = true
  try {
    await bookApi.createReview(route.params.id, reviewForm.value)
    ElMessage.success('评论提交成功')
    reviewDialogVisible.value = false
    fetchReviews()
  } catch (err) {
    const msg = err.response?.data?.message || '提交失败，请确认已购买此书'
    ElMessage.error(msg)
  } finally {
    submittingReview.value = false
  }
}

async function addToCart() {
  await cartStore.addToCart(book.value.id, quantity.value)
}

async function buyNow() {
  await cartStore.addToCart(book.value.id, quantity.value)
  router.push('/cart')
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('zh-CN')
}

onMounted(fetchBook)
</script>

<style lang="scss" scoped>
.book-detail-page {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}

.back-btn {
  margin-bottom: 20px;
}

.cover-wrap {
  width: 100%;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;

  .cover-img {
    width: 100%;
    object-fit: contain;
    max-height: 400px;
  }

  .cover-placeholder {
    font-size: 80px;
    color: #ddd;
  }
}

.book-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 12px;
}

.book-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;

  .author { color: #666; }
}

.book-desc {
  margin-bottom: 20px;
}

.price-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;

  .price {
    font-size: 28px;
    font-weight: bold;
    color: #C75B39;
  }

  .stock-info {
    color: #52C41A;
    font-size: 14px;
    &.out { color: #F5222D; }
  }
}

.quantity-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.action-row {
  display: flex;
  gap: 12px;
}

.desc-card {
  margin-top: 30px;

  .description {
    line-height: 1.8;
    color: #555;
    white-space: pre-line;
  }
}

.reviews-card {
  margin-top: 24px;

  .reviews-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .review-item {
    padding: 16px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child { border-bottom: none; }

    .review-top {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .reviewer { font-weight: bold; color: #303133; }
      .review-date { color: #909399; font-size: 12px; margin-left: auto; }
    }

    .review-content {
      color: #555;
      line-height: 1.6;
      margin: 0 0 8px;
    }

    .merchant-reply {
      background: #f5f7fa;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 13px;
      color: #606266;
      display: flex;
      align-items: flex-start;
      gap: 6px;

      .reply-label { font-weight: bold; white-space: nowrap; }
    }
  }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: center;
  }
}
</style>
