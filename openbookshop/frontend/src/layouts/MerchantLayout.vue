<template>
  <el-container class="merchant-layout">
    <el-aside width="200px" class="sidebar">
      <div class="sidebar-logo">🏪 商家中心</div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#FFFFFF"
        text-color="#666666"
        active-text-color="#2C5F2D"
      >
        <el-menu-item index="/merchant/profile">
          <el-icon><Shop /></el-icon>
          <span>店铺资料</span>
        </el-menu-item>
        <el-menu-item index="/merchant/books">
          <el-icon><Reading /></el-icon>
          <span>图书管理</span>
        </el-menu-item>
        <el-menu-item index="/merchant/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/merchant/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="/merchant/finance">
          <el-icon><Wallet /></el-icon>
          <span>收支记录</span>
        </el-menu-item>
        <el-menu-item index="/merchant/stock-warning">
          <el-icon><Warning /></el-icon>
          <span>库存预警</span>
        </el-menu-item>
        <el-menu-item index="/merchant/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <span>评论管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="merchant-header">
        <div class="header-left">商家管理系统</div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="28" icon="UserFilled" />
              <span>{{ authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home">用户端</el-dropdown-item>
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
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

async function handleCommand(command) {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/auth/login')
  } else if (command === 'home') {
    router.push('/profile')
  }
}
</script>

<style lang="scss" scoped>
.merchant-layout {
  min-height: 100vh;
  background: #F5F5F5;
}

.sidebar {
  background: #FFFFFF;
  border-right: 1px solid #E5E5E5;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0,0,0,0.04);

  .sidebar-logo {
    padding: 0 24px;
    height: 64px;
    font-size: 16px;
    font-weight: 700;
    color: #2C5F2D;
    border-bottom: 1px solid #E5E5E5;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: 0.5px;
  }

  :deep(.el-menu) {
    border-right: none;
    padding: 8px 0;
  }

  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    margin: 2px 8px;
    border-radius: 6px;
    padding: 0 16px !important;
  }

  :deep(.el-menu-item.is-active) {
    background-color: #E8F5E9 !important;
    color: #2C5F2D !important;
    font-weight: 600;
    border-left: 3px solid #2C5F2D;
  }

  :deep(.el-menu-item:hover:not(.is-active)) {
    background-color: #F5F5F5 !important;
    color: #333333 !important;
  }
}

.merchant-header {
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  font-weight: 600;
  color: #1A1A1A;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #333333;
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: 400;
    transition: background 0.2s;

    &:hover { background: #F5F5F5; }
  }
}

:deep(.el-main) {
  padding: 24px;
}
</style>
