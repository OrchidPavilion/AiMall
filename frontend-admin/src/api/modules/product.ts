import request from '../request';
import type { PageResponse, Product, ProductQuery, ProductForm } from '@/types';

export const productApi = {
  // 获取商品列表（分页）
  getList(params: ProductQuery) {
    return request.post<PageResponse<Product>>('/store/product/list', null, { params });
  },
  
  // 获取商品详情
  getDetail(id: number) {
    return request.post<any>(`/store/product/${id}`).then((result: any) => ({
      ...result,
      data: normalizeProduct(result.data)
    }));
  },
  
  // 创建商品
  async create(data: ProductForm) {
    return request.post<{ id: number }>('/store/product', await normalizeCreatePayload(data));
  },
  
  // 更新商品
  async update(id: number, data: ProductForm) {
    return request.put(`/store/product/${id}`, await normalizeUpdatePayload(data));
  },
  
  // 删除商品
  delete(id: number) {
    return request.delete(`/store/product/${id}`);
  },

  // 修改库存
  updateStock(id: number, stock: number, reason = '后台批量修改库存') {
    return request.post(`/store/product/${id}/stock`, {
      operation: 'SET',
      quantity: Number(stock),
      remark: reason
    });
  },
  
  // 上架/下架商品
  toggleStatus(id: number, status: string | boolean) {
    const isActive = typeof status === 'boolean' ? status : status === 'ON_SHELF';
    return request.put(`/store/product/${id}/status`, null, {
      params: { isActive }
    });
  },
  
  // 导出商品
  exportList(params: ProductQuery) {
    return request.post('/store/product/list', null, { params }).then((result: any) => {
      downloadJson('products-export.json', result.data?.list || []);
      return result;
    });
  }
};

async function normalizeCreatePayload(data: ProductForm) {
  const mainImage = await serializeImageInput(data.mainImage);
  const images = await serializeImageList(data.gallery);
  return {
    name: data.name,
    categoryId: data.categoryId,
    price: Math.round(Number(data.price || 0) * 100),
    originalPrice: data.originalPrice != null ? Math.round(Number(data.originalPrice) * 100) : undefined,
    stock: data.stock,
    description: data.description || '',
    mainImage,
    images,
    skus: (data.skus || []).map((sku) => ({
      spec: sku.spec || {},
      price: Math.round(Number(sku.price || 0) * 100),
      stock: sku.stock || 0
    })),
    extraFields: data.extraFields || {},
    status: 'DRAFT'
  };
}

async function normalizeUpdatePayload(data: ProductForm) {
  const mainImage = await serializeImageInput(data.mainImage);
  const galleryImages = await serializeImageList(data.gallery);
  return {
    name: data.name,
    categoryId: data.categoryId,
    price: Math.round(Number(data.price || 0) * 100),
    originalPrice: data.originalPrice != null ? Math.round(Number(data.originalPrice) * 100) : undefined,
    stock: data.stock,
    description: data.description || '',
    mainImage,
    galleryImages: JSON.stringify(galleryImages),
    skus: (data.skus || []).map((sku) => ({
      spec: sku.spec || {},
      price: Math.round(Number(sku.price || 0) * 100),
      stock: sku.stock || 0
    })),
    extraFields: data.extraFields || {}
  };
}

async function serializeImageInput(value: unknown): Promise<string> {
  if (!value) return '';
  if (typeof value === 'string') return value;
  if (typeof File !== 'undefined' && value instanceof File) {
    return fileToDataUrl(value);
  }
  return '';
}

async function serializeImageList(values: unknown): Promise<string[]> {
  if (!Array.isArray(values)) return [];
  const serialized = await Promise.all(values.map((item) => serializeImageInput(item)));
  return serialized.filter(Boolean);
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(typeof reader.result === 'string' ? reader.result : '');
    reader.onerror = () => reject(reader.error || new Error('文件读取失败'));
    reader.readAsDataURL(file);
  });
}

function normalizeProduct(item: any): any {
  if (!item) return item;
  const gallery = Array.isArray(item.gallery)
    ? item.gallery
    : (Array.isArray(item.images) ? item.images : []);
  return {
    ...item,
    gallery,
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
