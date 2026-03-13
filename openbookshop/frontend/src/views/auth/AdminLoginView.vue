<template>
  <div class="admin-login-container">
    <!-- Background Effects -->
    <div class="bg-effects">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- Main Content -->
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Header Section -->
        <div class="auth-header">
          <div class="logo-section">
            <div class="logo-icon">
              <el-icon size="32"><Management /></el-icon>
            </div>
            <h1 class="logo-text">书店管理后台</h1>
          </div>
          <p class="auth-subtitle">超级管理员登录</p>
        </div>

        <!-- Form Section -->
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <!-- Username Field -->
          <div class="form-group">
            <label class="field-label">
              <el-icon><User /></el-icon>
              用户名
            </label>
            <el-input
              v-model="form.username"
              placeholder="输入管理员用户名"
              size="large"
              clearable
              :prefix-icon="User"
              class="auth-input"
              @keyup.enter="handleLogin"
            />
          </div>

          <!-- Password Field -->
          <div class="form-group">
            <label class="field-label">
              <el-icon><Lock /></el-icon>
              密码
            </label>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="输入密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              class="auth-input"
              @keyup.enter="handleLogin"
            />
          </div>

          <!-- Remember Me -->
          <div class="remember-me">
            <el-checkbox v-model="form.remember">记住我</el-checkbox>
            <RouterLink to="#" class="forgot-link">忘记密码？</RouterLink>
          </div>

          <!-- Submit Button -->
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="submit-btn"
            @click="handleLogin"
          >
            <el-icon v-if="!loading"><Login /></el-icon>
            {{ loading ? '登录中...' : '登录管理后台' }}
          </el-button>
        </el-form>

        <!-- Footer -->
        <div class="auth-footer">
          <p class="security-notice">
            <el-icon size="16"><InfoFilled /></el-icon>
            仅限授权的管理员访问
          </p>
        </div>
      </div>

      <!-- Right Panel - Info -->
      <div class="info-panel">
        <div class="panel-content">
          <h2>系统管理</h2>
          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <div class="feature-text">
                <h3>数据统计</h3>
                <p>实时查看平台数据</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">👥</div>
              <div class="feature-text">
                <h3>用户管理</h3>
                <p>管理用户和商家</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📦</div>
              <div class="feature-text">
                <h3>商品审核</h3>
                <p>控制商品质量</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💰</div>
              <div class="feature-text">
                <h3>财务管理</h3>
                <p>追踪平台收益</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { User, Lock, Management, Login, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  remember: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authStore.login(form.username, form.password)
    if (res.code === 200) {
      // Check admin status
      if (!authStore.isAdmin) {
        ElMessage.error('权限不足，仅限管理员访问')
        authStore.logout()
        return
      }
      ElMessage.success('登录成功，欢迎回来')
      router.push('/admin')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
// ============================================
// Admin Login - Elegant Enterprise Design
// ============================================

.admin-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f1729 100%);
  position: relative;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

  // Background Effects
  .bg-effects {
    position: absolute;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .gradient-blob {
      position: absolute;
      border-radius: 50%;
      opacity: 0.1;
      filter: blur(60px);

      &.blob-1 {
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, #60a5fa, #0ea5e9);
        top: -100px;
        left: -100px;
        animation: float 20s infinite ease-in-out;
      }

      &.blob-2 {
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, #34d399, #06b6d4);
        bottom: -150px;
        right: -150px;
        animation: float 25s infinite ease-in-out reverse;
      }
    }

    .grid-pattern {
      position: absolute;
      width: 100%;
      height: 100%;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 50px 50px;
    }
  }

  @keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, -30px); }
  }
}

.login-wrapper {
  display: flex;
  align-items: stretch;
  width: 90%;
  max-width: 1200px;
  height: 600px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 1;
  overflow: hidden;

  @media (max-width: 900px) {
    flex-direction: column;
    height: auto;
    max-width: 500px;
  }
}

// ============================================
// Login Card Section
// ============================================

.login-card {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);

  @media (max-width: 900px) {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 40px 30px;
  }

  .auth-header {
    margin-bottom: 40px;

    .logo-section {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;

      .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #60a5fa 0%, #06b6d4 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(96, 165, 250, 0.3);

        :deep(.el-icon) {
          color: white;
        }
      }

      .logo-text {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
      }
    }

    .auth-subtitle {
      color: rgba(255, 255, 255, 0.6);
      font-size: 14px;
      margin: 0;
      font-weight: 500;
      letter-spacing: 0.5px;
    }
  }

  // Form Groups
  .form-group {
    margin-bottom: 20px;

    .field-label {
      display: flex;
      align-items: center;
      gap: 6px;
      color: rgba(255, 255, 255, 0.8);
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;

      :deep(.el-icon) {
        opacity: 0.8;
      }
    }

    :deep(.auth-input) {
      .el-input__wrapper {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          background: rgba(255, 255, 255, 0.12);
          border-color: rgba(96, 165, 250, 0.3);
        }

        &.is-focus {
          background: rgba(255, 255, 255, 0.15);
          border-color: #60a5fa;
          box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
        }
      }

      .el-input__inner {
        color: #ffffff;
        font-size: 14px;

        &::placeholder {
          color: rgba(255, 255, 255, 0.4);
        }
      }

      :deep(.el-icon) {
        color: rgba(255, 255, 255, 0.5);
      }
    }
  }

  .remember-me {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    font-size: 13px;

    :deep(.el-checkbox) {
      .el-checkbox__label {
        color: rgba(255, 255, 255, 0.7);
      }

      &.is-checked .el-checkbox__inner {
        background-color: #60a5fa;
        border-color: #60a5fa;
      }
    }

    .forgot-link {
      color: rgba(96, 165, 250, 0.8);
      text-decoration: none;
      transition: color 0.3s;

      &:hover {
        color: #60a5fa;
      }
    }
  }

  .submit-btn {
    width: 100%;
    height: 44px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
    background: linear-gradient(135deg, #60a5fa 0%, #06b6d4 100%);
    border: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 24px rgba(96, 165, 250, 0.3);

    &:hover {
      box-shadow: 0 12px 32px rgba(96, 165, 250, 0.4);
      transform: translateY(-2px);
    }

    &:active {
      transform: translateY(0);
    }

    :deep(.el-icon) {
      margin-right: 6px;
    }
  }

  :deep(.el-button--primary:disabled) {
    opacity: 0.6;
  }

  .auth-footer {
    margin-top: 32px;
    text-align: center;

    .security-notice {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      color: rgba(255, 255, 255, 0.5);
      font-size: 12px;
      margin: 0;

      :deep(.el-icon) {
        color: rgba(52, 211, 153, 0.7);
      }
    }
  }
}

// ============================================
// Info Panel Section
// ============================================

.info-panel {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(3, 102, 214, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);

  @media (max-width: 900px) {
    display: none;
  }

  .panel-content {
    width: 100%;

    h2 {
      color: #ffffff;
      font-size: 26px;
      font-weight: 700;
      margin-bottom: 36px;
      letter-spacing: -0.5px;
    }

    .features-list {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .feature-item {
        display: flex;
        gap: 16px;
        padding: 16px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.6s ease-out both;

        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(96, 165, 250, 0.3);
          transform: translateX(8px);
        }

        &:nth-child(1) { animation-delay: 0.1s; }
        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.3s; }
        &:nth-child(4) { animation-delay: 0.4s; }

        .feature-icon {
          font-size: 32px;
          flex-shrink: 0;
        }

        .feature-text {
          flex: 1;

          h3 {
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 4px 0;
          }

          p {
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
            margin: 0;
          }
        }
      }
    }
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
