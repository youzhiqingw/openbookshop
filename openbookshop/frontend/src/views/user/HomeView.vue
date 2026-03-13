<template>
  <div class="home-page">
    <div class="hero-banner">
      <div class="hero-grid">
        <div class="hero-content">
          <p class="hero-kicker">OPENBOOKSHOP</p>
          <h1 class="hero-title">发现好书，开启阅读之旅</h1>
          <p class="hero-sub">知书坊汇聚海量优质图书，在一屏之内帮你完成发现、筛选与购买。</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="router.push('/books')" class="hero-btn primary">
              立即探索
            </el-button>
            <el-button plain size="large" @click="router.push('/orders')" class="hero-btn ghost">
              查看订单
            </el-button>
          </div>
        </div>
        <div class="hero-panel">
          <div class="metric-card">
            <span class="label">精选分类</span>
            <strong>{{ categories.length || 8 }}</strong>
          </div>
          <div class="metric-card warm">
            <span class="label">新书上架</span>
            <strong>{{ newBooks.length || 10 }}</strong>
          </div>
          <div class="metric-card cool">
            <span class="label">热门推荐</span>
            <strong>{{ hotBooks.length || 10 }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>分类导航</h2>
        <RouterLink to="/books" class="see-more">进入书城</RouterLink>
      </div>
      <div class="category-grid">
        <div v-for="cat in categories" :key="cat.id" class="category-card" @click="goCategory(cat.id)">
          <div class="cat-icon">{{ getCatEmoji(cat.name) }}</div>
          <span>{{ cat.name }}</span>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>新书上架</h2>
        <RouterLink to="/books" class="see-more">查看更多</RouterLink>
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

    <div class="section">
      <div class="section-header">
        <h2>热门推荐</h2>
        <RouterLink to="/books?ordering=-sales" class="see-more">查看更多</RouterLink>
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
  padding: 0 12px 40px;
}

.hero-banner {
  background:
    radial-gradient(circle at 76% 20%, rgba(242, 255, 238, 0.25) 0%, rgba(242, 255, 238, 0) 36%),
    radial-gradient(circle at 20% 76%, rgba(255, 236, 207, 0.25) 0%, rgba(255, 236, 207, 0) 48%),
    linear-gradient(136deg, #17422f 0%, #25563e 58%, #2f6f4a 100%);
  border-radius: 28px;
  padding: 34px;
  margin-bottom: 40px;
  color: white;
  box-shadow: 0 28px 42px -36px rgba(25, 44, 31, 0.95);
  overflow: hidden;

  .hero-grid {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    gap: 24px;
    align-items: center;
  }

  .hero-content {
    max-width: 620px;
  }

  .hero-kicker {
    font-size: 12px;
    letter-spacing: 2px;
    opacity: 0.88;
    margin-bottom: 10px;
  }

  .hero-title {
    font-size: 42px;
    font-weight: 700;
    line-height: 1.16;
    margin-bottom: 14px;
    text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.28);
    font-family: 'STZhongsong', 'KaiTi', serif;
  }

  .hero-sub {
    font-size: 16px;
    opacity: 0.92;
    margin-bottom: 26px;
    line-height: 1.75;
  }

  .hero-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .hero-btn {
    min-width: 116px;
  }

  .hero-btn.primary {
    border: none;
    color: #18402d;
    background: #f1f8ea;
    font-weight: 700;

    &:hover {
      color: #113323;
      background: #ffffff;
    }
  }

  .hero-btn.ghost {
    color: #ebf7e8;
    border-color: rgba(238, 252, 231, 0.64);
    background: transparent;

    &:hover {
      color: #163f2d;
      background: #f2faed;
      border-color: #f2faed;
    }
  }

  .hero-panel {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .metric-card {
    border: 1px solid rgba(216, 238, 210, 0.32);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(3px);
    border-radius: 16px;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .label {
      font-size: 13px;
      opacity: 0.92;
    }

    strong {
      font-size: 30px;
      font-family: Georgia, 'Times New Roman', serif;
      line-height: 1;
    }
  }

  .metric-card.warm {
    background: rgba(255, 230, 199, 0.2);
  }

  .metric-card.cool {
    background: rgba(204, 246, 232, 0.18);
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
      color: #1f3227;
      margin: 0;
      font-family: 'STZhongsong', 'KaiTi', serif;
    }

    .see-more {
      color: #2c5f2d;
      text-decoration: none;
      font-size: 14px;
      border-bottom: 1px dashed #9dbc96;
      padding-bottom: 1px;

      &:hover {
        color: #1f4923;
        border-bottom-color: #2c5f2d;
      }
    }
  }
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(6, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: repeat(4, 1fr);
  }

  @media (max-width: 520px) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.category-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 14px;
  padding: 20px 12px;
  text-align: center;
  cursor: pointer;
  border: 1px solid #e8ede1;
  box-shadow: 0 18px 24px -28px rgba(24, 31, 18, 0.7);
  transition: all 0.26s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;

  &:hover {
    box-shadow: 0 20px 34px -26px rgba(39, 56, 35, 0.7);
    transform: translateY(-5px);
    border-color: #cbd9c2;
  }

  .cat-icon {
    font-size: 28px;
    width: 56px;
    height: 56px;
    background: #eaf3e6;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  span {
    font-size: 13px;
    color: #344739;
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
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #e5ebdf;
  box-shadow: 0 18px 30px -30px rgba(33, 45, 28, 0.85);
  cursor: pointer;
  transition: all 0.28s;

  &:hover {
    box-shadow: 0 30px 42px -32px rgba(24, 36, 20, 0.82);
    transform: translateY(-6px);
    border-color: #c8d8c0;
  }

  .book-cover {
    position: relative;
    height: 180px;
    background: linear-gradient(140deg, #e9efe7, #f4f8f3);
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s;
    }

    .new-badge {
      position: absolute;
      top: 10px;
      right: 10px;
      background: linear-gradient(120deg, #cb5c3f, #e38658);
      color: white;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 999px;
      box-shadow: 0 8px 14px -8px rgba(138, 49, 28, 0.95);
    }

    .cover-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      color: #aec2b1;
    }
  }

  &:hover .book-cover img {
    transform: scale(1.04);
  }

  .book-info {
    padding: 14px;

    .book-title {
      font-size: 14px;
      font-weight: 600;
      color: #1d2d22;
      margin: 0 0 6px;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      min-height: 40px;
    }

    .book-author {
      font-size: 12px;
      color: #667667;
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
        color: #2a5935;
      }

      :deep(.el-button) {
        border-radius: 999px;
        border: none;
        background: linear-gradient(130deg, #2d6a45, #1f4f35);
      }
    }
  }
}

@media (max-width: 980px) {
  .hero-banner {
    padding: 24px;

    .hero-grid {
      grid-template-columns: 1fr;
      gap: 18px;
    }

    .hero-title {
      font-size: 34px;
    }
  }
}

@media (max-width: 680px) {
  .hero-banner {
    border-radius: 22px;

    .hero-title {
      font-size: 30px;
    }
  }
}
</style>
