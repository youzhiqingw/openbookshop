<template>
  <el-container class="merchant-layout">
    <!-- Sidebar -->
    <el-aside :width="isCollapsed ? '64px' : '210px'" class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-logo">
        <span class="logo-icon">🏪</span>
        <span v-show="!isCollapsed" class="logo-text">商家中心</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="transparent"
        text-color="#c7d2d8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/merchant/profile">
          <el-icon><Shop /></el-icon>
          <template #title><span>店铺资料</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/books">
          <el-icon><Reading /></el-icon>
          <template #title><span>图书管理</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/orders">
          <el-icon><List /></el-icon>
          <template #title><span>订单管理</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/analytics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title><span>数据分析</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/finance">
          <el-icon><Wallet /></el-icon>
          <template #title><span>收支记录</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/stock-warning">
          <el-icon><Warning /></el-icon>
          <template #title><span>库存预警</span></template>
        </el-menu-item>
        <el-menu-item index="/merchant/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <template #title><span>评论管理</span></template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-show="!isCollapsed">
        <el-avatar :size="32" style="background:#1a6b5a">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
        <div class="sidebar-user-info">
          <div class="sidebar-username">{{ authStore.user?.username }}</div>
          <div class="sidebar-role">商家账号</div>
        </div>
      </div>
    </el-aside>

    <!-- Main content -->
    <el-container class="main-container">
      <el-header class="merchant-header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            text
            :icon="isCollapsed ? Expand : Fold"
            @click="isCollapsed = !isCollapsed"
          />
          <span class="system-name">商家管理系统</span>
        </div>

        <div class="header-right">
          <el-tooltip content="前往用户端" placement="bottom">
            <el-button text :icon="HomeFilled" @click="router.push('/')" />
          </el-tooltip>
          <el-divider direction="vertical" />
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" style="background:#1a6b5a; font-size:14px;">
                {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username-text">{{ authStore.user?.username }}</span>
              <el-icon class="arrow-down"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home" :icon="HomeFilled">用户端首页</el-dropdown-item>
                <el-dropdown-item command="logout" :icon="SwitchButton" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="merchant-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import {
  Fold, Expand, HomeFilled, ArrowDown, SwitchButton,
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)

async function handleCommand(command) {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/auth/login')
  } else if (command === 'home') {
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.merchant-layout {
  min-height: 100vh;
  background: #f0f2f5;
}

// ── Sidebar ────────────────────────────────────────────────
.sidebar {
  background: linear-gradient(180deg, #0f3040 0%, #1a5068 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.25s ease;
  position: relative;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 100;

  .sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 18px;
    height: 60px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;

    .logo-icon { font-size: 22px; flex-shrink: 0; }
    .logo-text {
      font-size: 16px;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
    }
  }

  :deep(.el-menu) {
    border-right: none;
    background: transparent;
    flex: 1;
    padding-top: 8px;
  }

  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    margin: 2px 8px;
    border-radius: 8px;
    color: #9bbfcc !important;
    transition: all 0.2s;

    &:hover {
      background-color: rgba(255, 255, 255, 0.12) !important;
      color: #ffffff !important;
    }

    &.is-active {
      background-color: rgba(255, 255, 255, 0.2) !important;
      color: #ffffff !important;
      font-weight: 600;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
  }

  :deep(.el-menu--collapse .el-menu-item) {
    margin: 2px 4px;
    justify-content: center;
  }

  .sidebar-footer {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;

    .sidebar-user-info {
      overflow: hidden;
    }
    .sidebar-username {
      font-size: 13px;
      color: #ffffff;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .sidebar-role {
      font-size: 11px;
      color: #9bbfcc;
    }
  }
}

// ── Main Container ────────────────────────────────────────
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

// ── Header ────────────────────────────────────────────────
.merchant-header {
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px 0 8px;
  height: 60px !important;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 99;

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;

    .collapse-btn {
      font-size: 18px;
      color: #666;
      padding: 8px;
      &:hover { color: #1a5068; }
    }

    .system-name {
      font-size: 15px;
      font-weight: 600;
      color: #1a5068;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 4px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 8px;
      transition: background 0.2s;

      &:hover { background: #f5f5f5; }

      .username-text {
        font-size: 14px;
        color: #333;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .arrow-down {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

// ── Main Content ────────────────────────────────────────
.merchant-main {
  padding: 20px;
  overflow-y: auto;
  background: #f0f2f5;
}
</style>
