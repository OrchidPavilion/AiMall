// ===================================
// 常量定义
// ===================================

// 客户等级
export const CUSTOMER_LEVELS = {
  REGULAR: { label: '普通', tagType: 'info' },
  VIP: { label: 'VIP', tagType: 'warning' },
  SVIP: { label: 'SVIP', tagType: 'danger' }
};

// 客户状态
export const CUSTOMER_STATUS = {
  ACTIVE: { label: '活跃', tagType: 'success' },
  INACTIVE: { label: '沉睡', tagType: 'info' },
  FOLLOWING: { label: '跟进中', tagType: 'warning' }
};

// 客户性别
export const GENDER = {
  MALE: '男',
  FEMALE: '女',
  UNKNOWN: '未知'
};

// 订单状态
export const ORDER_STATUS = {
  PENDING: { label: '待支付', tagType: 'warning' },
  PAID: { label: '已支付', tagType: 'info' },
  SHIPPED: { label: '已发货', tagType: 'primary' },
  COMPLETED: { label: '已完成', tagType: 'success' },
  REFUNDED: { label: '已退款', tagType: 'danger' },
  CANCELLED: { label: '已取消', tagType: 'info' }
};

// 支付方式
export const PAYMENT_METHODS = {
  WECHAT: '微信支付',
  ALIPAY: '支付宝',
  BANK: '银行转账',
  CASH: '现金'
};

// 退款状态
export const REFUND_STATUS = {
  NONE: '无退款',
  APPLIED: '申请中',
  APPROVED: '已同意',
  REFUNDED: '已退款',
  REJECTED: '已拒绝'
};

// 商品状态
export const PRODUCT_STATUS = {
  ON_SHELF: { label: '已上架', tagType: 'success' },
  OFF_SHELF: { label: '已下架', tagType: 'info' },
  DRAFT: { label: '草稿', tagType: 'warning' }
};

// 用户角色
export const USER_ROLES = {
  SUPER_ADMIN: { label: '超级管理员', permission: '*' },
  OPERATION_MANAGER: { label: '运营经理', permission: 'operation:*' },
  CUSTOMER_SERVICE: { label: '客服', permission: 'customer:*' },
  FINANCE: { label: '财务', permission: 'finance:*' }
};

// 用户状态
export const USER_STATUS = {
  ACTIVE: '启用',
  DISABLED: '禁用'
};

// 数据范围
export const DATA_SCOPE = {
  ALL: '全部',
  ORG: '所属机构',
  SELF_DEPT: '本部门',
  SELF: '仅个人'
};

// 页面默认配置
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZES = [20, 50, 100, 200];

// 日期格式
export const DATE_FORMATS = {
  DATE: 'yyyy-MM-dd',
  DATETIME: 'yyyy-MM-dd HH:mm:ss',
  TIME: 'HH:mm:ss'
};

// 金额单位
export const CURRENCY_UNIT = '分'; // 后端金额单位：分
export const CURRENCY_SYMBOL = '¥';

// API 超时时间（毫秒）
export const API_TIMEOUT = 15000;

// 图片上传限制
export const UPLOAD_LIMITS = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  MAX_COUNT: 9 // 最多上传9张
};

// 表格操作类型
export const BATCH_ACTIONS = {
  DELETE: 'DELETE',
  ON_SHELF: 'ON_SHELF',
  OFF_SHELF: 'OFF_SHELF',
  SHIP: 'SHIP',
  CANCEL: 'CANCEL'
};

// 路由元信息字段
export const ROUTE_META = {
  HIDDEN: 'hidden',             // 是否隐藏菜单
  AFFIX: 'affix',               // 是否固定标签
  ICON: 'icon',                 // 菜单图标
  TITLE: 'title',               // 菜单标题
  PERMISSION: 'permission',     // 所需权限
  KEEP_ALIVE: 'keepAlive',      // 是否缓存
  REQUIRES_GUEST: 'requiresGuest' // 仅游客访问
};

// 权限前缀
export const PERMISSION_PREFIX = {
  READ: ':read',
  CREATE: ':create',
  UPDATE: ':update',
  DELETE: ':delete'
};