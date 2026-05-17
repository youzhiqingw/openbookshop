import * as api from '/@/api/bookshop/merchant';
import { UserPageQuery, DelReq, CreateCrudOptionsProps, CreateCrudOptionsRet, dict, compute } from '@fast-crud/fast-crud';
import { ElMessage, ElMessageBox } from 'element-plus';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetList(query);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	const handleAudit = async (row: any, action: string) => {
		if (action === 'approve') {
			await ElMessageBox.confirm('确定通过该商家审核吗？', '审核确认', { type: 'warning' });
			await api.AuditObj(row.id, { action: 'approve' });
			ElMessage.success('审核通过');
		} else {
			const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回审核', {
				inputValidator: (val: string) => (val && val.trim() ? true : '驳回原因不能为空'),
			});
			await api.AuditObj(row.id, { action: 'reject', reject_reason: value.trim() });
			ElMessage.success('已驳回');
		}
		crudExpose.doRefresh();
	};

	const handleDisable = async (row: any) => {
		await ElMessageBox.confirm('确定禁用该商家吗？', '操作确认', { type: 'warning' });
		await api.DisableObj(row.id);
		ElMessage.success('已禁用');
		crudExpose.doRefresh();
	};

	const handleEnable = async (row: any) => {
		await ElMessageBox.confirm('确定启用该商家吗？', '操作确认', { type: 'warning' });
		await api.EnableObj(row.id);
		ElMessage.success('已启用');
		crudExpose.doRefresh();
	};

	return {
		crudOptions: {
			request: {
				pageRequest,
				delRequest,
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
					view: {
						text: '查看',
						type: 'text',
					},
					edit: { show: false },
					remove: { show: false },
					approve: {
						text: '通过',
						type: 'text',
						order: 1,
						click: async ({ row }: any) => handleAudit(row, 'approve'),
						show: compute(({ row }) => row.status === 'pending'),
					},
					reject: {
						text: '驳回',
						type: 'text',
						order: 2,
						click: async ({ row }: any) => handleAudit(row, 'reject'),
						show: compute(({ row }) => row.status === 'pending'),
					},
					disable: {
						text: '禁用',
						type: 'text',
						order: 3,
						click: async ({ row }: any) => handleDisable(row),
						show: compute(({ row }) => row.status === 'approved'),
					},
					enable: {
						text: '启用',
						type: 'text',
						order: 4,
						click: async ({ row }: any) => handleEnable(row),
						show: compute(({ row }) => row.status === 'disabled'),
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
				name: {
					title: '商家名称',
					type: 'input',
					search: { show: true },
					column: { minWidth: 140 },
				},
				status: {
					title: '状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '待审核', value: 'pending', color: 'warning' },
							{ label: '已通过', value: 'approved', color: 'success' },
							{ label: '已驳回', value: 'rejected', color: 'danger' },
							{ label: '已禁用', value: 'disabled', color: 'info' },
						],
					}),
					column: { minWidth: 100, align: 'center' },
					form: { show: false },
				},
				contact_name: {
					title: '联系人',
					type: 'input',
					column: { minWidth: 100 },
				},
				contact_phone: {
					title: '联系电话',
					type: 'input',
					column: { minWidth: 120 },
				},
				contact_email: {
					title: '联系邮箱',
					type: 'input',
					column: { minWidth: 160 },
				},
				address: {
					title: '地址',
					type: 'input',
					column: { minWidth: 180 },
				},
				is_open: {
					title: '营业状态',
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '营业中', value: true, color: 'success' },
							{ label: '休息中', value: false, color: 'info' },
						],
					}),
					column: { minWidth: 90, align: 'center' },
					form: { show: false },
				},
				reject_reason: {
					title: '驳回原因',
					type: 'input',
					column: { minWidth: 160 },
					form: { show: false },
				},
				description: {
					title: '简介',
					type: 'textarea',
					column: { minWidth: 200 },
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
