<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #header-top>
				<el-button type="warning" @click="openThresholdDialog">
					<el-icon><Setting /></el-icon>
					设置预警阈值
				</el-button>
			</template>
		</fs-crud>
		<el-dialog v-model="thresholdDialogVisible" title="设置全局预警阈值" width="400px">
			<el-form :model="thresholdForm" :rules="thresholdRules" ref="thresholdFormRef" label-width="100px">
				<el-form-item label="当前阈值">
					<span>{{ currentThreshold }}</span>
				</el-form-item>
				<el-form-item label="新阈值" prop="threshold">
					<el-input-number v-model="thresholdForm.threshold" :min="1" :max="99999" :step="1" />
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="thresholdDialogVisible = false">取消</el-button>
				<el-button type="primary" @click="handleSetThreshold">确定</el-button>
			</template>
		</el-dialog>
	</fs-page>
</template>

<script lang="ts" setup name="stockWarning">
import { onMounted, watch, ref, reactive } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';
import { GetThreshold, SetThreshold } from '/@/api/bookshop/warning';
import { ElMessage } from 'element-plus';
import { Setting } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';

const { themeConfig } = storeToRefs(useThemeConfig());
const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions });

watch(
	() => themeConfig.value.globalI18n,
	() => {
		resetCrudOptions();
	}
);

onMounted(() => {
	crudExpose.doRefresh();
});

// 阈值设置弹窗
const thresholdDialogVisible = ref(false);
const currentThreshold = ref(10);
const thresholdFormRef = ref<FormInstance>();
const thresholdForm = reactive({ threshold: 10 });
const thresholdRules: FormRules = {
	threshold: [{ required: true, message: '请输入预警阈值', trigger: 'blur' }],
};

const openThresholdDialog = async () => {
	try {
		const res = await GetThreshold();
		currentThreshold.value = res.data?.threshold ?? 10;
		thresholdForm.threshold = currentThreshold.value;
		thresholdDialogVisible.value = true;
	} catch {
		ElMessage.error('获取阈值失败');
	}
};

const handleSetThreshold = async () => {
	await thresholdFormRef.value?.validate();
	try {
		await SetThreshold({ threshold: thresholdForm.threshold });
		ElMessage.success('预警阈值设置成功');
		currentThreshold.value = thresholdForm.threshold;
		thresholdDialogVisible.value = false;
		crudExpose.doRefresh();
	} catch {
		ElMessage.error('设置阈值失败');
	}
};
</script>
