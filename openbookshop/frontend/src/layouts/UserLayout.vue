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
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { ElMessage } from 'element-plus'
import { onMounted } from 'vue'
import { Search, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
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
  background: #f8fafc;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex-shrink: 0;

  .logo-icon { font-size: 24px; }

  .logo-text {
    font-size: 20px;
    font-weight: 700;
    color: #1e40af;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }
}

.search-bar {
  flex: 1;
  max-width: 480px;

  .search-input {
    :deep(.el-input-group__append) {
      background: #1e40af;
      color: #fff;
      border-color: #1e40af;
      cursor: pointer;

      &:hover { background: #1e3a8a; }

      button {
        color: #fff;
        border: none;
        background: transparent;
      }
    }

    :deep(.el-input__wrapper) {
      border-color: #dbeafe;

      &:hover { border-color: #3b82f6; }
    }
  }
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;

  .nav-link {
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 14px;
    color: #374151;
    text-decoration: none;
    transition: color 0.2s, background 0.2s;
    white-space: nowrap;
    position: relative;

    &:hover {
      color: #1e40af;
      background: #eff6ff;
    }

    &.router-link-active {
      color: #1e40af;
      font-weight: 600;
      background: #eff6ff;
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
    color: #374151;
    padding: 4px 8px;
    border-radius: 8px;
    transition: background 0.2s;

    &:hover {
      background: #f3f4f6;
      color: #1e40af;
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
  padding: 24px;
}

.footer {
  background: #1e3a8a;
  color: #cbd5e1;
  padding: 32px 24px 24px;

  .footer-inner {
    max-width: 1280px;
    margin: 0 auto;
    text-align: center;
  }

  .footer-logo {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
  }

  .footer-desc {
    font-size: 13px;
    color: #94a3b8;
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

      &:hover { color: #fff; }
    }
  }

  .footer-copy {
    font-size: 12px;
    color: #64748b;
    margin: 0;
  }
}
</style>

