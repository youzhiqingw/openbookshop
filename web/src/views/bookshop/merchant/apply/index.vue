<template>
	<div class="merchant-apply">
		<el-card shadow="hover" class="apply-card">
			<template #header>
				<div class="card-header">
					<span class="title">商家入驻申请</span>
				</div>
			</template>

			<!-- 未申请状态：显示申请表单 -->
			<template v-if="!applyStatus">
				<el-form ref="formRef" :model="form" :rules="rules" label-width="100px" size="default">
					<el-form-item label="店铺名称" prop="name">
						<el-input v-model="form.name" placeholder="请输入店铺名称" maxlength="100" />
					</el-form-item>
					<el-form-item label="联系人" prop="contact_name">
						<el-input v-model="form.contact_name" placeholder="请输入联系人姓名" maxlength="50" />
					</el-form-item>
					<el-form-item label="联系电话" prop="contact_phone">
						<el-input v-model="form.contact_phone" placeholder="请输入手机号" maxlength="20" />
					</el-form-item>
					<el-form-item label="联系邮箱" prop="contact_email">
						<el-input v-model="form.contact_email" placeholder="请输入邮箱" />
					</el-form-item>
					<el-form-item label="店铺地址" prop="address">
						<el-input v-model="form.address" placeholder="请输入店铺地址" maxlength="255" />
					</el-form-item>
					<el-form-item label="店铺描述" prop="description">
						<el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入店铺描述" maxlength="500" show-word-limit />
					</el-form-item>
					<el-form-item>
						<el-button type="primary" :loading="submitting" @click="handleSubmit">提交申请</el-button>
						<el-button @click="resetForm">重置</el-button>
					</el-form-item>
				</el-form>
			</template>

			<!-- 已申请状态：显示审核状态 -->
			<template v-else>
				<el-descriptions :column="2" border>
					<el-descriptions-item label="店铺名称">{{ applyStatus.name }}</el-descriptions-item>
					<el-descriptions-item label="联系人">{{ applyStatus.contact_name }}</el-descriptions-item>
					<el-descriptions-item label="联系电话">{{ applyStatus.contact_phone }}</el-descriptions-item>
					<el-descriptions-item label="联系邮箱">{{ applyStatus.contact_email }}</el-descriptions-item>
					<el-descriptions-item label="店铺地址" :span="2">{{ applyStatus.address }}</el-descriptions-item>
					<el-descriptions-item label="店铺描述" :span="2">{{ applyStatus.description || '无' }}</el-descriptions-item>
					<el-descriptions-item label="审核状态">
						<el-tag :type="statusTagType(applyStatus.status)">{{ statusLabel(applyStatus.status) }}</el-tag>
					</el-descriptions-item>
					<el-descriptions-item label="申请时间">{{ applyStatus.create_datetime }}</el-descriptions-item>
					<el-descriptions-item v-if="applyStatus.reject_reason" label="拒绝原因" :span="2">
						<span style="color: #f56c6c">{{ applyStatus.reject_reason }}</span>
					</el-descriptions-item>
				</el-descriptions>

				<div v-if="applyStatus.status === 'rejected'" style="margin-top: 20px">
					<el-button type="primary" @click="reApply">重新申请</el-button>
				</div>
			</template>
		</el-card>
	</div>
</template>

<script lang="ts" setup name="merchantApply">
import { ref, onMounted } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { GetApplyStatus, SubmitApply } from '/@/api/bookshop/merchant';

const formRef = ref<FormInstance>();
const submitting = ref(false);
const loading = ref(true);
const applyStatus = ref<any>(null);

const form = ref({
	name: '',
	contact_name: '',
	contact_phone: '',
	contact_email: '',
	address: '',
	description: '',
});

const rules: FormRules = {
	name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
	contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
	contact_phone: [
		{ required: true, message: '请输入联系电话', trigger: 'blur' },
		{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
	],
	contact_email: [
		{ required: true, message: '请输入邮箱', trigger: 'blur' },
		{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
	],
	address: [{ required: true, message: '请输入店铺地址', trigger: 'blur' }],
};

const statusTagType = (status: string) => {
	const map: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger', disabled: 'info' };
	return map[status] || 'info';
};

const statusLabel = (status: string) => {
	const map: Record<string, string> = { pending: '待审核', approved: '已通过', rejected: '已拒绝', disabled: '已禁用' };
	return map[status] || status;
};

const loadApplyStatus = async () => {
	try {
		loading.value = true;
		const res: any = await GetApplyStatus();
		if (res.data) {
			applyStatus.value = res.data;
		}
	} catch (e: any) {
		// 没有申请记录时忽略错误
	} finally {
		loading.value = false;
	}
};

const handleSubmit = async () => {
	if (!formRef.value) return;
	await formRef.value.validate(async (valid) => {
		if (!valid) return;
		submitting.value = true;
		try {
			const res: any = await SubmitApply(form.value);
			ElMessage.success(res.msg || '申请提交成功');
			applyStatus.value = res.data;
		} catch (e: any) {
			ElMessage.error(e?.msg || '提交失败');
		} finally {
			submitting.value = false;
		}
	});
};

const resetForm = () => {
	formRef.value?.resetFields();
};

const reApply = () => {
	applyStatus.value = null;
	form.value = { name: '', contact_name: '', contact_phone: '', contact_email: '', address: '', description: '' };
};

onMounted(() => {
	loadApplyStatus();
});
</script>

<style scoped>
.merchant-apply {
	padding: 20px;
}
.apply-card {
	max-width: 800px;
	margin: 0 auto;
}
.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.title {
	font-size: 18px;
	font-weight: 600;
}
</style>
