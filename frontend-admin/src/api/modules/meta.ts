import request from '../request';

export const metaApi = {
  getCustomerListMeta() {
    return request.get<{ searchFields?: any[]; columns?: any[] }>('/meta/customer-list');
  },
  getUserListMeta() {
    return request.get<{ columns?: any[] }>('/meta/user-list');
  },
  getOrderListMeta() {
    return request.get<{ searchFields?: any[]; columns?: any[] }>('/meta/order-list');
  },
  getOrderActionFormsMeta() {
    return request.get<Record<string, any>>('/meta/order-action-forms');
  },
  getProductListMeta() {
    return request.get<{ searchFields?: any[]; columns?: any[] }>('/meta/product-list');
  },
  getProductFormMeta() {
    return request.get<{
      basicFields?: any[];
      mediaFields?: any[];
      detailFields?: any[];
      rules?: Record<string, any[]>;
    }>('/meta/product-form');
  },
  getCustomerFormMeta() {
    return request.get<{ fields?: any[]; rules?: Record<string, any[]> }>('/meta/customer-form');
  }
};
