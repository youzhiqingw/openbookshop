import { request } from '/@/utils/service';

export const orderApiPrefix = '/api/bookshop/admin/orders/';
export const merchantOrderApiPrefix = '/api/bookshop/merchant/orders/';

// ====== 管理端订单 ======

export function GetOrderList(query: any) {
	return request({ url: orderApiPrefix, method: 'get', params: query });
}

export function GetOrderObj(id: any) {
	return request({ url: orderApiPrefix + id + '/', method: 'get' });
}

export function ForceRefund(id: any, data: { reason?: string }) {
	return request({ url: orderApiPrefix + id + '/force_refund/', method: 'post', data });
}

// ====== 商家端订单 ======

export function GetMerchantOrderList(query: any) {
	return request({ url: merchantOrderApiPrefix, method: 'get', params: query });
}

export function GetMerchantOrderObj(id: any) {
	return request({ url: merchantOrderApiPrefix + id + '/', method: 'get' });
}

export function MerchantShip(id: any, data: { express_company: string; express_no: string }) {
	return request({ url: merchantOrderApiPrefix + id + '/ship/', method: 'post', data });
}

export function MerchantRefundApprove(id: any) {
	return request({ url: merchantOrderApiPrefix + id + '/refund_approve/', method: 'post' });
}

export function MerchantRefundReject(id: any) {
	return request({ url: merchantOrderApiPrefix + id + '/refund_reject/', method: 'post' });
}
