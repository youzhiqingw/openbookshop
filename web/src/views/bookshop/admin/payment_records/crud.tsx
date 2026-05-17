import * as api from '/@/api/bookshop/payment';
import { UserPageQuery, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetPaymentList(query);
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
				width: 100,
				buttons: {
					view: { text: '查看', type: 'text' },
					edit: { show: false },
					remove: { show: false },
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
				transaction_no: {
					title: '交易号',
					type: 'input',
					search: { show: true },
					column: { minWidth: 180 },
					form: { show: false },
				},
				order_no: {
					title: '订单号',
					type: 'input',
					search: { show: true },
					column: { minWidth: 180 },
					form: { show: false },
				},
				pay_method: {
					title: '支付方式',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '模拟支付宝', value: 'mock_alipay', color: 'primary' },
							{ label: '模拟微信', value: 'mock_wechat', color: 'success' },
						],
					}),
					column: { minWidth: 120, align: 'center' },
					form: { show: false },
				},
				pay_amount: {
					title: '支付金额',
					type: 'number',
					column: { minWidth: 100, align: 'right' },
					form: { show: false },
					formatter: (row: any, column: any, cellValue: any) => {
						return '¥' + parseFloat(String(cellValue || 0)).toFixed(2);
					},
				},
				status: {
					title: '状态',
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '成功', value: 'success', color: 'success' },
							{ label: '失败', value: 'failed', color: 'danger' },
						],
					}),
					column: { minWidth: 80, align: 'center' },
					form: { show: false },
				},
				pay_time: {
					title: '支付时间',
					type: 'datetime',
					column: { minWidth: 160 },
					form: { show: false },
				},
			},
		},
	};
};
