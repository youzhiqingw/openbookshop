<template>
	<div class="merchant-profile">
		<el-card shadow="hover" class="profile-card">
			<template #header>
				<div class="card-header">
					<span class="title">店铺信息</span>
					<el-button v-if="!editing" type="primary" size="small" @click="startEdit">编辑</el-button>
					<template v-else>
						<el-button type="primary" size="small" :loading="saving" @click="handleSave">保存</el-button>
						<el-button size="small" @click="cancelEdit">取消</el-button>
					</template>
				</div>
			</template>

			<div v-loading="loading">
				<template v-if="profile">
					<!-- 显示模式 -->
					<el-descriptions v-if="!editing" :column="2" border>
						<el-descriptions-item label="店铺名称">{{ profile.name }}</el-descriptions-item>
						<el-descriptions-item label="营业状态">
							<el-switch :model-value="profile.is_open" disabled active-text="营业中" inactive-text="休息中" />
						</el-descriptions-item>
						<el-descriptions-item label="联系人">{{ profile.contact_name }}</el-descriptions-item>
						<el-descriptions-item label="联系电话">{{ profile.contact_phone }}</el-descriptions-item>
						<el-descriptions-item label="联系邮箱">{{ profile.contact_email }}</el-descriptions-item>
						<el-descriptions-item label="店铺地址" :span="2">{{ profile.address }}</el-descriptions-item>
						<el-descriptions-item label="店铺描述" :span="2">{{ profile.description || '无' }}</el-descriptions-item>
						<el-descriptions-item label="审核状态">
							<el-tag type="success">已通过</el-tag>
						</el-descriptions-item>
						<el-descriptions-item label="创建时间">{{ profile.create_datetime }}</el-descriptions-item>
					</el-descriptions>

					<!-- 编辑模式 -->
					<el-form v-else ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px" size="default">
						<el-form-item label="店铺名称" prop="name">
							<el-input v-model="editForm.name" maxlength="100" />
						</el-form-item>
						<el-form-item label="营业状态" prop="is_open">
							<el-switch v-model="editForm.is_open" active-text="营业中" inactive-text="休息中" />
						</el-form-item>
						<el-form-item label="联系人" prop="contact_name">
							<el-input v-model="editForm.contact_name" maxlength="50" />
						</el-form-item>
						<el-form-item label="联系电话" prop="contact_phone">
							<el-input v-model="editForm.contact_phone" maxlength="20" />
						</el-form-item>
						<el-form-item label="联系邮箱" prop="contact_email">
							<el-input v-model="editForm.contact_email" />
						</el-form-item>
						<el-form-item label="店铺地址" prop="address">
							<el-input v-model="editForm.address" maxlength="255" />
						</el-form-item>
						<el-form-item label="店铺描述" prop="description">
							<el-input v-model="editForm.description" type="textarea" :rows="4" maxlength="500" show-word-limit />
						</el-form-item>
					</el-form>
				</template>

				<el-empty v-else description="暂无店铺信息" />
			</div>
		</el-card>
	</div>
</template>

<script lang="ts" setup name="merchantProfile">
import { ref, onMounted } from 'vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { GetMerchantProfile, UpdateMerchantProfile } from '/@/api/bookshop/merchant';

const loading = ref(true);
const editing = ref(false);
const saving = ref(false);
const profile = ref<any>(null);
const editFormRef = ref<FormInstance>();

const editForm = ref({
	name: '',
	contact_name: '',
	contact_phone: '',
	contact_email: '',
	address: '',
	description: '',
	is_open: true,
});

const editRules: FormRules = {
	name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
	contact_name: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
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

const loadProfile = async () => {
	try {
		loading.value = true;
		const res: any = await GetMerchantProfile();
		if (res.data) {
			profile.value = res.data;
		}
	} catch (e: any) {
		ElMessage.error(e?.msg || '获取店铺信息失败');
	} finally {
		loading.value = false;
	}
};

const startEdit = () => {
	if (!profile.value) return;
	editForm.value = {
		name: profile.value.name || '',
		contact_name: profile.value.contact_name || '',
		contact_phone: profile.value.contact_phone || '',
		contact_email: profile.value.contact_email || '',
		address: profile.value.address || '',
		description: profile.value.description || '',
		is_open: profile.value.is_open ?? true,
	};
	editing.value = true;
};

const cancelEdit = () => {
	editing.value = false;
	editFormRef.value?.resetFields();
};

const handleSave = async () => {
	if (!editFormRef.value) return;
	await editFormRef.value.validate(async (valid) => {
		if (!valid) return;
		saving.value = true;
		try {
			const res: any = await UpdateMerchantProfile(editForm.value);
			ElMessage.success(res.msg || '更新成功');
			profile.value = res.data;
			editing.value = false;
		} catch (e: any) {
			ElMessage.error(e?.msg || '更新失败');
		} finally {
			saving.value = false;
		}
	});
};

onMounted(() => {
	loadProfile();
});
</script>

<style scoped>
.merchant-profile {
	padding: 20px;
}
.profile-card {
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
