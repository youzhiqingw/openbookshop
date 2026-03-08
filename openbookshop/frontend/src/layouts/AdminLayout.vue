<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="sidebar-logo">📚 管理后台</div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#FFFFFF"
        text-color="#666666"
        active-text-color="#2C5F2D"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/merchants">
          <el-icon><Shop /></el-icon>
          <span>商家管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/books">
          <el-icon><Reading /></el-icon>
          <span>图书管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <span>评论审核</span>
        </el-menu-item>
        <el-menu-item index="/admin/finance">
          <el-icon><Wallet /></el-icon>
          <span>财务流水</span>
        </el-menu-item>
        <el-menu-item index="/admin/stock-warning">
          <el-icon><Warning /></el-icon>
          <span>库存预警</span>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="admin-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const titleMap = {
  '/admin/dashboard': '数据概览',
  '/admin/users': '用户管理',
  '/admin/merchants': '商家管理',
  '/admin/books': '图书管理',
  '/admin/reviews': '评论审核',
  '/admin/finance': '财务流水',
  '/admin/stock-warning': '库存预警',
  '/admin/logs': '操作日志',
}
const currentTitle = computed(() => titleMap[route.path] || '管理后台')

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
.admin-layout {
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

.admin-header {
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #333333;
    padding: 6px 12px;
    border-radius: 6px;
    transition: background 0.2s;

    &:hover { background: #F5F5F5; }
  }
}

:deep(.el-main) {
  padding: 24px;
}
</style>
