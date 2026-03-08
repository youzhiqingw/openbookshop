<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span class="section-title">个人资料</span>
          <el-button v-if="!editing" type="primary" text @click="editing = true">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <div v-else class="edit-actions">
            <el-button text @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
          </div>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="88" icon="UserFilled" class="user-avatar" />
          <div class="user-meta">
            <div class="username">{{ authStore.user?.username }}</div>
            <div class="user-role">
              <el-tag :type="roleTagType" size="small">{{ roleLabel }}</el-tag>
              <el-tag v-if="authStore.user?.is_vip" type="warning" size="small">VIP {{ authStore.user?.vip_level }}</el-tag>
            </div>
            <div class="user-points" v-if="authStore.user?.points !== undefined">
              <el-icon class="points-icon"><Star /></el-icon>
              积分：{{ authStore.user?.points }}
            </div>
          </div>
        </div>

        <el-form
          v-if="editing"
          ref="formRef"
          :model="editForm"
          :rules="rules"
          label-width="100px"
          class="edit-form"
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

        <div v-else class="info-grid">
          <div class="info-item">
            <span class="info-label">邮箱</span>
            <span class="info-value">{{ authStore.user?.email || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">手机号</span>
            <span class="info-value">{{ authStore.user?.phone || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">注册时间</span>
            <span class="info-value">{{ formatDate(authStore.user?.date_joined) }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Change Password -->
    <el-card class="password-card">
      <template #header>
        <span class="section-title">修改密码</span>
      </template>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="120px" class="pwd-form">
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
          <el-button type="primary" :loading="changingPwd" @click="changePassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Star } from '@element-plus/icons-vue'
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
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1A1A1A;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.profile-content {
  .avatar-section {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 16px 0 24px;
    border-bottom: 1px solid #F5F5F5;
    margin-bottom: 24px;

    .user-avatar {
      background: linear-gradient(135deg, #2C5F2D, #4A7C4B);
      flex-shrink: 0;
    }

    .user-meta {
      .username {
        font-size: 20px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 8px;
      }

      .user-role {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
      }

      .user-points {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #666;

        .points-icon { color: #FAAD14; }
      }
    }
  }
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .info-label {
      font-size: 12px;
      color: #999;
      font-weight: 500;
    }

    .info-value {
      font-size: 14px;
      color: #333;
    }
  }
}

.edit-form { max-width: 480px; }
.pwd-form { max-width: 420px; }
</style>
