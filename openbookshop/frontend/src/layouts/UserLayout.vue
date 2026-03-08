<template>
  <el-container class="user-layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo" @click="router.push('/books')">📚 在线书店</span>
        <el-menu
          :default-active="route.path"
          mode="horizontal"
          :ellipsis="false"
          router
          class="nav-menu"
        >
          <el-menu-item index="/books">书城</el-menu-item>
          <el-menu-item index="/cart">
            购物车
            <el-badge v-if="cartStore.totalCount" :value="cartStore.totalCount" class="cart-badge" />
          </el-menu-item>
          <el-menu-item index="/orders">我的订单</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" icon="UserFilled" />
            <span>{{ authStore.user?.username }}</span>
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
    </el-header>
    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { ElMessage } from 'element-plus'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

onMounted(() => cartStore.fetchCart())

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
  background: #F5F5F5;
}

.header {
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);

  .header-left {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .logo {
    font-size: 22px;
    font-weight: 700;
    color: #2C5F2D;
    cursor: pointer;
    white-space: nowrap;
    letter-spacing: 0.5px;
    transition: color 0.2s;

    &:hover { color: #4A7C4B; }
  }

  .nav-menu {
    border-bottom: none;
    height: 64px;

    :deep(.el-menu-item) {
      font-size: 14px;
      color: #333333;
      border-bottom: 2px solid transparent;
      transition: color 0.3s, border-color 0.3s;
      height: 64px;
      line-height: 64px;
      padding: 0 16px;

      &:hover {
        color: #2C5F2D !important;
        background-color: transparent !important;
      }

      &.is-active {
        color: #2C5F2D !important;
        border-bottom-color: #2C5F2D !important;
        font-weight: 600;
        background-color: transparent !important;
      }
    }
  }

  .cart-badge {
    margin-left: 4px;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #333333;
    padding: 6px 12px;
    border-radius: 6px;
    transition: background 0.2s;

    &:hover {
      background: #F5F5F5;
      color: #2C5F2D;
    }
  }
}

:deep(.el-main) {
  padding: 24px 32px;
}
</style>

