import * as api from '/@/api/bookshop/order';
import {
	UserPageQuery,
	CreateCrudOptionsProps,
	CreateCrudOptionsRet,
	dict,
	compute,
} from '@fast-crud/fast-crud';
import { ElMessage, ElMessageBox } from 'element-plus';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetOrderList(query);
	};

	const handleForceRefund = async (row: any) => {
		const { value } = await ElMessageBox.prompt('请输入退款原因（可选）', '强制退款确认', {
			confirmButtonText: '确认退款',
			cancelButtonText: '取消',
			type: 'warning',
			inputPlaceholder: '管理员强制退款',
		});
		try {
			await api.ForceRefund(row.id, { reason: value || '管理员强制退款' });
			ElMessage.success('强制退款成功');
			crudExpose.doRefresh();
		} catch {
			ElMessage.error('强制退款失败');
		}
	};

	const handleViewDetail = async (row: any) => {
		try {
			const res = await api.GetOrderObj(row.id);
			const store = (window as any).__adminOrders;
			if (store) {
				store.currentOrder.value = res.data;
				store.detailVisible.value = true;
			}
		} catch {
			ElMessage.error('获取订单详情失败');
		}
	};

	return {
		crudOptions: {
			request: {
				pageRequest,
			},
			actionbar: {
				buttons: {
					add: { show: false },
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 200,
				buttons: {
					view: { show: false },
					edit: { show: false },
					remove: { show: false },
					detail: {
						text: '详情',
						type: 'text',
						order: 1,
						click: async ({ row }: any) => handleViewDetail(row),
					},
					forceRefund: {
						text: '强制退款',
						type: 'text',
						order: 2,
						click: async ({ row }: any) => handleForceRefund(row),
						show: compute(({ row }: any) => !['cancelled', 'refunded', 'completed'].includes(row.status)),
					},
				},
			},
			columns: {
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						align: 'center',
						width: '70px',
						columnSetDisabled: true,
						formatter: (context: any) => {
							let index = context.index ?? 1;
							let pagination = crudExpose!.crudBinding.value.pagination;
							return ((pagination!.currentPage ?? 1) - 1) * pagination!.pageSize + index + 1;
						},
					},
				},
				order_no: {
					title: '订单号',
					type: 'input',
					search: { show: true },
					column: { minWidth: 180 },
					form: { show: false },
				},
				status: {
					title: '状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '待支付', value: 'pending', color: 'warning' },
							{ label: '已支付', value: 'paid', color: 'primary' },
							{ label: '已发货', value: 'shipped', color: '' },
							{ label: '已收货', value: 'received', color: 'success' },
							{ label: '已完成', value: 'completed', color: 'success' },
							{ label: '已取消', value: 'cancelled', color: 'info' },
							{ label: '退款中', value: 'refunding', color: 'warning' },
							{ label: '已退款', value: 'refunded', color: 'danger' },
						],
					}),
					column: { minWidth: 100, align: 'center' },
					form: { show: false },
				},
				user_name: {
					title: '用户',
					type: 'input',
					column: { minWidth: 100 },
					form: { show: false },
				},
				merchant: {
					title: '商家',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						url: '/api/bookshop/admin/merchants/',
						value: 'id',
						label: 'name',
					}),
					column: { show: false },
					form: { show: false },
				},
				merchant_name: {
					title: '商家',
					type: 'input',
					column: { minWidth: 120 },
					form: { show: false },
				},
				pay_amount: {
					title: '实付金额',
					type: 'number',
					column: { minWidth: 100, align: 'right' },
					form: { show: false },
					formatter: (row: any, column: any, cellValue: any) => {
						return '¥' + parseFloat(String(cellValue || 0)).toFixed(2);
					},
				},
				items: {
					title: '商品',
					type: 'input',
					form: { show: false },
					column: {
						minWidth: 200,
						component: { name: 'fs-slot', slotName: 'order_items' },
					},
				},
				receiver_name: {
					title: '收货人',
					type: 'input',
					column: { minWidth: 80 },
					form: { show: false },
				},
				receiver_phone: {
					title: '联系电话',
					type: 'input',
					column: { minWidth: 120 },
					form: { show: false },
				},
				pay_method: {
					title: '支付方式',
					type: 'input',
					column: { minWidth: 100 },
					form: { show: false },
				},
				create_datetime: {
					title: '下单时间',
					type: 'datetime',
					search: { show: true },
					column: { minWidth: 160 },
					form: { show: false },
				},
			},
		},
	};
};
