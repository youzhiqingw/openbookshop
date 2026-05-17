import { request } from '/@/utils/service';

export const statisticsApiPrefix = '/api/bookshop/admin/statistics/';

export function GetOverview() {
	return request({ url: statisticsApiPrefix + 'overview/', method: 'get' });
}

export function GetTrend(params?: { days?: number; start_date?: string; end_date?: string }) {
	return request({ url: statisticsApiPrefix + 'trend/', method: 'get', params });
}

export function GetCategoryDistribution() {
	return request({ url: statisticsApiPrefix + 'category_distribution/', method: 'get' });
}

export function GetMerchantRanking(params?: { limit?: number; order_by?: string }) {
	return request({ url: statisticsApiPrefix + 'merchant_ranking/', method: 'get', params });
}
