import request from '../request';
import type { PageResponse, Order, OrderQuery, ShipOrderRequest, RefundApplyRequest, RefundApproveRequest } from '@/types';

export const orderApi = {
  // 获取订单列表（分页）
  getList(params: OrderQuery) {
    const { orderNo, customerName, customerPhone, ...rest } = params as any;
    return request.post<PageResponse<Order>>('/order/list', null, {
      params: {
        ...rest,
        customerName,
        customerPhone,
        keyword: orderNo || rest.keyword
      }
    });
  },
  
  // 获取订单详情
  getDetail(id: number) {
    return request.post<any>(`/order/${id}`).then((result: any) => ({
      ...result,
      data: normalizeOrder(result.data)
    }));
  },
  
  // 订单发货
  ship(id: number, data: ShipOrderRequest) {
    return request.put(`/order/${id}/ship`, data);
  },
  
  // 申请退款
  refundApply(id: number, data: RefundApplyRequest) {
    return request.post(`/order/${id}/refund`, data);
  },
  
  // 审核退款
  refundApprove(id: number, data: RefundApproveRequest) {
    return request.put(`/order/${id}/refund/approve`, data);
  },
  
  // 取消订单
  cancel(id: number) {
    return request.put(`/order/${id}/cancel`, {});
  },
  
  // 完成订单
  complete(id: number) {
    return request.put(`/order/${id}/complete`, {});
  },
  
  // 导出订单
  async exportList(params: OrderQuery) {
    const result = await request.post<PageResponse<Order>>('/order/list', null, { params });
    downloadJson('orders-export.json', result.data.list || []);
    return result;
  }
};

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function normalizeOrder(item: any): any {
  if (!item) return item;
  return {
    ...item,
    extraFields: parseJsonObject(item.extraFieldsJson)
  };
}

function parseJsonObject(value: any): Record<string, any> {
  if (value && typeof value === 'object' && !Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    try {
      const parsed = JSON.parse(value);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
    } catch {
      // ignore
    }
  }
  return {};
}
