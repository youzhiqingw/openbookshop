import { request } from '/@/utils/service';

export const apiPrefix = '/api/bookshop/admin/warnings/';

export function GetWarningList(query: any) {
	return request({ url: apiPrefix, method: 'get', params: query });
}

export function GetThreshold() {
	return request({ url: apiPrefix + 'threshold/', method: 'get' });
}

export function SetThreshold(data: { threshold: number }) {
	return request({ url: apiPrefix + 'threshold/', method: 'put', data });
}
