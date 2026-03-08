<template>
  <div v-loading="loading" class="book-detail-page">
    <div class="back-bar">
      <el-button text @click="router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回书城
      </el-button>
    </div>

    <template v-if="book">
      <div class="detail-container">
        <el-row :gutter="40">
          <!-- Cover -->
          <el-col :xs="24" :sm="8">
            <div class="cover-wrap">
              <img v-if="book.cover" :src="book.cover" :alt="book.title" class="cover-img" />
              <div v-else class="cover-placeholder">📚</div>
            </div>
          </el-col>

          <!-- Info -->
          <el-col :xs="24" :sm="16">
            <div class="book-info-panel">
              <div class="book-category" v-if="book.category_name">
                <el-tag type="" class="category-tag">{{ book.category_name }}</el-tag>
              </div>
              <h1 class="book-title">{{ book.title }}</h1>
              <div class="book-author-row">
                <span class="author-label">作者：</span>
                <span class="author-name">{{ book.author }}</span>
              </div>

              <div class="book-attrs">
                <div v-if="book.publisher" class="attr-item">
                  <span class="attr-label">出版社</span>
                  <span class="attr-value">{{ book.publisher }}</span>
                </div>
                <div v-if="book.publish_date" class="attr-item">
                  <span class="attr-label">出版日期</span>
                  <span class="attr-value">{{ book.publish_date }}</span>
                </div>
                <div v-if="book.isbn" class="attr-item">
                  <span class="attr-label">ISBN</span>
                  <span class="attr-value">{{ book.isbn }}</span>
                </div>
                <div class="attr-item">
                  <span class="attr-label">销量</span>
                  <span class="attr-value">{{ book.sales }} 册</span>
                </div>
                <div class="attr-item">
                  <span class="attr-label">商家</span>
                  <span class="attr-value">{{ book.merchant_name }}</span>
                </div>
              </div>

              <div class="price-section">
                <span class="price">¥{{ book.price }}</span>
                <span :class="['stock-badge', { 'out': book.stock === 0 }]">
                  {{ book.stock === 0 ? '缺货' : `库存 ${book.stock} 件` }}
                </span>
              </div>

              <div class="quantity-row">
                <span class="qty-label">数量：</span>
                <el-input-number v-model="quantity" :min="1" :max="book.stock" :disabled="book.stock === 0" />
              </div>

              <div class="action-row">
                <el-button
                  type="primary"
                  size="large"
                  class="btn-cart"
                  :disabled="book.stock === 0"
                  @click="addToCart"
                >
                  <el-icon><ShoppingCart /></el-icon>
                  加入购物车
                </el-button>
                <el-button
                  size="large"
                  class="btn-buy"
                  :disabled="book.stock === 0"
                  @click="buyNow"
                >
                  立即购买
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Description -->
      <el-card v-if="book.description" class="desc-card">
        <template #header>
          <span class="section-title">图书简介</span>
        </template>
        <p class="description">{{ book.description }}</p>
      </el-card>

      <!-- Reviews -->
      <el-card class="reviews-card">
        <template #header>
          <div class="reviews-header">
            <span class="section-title">读者评论（{{ total }}条）</span>
            <el-button
              v-if="authStore.isLoggedIn && !authStore.isAdmin && !authStore.isMerchant"
              type="primary"
              size="small"
              @click="openReviewDialog"
            >✏️ 写评论</el-button>
          </div>
        </template>

        <div v-if="reviews.length === 0" class="no-reviews">
          <el-empty description="暂无评论，快来写第一条评论吧" />
        </div>
        <div v-else>
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-top">
              <el-avatar :size="32" icon="UserFilled" class="reviewer-avatar" />
              <div class="reviewer-info">
                <span class="reviewer">{{ review.username }}</span>
                <el-rate :model-value="review.rating" disabled show-score size="small" />
              </div>
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
        <el-button type="primary" :loading="submittingReview" @click="submitReview">提交评论</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, ArrowLeft, ShoppingCart } from '@element-plus/icons-vue'
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

.back-bar {
  margin-bottom: 16px;

  .el-button {
    color: #666;
    font-size: 14px;
    &:hover { color: #2C5F2D; }
  }
}

.detail-container {
  background: #fff;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.cover-wrap {
  width: 100%;
  background: #F5F5F5;
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

.book-info-panel {
  .book-category {
    margin-bottom: 12px;

    .category-tag {
      background: #E8F5E9;
      color: #2C5F2D;
      border-color: #E8F5E9;
    }
  }

  .book-title {
    font-size: 24px;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1.3;
    margin-bottom: 12px;
  }

  .book-author-row {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    font-size: 14px;

    .author-label { color: #999; }
    .author-name { color: #333; font-weight: 500; }
  }

  .book-attrs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 16px;
    margin-bottom: 24px;
    padding: 16px;
    background: #F9FAFB;
    border-radius: 6px;

    .attr-item {
      display: flex;
      gap: 8px;
      font-size: 13px;

      .attr-label {
        color: #999;
        white-space: nowrap;
        min-width: 52px;
      }
      .attr-value { color: #333; }
    }
  }

  .price-section {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    .price {
      font-size: 32px;
      font-weight: 700;
      color: #C75B39;
    }

    .stock-badge {
      background: #E8F5E9;
      color: #2C5F2D;
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 500;

      &.out {
        background: #FFF2F2;
        color: #F5222D;
      }
    }
  }

  .quantity-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;

    .qty-label { font-size: 14px; color: #666; }
  }

  .action-row {
    display: flex;
    gap: 12px;

    .btn-cart {
      flex: 1;
      background: #2C5F2D;
      border-color: #2C5F2D;
      &:hover:not(:disabled) { background: #4A7C4B; border-color: #4A7C4B; }
    }

    .btn-buy {
      flex: 1;
      background: #FBE9E7;
      color: #C75B39;
      border-color: #C75B39;
      &:hover:not(:disabled) {
        background: #C75B39;
        color: #fff;
      }
    }
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1A1A1A;
}

.desc-card {
  margin-bottom: 24px;
  border-radius: 8px;

  .description {
    line-height: 1.8;
    color: #555;
    white-space: pre-line;
    font-size: 14px;
  }
}

.reviews-card {
  border-radius: 8px;

  .reviews-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .review-item {
    padding: 20px 0;
    border-bottom: 1px solid #F5F5F5;

    &:last-child { border-bottom: none; }

    .review-top {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;

      .reviewer-avatar { flex-shrink: 0; }

      .reviewer-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;

        .reviewer {
          font-weight: 600;
          color: #1A1A1A;
          font-size: 14px;
        }
      }

      .review-date { color: #999; font-size: 12px; }
    }

    .review-content {
      color: #555;
      line-height: 1.7;
      margin: 0 0 10px;
      font-size: 14px;
      padding-left: 42px;
    }

    .merchant-reply {
      background: #F5F5F5;
      padding: 10px 14px;
      border-radius: 4px;
      font-size: 13px;
      color: #606266;
      display: flex;
      align-items: flex-start;
      gap: 6px;
      margin-left: 42px;
      border-left: 3px solid #2C5F2D;

      .reply-label { font-weight: 600; white-space: nowrap; color: #2C5F2D; }
    }
  }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: center;
  }
}
</style>
