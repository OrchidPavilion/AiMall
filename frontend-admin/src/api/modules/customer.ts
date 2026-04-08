import request from '../request';
import type { PageResponse, Customer, CustomerDetail, CustomerQuery, AssignCustomerRequest } from '@/types';

export const customerApi = {
  // 获取客户列表（分页）
  getList(params: CustomerQuery) {
    return request.post<PageResponse<any>>('/customer/list', null, { params }).then((result: any) => ({
      ...result,
      data: {
        ...result.data,
        list: (result.data?.list || []).map(normalizeCustomer)
      }
    }));
  },

  // 获取公海客户列表（分页）
  getPublicSeaList(params: CustomerQuery) {
    return request.post<PageResponse<any>>('/customer/public-sea', null, { params }).then((result: any) => ({
      ...result,
      data: {
        ...result.data,
        list: (result.data?.list || []).map(normalizeCustomer)
      }
    }));
  },
  
  // 获取客户详情
  getDetail(id: number | string) {
    return request.post<any>(`/customer/${id}`).then((result: any) => ({
      ...result,
      data: normalizeCustomer(result.data)
    }));
  },
  
  // 新增客户
  addCustomer(data: Partial<Customer>) {
    return request.post<{ id: number }>('/customer/addCustomer', data);
  },
  
  // 更新客户
  update(id: number | string, data: Partial<Customer>) {
    return request.put<{ id: number }>(`/customer/${id}`, data);
  },
  
  // 删除客户
  delete(id: number | string) {
    return request.delete(`/customer/${id}`);
  },
  
  // 分配客户
  assign(id: number, data: AssignCustomerRequest) {
    return request.post(`/customer/${id}/assign`, data);
  },

  getBehaviors(id: number | string, params?: { type?: string }) {
    return request.get(`/customer/${id}/behaviors`, { params });
  },

  recordBehavior(id: number | string, data: any) {
    return request.post(`/customer/${id}/behavior`, data);
  },
  
  // 导出客户列表
  async exportList(params: CustomerQuery) {
    const result = await request.post<PageResponse<Customer>>('/customer/list', null, { params });
    downloadJson('customers-export.json', result.data.list || []);
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

function normalizeCustomer(item: any): any {
  if (!item) return item;
  const genderMap: Record<number, string> = {
    0: 'UNKNOWN',
    1: 'MALE',
    2: 'FEMALE'
  };
  const phones = normalizePhones(item);
  return {
    ...item,
    id: item.id != null ? String(item.id) : item.id,
    gender: typeof item.gender === 'number' ? (genderMap[item.gender] || 'UNKNOWN') : item.gender,
    assignee: item.assignee || (item.assigneeName ? { id: item.assigneeId || 0, name: item.assigneeName } : undefined),
    phones,
    extraFields: parseJsonObject(item.extraFieldsJson)
  };
}

function normalizePhones(item: any) {
  const parsed: string[] = [];
  if (typeof item?.phoneNumbersJson === 'string' && item.phoneNumbersJson.trim()) {
    try {
      const arr = JSON.parse(item.phoneNumbersJson);
      if (Array.isArray(arr)) {
        arr.forEach((v) => {
          if (typeof v === 'string' && v.trim()) parsed.push(v.trim());
        });
      }
    } catch {
      // ignore malformed json
    }
  }
  if (item?.phone && !parsed.includes(item.phone)) {
    parsed.unshift(String(item.phone));
  }
  return parsed.map((full) => {
    const raw = String(full).trim();
    const digits = raw.replace(/[^\d]/g, '');

    // Prefer China mobile split for +86/86 + 11-digit numbers.
    if (digits.length === 13 && digits.startsWith('86')) {
      return { full, prefix: '86', number: digits.slice(2) };
    }
    if (digits.length === 11 && /^1\d{10}$/.test(digits)) {
      return { full, prefix: '86', number: digits };
    }

    // Fallback: keep last 11 digits as local number when possible.
    if (digits.length > 11 && digits.length <= 16) {
      const prefix = digits.slice(0, digits.length - 11);
      const number = digits.slice(-11);
      if (/^\d{1,5}$/.test(prefix) && /^\d{11}$/.test(number)) {
        return { full, prefix, number };
      }
    }

    // Final fallback for uncommon formats.
    return { full, prefix: '86', number: digits };
  });
}

function parseJsonObject(value: any): Record<string, any> {
  if (value && typeof value === 'object' && !Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    try {
      const parsed = JSON.parse(value);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        return parsed;
      }
    } catch {
      // ignore
    }
  }
  return {};
}
