<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #order_items="{ row }">
				<el-tag v-for="item in row.items" :key="item.id" size="small" style="margin: 2px">
					{{ item.book_title }} x{{ item.quantity }}
				</el-tag>
			</template>
		</fs-crud>

		<!-- 订单详情抽屉 -->
		<el-drawer v-model="detailVisible" title="订单详情" size="550px">
			<template v-if="currentOrder">
				<el-descriptions :column="2" border>
					<el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
					<el-descriptions-item label="状态">
						<el-tag :type="statusTagType(currentOrder.status)">{{ currentOrder.status_display }}</el-tag>
					</el-descriptions-item>
					<el-descriptions-item label="用户">{{ currentOrder.user_name }}</el-descriptions-item>
					<el-descriptions-item label="商家">{{ currentOrder.merchant_name }}</el-descriptions-item>
					<el-descriptions-item label="下单时间">{{ currentOrder.create_datetime }}</el-descriptions-item>
					<el-descriptions-item label="支付时间">{{ currentOrder.pay_time || '-' }}</el-descriptions-item>
					<el-descriptions-item label="发货时间">{{ currentOrder.ship_time || '-' }}</el-descriptions-item>
					<el-descriptions-item label="支付方式">{{ currentOrder.pay_method || '-' }}</el-descriptions-item>
					<el-descriptions-item label="快递公司">{{ currentOrder.express_company || '-' }}</el-descriptions-item>
					<el-descriptions-item label="快递单号">{{ currentOrder.express_no || '-' }}</el-descriptions-item>
				</el-descriptions>

				<h4 style="margin: 16px 0 8px">收货信息</h4>
				<el-descriptions :column="1" border>
					<el-descriptions-item label="收货人">{{ currentOrder.receiver_name }}</el-descriptions-item>
					<el-descriptions-item label="联系电话">{{ currentOrder.receiver_phone }}</el-descriptions-item>
					<el-descriptions-item label="收货地址">{{ currentOrder.receiver_address }}</el-descriptions-item>
				</el-descriptions>

				<h4 style="margin: 16px 0 8px">商品明细</h4>
				<el-table :data="currentOrder.items" border size="small">
					<el-table-column prop="book_title" label="书名" />
					<el-table-column prop="price" label="单价" width="90" align="right">
						<template #default="{ row }">¥{{ parseFloat(row.price).toFixed(2) }}</template>
					</el-table-column>
					<el-table-column prop="quantity" label="数量" width="70" align="center" />
					<el-table-column prop="total_price" label="小计" width="90" align="right">
						<template #default="{ row }">¥{{ parseFloat(row.total_price).toFixed(2) }}</template>
					</el-table-column>
				</el-table>

				<h4 style="margin: 16px 0 8px">金额信息</h4>
				<el-descriptions :column="2" border>
					<el-descriptions-item label="商品总额">¥{{ parseFloat(currentOrder.total_amount).toFixed(2) }}</el-descriptions-item>
					<el-descriptions-item label="优惠金额">¥{{ parseFloat(currentOrder.discount_amount).toFixed(2) }}</el-descriptions-item>
					<el-descriptions-item label="运费">¥{{ parseFloat(currentOrder.freight_amount).toFixed(2) }}</el-descriptions-item>
					<el-descriptions-item label="实付金额">
						<span style="color: #f56c6c; font-weight: 700">¥{{ parseFloat(currentOrder.pay_amount).toFixed(2) }}</span>
					</el-descriptions-item>
				</el-descriptions>

				<div v-if="currentOrder.cancel_reason" style="margin-top: 12px">
					<el-alert :title="'取消/退款原因: ' + currentOrder.cancel_reason" type="warning" :closable="false" />
				</div>
			</template>
		</el-drawer>
	</fs-page>
</template>

<script lang="ts" setup name="adminOrders">
import { onMounted, watch, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';

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

// 订单详情
const detailVisible = ref(false);
const currentOrder = ref<any>(null);

const statusTagType = (status: string) => {
	const map: Record<string, string> = {
		pending: 'warning',
		paid: 'primary',
		shipped: '',
		received: 'success',
		completed: 'success',
		cancelled: 'info',
		refunding: 'warning',
		refunded: 'danger',
	};
	return map[status] || '';
};

// 暴露给crud.tsx使用
(window as any).__adminOrders = { detailVisible, currentOrder };
</script>
