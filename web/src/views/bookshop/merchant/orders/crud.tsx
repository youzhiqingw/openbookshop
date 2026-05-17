import { GetMerchantOrderList } from '/@/api/bookshop/order';
import {
	UserPageQuery,
	CreateCrudOptionsProps, CreateCrudOptionsRet, dict, compute,
} from '@fast-crud/fast-crud';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await GetMerchantOrderList(query);
	};

	const merchantOrders = (window as any).__merchantOrders;

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
				width: 260,
				buttons: {
					view: { text: '详情', type: 'text' },
					ship: {
						text: '发货',
						type: 'text',
						order: 1,
						click: async ({ row }: any) => merchantOrders.openShip(row),
						show: compute(({ row }) => row.status === 'paid'),
					},
					refund_approve: {
						text: '退款审核',
						type: 'text',
						order: 2,
						click: async ({ row }: any) => merchantOrders.openRefund(row),
						show: compute(({ row }) => row.status === 'refunding'),
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
					column: { minWidth: 160 },
					form: { show: false },
				},
				status: {
					title: '状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '待付款', value: 'pending', color: 'info' },
							{ label: '已付款', value: 'paid', color: 'warning' },
							{ label: '已发货', value: 'shipped', color: '' },
							{ label: '已收货', value: 'received', color: 'success' },
							{ label: '已完成', value: 'completed', color: 'success' },
							{ label: '已取消', value: 'cancelled', color: 'danger' },
							{ label: '退款中', value: 'refunding', color: 'danger' },
							{ label: '已退款', value: 'refunded', color: 'info' },
						],
					}),
					column: { minWidth: 90, align: 'center' },
					form: { show: false },
				},
				user_name: {
					title: '下单用户',
					type: 'input',
					column: { minWidth: 90 },
					form: { show: false },
				},
				total_amount: {
					title: '订单金额',
					type: 'text',
					column: { minWidth: 90, align: 'right' },
					form: { show: false },
					formatter: ({ row }: any) => '¥' + parseFloat(row.total_amount).toFixed(2),
				},
				pay_amount: {
					title: '实付金额',
					type: 'text',
					column: { minWidth: 90, align: 'right' },
					form: { show: false },
					formatter: ({ row }: any) => '¥' + parseFloat(row.pay_amount).toFixed(2),
				},
				receiver_name: {
					title: '收货人',
					type: 'input',
					search: { show: true },
					column: { minWidth: 80 },
					form: { show: false },
				},
				receiver_phone: {
					title: '联系电话',
					type: 'input',
					column: { minWidth: 110 },
					form: { show: false },
				},
				receiver_address: {
					title: '收货地址',
					type: 'input',
					column: { minWidth: 180 },
					form: { show: false },
				},
				express_company: {
					title: '快递公司',
					type: 'input',
					column: { minWidth: 90 },
					form: { show: false },
				},
				express_no: {
					title: '快递单号',
					type: 'input',
					column: { minWidth: 120 },
					form: { show: false },
				},
				cancel_reason: {
					title: '原因',
					type: 'input',
					column: { minWidth: 120 },
					form: { show: false },
				},
				create_datetime: {
					title: '下单时间',
					type: 'datetime',
					column: { minWidth: 160 },
					form: { show: false },
				},
			},
		},
	};
};
