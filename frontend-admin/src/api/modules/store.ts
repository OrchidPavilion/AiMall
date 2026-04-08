import request from '../request';
import type { PageResponse, ProductCategory, AppPreviewContext, AppPreviewTrackPayload } from '@/types';

export const storeApi = {
  // ========== APP 排版 ==========
  
  // 获取排版配置
  async getLayout() {
    const result = await request.post<any[]>('/store/layout/list');
    const list = Array.isArray(result.data) ? result.data : [];
    return {
      ...result,
      data: {
        modules: list.map((item: any) => ({
          id: item.id,
          type: item.moduleType || item.type || 'UNKNOWN',
          enabled: item.enabled ?? true,
          sort: item.sort ?? 0,
          config: typeof item.configJson === 'string'
            ? safeParseJson(item.configJson)
            : (item.config || {})
        })),
        publishedAt: null
      }
    } as any;
  },
  
  // 更新排版配置
  updateLayout(data: { modules: any[]; publish: boolean }) {
    const groups = new Map<string, any[]>();
    (data.modules || []).forEach((module, index) => {
      const type = module.type || 'UNKNOWN';
      if (!groups.has(type)) groups.set(type, []);
      groups.get(type)!.push({
        id: String(module.id ?? `${type}-${index}`),
        type,
        title: module.config?.title || '',
        enabled: module.enabled !== false,
        config: module.config || {}
      });
    });

    const tasks = Array.from(groups.entries()).map(([type, modules]) =>
      request.post(`/store/layout/${encodeURIComponent(type)}/default`, {
        modules,
        publish: !!data.publish
      })
    );

    return Promise.all(tasks).then(() => ({
      code: 0,
      message: 'success',
      data: null,
      timestamp: Date.now()
    } as any));
  },
  
  // ========== 广告位管理 ==========
  
  // 获取广告位列表
  getAdSpaces() {
    return request.post<any[]>('/store/ad-space/all').then((result: any) => ({
      ...result,
      data: (result.data || []).map((item: any) => ({
        id: item.id,
        name: item.name,
        type: item.type,
        position: item.position,
        enabled: item.enabled === 1 || item.enabled === true,
        config: {
          imageUrl: item.imageUrl,
          videoUrl: item.videoUrl,
          linkUrl: item.linkUrl,
          startTime: item.startTime,
          endTime: item.endTime,
          maxImpressions: item.maxImpressions
        },
        createdAt: item.createdAt,
        updatedAt: item.updatedAt
      }))
    })) as any;
  },
  
  // 更新广告位
  updateAdSpace(id: number, data: { config: any; enabled?: boolean }) {
    return request.put(`/store/ad-space/${id}`, {
      enabled: data.enabled,
      imageUrl: data.config?.imageUrl,
      videoUrl: data.config?.videoUrl,
      linkUrl: data.config?.linkUrl
    });
  },
  
  // ========== 商品分类 ==========
  
  // 获取分类树
  getCategoryTree() {
    return request.post<ProductCategory[]>('/store/category/tree');
  },
  
  // 获取分类列表（分页）
  getCategoryList(params: { page: number; pageSize: number; keyword?: string; enabled?: boolean }) {
    return request.post<PageResponse<ProductCategory>>('/store/category/list', null, { params });
  },
  
  // 创建分类
  createCategory(data: { name: string; parentId?: number | null; icon?: string; sort: number; enabled: boolean }) {
    return request.post<{ id: number }>('/store/category', data);
  },
  
  // 更新分类
  updateCategory(id: number, data: Partial<{ name: string; parentId: number | null; icon: string; sort: number; enabled: boolean }>) {
    return request.put(`/store/category/${id}`, data);
  },
  
  // 删除分类
  deleteCategory(id: number) {
    return request.delete(`/store/category/${id}`);
  },
  
  // 批量更新分类排序
  batchUpdateSort(updates: Array<{ id: number; sort: number }>) {
    return request.post('/store/category/batch-sort', { updates });
  },

  // 广告位启停（兼容 AdSpaces 页面旧调用）
  toggleIntegration(id: number, enabled: boolean) {
    return request.put(`/store/ad-space/${id}/status`, null, { params: { enabled } });
  },

  // 广告位测试
  testIntegration(id: number, _data: { url: string; method: string }) {
    return request.post(`/store/ad-space/${id}/test`);
  },

  getAppPreviewContext() {
    return request.post<AppPreviewContext>('/store/app-preview/context').then((result: any) => ({
      ...result,
      data: result?.data
        ? {
            ...result.data,
            customerId: result.data.customerId != null ? String(result.data.customerId) : undefined
          }
        : result?.data
    }));
  },

  trackAppPreviewBehavior(data: AppPreviewTrackPayload) {
    return request.post('/store/app-preview/track', data);
  },

  getAppPreviewBehaviors(customerId: number | string) {
    return request.get(`/store/app-preview/behaviors/${customerId}`);
  }
};

function safeParseJson(input: string) {
  try {
    return JSON.parse(input);
  } catch {
    return {};
  }
}
