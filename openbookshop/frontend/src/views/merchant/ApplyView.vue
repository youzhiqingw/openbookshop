<template>
  <div class="apply-page">
    <el-card style="max-width: 600px; margin: 40px auto">
      <template #header><span>商家入驻申请</span></template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="店铺名称" prop="store_name">
          <el-input v-model="form.store_name" placeholder="请输入店铺名称" />
        </el-form-item>
        <el-form-item label="店铺描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="4" placeholder="请简要描述您的店铺" />
        </el-form-item>
        <el-form-item label="营业执照" prop="business_license">
          <el-input v-model="form.business_license" placeholder="请输入营业执照号" />
        </el-form-item>
        <el-form-item label="经营地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入经营地址" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleApply">提交申请</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { merchantApi } from '@/api'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)
const form = reactive({ store_name: '', description: '', business_license: '', address: '' })

const rules = {
  store_name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
}

async function handleApply() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await merchantApi.applyMerchant(form)
    ElMessage.success('申请已提交，请等待审核')
    router.push('/merchant/profile')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '提交失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>
