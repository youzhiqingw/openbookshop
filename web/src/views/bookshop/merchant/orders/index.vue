<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #header-bottom>
				<!-- 发货弹窗 -->
				<el-dialog v-model="shipVisible" title="发货" width="480px" destroy-on-close>
					<el-form :model="shipForm" label-width="90px">
						<el-form-item label="订单号">
							<span>{{ shipForm.orderNo }}</span>
						</el-form-item>
						<el-form-item label="快递公司">
							<el-input v-model="shipForm.express_company" placeholder="如：顺丰、中通" />
						</el-form-item>
						<el-form-item label="快递单号">
							<el-input v-model="shipForm.express_no" placeholder="请输入快递单号" />
						</el-form-item>
					</el-form>
					<template #footer>
						<el-button @click="shipVisible = false">取消</el-button>
						<el-button type="primary" :loading="shipLoading" @click="handleShip">确认发货</el-button>
					</template>
				</el-dialog>
				<!-- 退款审核弹窗 -->
				<el-dialog v-model="refundVisible" title="退款审核" width="480px" destroy-on-close>
					<el-descriptions :column="1" border>
						<el-descriptions-item label="订单号">{{ refundForm.orderNo }}</el-descriptions-item>
						<el-descriptions-item label="退款原因">{{ refundForm.reason || '无' }}</el-descriptions-item>
						<el-descriptions-item label="实付金额">¥{{ parseFloat(refundForm.payAmount || 0).toFixed(2) }}</el-descriptions-item>
					</el-descriptions>
					<template #footer>
						<el-button @click="refundVisible = false">取消</el-button>
						<el-button type="danger" :loading="refundLoading" @click="handleRefundReject">拒绝退款</el-button>
						<el-button type="primary" :loading="refundLoading" @click="handleRefundApprove">同意退款</el-button>
					</template>
				</el-dialog>
				<!-- 订单详情抽屉 -->
				<el-drawer v-model="detailVisible" title="订单详情" size="500px" destroy-on-close>
					<el-descriptions :column="2" border v-if="currentOrder">
						<el-descriptions-item label="订单号" :span="2">{{ currentOrder.order_no }}</el-descriptions-item>
						<el-descriptions-item label="状态">
							<el-tag :type="statusTagType(currentOrder.status)">{{ currentOrder.status_display }}</el-tag>
						</el-descriptions-item>
						<el-descriptions-item label="下单时间">{{ currentOrder.create_datetime }}</el-descriptions-item>
						<el-descriptions-item label="收货人">{{ currentOrder.receiver_name }}</el-descriptions-item>
						<el-descriptions-item label="联系电话">{{ currentOrder.receiver_phone }}</el-descriptions-item>
						<el-descriptions-item label="收货地址" :span="2">{{ currentOrder.receiver_address }}</el-descriptions-item>
						<el-descriptions-item label="订单金额">¥{{ parseFloat(currentOrder.total_amount).toFixed(2) }}</el-descriptions-item>
						<el-descriptions-item label="实付金额">¥{{ parseFloat(currentOrder.pay_amount).toFixed(2) }}</el-descriptions-item>
						<el-descriptions-item v-if="currentOrder.pay_time" label="支付时间" :span="2">{{ currentOrder.pay_time }}</el-descriptions-item>
						<el-descriptions-item v-if="currentOrder.express_company" label="快递公司">{{ currentOrder.express_company }}</el-descriptions-item>
						<el-descriptions-item v-if="currentOrder.express_no" label="快递单号">{{ currentOrder.express_no }}</el-descriptions-item>
						<el-descriptions-item v-if="currentOrder.cancel_reason" label="原因" :span="2">{{ currentOrder.cancel_reason }}</el-descriptions-item>
					</el-descriptions>
					<el-table v-if="currentOrder" :data="currentOrder.items" style="margin-top: 16px" border>
						<el-table-column prop="book_title" label="书名" min-width="140" />
						<el-table-column prop="price" label="单价" width="100" align="right">
							<template #default="{ row }">¥{{ parseFloat(row.price).toFixed(2) }}</template>
						</el-table-column>
						<el-table-column prop="quantity" label="数量" width="70" align="center" />
						<el-table-column prop="total_price" label="小计" width="100" align="right">
							<template #default="{ row }">¥{{ parseFloat(row.total_price).toFixed(2) }}</template>
						</el-table-column>
					</el-table>
				</el-drawer>
			</template>
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="merchantOrders">
import { onMounted, watch, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';
import { MerchantShip, MerchantRefundApprove, MerchantRefundReject } from '/@/api/bookshop/order';
import { ElMessage } from 'element-plus';

const { themeConfig } = storeToRefs(useThemeConfig());
const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions });

watch(
	() => themeConfig.value.globalI18n,
	() => {
		resetCrudOptions();
	}
);

const statusTagType = (status: string) => {
	const map: Record<string, string> = {
		pending: 'info', paid: 'warning', shipped: '', received: 'success',
		completed: 'success', cancelled: 'danger', refunding: 'danger', refunded: 'info',
	};
	return map[status] || 'info';
};

// 发货
const shipVisible = ref(false);
const shipLoading = ref(false);
const shipForm = ref({ orderId: 0, orderNo: '', express_company: '', express_no: '' });

const openShip = (row: any) => {
	shipForm.value = { orderId: row.id, orderNo: row.order_no, express_company: '', express_no: '' };
	shipVisible.value = true;
};

const handleShip = async () => {
	if (!shipForm.value.express_company || !shipForm.value.express_no) {
		ElMessage.warning('请填写快递公司和快递单号');
		return;
	}
	shipLoading.value = true;
	try {
		const res: any = await MerchantShip(shipForm.value.orderId, {
			express_company: shipForm.value.express_company,
			express_no: shipForm.value.express_no,
		});
		ElMessage.success(res.msg || '发货成功');
		shipVisible.value = false;
		crudExpose.doRefresh();
	} catch (e: any) {
		ElMessage.error(e?.msg || '发货失败');
	} finally {
		shipLoading.value = false;
	}
};

// 退款审核
const refundVisible = ref(false);
const refundLoading = ref(false);
const refundForm = ref({ orderId: 0, orderNo: '', reason: '', payAmount: '' });

const openRefund = (row: any) => {
	refundForm.value = { orderId: row.id, orderNo: row.order_no, reason: row.cancel_reason || '', payAmount: row.pay_amount };
	refundVisible.value = true;
};

const handleRefundApprove = async () => {
	refundLoading.value = true;
	try {
		const res: any = await MerchantRefundApprove(refundForm.value.orderId);
		ElMessage.success(res.msg || '已同意退款');
		refundVisible.value = false;
		crudExpose.doRefresh();
	} catch (e: any) {
		ElMessage.error(e?.msg || '操作失败');
	} finally {
		refundLoading.value = false;
	}
};

const handleRefundReject = async () => {
	refundLoading.value = true;
	try {
		const res: any = await MerchantRefundReject(refundForm.value.orderId);
		ElMessage.success(res.msg || '已拒绝退款');
		refundVisible.value = false;
		crudExpose.doRefresh();
	} catch (e: any) {
		ElMessage.error(e?.msg || '操作失败');
	} finally {
		refundLoading.value = false;
	}
};

// 详情
const detailVisible = ref(false);
const currentOrder = ref<any>(null);

const openDetail = (row: any) => {
	currentOrder.value = row;
	detailVisible.value = true;
};

// 暴露给crud.tsx
(window as any).__merchantOrders = { openShip, openRefund, openDetail };

onMounted(() => {
	crudExpose.doRefresh();
});
</script>
