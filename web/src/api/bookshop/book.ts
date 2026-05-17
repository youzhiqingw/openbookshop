import { request } from '/@/utils/service';

export const bookApiPrefix = '/api/bookshop/admin/books/';
export const categoryApiPrefix = '/api/bookshop/admin/categories/';
export const merchantBookApiPrefix = '/api/bookshop/merchant/books/';
export const merchantCategoryApiPrefix = '/api/bookshop/merchant/categories/';

// ====== 管理端图书 ======

export function GetBookList(query: any) {
	return request({ url: bookApiPrefix, method: 'get', params: query });
}

export function GetBookObj(id: any) {
	return request({ url: bookApiPrefix + id + '/', method: 'get' });
}

export function AddBookObj(obj: any) {
	return request({ url: bookApiPrefix, method: 'post', data: obj });
}

export function UpdateBookObj(obj: any) {
	return request({ url: bookApiPrefix + obj.id + '/', method: 'put', data: obj });
}

export function DelBookObj(id: any) {
	return request({ url: bookApiPrefix + id + '/', method: 'delete', data: { id } });
}

export function BookStatusAction(id: any, data: { status: string }) {
	return request({ url: bookApiPrefix + id + '/status/', method: 'patch', data });
}

// ====== 管理端分类 ======

export function GetCategoryList(query: any) {
	return request({ url: categoryApiPrefix, method: 'get', params: query });
}

export function GetCategoryObj(id: any) {
	return request({ url: categoryApiPrefix + id + '/', method: 'get' });
}

export function AddCategoryObj(obj: any) {
	return request({ url: categoryApiPrefix, method: 'post', data: obj });
}

export function UpdateCategoryObj(obj: any) {
	return request({ url: categoryApiPrefix + obj.id + '/', method: 'put', data: obj });
}

export function DelCategoryObj(id: any) {
	return request({ url: categoryApiPrefix + id + '/', method: 'delete', data: { id } });
}

export function GetCategoryTree() {
	return request({ url: categoryApiPrefix + 'tree/', method: 'get' });
}

// ====== 商家端图书 ======

export function GetMerchantBookList(query: any) {
	return request({ url: merchantBookApiPrefix, method: 'get', params: query });
}

export function GetMerchantBookObj(id: any) {
	return request({ url: merchantBookApiPrefix + id + '/', method: 'get' });
}

export function AddMerchantBookObj(obj: any) {
	return request({ url: merchantBookApiPrefix, method: 'post', data: obj });
}

export function UpdateMerchantBookObj(obj: any) {
	return request({ url: merchantBookApiPrefix + obj.id + '/', method: 'put', data: obj });
}

export function DelMerchantBookObj(id: any) {
	return request({ url: merchantBookApiPrefix + id + '/', method: 'delete', data: { id } });
}

export function MerchantBookStatusAction(id: any, data: { status: string }) {
	return request({ url: merchantBookApiPrefix + id + '/status/', method: 'patch', data });
}

export function MerchantBookRestock(id: any, data: { quantity: number }) {
	return request({ url: merchantBookApiPrefix + id + '/restock/', method: 'post', data });
}

export function MerchantBookWarningStock(id: any, data: { warning_stock: number }) {
	return request({ url: merchantBookApiPrefix + id + '/warning_stock/', method: 'post', data });
}

// ====== 商家端分类（只读） ======

export function GetMerchantCategoryTree() {
	return request({ url: merchantCategoryApiPrefix + 'tree/', method: 'get' });
}
