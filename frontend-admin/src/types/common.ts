// 分页响应类型
export interface PageResponse<T> {
  list: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// API 响应基础类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: number;
}

// 表格查询参数
export interface TableQuery {
  page: number;
  pageSize: number;
  keyword?: string;
  startTime?: string;
  endTime?: string;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC';
}

// 用户角色枚举
export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  OPERATION_MANAGER = 'OPERATION_MANAGER',
  CUSTOMER_SERVICE = 'CUSTOMER_SERVICE',
  FINANCE = 'FINANCE'
}

// 操作日志
export interface OperationLog {
  id: number;
  userId: number;
  username: string;
  action: string;
  resourceType: string;
  resourceId: string;
  description: string;
  ip: string;
  userAgent: string;
  createdAt: string;
}

// 文件上传响应
export interface UploadResponse {
  url: string;
  name: string;
  size: number;
  mimeType: string;
}