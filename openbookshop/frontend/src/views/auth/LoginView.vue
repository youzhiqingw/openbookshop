<template>
  <div>
    <h2 class="form-title">登录</h2>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          size="large"
          prefix-icon="Lock"
          show-password
          @keyup.enter="handleLogin"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          style="width: 100%"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
    <div class="form-footer">
      还没有账号？
      <RouterLink to="/auth/register">立即注册</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authStore.login(form.username, form.password)
    if (res.code === 200) {
      ElMessage.success('登录成功')
      const redirect = route.query.redirect || getDefaultRoute()
      router.push(redirect)
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}

function getDefaultRoute() {
  if (authStore.isAdmin) return '/admin'
  if (authStore.isMerchant) return '/merchant'
  return '/profile'
}
</script>

<style lang="scss" scoped>
.form-title {
  font-size: 22px;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
  color: #666;

  a {
    color: #409eff;
    &:hover { text-decoration: underline; }
  }
}
</style>
