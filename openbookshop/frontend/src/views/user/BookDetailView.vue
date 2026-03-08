<template>
  <div v-loading="loading" class="book-detail-page">
    <el-button class="back-btn" @click="router.back()">← 返回</el-button>

    <template v-if="book">
      <el-row :gutter="40">
        <!-- Cover -->
        <el-col :span="8">
          <div class="cover-wrap">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" class="cover-img" />
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
    </template>

    <el-empty v-else-if="!loading" description="图书不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { bookApi } from '@/api'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const book = ref(null)
const loading = ref(false)
const quantity = ref(1)

async function fetchBook() {
  loading.value = true
  try {
    const res = await bookApi.getDetail(route.params.id)
    book.value = res.data || res
  } catch {
    book.value = null
  } finally {
    loading.value = false
  }
}

async function addToCart() {
  await cartStore.addToCart(book.value.id, quantity.value)
}

async function buyNow() {
  await cartStore.addToCart(book.value.id, quantity.value)
  router.push('/cart')
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
    color: #e6a23c;
  }

  .stock-info {
    color: #67c23a;
    font-size: 14px;
    &.out { color: #f56c6c; }
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
</style>
