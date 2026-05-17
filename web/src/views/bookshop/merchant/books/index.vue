<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #header-bottom>
				<!-- 补货弹窗 -->
				<el-dialog v-model="restockVisible" title="补货" width="400px" destroy-on-close>
					<el-form :model="restockForm" label-width="80px">
						<el-form-item label="当前库存">
							<span>{{ restockForm.currentStock }}</span>
						</el-form-item>
						<el-form-item label="补货数量">
							<el-input-number v-model="restockForm.quantity" :min="1" :max="99999" />
						</el-form-item>
					</el-form>
					<template #footer>
						<el-button @click="restockVisible = false">取消</el-button>
						<el-button type="primary" :loading="restockLoading" @click="handleRestock">确认补货</el-button>
					</template>
				</el-dialog>
				<!-- 预警值弹窗 -->
				<el-dialog v-model="warningVisible" title="设置预警阈值" width="400px" destroy-on-close>
					<el-form :model="warningForm" label-width="80px">
						<el-form-item label="当前库存">
							<span>{{ warningForm.currentStock }}</span>
						</el-form-item>
						<el-form-item label="预警阈值">
							<el-input-number v-model="warningForm.warning_stock" :min="0" :max="99999" />
						</el-form-item>
					</el-form>
					<template #footer>
						<el-button @click="warningVisible = false">取消</el-button>
						<el-button type="primary" :loading="warningLoading" @click="handleWarning">确认设置</el-button>
					</template>
				</el-dialog>
			</template>
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="merchantBooks">
import { onMounted, watch, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';
import { MerchantBookRestock, MerchantBookWarningStock } from '/@/api/bookshop/book';
import { ElMessage } from 'element-plus';

const { themeConfig } = storeToRefs(useThemeConfig());
const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions });

watch(
	() => themeConfig.value.globalI18n,
	() => {
		resetCrudOptions();
	}
);

// 补货
const restockVisible = ref(false);
const restockLoading = ref(false);
const restockForm = ref({ bookId: 0, currentStock: 0, quantity: 1 });

const openRestock = (row: any) => {
	restockForm.value = { bookId: row.id, currentStock: row.stock, quantity: 1 };
	restockVisible.value = true;
};

const handleRestock = async () => {
	restockLoading.value = true;
	try {
		const res: any = await MerchantBookRestock(restockForm.value.bookId, { quantity: restockForm.value.quantity });
		ElMessage.success(res.msg || '补货成功');
		restockVisible.value = false;
		crudExpose.doRefresh();
	} catch (e: any) {
		ElMessage.error(e?.msg || '补货失败');
	} finally {
		restockLoading.value = false;
	}
};

// 预警值
const warningVisible = ref(false);
const warningLoading = ref(false);
const warningForm = ref({ bookId: 0, currentStock: 0, warning_stock: 10 });

const openWarning = (row: any) => {
	warningForm.value = { bookId: row.id, currentStock: row.stock, warning_stock: row.warning_stock ?? 10 };
	warningVisible.value = true;
};

const handleWarning = async () => {
	warningLoading.value = true;
	try {
		const res: any = await MerchantBookWarningStock(warningForm.value.bookId, { warning_stock: warningForm.value.warning_stock });
		ElMessage.success(res.msg || '设置成功');
		warningVisible.value = false;
		crudExpose.doRefresh();
	} catch (e: any) {
		ElMessage.error(e?.msg || '设置失败');
	} finally {
		warningLoading.value = false;
	}
};

// 暴露给crud.tsx使用
(window as any).__merchantBooks = { openRestock, openWarning };

onMounted(() => {
	crudExpose.doRefresh();
});
</script>
