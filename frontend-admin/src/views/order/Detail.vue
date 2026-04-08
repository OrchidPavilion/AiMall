<template>
  <div class="order-detail">
    <el-page-header @back="handleBack" class="mb-16" />
    
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card title="订单信息" class="mb-16">
          <el-descriptions :column="2" border>
            <el-descriptions-item v-if="fieldVisible('orderNo')" :label="fieldLabel('orderNo', '订单号')">{{ order.orderNo }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('status')" :label="fieldLabel('status', '订单状态')">
              <el-tag :type="getOrderStatusTagType(order.status)">
                {{ getOrderStatusLabel(order.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('customerName')" :label="fieldLabel('customerName', '客户姓名')">{{ order.customer.name }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('customerPhone')" :label="fieldLabel('customerPhone', '客户手机')">{{ maskPhone(order.customer.phone) }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('address')" :label="fieldLabel('address', '收货地址')" :span="2">{{ order.customer.address || '-' }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('paymentMethod')" :label="fieldLabel('paymentMethod', '支付方式')">{{ getPaymentMethodLabel(order.paymentMethod) }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('createdAt')" :label="fieldLabel('createdAt', '下单时间')">{{ formatDate(order.createdAt) }}</el-descriptions-item>
            <el-descriptions-item v-if="fieldVisible('paidAt')" :label="fieldLabel('paidAt', '支付时间')" :span="2">
              {{ order.paidAt ? formatDate(order.paidAt) : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card title="商品清单" class="mb-16">
          <el-table :data="order.items" stripe>
            <el-table-column prop="productName" label="商品名称" min-width="180" />
            <el-table-column prop="skuSpec" label="规格" width="150" />
            <el-table-column prop="price" label="单价" width="100">
              <template #default="{ row }">
                ¥{{ (row.price / 100).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="total" label="小计" width="100">
              <template #default="{ row }">
                ¥{{ (row.total / 100).toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        
        <el-card title="物流信息">
          <el-descriptions :column="2" border v-if="order.shipping">
            <el-descriptions-item label="物流公司">{{ order.shipping.company }}</el-descriptions-item>
            <el-descriptions-item label="物流单号">{{ order.shipping.trackingNo }}</el-descriptions-item>
            <el-descriptions-item label="发货时间" :span="2">
              {{ order.shipping.shippedAt ? formatDate(order.shipping.shippedAt) : '-' }}
            </el-descriptions-item>
          </el-descriptions>
          <div v-else class="empty-text">暂无物流信息</div>
          
          <div class="mt-16" v-if="order.status === 'PAID'">
            <el-button type="primary" @click="handleShip">发货</el-button>
          </div>
        </el-card>

        <el-card v-if="visibleOrderCustomFields.length" title="自定义字段" class="mt-16">
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="item in visibleOrderCustomFields"
              :key="item.key"
              :label="item.displayName"
            >
              {{ formatOrderCustomFieldValue(item) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card title="费用明细" class="mb-16">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="商品总额">
              ¥{{ (order.totalAmount / 100).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="运费">
              ¥{{ (order.freight / 100).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="优惠金额">
              -¥{{ (order.discount / 100).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="实付金额">
              <span class="text-primary text-bold">¥{{ (order.payAmount / 100).toFixed(2) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card title="退款信息">
          <div v-if="order.refund && order.refund.status !== 'NONE'">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="退款状态">
                <el-tag :type="getRefundStatusTagType(order.refund.status)">
                  {{ getRefundStatusLabel(order.refund.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="退款金额">
                ¥{{ (order.refund.amount / 100).toFixed(2) }}
              </el-descriptions-item>
              <el-descriptions-item label="退款原因">{{ order.refund.reason }}</el-descriptions-item>
              <el-descriptions-item label="申请时间">
                {{ formatDate(order.refund.appliedAt) }}
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="mt-16" v-if="order.refund.status === 'APPLIED'">
              <el-button type="primary" size="small" @click="handleApproveRefund(true)">同意退款</el-button>
              <el-button type="danger" size="small" @click="handleApproveRefund(false)">拒绝退款</el-button>
            </div>
          </div>
          <div v-else class="empty-text">无退款信息</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { orderApi, systemApi } from '@/api';
import {
  getOrderStatusLabel as getOrderStatusLabelFromDict,
  getOrderStatusTag as getOrderStatusTagFromDict,
  getPaymentMethodLabel as getPaymentMethodLabelFromDict,
  getRefundStatusLabel as getRefundStatusLabelFromDict,
  getRefundStatusTag as getRefundStatusTagFromDict
} from '@/constants/dictionaries';
import { formatDate, maskPhone } from '@/utils/format';
import { formatFieldConfigValue, getFieldLabel, isFieldVisible } from '@/utils/fieldConfig';
import type { Order } from '@/types';
import type { FieldConfigItem, FieldConfigSchema } from '@/types';

const route = useRoute();
const router = useRouter();
const orderId = Number(route.params.id);

const order = ref<Order>({} as any);
const orderFieldConfig = ref<FieldConfigSchema | null>(null);
const visibleOrderCustomFields = ref<FieldConfigItem[]>([]);

const fetchOrder = async () => {
  try {
    const { data } = await orderApi.getDetail(orderId);
    order.value = data;
  } catch (error) {
    ElMessage.error('获取订单信息失败');
    router.back();
  }
};

const handleBack = () => {
  router.back();
};

const handleShip = () => {
  // 发货逻辑，可以弹窗或跳转
  ElMessage.info('发货功能待实现');
};

const handleApproveRefund = async (approved: boolean) => {
  try {
    await ElMessageBox.confirm(
      approved ? '确定同意退款吗？' : '确定拒绝退款吗？',
      '提示',
      { type: 'warning' }
    );
    
    await orderApi.refundApprove(orderId, { approved, remark: '' });
    ElMessage.success(approved ? '已同意退款' : '已拒绝退款');
    await fetchOrder();
  } catch (error) {
    // 取消或出错
  }
};

const getOrderStatusLabel = (status: string) => getOrderStatusLabelFromDict(status);
const getOrderStatusTagType = (status: string) => getOrderStatusTagFromDict(status);
const getPaymentMethodLabel = (method: string) => getPaymentMethodLabelFromDict(method);
const getRefundStatusLabel = (status: string) => getRefundStatusLabelFromDict(status);
const getRefundStatusTagType = (status: string) => getRefundStatusTagFromDict(status);

onMounted(() => {
  loadOrderFieldConfig();
  fetchOrder();
});

if (typeof window !== 'undefined') {
  window.addEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
}
onActivated(() => {
  loadOrderFieldConfig();
});
onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
  }
});

async function loadOrderFieldConfig() {
  try {
    const { data } = await systemApi.getFieldConfig('order');
    orderFieldConfig.value = data;
    visibleOrderCustomFields.value = Array.isArray(data?.customFields)
      ? data.customFields.filter((item: any) => item?.visible !== false)
      : [];
  } catch (error) {
    console.warn('load order field config failed', error);
  }
}

function fieldLabel(key: string, fallback: string) {
  return getFieldLabel(orderFieldConfig.value, key, fallback);
}

function fieldVisible(key: string) {
  return isFieldVisible(orderFieldConfig.value, key, true);
}

function formatOrderCustomFieldValue(item: FieldConfigItem) {
  return formatFieldConfigValue(item, (order.value as any)?.extraFields?.[item.key]);
}

function handleFieldConfigChanged(event: Event) {
  const domain = (event as CustomEvent<{ domain?: string }>).detail?.domain;
  if (!domain || domain === 'order') {
    loadOrderFieldConfig();
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.mt-16 {
  margin-top: $spacing-md;
}

.text-bold {
  font-weight: 600;
}

.empty-text {
  text-align: center;
  padding: $spacing-lg;
  color: $text-secondary;
}
</style>
