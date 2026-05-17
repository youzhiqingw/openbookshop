import {
	GetMerchantBookList, AddMerchantBookObj, UpdateMerchantBookObj,
	DelMerchantBookObj, MerchantBookStatusAction, GetMerchantCategoryTree,
} from '/@/api/bookshop/book';
import {
	UserPageQuery, AddReq, DelReq, EditReq,
	CreateCrudOptionsProps, CreateCrudOptionsRet, dict, compute,
} from '@fast-crud/fast-crud';
import { ElMessage, ElMessageBox } from 'element-plus';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await GetMerchantBookList(query);
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await UpdateMerchantBookObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await DelMerchantBookObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		return await AddMerchantBookObj(form);
	};

	const handleStatus = async (row: any, status: string) => {
		const label = status === 'on_sale' ? '上架' : '下架';
		await ElMessageBox.confirm(`确定${label}该图书吗？`, '操作确认', { type: 'warning' });
		await MerchantBookStatusAction(row.id, { status });
		ElMessage.success(`已${label}`);
		crudExpose.doRefresh();
	};

	const merchantBooks = (window as any).__merchantBooks;

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
						text: '新增图书',
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 320,
				buttons: {
					view: { text: '查看', type: 'text' },
					edit: { text: '编辑', type: 'text' },
					remove: { text: '删除', type: 'text' },
					on_sale: {
						text: '上架',
						type: 'text',
						order: 1,
						click: async ({ row }: any) => handleStatus(row, 'on_sale'),
						show: compute(({ row }) => row.status === 'draft' || row.status === 'off_sale'),
					},
					off_sale: {
						text: '下架',
						type: 'text',
						order: 2,
						click: async ({ row }: any) => handleStatus(row, 'off_sale'),
						show: compute(({ row }) => row.status === 'on_sale'),
					},
					restock: {
						text: '补货',
						type: 'text',
						order: 3,
						click: async ({ row }: any) => merchantBooks.openRestock(row),
					},
					warning: {
						text: '预警值',
						type: 'text',
						order: 4,
						click: async ({ row }: any) => merchantBooks.openWarning(row),
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
				title: {
					title: '书名',
					type: 'input',
					search: { show: true },
					column: { minWidth: 160 },
					form: {
						rules: [{ required: true, message: '请输入书名' }],
					},
				},
				isbn: {
					title: 'ISBN',
					type: 'input',
					search: { show: true },
					column: { minWidth: 140 },
					form: {
						rules: [{ required: true, message: '请输入ISBN' }],
					},
				},
				author: {
					title: '作者',
					type: 'input',
					search: { show: true },
					column: { minWidth: 100 },
					form: {
						rules: [{ required: true, message: '请输入作者' }],
					},
				},
				publisher: {
					title: '出版社',
					type: 'input',
					column: { minWidth: 120 },
				},
				publish_date: {
					title: '出版日期',
					type: 'date',
					column: { minWidth: 110 },
					form: {
						rules: [{ required: true, message: '请选择出版日期' }],
					},
				},
				category: {
					title: '分类',
					type: 'dict-tree',
					search: { show: true },
					dict: dict({
						url: '/api/bookshop/merchant/categories/tree/',
						isTree: true,
						value: 'id',
						label: 'name',
						children: 'children',
					}),
					column: { minWidth: 100 },
					form: {
						component: {
							props: {
								checkStrictly: true,
							},
						},
						rules: [{ required: true, message: '请选择分类' }],
					},
				},
				price: {
					title: '售价',
					type: 'number',
					column: { minWidth: 80, align: 'right' },
					form: {
						rules: [{ required: true, message: '请输入售价' }],
						component: { props: { min: 0, precision: 2 } },
					},
				},
				original_price: {
					title: '原价',
					type: 'number',
					column: { minWidth: 80, align: 'right' },
					form: {
						rules: [{ required: true, message: '请输入原价' }],
						component: { props: { min: 0, precision: 2 } },
					},
				},
				stock: {
					title: '库存',
					type: 'number',
					column: { minWidth: 70, align: 'center' },
					form: {
						rules: [{ required: true, message: '请输入库存' }],
						component: { props: { min: 0 } },
					},
				},
				warning_stock: {
					title: '预警值',
					type: 'number',
					column: { minWidth: 70, align: 'center' },
					form: { show: false },
				},
				sales_count: {
					title: '销量',
					type: 'number',
					column: { minWidth: 70, align: 'center' },
					form: { show: false },
				},
				status: {
					title: '状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '草稿', value: 'draft', color: 'info' },
							{ label: '在售', value: 'on_sale', color: 'success' },
							{ label: '已下架', value: 'off_sale', color: 'warning' },
						],
					}),
					column: { minWidth: 80, align: 'center' },
					form: { show: false },
				},
				cover_image: {
					title: '封面',
					type: 'input',
					column: { minWidth: 80 },
					form: {
						component: { placeholder: '封面图URL' },
					},
				},
				merchant: {
					title: '商家',
					type: 'input',
					column: { show: false },
					form: { show: false },
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
