<template>
  <div>
    <h2 class="form-title">注册</h2>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱（可选）" size="large" prefix-icon="Message" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入手机号（可选）" size="large" prefix-icon="Phone" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码（至少8位）"
          size="large"
          prefix-icon="Lock"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="password2">
        <el-input
          v-model="form.password2"
          type="password"
          placeholder="请再次输入密码"
          size="large"
          prefix-icon="Lock"
          show-password
          @keyup.enter="handleRegister"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          style="width: 100%"
          @click="handleRegister"
        >
          注册
        </el-button>
      </el-form-item>
    </el-form>
    <div class="form-footer">
      已有账号？
      <RouterLink to="/auth/login">立即登录</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  password2: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
  password2: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authStore.register(form)
    if (res.code === 201) {
      ElMessage.success('注册成功')
      router.push('/profile')
    } else {
      ElMessage.error(res.message || '注册失败')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.form-title {
  font-size: 22px;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 24px;
  text-align: center;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
  color: #666666;

  a {
    color: #2C5F2D;
    &:hover { text-decoration: underline; }
  }
}
</style>
