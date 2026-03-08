<template>
  <div class="merchant-profile-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>店铺资料</span>
          <el-button v-if="!editing" type="primary" text @click="editing = true">编辑</el-button>
          <div v-else>
            <el-button text @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <el-alert
          v-if="merchant?.status === 'pending'"
          title="您的商家申请正在审核中，请耐心等待"
          type="warning"
          show-icon
          style="margin-bottom: 20px"
        />
        <el-alert
          v-if="merchant?.status === 'rejected'"
          title="您的商家申请未通过审核，请联系客服"
          type="error"
          show-icon
          style="margin-bottom: 20px"
        />

        <el-form
          v-if="editing && merchant"
          ref="formRef"
          :model="editForm"
          label-width="100px"
          style="max-width: 600px"
        >
          <el-form-item label="店铺名称">
            <el-input v-model="editForm.store_name" />
          </el-form-item>
          <el-form-item label="店铺描述">
            <el-input v-model="editForm.description" type="textarea" rows="4" />
          </el-form-item>
          <el-form-item label="经营地址">
            <el-input v-model="editForm.address" />
          </el-form-item>
        </el-form>

        <el-descriptions v-else-if="merchant" :column="1" border>
          <el-descriptions-item label="店铺名称">{{ merchant.store_name }}</el-descriptions-item>
          <el-descriptions-item label="店铺描述">{{ merchant.description || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="营业执照">{{ merchant.business_license || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="经营地址">{{ merchant.address || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="审核状态">
            <el-tag :type="statusTagType(merchant.status)">{{ statusLabel(merchant.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatDate(merchant.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { merchantApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const formRef = ref()
const merchant = ref(null)
const editForm = reactive({ store_name: '', description: '', address: '' })

async function loadProfile() {
  loading.value = true
  try {
    const res = await merchantApi.getProfile()
    merchant.value = res.data || res
    Object.assign(editForm, {
      store_name: merchant.value.store_name,
      description: merchant.value.description,
      address: merchant.value.address,
    })
  } catch {
    ElMessage.error('获取店铺信息失败')
  } finally {
    loading.value = false
  }
}

function cancelEdit() {
  editing.value = false
  Object.assign(editForm, {
    store_name: merchant.value.store_name,
    description: merchant.value.description,
    address: merchant.value.address,
  })
}

async function saveProfile() {
  saving.value = true
  try {
    const res = await merchantApi.updateProfile(editForm)
    merchant.value = res.data || res
    ElMessage.success('店铺信息更新成功')
    editing.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '更新失败')
  } finally {
    saving.value = false
  }
}

const statusMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
const statusTagTypeMap = { pending: 'warning', approved: 'success', rejected: 'danger' }
const statusLabel = (s) => statusMap[s] || s
const statusTagType = (s) => statusTagTypeMap[s] || ''

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(loadProfile)
</script>

<style lang="scss" scoped>
.merchant-profile-page {
  max-width: 700px;
  margin: 24px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
