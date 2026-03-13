<template>
  <el-container class="user-layout">
    <!-- Header -->
    <el-header class="header" height="64px">
      <div class="header-inner">
        <!-- Logo -->
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">📚</span>
          <span class="logo-text">知书坊</span>
        </div>

        <!-- Search Bar -->
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名、作者或ISBN..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>

        <!-- Nav Links -->
        <nav class="nav-links">
          <RouterLink to="/" class="nav-link">首页</RouterLink>
          <RouterLink to="/books" class="nav-link">书城</RouterLink>
          <RouterLink to="/cart" class="nav-link">
            购物车
            <el-badge v-if="cartStore.totalCount" :value="cartStore.totalCount" class="cart-badge" />
          </RouterLink>
          <RouterLink to="/orders" class="nav-link">我的订单</RouterLink>
        </nav>

        <!-- User -->
        <div class="user-area">
          <el-dropdown @command="handleCommand">
            <span class="user-trigger">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="addresses">收货地址</el-dropdown-item>
                <el-dropdown-item v-if="authStore.isAdmin" command="admin" divided>管理后台</el-dropdown-item>
                <el-dropdown-item v-if="authStore.isMerchant" command="merchant" divided>商家中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- Main Content -->
    <el-main class="main-content">
      <RouterView />
    </el-main>

    <!-- Footer -->
    <el-footer class="footer" height="auto">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">📚 知书坊</span>
          <p class="footer-desc">发现好书，开启阅读之旅</p>
        </div>
        <div class="footer-links">
          <span>关于我们</span>
          <span>联系我们</span>
          <span>帮助中心</span>
          <span>隐私政策</span>
        </div>
        <p class="footer-copy">© 2024 知书坊 OpenBookShop. All rights reserved.</p>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { ElMessage } from 'element-plus'
import { onMounted } from 'vue'
import { Search, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const searchKeyword = ref('')

onMounted(() => cartStore.fetchCart())

function handleSearch() {
  router.push({ path: '/books', query: searchKeyword.value ? { search: searchKeyword.value } : {} })
}

async function handleCommand(command) {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/auth/login')
  } else if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'addresses') {
    router.push('/addresses')
  } else if (command === 'admin') {
    router.push('/admin')
  } else if (command === 'merchant') {
    router.push('/merchant')
  }
}
</script>

<style lang="scss" scoped>
.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 12% 18%, rgba(206, 232, 208, 0.7) 0%, rgba(206, 232, 208, 0) 34%),
    radial-gradient(circle at 88% 10%, rgba(253, 234, 203, 0.66) 0%, rgba(253, 234, 203, 0) 30%),
    #f6f3ed;
}

.header {
  background: linear-gradient(130deg, rgba(255, 255, 255, 0.92), rgba(249, 246, 241, 0.9));
  border-bottom: 1px solid #d8d3c8;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 26px -22px rgba(41, 45, 30, 0.55);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;

  .logo-icon {
    font-size: 24px;
    filter: saturate(1.2);
  }

  .logo-text {
    font-size: 21px;
    font-weight: 700;
    color: #1f3b2a;
    letter-spacing: 1px;
    white-space: nowrap;
    font-family: 'STZhongsong', 'KaiTi', serif;
  }
}

.search-bar {
  flex: 1;
  max-width: 520px;

  .search-input {
    :deep(.el-input-group__append),
    :deep(.el-input-group__prepend) {
      border-color: #c8d3c8;
    }

    :deep(.el-input-group__append) {
      background: linear-gradient(140deg, #2f6b46, #21553a);
      color: #fff;
      border-color: #21553a;
      cursor: pointer;

      &:hover { background: linear-gradient(140deg, #3a7f54, #2a6846); }

      button {
        color: #fff;
        border: none;
        background: transparent;
      }
    }

    :deep(.el-input__wrapper) {
      border: 1px solid #c8d3c8;
      box-shadow: none;
      background: rgba(255, 255, 255, 0.85);

      &.is-focus {
        border-color: #2f6b46;
      }

      &:hover { border-color: #7ba587; }
    }
  }
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;

  .nav-link {
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 14px;
    color: #485946;
    text-decoration: none;
    transition: color 0.25s, background 0.25s, transform 0.25s;
    white-space: nowrap;
    position: relative;
    font-weight: 500;

    &:hover {
      color: #1f3b2a;
      background: #e4efdf;
      transform: translateY(-1px);
    }

    &.router-link-active {
      color: #12311f;
      font-weight: 600;
      background: linear-gradient(120deg, #d7e9d2, #e8f4e5);
    }

    .cart-badge {
      margin-left: 4px;
      vertical-align: middle;
    }
  }
}

.user-area {
  flex-shrink: 0;

  .user-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #344436;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #d6ddd0;
    transition: background 0.22s, border-color 0.22s;
    background: rgba(255, 255, 255, 0.72);

    &:hover {
      background: #f3f7ef;
      color: #1f3b2a;
      border-color: #b7cab5;
    }

    .username {
      font-size: 14px;
      max-width: 100px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }
}

.main-content {
  flex: 1;
  padding: 28px 20px 36px;
}

.footer {
  background: linear-gradient(120deg, #22342a, #18241d);
  color: #cfd9cc;
  padding: 32px 24px 24px;
  border-top: 1px solid rgba(197, 216, 200, 0.26);

  .footer-inner {
    max-width: 1280px;
    margin: 0 auto;
    text-align: center;
  }

  .footer-logo {
    font-size: 20px;
    font-weight: 700;
    color: #f3fbf0;
  }

  .footer-desc {
    font-size: 13px;
    color: #93aa96;
    margin: 8px 0 20px;
  }

  .footer-links {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-bottom: 16px;

    span {
      font-size: 13px;
      cursor: pointer;
      transition: color 0.2s;

      &:hover { color: #f7fff5; }
    }
  }

  .footer-copy {
    font-size: 12px;
    color: #708474;
    margin: 0;
  }
}

@media (max-width: 980px) {
  .header-inner {
    gap: 12px;
    padding: 0 14px;
  }

  .search-bar {
    max-width: none;
  }

  .nav-links {
    display: none;
  }

  .main-content {
    padding: 22px 12px 28px;
  }
}

@media (max-width: 680px) {
  .logo .logo-text {
    display: none;
  }

  .footer .footer-links {
    gap: 14px;
    flex-wrap: wrap;
  }
}
</style>

