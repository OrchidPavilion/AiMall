import type { TableQuery } from './common';

// 商品状态
export enum ProductStatus {
  ON_SHELF = 'ON_SHELF',
  OFF_SHELF = 'OFF_SHELF',
  DRAFT = 'DRAFT'
}

// 商品分类
export interface ProductCategory {
  id: number;
  name: string;
  parentId: number | null;
  icon?: string;
  sort: number;
  enabled: boolean;
  productCount: number;
  children: ProductCategory[];
  createdAt: string;
  updatedAt: string;
}

// 商品 SKU
export interface ProductSku {
  id: number;
  productId: number;
  spec: Record<string, string>;  // 规格键值对 { "口味": "巧克力", "规格": "2kg" }
  price: number;                // 价格（分）
  stock: number;                // 库存
  sales: number;                // 销量
}

// 商品基础信息
export interface Product {
  id: number;
  name: string;
  categoryId: number;
  categoryName: string;
  price: number;                // 起售价（分）
  originalPrice?: number;       // 原价（分）
  stock: number;                // 总库存
  sales: number;                // 总销量
  mainImage: string;
  gallery?: string[];           // 图集URL
  description?: string;         // 商品详情 (HTML)
  status: ProductStatus;
  skus?: ProductSku[];
  extraFieldsJson?: string;
  extraFields?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// 商品查询参数
export interface ProductQuery extends TableQuery {
  keyword?: string;
  categoryId?: number;
  status?: ProductStatus;
  hasStock?: boolean;
  minPrice?: number;
  maxPrice?: number;
}

// 创建/更新商品参数
export interface ProductForm {
  name: string;
  categoryId: number;
  price: number;
  originalPrice?: number;
  stock: number;
  description?: string;
  mainImage: File | string;
  gallery?: File[] | string[];
  skus?: ProductSkuForm[];
  extraFields?: Record<string, any>;
}

// SKU 表单
export interface ProductSkuForm {
  spec: Record<string, string>;
  price: number;
  stock: number;
}
