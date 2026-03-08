<template>
  <el-container class="user-layout">
    <el-header class="header">
      <div class="header-left">
        <span class="logo">📚 在线书店</span>
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
}

.header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;

  .logo {
    font-size: 20px;
    font-weight: bold;
    color: #409eff;
    cursor: pointer;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: #333;
  }
}
</style>
