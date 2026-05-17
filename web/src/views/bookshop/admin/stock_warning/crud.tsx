import * as api from '/@/api/bookshop/warning';
import { UserPageQuery, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetWarningList(query);
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
				book_name: {
					title: '书名',
					type: 'input',
					column: { minWidth: 160 },
					form: { show: false },
				},
				isbn: {
					title: 'ISBN',
					type: 'input',
					column: { minWidth: 140 },
					form: { show: false },
				},
				cover: {
					title: '封面',
					type: 'input',
					column: { minWidth: 80 },
					form: { show: false },
				},
				stock: {
					title: '当前库存',
					type: 'number',
					column: { minWidth: 90, align: 'center' },
					form: { show: false },
				},
				warning_stock: {
					title: '图书预警值',
					type: 'number',
					column: { minWidth: 100, align: 'center' },
					form: { show: false },
				},
				effective_warning_stock: {
					title: '有效预警值',
					type: 'number',
					column: { minWidth: 100, align: 'center' },
					form: { show: false },
				},
				warning_level: {
					title: '预警等级',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '严重缺货', value: 'critical', color: 'danger' },
							{ label: '库存警告', value: 'warning', color: 'warning' },
							{ label: '库存偏低', value: 'info', color: 'info' },
						],
					}),
					column: { minWidth: 110, align: 'center' },
					form: { show: false },
				},
				merchant_id: {
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
				category_id: {
					title: '分类',
					type: 'dict-tree',
					search: { show: true },
					dict: dict({
						url: '/api/bookshop/admin/categories/tree/',
						isTree: true,
						value: 'id',
						label: 'name',
						children: 'children',
					}),
					column: { show: false },
					form: { show: false },
					search: {
						show: true,
						component: {
							props: {
								checkStrictly: true,
							},
						},
					},
				},
				category_name: {
					title: '分类',
					type: 'input',
					column: { minWidth: 100 },
					form: { show: false },
				},
			},
		},
	};
};
