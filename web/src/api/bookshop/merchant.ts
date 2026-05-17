import { request } from '/@/utils/service';

// 管理端API
export const apiPrefix = '/api/bookshop/admin/merchants/';

export function GetList(query: any) {
	return request({ url: apiPrefix, method: 'get', params: query });
}

export function GetObj(id: any) {
	return request({ url: apiPrefix + id + '/', method: 'get' });
}

export function UpdateObj(obj: any) {
	return request({ url: apiPrefix + obj.id + '/', method: 'put', data: obj });
}

export function DelObj(id: any) {
	return request({ url: apiPrefix + id + '/', method: 'delete', data: { id } });
}

export function AuditObj(id: any, data: { action: string; reject_reason?: string }) {
	return request({ url: apiPrefix + id + '/audit/', method: 'post', data });
}

export function DisableObj(id: any) {
	return request({ url: apiPrefix + id + '/disable/', method: 'post' });
}

export function EnableObj(id: any) {
	return request({ url: apiPrefix + id + '/enable/', method: 'post' });
}

// 商家端API
export const merchantApplyPrefix = '/api/bookshop/merchant/apply/';
export const merchantProfilePrefix = '/api/bookshop/merchant/profile/';

export function GetApplyStatus() {
	return request({ url: merchantApplyPrefix, method: 'get' });
}

export function SubmitApply(data: {
	name: string;
	logo?: string;
	description?: string;
	contact_name: string;
	contact_phone: string;
	contact_email: string;
	address: string;
}) {
	return request({ url: merchantApplyPrefix, method: 'post', data });
}

export function GetMerchantProfile() {
	return request({ url: merchantProfilePrefix, method: 'get' });
}

export function UpdateMerchantProfile(data: any) {
	return request({ url: merchantProfilePrefix + 'update_profile/', method: 'put', data });
}
