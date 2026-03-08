<template>
  <div class="book-list-page">
    <!-- Search & Filter -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="10">
          <el-input
            v-model="searchQuery"
            placeholder="搜索书名、作者、ISBN…"
            clearable
            @keyup.enter="search"
          >
            <template #append>
              <el-button @click="search">搜索</el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="8">
          <el-select
            v-model="selectedCategory"
            placeholder="全部分类"
            clearable
            @change="search"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="ordering" placeholder="排序" @change="search">
            <el-option label="最新上架" value="-created_at" />
            <el-option label="销量最高" value="-sales" />
            <el-option label="价格从低到高" value="price" />
            <el-option label="价格从高到低" value="-price" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- Book Grid -->
    <div v-loading="loading" class="book-grid">
      <el-empty v-if="!loading && !books.length" description="暂无图书" />
      <el-row :gutter="20">
        <el-col
          v-for="book in books"
          :key="book.id"
          :xs="12" :sm="8" :md="6" :lg="4"
        >
          <el-card class="book-card" shadow="hover" @click="goDetail(book.id)">
            <div class="book-cover">
              <img
                v-if="book.cover"
                :src="book.cover"
                :alt="book.title"
                class="cover-img"
              />
              <div v-else class="cover-placeholder">📚</div>
            </div>
            <div class="book-info">
              <div class="book-title" :title="book.title">{{ book.title }}</div>
              <div class="book-author">{{ book.author }}</div>
              <div class="book-meta">
                <span class="price">¥{{ book.price }}</span>
                <span class="sales">销量 {{ book.sales }}</span>
              </div>
              <el-button
                type="primary"
                size="small"
                class="cart-btn"
                :disabled="book.stock === 0"
                @click.stop="addToCart(book.id)"
              >
                {{ book.stock === 0 ? '缺货' : '加入购物车' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="fetchBooks"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { bookApi } from '@/api'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()

const books = ref([])
const categories = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const selectedCategory = ref(null)
const ordering = ref('-created_at')

async function fetchBooks(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: ordering.value,
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category = selectedCategory.value
    const res = await bookApi.getList(params)
    books.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await bookApi.getCategories()
    const list = res.data?.results || res.results || res.data || res || []
    // Flatten tree to flat list for select
    const flat = []
    ;(Array.isArray(list) ? list : []).forEach((cat) => {
      flat.push(cat)
      ;(cat.children || []).forEach((child) => flat.push(child))
    })
    categories.value = flat
  } catch {
    // ignore
  }
}

function search() {
  fetchBooks(1)
}

function goDetail(id) {
  router.push(`/books/${id}`)
}

async function addToCart(bookId) {
  await cartStore.addToCart(bookId)
}

onMounted(() => {
  fetchCategories()
  fetchBooks()
})
</script>

<style lang="scss" scoped>
.book-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.book-grid {
  min-height: 200px;
}

.book-card {
  margin-bottom: 24px;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.3s, transform 0.3s;

  &:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-4px);
  }

  :deep(.el-card__body) { padding: 0; }
}

.book-cover {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;

  .cover-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder {
    font-size: 48px;
    color: #ccc;
  }
}

.book-info {
  padding: 14px;

  .book-title {
    font-size: 14px;
    font-weight: 600;
    color: #1A1A1A;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 6px;
    min-height: 40px;
  }

  .book-author {
    font-size: 12px;
    color: #666666;
    margin-bottom: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .book-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    .price {
      font-size: 16px;
      font-weight: 700;
      color: #C75B39;
    }

    .sales {
      font-size: 12px;
      color: #999999;
    }
  }

  .cart-btn {
    width: 100%;
  }
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
