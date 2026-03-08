<template>
  <el-container class="merchant-layout">
    <el-aside width="200px" class="sidebar">
      <div class="sidebar-logo">🏪 商家中心</div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/merchant/profile">
          <el-icon><Shop /></el-icon>
          <span>店铺资料</span>
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
}

.sidebar {
  background: #304156;
  overflow-y: auto;

  .sidebar-logo {
    padding: 20px;
    font-size: 16px;
    font-weight: bold;
    color: #fff;
    border-bottom: 1px solid #263445;
  }

  :deep(.el-menu) {
    border-right: none;
  }
}

.merchant-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
}
</style>
