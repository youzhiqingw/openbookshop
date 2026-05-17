import * as api from '/@/api/bookshop/book';
import {
	UserPageQuery, AddReq, DelReq, EditReq,
	CreateCrudOptionsProps, CreateCrudOptionsRet, dict,
} from '@fast-crud/fast-crud';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetCategoryList(query);
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateCategoryObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelCategoryObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddCategoryObj(form);
	};

	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			actionbar: {
				buttons: {
					add: {
						text: '新增分类',
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 160,
				buttons: {
					view: { text: '查看', type: 'text' },
					edit: { text: '编辑', type: 'text' },
					remove: { text: '删除', type: 'text' },
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
				name: {
					title: '分类名称',
					type: 'input',
					search: { show: true },
					column: { minWidth: 160 },
					form: {
						rules: [{ required: true, message: '请输入分类名称' }],
					},
				},
				parent: {
					title: '父分类',
					type: 'dict-tree',
					search: { show: true },
					dict: dict({
						url: '/api/bookshop/admin/categories/tree/',
						isTree: true,
						value: 'id',
						label: 'name',
						children: 'children',
					}),
					column: { minWidth: 160 },
					form: {
						component: {
							props: {
								checkStrictly: true,
								clearable: true,
								placeholder: '留空为一级分类',
							},
						},
						helper: '留空为一级分类，选择一级分类则为二级分类',
					},
				},
				sort: {
					title: '排序',
					type: 'number',
					column: { minWidth: 80, align: 'center' },
					form: {
						component: { props: { min: 0 } },
						value: 0,
					},
				},
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					column: { minWidth: 160 },
					form: { show: false },
				},
			},
		},
	};
};
