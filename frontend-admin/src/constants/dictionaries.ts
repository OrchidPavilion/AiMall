type DictLabelMap = Record<string, string>;
type DictTagMap = Record<string, string>;

function normalizeKey(value: unknown, fallback = '') {
  return String(value ?? fallback);
}

function getLabel(map: DictLabelMap, value: unknown, fallback = '-') {
  const key = normalizeKey(value);
  return map[key] || (key ? key : fallback);
}

function getTag(map: DictTagMap, value: unknown) {
  return map[normalizeKey(value)] || '';
}

export const customerGenderLabels: DictLabelMap = {
  MALE: '男',
  FEMALE: '女',
  UNKNOWN: '未知'
};

export const customerLevelLabels: DictLabelMap = {
  REGULAR: '普通',
  VIP: 'VIP',
  SVIP: 'SVIP'
};

export const customerLevelTags: DictTagMap = {
  REGULAR: 'info',
  VIP: 'warning',
  SVIP: 'danger'
};

export const customerStatusLabels: DictLabelMap = {
  PENDING_FOLLOW_UP: '待跟进',
  FOLLOWING: '跟进中',
  DEAL: '已成单',
  REPURCHASE: '复购',
  INVALID: '无效',
  ACTIVE: '活跃',
  INACTIVE: '沉睡'
};

export const productStatusLabels: DictLabelMap = {
  ON_SHELF: '已上架',
  OFF_SHELF: '已下架',
  DRAFT: '草稿'
};

export const productStatusTags: DictTagMap = {
  ON_SHELF: 'success',
  OFF_SHELF: 'info',
  DRAFT: 'warning'
};

export const orderStatusLabels: DictLabelMap = {
  PENDING: '待支付',
  PAID: '已支付',
  SHIPPED: '已发货',
  COMPLETED: '已完成',
  REFUNDED: '已退款',
  CANCELLED: '已取消'
};

export const orderStatusTags: DictTagMap = {
  PENDING: 'warning',
  PAID: 'primary',
  SHIPPED: 'primary',
  COMPLETED: 'success',
  REFUNDED: 'danger',
  CANCELLED: 'info'
};

export const paymentMethodLabels: DictLabelMap = {
  WECHAT: '微信支付',
  ALIPAY: '支付宝',
  BANK: '银行转账',
  CASH: '现金'
};

export const refundStatusLabels: DictLabelMap = {
  NONE: '无退款',
  APPLIED: '申请中',
  APPROVED: '已同意',
  REFUNDED: '已退款',
  REJECTED: '已拒绝'
};

export const refundStatusTags: DictTagMap = {
  APPLIED: 'warning',
  APPROVED: 'primary',
  REFUNDED: 'success',
  REJECTED: 'danger'
};

export const userStatusLabels: DictLabelMap = {
  ACTIVE: '启用',
  DISABLED: '禁用'
};

export const userStatusTags: DictTagMap = {
  ACTIVE: 'success',
  DISABLED: 'danger'
};

export const dictHelpers = {
  label: getLabel,
  tag: getTag
};

export const getCustomerGenderLabel = (v: unknown) => getLabel(customerGenderLabels, v);
export const getCustomerLevelLabel = (v: unknown) => getLabel(customerLevelLabels, v);
export const getCustomerLevelTag = (v: unknown) => getTag(customerLevelTags, v);
export const getCustomerStatusLabel = (v: unknown) => getLabel(customerStatusLabels, v);

export const getProductStatusLabel = (v: unknown) => getLabel(productStatusLabels, v);
export const getProductStatusTag = (v: unknown) => getTag(productStatusTags, v);

export const getOrderStatusLabel = (v: unknown) => getLabel(orderStatusLabels, v);
export const getOrderStatusTag = (v: unknown) => getTag(orderStatusTags, v);

export const getPaymentMethodLabel = (v: unknown) => getLabel(paymentMethodLabels, v);
export const getRefundStatusLabel = (v: unknown) => getLabel(refundStatusLabels, v);
export const getRefundStatusTag = (v: unknown) => getTag(refundStatusTags, v);

export const getUserStatusLabel = (v: unknown) => getLabel(userStatusLabels, v);
export const getUserStatusTag = (v: unknown) => getTag(userStatusTags, v);
