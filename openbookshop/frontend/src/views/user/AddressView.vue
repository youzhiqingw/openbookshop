<template>
  <div class="address-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>收货地址 ({{ addresses.length }}/5)</span>
          <el-button
            type="primary"
            :disabled="addresses.length >= 5"
            @click="openDialog()"
          >
            新增地址
          </el-button>
        </div>
      </template>

      <el-empty v-if="!addresses.length" description="暂无收货地址" />
      <div v-else class="address-list">
        <div v-for="addr in addresses" :key="addr.id" class="address-item">
          <div class="address-info">
            <div class="address-name">
              <span>{{ addr.name }}</span>
              <span class="phone">{{ addr.phone }}</span>
              <el-tag v-if="addr.is_default" type="success" size="small">默认</el-tag>
            </div>
            <div class="address-detail">{{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.detail }}</div>
          </div>
          <div class="address-actions">
            <el-button text type="primary" @click="openDialog(addr)">编辑</el-button>
            <el-button v-if="!addr.is_default" text @click="setDefault(addr)">设为默认</el-button>
            <el-button text type="danger" @click="removeAddress(addr.id)">删除</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Address Dialog -->
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑地址' : '新增地址'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="收货人" prop="name">
          <el-input v-model="form.name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input v-model="form.province" placeholder="如：广东省" />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="如：深圳市" />
        </el-form-item>
        <el-form-item label="区县" prop="district">
          <el-input v-model="form.district" placeholder="如：南山区" />
        </el-form-item>
        <el-form-item label="详细地址" prop="detail">
          <el-input v-model="form.detail" type="textarea" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api'

const addresses = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const submitting = ref(false)
const formRef = ref()

const form = reactive({
  name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false,
})

const rules = {
  name: [{ required: true, message: '请输入收货人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区县', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
}

async function loadAddresses() {
  try {
    const res = await userApi.getAddresses()
    addresses.value = res.results || res
  } catch {
    ElMessage.error('获取地址列表失败')
  }
}

function openDialog(addr = null) {
  editing.value = addr
  if (addr) {
    Object.assign(form, { ...addr })
  } else {
    Object.assign(form, { name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false })
  }
  dialogVisible.value = true
}

async function submitAddress() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editing.value) {
      await userApi.updateAddress(editing.value.id, form)
      ElMessage.success('地址更新成功')
    } else {
      await userApi.createAddress(form)
      ElMessage.success('地址添加成功')
    }
    dialogVisible.value = false
    await loadAddresses()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function setDefault(addr) {
  try {
    await userApi.updateAddress(addr.id, { ...addr, is_default: true })
    ElMessage.success('已设为默认地址')
    await loadAddresses()
  } catch {
    ElMessage.error('操作失败')
  }
}

async function removeAddress(id) {
  await ElMessageBox.confirm('确定要删除这个地址吗？', '提示', { type: 'warning' })
  try {
    await userApi.deleteAddress(id)
    ElMessage.success('地址已删除')
    await loadAddresses()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(loadAddresses)
</script>

<style lang="scss" scoped>
.address-page {
  max-width: 800px;
  margin: 24px auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.address-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;

  .address-name {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 500;
    margin-bottom: 6px;

    .phone { color: #666; }
  }

  .address-detail { color: #666; font-size: 14px; }
}
</style>
