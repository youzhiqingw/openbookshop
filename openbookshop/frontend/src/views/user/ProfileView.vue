<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button v-if="!editing" type="primary" text @click="editing = true">编辑</el-button>
          <div v-else>
            <el-button text @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
          </div>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="80" icon="UserFilled" />
          <div class="user-role">
            <el-tag :type="roleTagType">{{ roleLabel }}</el-tag>
            <el-tag v-if="authStore.user?.is_vip" type="warning" class="ml-8">VIP {{ authStore.user?.vip_level }}</el-tag>
          </div>
        </div>

        <el-form
          v-if="editing"
          ref="formRef"
          :model="editForm"
          :rules="rules"
          label-width="100px"
        >
          <el-form-item label="用户名">
            <el-input :value="authStore.user?.username" disabled />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="editForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="editForm.phone" placeholder="请输入手机号" />
          </el-form-item>
        </el-form>

        <el-descriptions v-else :column="1" border>
          <el-descriptions-item label="用户名">{{ authStore.user?.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ authStore.user?.email || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ authStore.user?.phone || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="积分">{{ authStore.user?.points }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(authStore.user?.date_joined) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- Change Password -->
    <el-card class="password-card">
      <template #header><span>修改密码</span></template>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="120px" style="max-width: 400px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="new_password2">
          <el-input v-model="pwdForm.new_password2" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="changingPwd" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api'

const authStore = useAuthStore()

const editing = ref(false)
const saving = ref(false)
const formRef = ref()
const editForm = reactive({
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '',
})

const rules = {
  email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
}

function cancelEdit() {
  editing.value = false
  editForm.email = authStore.user?.email || ''
  editForm.phone = authStore.user?.phone || ''
}

async function saveProfile() {
  await formRef.value.validate()
  saving.value = true
  try {
    const res = await userApi.updateProfile(editForm)
    authStore.updateUser(res)
    ElMessage.success('资料更新成功')
    editing.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '更新失败')
  } finally {
    saving.value = false
  }
}

// Change password
const pwdFormRef = ref()
const changingPwd = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '', new_password2: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
  new_password2: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.new_password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function changePassword() {
  await pwdFormRef.value.validate()
  changingPwd.value = true
  try {
    await userApi.changePassword(pwdForm)
    ElMessage.success('密码修改成功')
    pwdFormRef.value.resetFields()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '修改失败')
  } finally {
    changingPwd.value = false
  }
}

const roleMap = { admin: '管理员', merchant: '商家', customer: '普通用户' }
const roleTagTypeMap = { admin: 'danger', merchant: 'warning', customer: 'info' }
const roleLabel = computed(() => roleMap[authStore.user?.role] || '用户')
const roleTagType = computed(() => roleTagTypeMap[authStore.user?.role] || 'info')

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<style lang="scss" scoped>
.profile-page {
  max-width: 700px;
  margin: 24px auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-content {
  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;

    .user-role {
      display: flex;
      gap: 8px;
    }
  }
}

.ml-8 { margin-left: 8px; }
</style>
