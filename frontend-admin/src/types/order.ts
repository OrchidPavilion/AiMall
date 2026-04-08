import type { TableQuery } from './common';

// 订单状态
export enum OrderStatus {
  PENDING = 'PENDING',       // 待支付
  PAID = 'PAID',            // 已支付
  SHIPPED = 'SHIPPED',      // 已发货
  COMPLETED = 'COMPLETED',  // 已完成
  REFUNDED = 'REFUNDED',    // 已退款
  CANCELLED = 'CANCELLED'   // 已取消
}

// 支付状态
export enum PaymentStatus {
  UNPAID = 'UNPAID',
  PAID = 'PAID',
  REFUNDED = 'REFUNDED'
}

// 支付方式
export enum PaymentMethod {
  WECHAT = 'WECHAT',
  ALIPAY = 'ALIPAY',
  BANK = 'BANK',
  CASH = 'CASH'
}

// 退款状态
export enum RefundStatus {
  NONE = 'NONE',
  APPLIED = 'APPLIED',
  APPROVED = 'APPROVED',
  REFUNDED = 'REFUNDED',
  REJECTED = 'REJECTED'
}

// 订单项
export interface OrderItem {
  id: number;
  productId: number;
  productName: string;
  skuId?: number;
  skuSpec?: string;          // 规格描述
  quantity: number;
  price: number;             // 单价（分）
  total: number;             // 小计（分）
  image?: string;
}

// 物流信息
export interface ShippingInfo {
  company: string;           // 物流公司
  trackingNo: string;        // 物流单号
  shippedAt?: string;
}

// 退款信息
export interface RefundInfo {
  status: RefundStatus;
  amount: number;            // 退款金额（分）
  reason: string;
  evidence?: string[];       // 凭证图片URL
  appliedAt?: string;
  approvedAt?: string;
  refundedAt?: string;
  remark?: string;
}

// 订单基础信息
export interface Order {
  id: number;
  orderNo: string;
  customer: {
    id: number;
    name: string;
    phone: string;
    address?: string;
  };
  items: OrderItem[];
  totalAmount: number;       // 商品总额（分）
  freight: number;           // 运费（分）
  discount: number;          // 优惠金额（分）
  payAmount: number;         // 实付金额（分）
  status: OrderStatus;
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
  paidAt?: string;
  shipping?: ShippingInfo;
  refund?: RefundInfo;
  extraFieldsJson?: string;
  extraFields?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// 订单查询参数
export interface OrderQuery extends TableQuery {
  orderNo?: string;
  customerName?: string;
  customerPhone?: string;
  status?: OrderStatus;
  paymentStatus?: PaymentStatus;
  startTime?: string;
  endTime?: string;
}

// 订单发货请求
export interface ShipOrderRequest {
  shippingCompany: string;
  trackingNo: string;
  remark?: string;
}

// 退款申请请求
export interface RefundApplyRequest {
  amount: number;
  reason: string;
  evidence?: string[];
}

// 退款审核请求
export interface RefundApproveRequest {
  approved: boolean;
  remark?: string;
}

// 订单操作历史
export interface OrderHistory {
  id: number;
  orderId: number;
  action: string;
  description: string;
  operator?: string;
  createdAt: string;
}
