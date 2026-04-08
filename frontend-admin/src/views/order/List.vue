<template>
  <div class="order-list">
    <ListPageScaffold
      :current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      @current-change="setPage"
      @size-change="setPageSize"
    >
      <template #search>
        <SchemaSearchForm :model="searchForm as any" :fields="searchFields" @search="handleSearch" @reset="handleReset" />
      </template>
      
      <SchemaTable :data="tableData" :columns="tableColumns" :loading="loading">
        <template #cell-customerName="{ row }">
          {{ row.customer?.name || '-' }}
        </template>
        <template #cell-customerPhone="{ row }">
            <span class="phone-masked">{{ maskPhone(row.customer.phone) }}</span>
        </template>
        <template #cell-items="{ row }">
          <div v-for="item in row.items" :key="item.id" class="order-item">
              <span>{{ item.productName }}</span>
              <span class="qty">x{{ item.quantity }}</span>
          </div>
        </template>
        <template #cell-payAmount="{ row }">
          <span class="text-primary">¥{{ (row.payAmount / 100).toFixed(2) }}</span>
        </template>
        <template #cell-status="{ row }">
          <el-tag :type="getStatusTagType(row.status)">
            {{ getOrderStatusLabel(row.status) }}
          </el-tag>
        </template>
        <template #cell-createdAt="{ row }">
          {{ formatDate(row.createdAt) }}
        </template>
        <template #cell-actions="{ row }">
          <el-button link type="primary" @click="handleView(row)">详情</el-button>
          <el-button v-if="row.status === 'PAID'" link type="primary" @click="handleShip(row)">发货</el-button>
        </template>
      </SchemaTable>
    </ListPageScaffold>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { metaApi, orderApi } from '@/api';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaSearchForm, { type SchemaSearchField } from '@/components/common/SchemaSearchForm.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import { usePagedList } from '@/composables/usePagedList';
import { getOrderStatusLabel as getOrderStatusLabelFromDict, getOrderStatusTag } from '@/constants/dictionaries';
import { formatDate, maskPhone } from '@/utils/format';
import type { Order } from '@/types';

const router = useRouter();
const defaultSearchFields: SchemaSearchField[] = [
  { prop: 'orderNo', label: '订单号', type: 'input', placeholder: '请输入订单号' },
  { prop: 'customerName', label: '客户', type: 'input', placeholder: '客户姓名/手机号' },
  {
    prop: 'status',
    label: '状态',
    type: 'select',
    options: [
      { label: '待支付', value: 'PENDING' },
      { label: '已支付', value: 'PAID' },
      { label: '已发货', value: 'SHIPPED' },
      { label: '已完成', value: 'COMPLETED' },
      { label: '已退款', value: 'REFUNDED' },
      { label: '已取消', value: 'CANCELLED' }
    ]
  }
];
const defaultTableColumns: SchemaTableColumn<Order>[] = [
  { prop: 'orderNo', label: '订单号', minWidth: 180 },
  { key: 'customerName', label: '客户', minWidth: 100, slot: 'customerName' },
  { key: 'customerPhone', label: '手机号', width: 120, slot: 'customerPhone' },
  { key: 'items', label: '商品', minWidth: 200, slot: 'items' },
  { key: 'payAmount', label: '实付金额', width: 100, slot: 'payAmount' },
  { key: 'status', label: '订单状态', width: 100, slot: 'status' },
  { key: 'createdAt', label: '下单时间', width: 160, slot: 'createdAt' },
  { key: 'actions', label: '操作', width: 150, fixed: 'right', slot: 'actions' }
];
const searchFields = ref<SchemaSearchField[]>(defaultSearchFields);
const tableColumns = ref<SchemaTableColumn<Order>[]>(defaultTableColumns);
const {
  loading,
  tableData,
  query: searchForm,
  pagination,
  fetchData,
  search,
  reset,
  setPage,
  setPageSize
} = usePagedList<{ orderNo: string; customerName: string; status: any }, Order>({
  initialQuery: {
    orderNo: '',
    customerName: '',
    status: undefined
  },
  fetcher: async (params) => {
    const { data } = await orderApi.getList(params);
    return data;
  },
  onError: (error) => {
    console.error('Failed to fetch orders:', error);
  }
});

const handleSearch = () => {
  search();
};

const handleReset = () => {
  reset();
};

const handleView = (row: Order) => {
  router.push(`/order/detail/${row.id}`);
};

const handleShip = (row: Order) => {
  router.push(`/order/detail/${row.id}?action=ship`);
};

const getOrderStatusLabel = (status: string) => getOrderStatusLabelFromDict(status);
const getStatusTagType = (status: string) => getOrderStatusTag(status);

onMounted(() => {
  loadMeta();
  fetchData();
});

async function loadMeta() {
  try {
    const { data } = await metaApi.getOrderListMeta();
    const remoteSearchFields = Array.isArray(data?.searchFields) ? data.searchFields : [];
    const remoteColumns = Array.isArray(data?.columns) ? data.columns : [];
    const normalizedSearchFields = remoteSearchFields
      .filter((f: any) => f && typeof f.prop === 'string' && typeof f.label === 'string' && typeof f.type === 'string')
      .map((f: any) => ({
        prop: f.prop,
        label: f.label,
        type: f.type,
        placeholder: f.placeholder,
        options: Array.isArray(f.options) ? f.options : undefined
      })) as SchemaSearchField[];
    const normalizedColumns = remoteColumns
      .filter((c: any) => c && typeof c.label === 'string')
      .map((c: any) => ({
        key: c.key,
        prop: c.prop,
        label: c.label,
        width: c.width,
        minWidth: c.minWidth,
        fixed: c.fixed,
        slot: c.slot
      })) as SchemaTableColumn<Order>[];
    if (normalizedSearchFields.length) searchFields.value = normalizedSearchFields;
    if (normalizedColumns.length) tableColumns.value = normalizedColumns;
  } catch (error) {
    console.warn('Failed to load order list meta, fallback to local schema', error);
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.order-item {
  display: flex;
  justify-content: space-between;
  
  .qty {
    color: $text-secondary;
    font-size: $font-size-sm;
  }
}

.phone-masked {
  font-family: monospace;
  letter-spacing: 1px;
}
</style>
