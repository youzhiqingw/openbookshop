<template>
  <div class="home-page">
    <!-- Hero Banner -->
    <div class="hero-banner">
      <div class="hero-content">
        <h1 class="hero-title">发现好书，开启阅读之旅</h1>
        <p class="hero-sub">知书坊汇聚海量优质图书，为您提供最佳阅读体验</p>
        <el-button type="primary" size="large" @click="router.push('/books')" class="hero-btn">
          立即探索 →
        </el-button>
      </div>
    </div>

    <!-- Category Section -->
    <div class="section">
      <div class="section-header">
        <h2>分类导航</h2>
      </div>
      <div class="category-grid">
        <div v-for="cat in categories" :key="cat.id" class="category-card" @click="goCategory(cat.id)">
          <div class="cat-icon">{{ getCatEmoji(cat.name) }}</div>
          <span>{{ cat.name }}</span>
        </div>
      </div>
    </div>

    <!-- New Books Section -->
    <div class="section">
      <div class="section-header">
        <h2>新书上架</h2>
        <RouterLink to="/books" class="see-more">查看更多 →</RouterLink>
      </div>
      <div v-loading="loading" class="book-grid">
        <div v-for="book in newBooks" :key="book.id" class="book-card" @click="router.push(`/books/${book.id}`)">
          <div class="book-cover">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" />
            <div v-else class="cover-placeholder">📚</div>
            <span class="new-badge">新书</span>
          </div>
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">{{ book.author }}</p>
            <div class="book-footer">
              <span class="price">¥{{ book.price }}</span>
              <el-button size="small" type="primary" @click.stop="addToCart(book.id)">
                加入购物车
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hot Books Section -->
    <div class="section">
      <div class="section-header">
        <h2>热门推荐</h2>
        <RouterLink to="/books?ordering=-sales" class="see-more">查看更多 →</RouterLink>
      </div>
      <div v-loading="loadingHot" class="book-grid">
        <div v-for="book in hotBooks" :key="book.id" class="book-card" @click="router.push(`/books/${book.id}`)">
          <div class="book-cover">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" />
            <div v-else class="cover-placeholder">📚</div>
          </div>
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">{{ book.author }}</p>
            <div class="book-footer">
              <span class="price">¥{{ book.price }}</span>
              <el-button size="small" type="primary" @click.stop="addToCart(book.id)">
                加入购物车
              </el-button>
            </div>
          </div>
        </div>
      </div>
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

const categories = ref([])
const newBooks = ref([])
const hotBooks = ref([])
const loading = ref(false)
const loadingHot = ref(false)

function getCatEmoji(name) {
  const map = { '文学': '📖', '小说': '📝', '科技': '🔬', '历史': '📜', '艺术': '🎨', '经管': '💼', '教育': '🎓', '科幻': '🚀', '生活': '🌿', '儿童': '🧸' }
  for (const [key, emoji] of Object.entries(map)) {
    if (name.includes(key)) return emoji
  }
  return '📚'
}

function goCategory(id) {
  router.push({ path: '/books', query: { category: id } })
}

async function addToCart(bookId) {
  await cartStore.addToCart(bookId)
}

async function fetchData() {
  try {
    const catRes = await bookApi.getCategories()
    const catList = catRes.data?.results || catRes.results || catRes.data || catRes || []
    const flat = []
    ;(Array.isArray(catList) ? catList : []).forEach((cat) => {
      flat.push(cat)
      ;(cat.children || []).forEach((child) => flat.push(child))
    })
    categories.value = flat.slice(0, 8)
  } catch {}

  loading.value = true
  try {
    const res = await bookApi.getList({ page: 1, page_size: 10, ordering: '-created_at' })
    newBooks.value = res.data?.results || res.results || []
  } finally {
    loading.value = false
  }

  loadingHot.value = true
  try {
    const res = await bookApi.getList({ page: 1, page_size: 10, ordering: '-sales' })
    hotBooks.value = res.data?.results || res.results || []
  } finally {
    loadingHot.value = false
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.hero-banner {
  background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 60%, #3b82f6 100%);
  border-radius: 16px;
  padding: 60px 48px;
  margin-bottom: 40px;
  color: white;

  .hero-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 16px;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
  }

  .hero-sub {
    font-size: 16px;
    opacity: 0.9;
    margin-bottom: 28px;
  }

  .hero-btn {
    font-size: 16px;
    padding: 12px 32px;
    background: white;
    color: #1e40af;
    border: none;
    font-weight: 600;

    &:hover {
      background: #f0f9ff;
    }
  }
}

.section {
  margin-bottom: 48px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      font-size: 22px;
      font-weight: 700;
      color: #1a1a1a;
      margin: 0;
    }

    .see-more {
      color: #1e40af;
      text-decoration: none;
      font-size: 14px;

      &:hover { text-decoration: underline; }
    }
  }
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(4, 1fr);
  }
}

.category-card {
  background: white;
  border-radius: 12px;
  padding: 20px 12px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;

  &:hover {
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    transform: translateY(-4px);
  }

  .cat-icon {
    font-size: 32px;
    width: 56px;
    height: 56px;
    background: #eff6ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  span {
    font-size: 13px;
    color: #374151;
  }
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  min-height: 100px;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(4, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.book-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    transform: translateY(-4px);
  }

  .book-cover {
    position: relative;
    height: 180px;
    background: #f3f4f6;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .cover-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      color: #ccc;
    }

    .new-badge {
      position: absolute;
      top: 8px;
      right: 8px;
      background: #ef4444;
      color: white;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
    }
  }

  .book-info {
    padding: 14px;

    .book-title {
      font-size: 14px;
      font-weight: 600;
      color: #1a1a1a;
      margin: 0 0 6px;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      min-height: 40px;
    }

    .book-author {
      font-size: 12px;
      color: #6b7280;
      margin: 0 0 10px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    .book-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .price {
        font-size: 16px;
        font-weight: 700;
        color: #1e40af;
      }
    }
  }
}
</style>
