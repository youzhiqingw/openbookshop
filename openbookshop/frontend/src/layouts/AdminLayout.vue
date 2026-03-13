<template>
  <el-container class="admin-layout">
    <!-- Sidebar -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-logo">
        <span class="logo-icon">📚</span>
        <span v-show="!isCollapsed" class="logo-text">管理后台</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="transparent"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title><span>数据概览</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title><span>用户管理</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/merchants">
          <el-icon><Shop /></el-icon>
          <template #title>
            <span>商家管理</span>
          </template>
        </el-menu-item>
        <el-menu-item index="/admin/books">
          <el-icon><Reading /></el-icon>
          <template #title><span>图书管理</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <template #title><span>评论审核</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/finance">
          <el-icon><Wallet /></el-icon>
          <template #title><span>财务流水</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/stock-warning">
          <el-icon><Warning /></el-icon>
          <template #title><span>库存预警</span></template>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <template #title><span>操作日志</span></template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-show="!isCollapsed">
        <el-avatar :size="32" style="background:#4A7C4B">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
        <div class="sidebar-user-info">
          <div class="sidebar-username">{{ authStore.user?.username }}</div>
          <div class="sidebar-role">超级管理员</div>
        </div>
      </div>
    </el-aside>

    <!-- Main content -->
    <el-container class="main-container">
      <el-header class="admin-header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            text
            :icon="isCollapsed ? Expand : Fold"
            @click="isCollapsed = !isCollapsed"
          />
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-center">
          <span class="page-title">{{ currentTitle }}</span>
        </div>

        <div class="header-right">
          <el-tooltip content="前往用户端" placement="bottom">
            <el-button text :icon="HomeFilled" @click="router.push('/')" />
          </el-tooltip>
          <el-divider direction="vertical" />
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" style="background:#2C5F2D; font-size:14px;">
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

      <el-main class="admin-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import {
  Fold, Expand, HomeFilled, ArrowDown, SwitchButton,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapsed = ref(false)

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
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.admin-layout {
  min-height: 100vh;
  background: #f0f2f5;
}

// ── Sidebar ────────────────────────────────────────────────
.sidebar {
  background: linear-gradient(180deg, #1a3a2a 0%, #2C5F2D 100%);
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
    color: #a8c4aa !important;
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
      color: #a8c4aa;
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
.admin-header {
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
    gap: 4px;
    flex: 1;

    .collapse-btn {
      font-size: 18px;
      color: #666;
      padding: 8px;
      &:hover { color: #2C5F2D; }
    }
  }

  .header-center {
    flex: 1;
    text-align: center;

    .page-title {
      font-size: 15px;
      font-weight: 600;
      color: #1a1a1a;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 4px;
    flex: 1;
    justify-content: flex-end;

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
.admin-main {
  padding: 20px;
  overflow-y: auto;
  background: #f0f2f5;
}

:deep(.el-breadcrumb__inner) {
  font-size: 13px;
}
</style>
