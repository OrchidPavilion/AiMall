import type { TableQuery } from './common';

// 客户等级
export enum CustomerLevel {
  REGULAR = 'REGULAR',
  VIP = 'VIP',
  SVIP = 'SVIP'
}

// 客户状态
export enum CustomerStatus {
  PENDING_FOLLOW_UP = 'PENDING_FOLLOW_UP',
  FOLLOWING = 'FOLLOWING',
  DEAL = 'DEAL',
  REPURCHASE = 'REPURCHASE',
  INVALID = 'INVALID',
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE'
}

// 性别
export enum Gender {
  MALE = 'MALE',
  FEMALE = 'FEMALE',
  UNKNOWN = 'UNKNOWN'
}

// 客户基础信息
export interface Customer {
  id: string;
  name: string;
  phone?: string;
  phoneNumbersJson?: string;
  phones?: Array<{
    full: string;
    prefix: string;
    number: string;
  }>;
  gender: Gender;
  age?: number;
  birthday?: string;
  level: CustomerLevel;
  status: CustomerStatus;
  address?: string;
  extraFieldsJson?: string;
  extraFields?: Record<string, any>;
  lastActiveTime: string;
  createdAt: string;
  updatedAt: string;
  
  // 关联数据
  assignee?: {
    id: number;
    name: string;
  };
}

// 客户查询参数
export interface CustomerQuery extends TableQuery {
  keyword?: string;
  level?: CustomerLevel;
  status?: CustomerStatus;
  assigneeId?: number;
}

// 客户详情扩展
export interface CustomerDetail extends Customer {
  orders?: SimpleOrder[];
  behaviors?: CustomerBehavior[];
  socialAccounts?: Partial<Record<'WECHAT' | 'QQ' | 'DOUYIN' | 'KUAISHOU', { name: string; avatar?: string }>>;
}

// 简单订单信息（客户详情中）
export interface SimpleOrder {
  id: number;
  orderNo: string;
  totalAmount: number;
  status: string;
  createdAt: string;
}

// 客户行为
export interface CustomerBehavior {
  id: number;
  customerId: string | number;
  type: BehaviorType;
  description: string;
  ip?: string;
  userAgent?: string;
  resourceId?: number;  // 关联资源ID (订单ID、商品ID等)
  resourceType?: string;
  createdAt: string;
}

// 行为类型
export enum BehaviorType {
  LOGIN = 'LOGIN',
  VIEW_PRODUCT = 'VIEW_PRODUCT',
  ADD_CART = 'ADD_CART',
  CREATE_ORDER = 'CREATE_ORDER',
  PAY_ORDER = 'PAY_ORDER',
  REFUND = 'REFUND',
  VIEW_AD = 'VIEW_AD'
}

// 分配客户请求
export interface AssignCustomerRequest {
  assigneeId: number;
  remark?: string;
}

// 公海客户池配置
export interface CustomerPoolConfig {
  id: number;
  maxFollowDays: number;    // 最大跟进天数
  autoRecycle: boolean;     // 是否自动回收
  recycleDays: number;      // 回收后天数
  assignRule: 'MANUAL' | 'AUTO' | 'ROTATE'; // 分配规则
}
