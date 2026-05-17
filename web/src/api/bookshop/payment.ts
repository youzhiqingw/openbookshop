import { request } from '/@/utils/service';

export const paymentApiPrefix = '/api/bookshop/admin/payments/';

export function GetPaymentList(query: any) {
	return request({ url: paymentApiPrefix, method: 'get', params: query });
}

export function GetPaymentObj(id: any) {
	return request({ url: paymentApiPrefix + id + '/', method: 'get' });
}
