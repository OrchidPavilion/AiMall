import type { TableQuery, UserRole } from './common';

// 系统配置
export interface SystemConfig {
  id: number;
  systemName: string;
  logoUrl?: string;
  themeColor: string;
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireNumber: boolean;
    requireSpecialChar: boolean;
    expireDays: number;
  };
  sessionTimeout: number;     // 会话超时时间（秒）
  registrationEnabled: boolean; // 是否允许注册
  contactEmail: string;
  contactPhone: string;
  updatedAt: string;
}

// 后台用户
export interface User {
  id: number;
  username: string;
  realName: string;
  phone: string;
  role: UserRole;
  roles?: UserRole[];
  status: 'ACTIVE' | 'DISABLED';
  lastLoginAt?: string;
  lastLoginIp?: string;
  createdAt: string;
}

// 用户创建/更新表单
export interface UserForm {
  username: string;
  password?: string;          // 创建必填，编辑可选
  realName: string;
  phone: string;
  roleId: number;
  status: 'ACTIVE' | 'DISABLED';
}

export type UserDTO = User;
export type UserCreateRequest = UserForm;
export type UserUpdateRequest = Partial<UserForm>;

// 角色
export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: RolePermission[];
  dataScope: 'ALL' | 'ORG' | 'SELF_DEPT' | 'SELF';
  createdAt: string;
  updatedAt: string;
}

// 角色权限
export interface RolePermission {
  module: string;             // 模块名称
  actions: string[];          // 操作权限 ['READ', 'CREATE', 'UPDATE', 'DELETE']
  dataScope?: string;         // 数据范围
}

// 接口配置
export interface Integration {
  id: number;
  name: string;
  type: 'PAYMENT' | 'LOGISTICS' | 'SMS' | 'EMAIL' | 'ANALYTICS';
  config: Record<string, any>; // 配置项（JSON）
  enabled: boolean;
  lastTestAt?: string;
  lastTestResult?: 'SUCCESS' | 'FAILED';
  createdAt: string;
  updatedAt: string;
}

// 接口测试请求
export interface IntegrationTestRequest {
  url: string;
  method: 'GET' | 'POST';
  headers?: Record<string, string>;
  body?: any;
}

// 商城首页模块（管理后台排版页）
export interface StoreModule {
  id: string | number;
  type: string;
  enabled: boolean;
  sort?: number;
  config: Record<string, any>;
}

// 操作日志查询
export interface OperationLogQuery extends TableQuery {
  userId?: number;
  action?: string;
  resourceType?: string;
  startTime?: string;
  endTime?: string;
}

export interface FieldConfigOption {
  label: string;
  value: string;
}

export interface FieldConfigItem {
  key: string;
  systemName: string;
  displayName: string;
  fieldType: string;
  builtin: boolean;
  visible: boolean;
  sort?: number;
  options?: FieldConfigOption[];
}

export interface FieldConfigSchema {
  domain: 'customer' | 'product' | 'order';
  baseFields: FieldConfigItem[];
  customFields: FieldConfigItem[];
}

export interface AppPreviewContext {
  adminUsername?: string;
  adminRealName?: string;
  adminPhone?: string;
  customerId?: string;
  customerName?: string;
  customerPhone?: string;
  h5PreviewUrl?: string;
  linkedToCustomer?: boolean;
}

export interface AppPreviewTrackPayload {
  customerId?: string | number;
  customerPhone?: string;
  actionType: string;
  actionVerb: string;
  infoType?: string;
  detail: string;
  relatedOrderId?: number;
  relatedProductId?: number;
  trailPath?: string[];
  page?: string;
}
