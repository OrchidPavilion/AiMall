import request from '../request';
import type {
  SystemConfig,
  OperationLog,
  OperationLogQuery,
  Integration,
  PageResponse,
  FieldConfigSchema
} from '@/types';

export const systemApi = {
  // 获取系统配置
  getConfig() {
    return request.post<any>('/system/config').then((result: any) => ({
      ...result,
      data: normalizeSystemConfig(result.data)
    }));
  },
  
  // 更新系统配置
  updateConfig(data: Partial<SystemConfig> & { logo?: File }) {
    const payload: Record<string, string> = {};
    Object.keys(data).forEach((key) => {
      const value = data[key as keyof typeof data];
      if (value === undefined || value === null) return;
      if (value instanceof File) return;
      payload[key] = typeof value === 'string' ? value : JSON.stringify(value);
    });
    return request.put('/system/config', payload);
  },
  
  // 获取操作日志
  getOperationLogs(params: OperationLogQuery) {
    return request.post<PageResponse<OperationLog>>('/system/logs', null, { params });
  },
  
  // 获取集成列表
  getIntegrations() {
    return request.post<Integration[]>('/system/integrations');
  },
  
  // 测试集成接口
  testIntegration(id: number, data: { url: string; method: string; headers?: Record<string, string>; body?: any }) {
    return request.post(`/system/integrations/${id}/test`, data);
  },
  
  // 更新集成配置
  updateIntegration(id: number, data: Partial<Integration>) {
    return request.put(`/system/integrations/${id}`, data);
  },
  
  // 启用/禁用集成
  toggleIntegration(id: number, enabled: boolean) {
    return request.put(`/system/integrations/${id}/enabled`, { enabled });
  },

  getFieldConfig(domain: 'customer' | 'product' | 'order') {
    return request.post<FieldConfigSchema>(`/system/field-config/${domain}`);
  },

  updateFieldConfig(domain: 'customer' | 'product' | 'order', data: FieldConfigSchema) {
    return request.put<FieldConfigSchema>(`/system/field-config/${domain}`, data);
  }
};

function normalizeSystemConfig(data: any): SystemConfig {
  return {
    id: 0,
    systemName: data?.systemName || 'GhostFit 管理后台',
    logoUrl: data?.logoUrl || '',
    themeColor: data?.themeColor || '#1890ff',
    passwordPolicy: {
      minLength: data?.passwordMinLength ?? 8,
      requireUppercase: data?.passwordRequireUppercase ?? true,
      requireNumber: data?.passwordRequireNumber ?? true,
      requireSpecialChar: false,
      expireDays: data?.passwordExpireDays ?? 90
    },
    sessionTimeout: data?.sessionTimeout ?? 86400,
    registrationEnabled: data?.registrationEnabled ?? false,
    contactEmail: data?.contactEmail || '',
    contactPhone: data?.contactPhone || '',
    updatedAt: data?.updatedAt || ''
  };
}
