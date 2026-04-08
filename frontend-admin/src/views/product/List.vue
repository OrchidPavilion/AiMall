<template>
  <div class="product-list">
    <ListPageScaffold
      :current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      @current-change="setPage"
      @size-change="setPageSize"
    >
      <template #search>
        <SchemaSearchForm :model="searchForm as any" :fields="searchFields" @search="handleSearch" @reset="handleReset">
          <template #field-categoryId>
            <el-select v-model="searchForm.categoryId" placeholder="全部分类" clearable>
              <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
            </el-select>
          </template>
        </SchemaSearchForm>
      </template>
      
      <template #actions>
        <div class="left">
          <el-button type="primary" size="small" @click="handleCreate">新增商品</el-button>
        </div>
      </template>
      
      <template #footer-left>
        <BatchActionBar :count="selectedRows.length">
          <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
          <el-button size="small" @click="handleBatchOffShelf">批量下架</el-button>
          <el-button size="small" type="primary" plain @click="handleBatchUpdateStock">批量修改库存数</el-button>
        </BatchActionBar>
      </template>
      
      <SchemaTable
        :data="tableData"
        :columns="tableColumns"
        :loading="loading"
        selection
        row-key="id"
        @selection-change="handleSelectionChange"
      >
        <template #cell-price="{ row }">¥{{ (row.price / 100).toFixed(2) }}</template>
        <template #cell-status="{ row }">
          <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
        <template #cell-createdAt="{ row }">{{ formatDate(row.createdAt) }}</template>
        <template #cell-actions="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleToggleStatus(row)">
            {{ row.status === 'ON_SHELF' ? '下架' : '上架' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </SchemaTable>
    </ListPageScaffold>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useProductStore } from '@/stores/product.store';
import { metaApi, productApi, storeApi } from '@/api';
import BatchActionBar from '@/components/common/BatchActionBar.vue';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaSearchForm, { type SchemaSearchField } from '@/components/common/SchemaSearchForm.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import { usePagedList } from '@/composables/usePagedList';
import { getProductStatusLabel, getProductStatusTag } from '@/constants/dictionaries';
import { formatDate } from '@/utils/format';
import type { Product, ProductCategory } from '@/types';

const router = useRouter();
const productStore = useProductStore();
const defaultSearchFields: SchemaSearchField[] = [
  { prop: 'keyword', label: '关键词', type: 'input', placeholder: '商品名称' },
  { prop: 'categoryId', label: '分类', type: 'custom' },
  {
    prop: 'status',
    label: '状态',
    type: 'select',
    options: [
      { label: '已上架', value: 'ON_SHELF' },
      { label: '已下架', value: 'OFF_SHELF' },
      { label: '草稿', value: 'DRAFT' }
    ]
  }
];
const defaultTableColumns: SchemaTableColumn<Product>[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'name', label: '商品名称', minWidth: 180 },
  { prop: 'categoryName', label: '分类', width: 120 },
  { key: 'price', label: '价格', width: 120, slot: 'price' },
  { prop: 'stock', label: '库存', width: 80 },
  { prop: 'sales', label: '销量', width: 80 },
  { key: 'status', label: '状态', width: 100, slot: 'status' },
  { key: 'createdAt', label: '创建时间', width: 160, slot: 'createdAt' },
  { key: 'actions', label: '操作', width: 180, fixed: 'right', slot: 'actions' }
];
const searchFields = ref<SchemaSearchField[]>(defaultSearchFields);
const tableColumns = ref<SchemaTableColumn<Product>[]>(defaultTableColumns);

const categories = ref<ProductCategory[]>([]);
const selectedRows = ref<Product[]>([]);
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
} = usePagedList<{ keyword: string; categoryId: number | undefined; status: any }, Product>({
  initialQuery: {
    keyword: '',
    categoryId: undefined,
    status: undefined
  },
  fetcher: async (params) => {
    const { data } = await productApi.getList(params);
    return data;
  },
  onError: (error) => {
    console.error('Failed to fetch products:', error);
  }
});

const fetchCategories = async () => {
  try {
    const { data } = await storeApi.getCategoryTree();
    categories.value = data;
  } catch (error) {
    console.error('Failed to fetch categories:', error);
  }
};

const handleSearch = () => {
  search();
};

const handleReset = () => {
  reset();
};

const handleCreate = () => {
  router.push('/product/create');
};

const handleEdit = (row: Product) => {
  router.push(`/product/edit/${row.id}`);
};

const handleToggleStatus = async (row: Product) => {
  try {
    const newStatus = row.status === 'ON_SHELF' ? 'OFF_SHELF' : 'ON_SHELF';
    await productApi.toggleStatus(row.id, newStatus);
    await fetchData();
  } catch (error) {
    console.error('Toggle status failed:', error);
  }
};

const handleDelete = async (row: Product) => {
  // 确认删除逻辑
  try {
    await productApi.delete(row.id);
    await fetchData();
  } catch (error) {
    console.error('Delete failed:', error);
  }
};

function handleSelectionChange(rows: Product[]) {
  selectedRows.value = rows || [];
}

async function handleBatchOffShelf() {
  if (selectedRows.value.length < 2) return;
  try {
    await ElMessageBox.confirm(`确认将已选 ${selectedRows.value.length} 个商品批量下架？`, '批量下架', {
      type: 'warning'
    });
    await Promise.all(selectedRows.value.map((row) => productApi.toggleStatus(Number(row.id), 'OFF_SHELF')));
    ElMessage.success('批量下架成功');
    selectedRows.value = [];
    await fetchData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '批量下架失败');
    }
  }
}

async function handleBatchUpdateStock() {
  if (selectedRows.value.length < 2) return;
  try {
    const { value } = await ElMessageBox.prompt(`为已选 ${selectedRows.value.length} 个商品设置统一库存数`, '批量修改库存', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPattern: /^\\d+$/,
      inputErrorMessage: '请输入非负整数库存'
    });
    const stock = Number(value);
    await Promise.all(selectedRows.value.map((row) => productApi.updateStock(Number(row.id), stock)));
    ElMessage.success('批量修改库存成功');
    selectedRows.value = [];
    await fetchData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '批量修改库存失败');
    }
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length < 2) return;
  try {
    await ElMessageBox.confirm(`确认删除已选 ${selectedRows.value.length} 个商品？`, '批量删除', {
      type: 'warning'
    });
    const results = await Promise.allSettled(selectedRows.value.map((row) => productApi.delete(Number(row.id))));
    const failed = results.filter((r): r is PromiseRejectedResult => r.status === 'rejected');
    if (failed.length === 0) {
      ElMessage.success('批量删除成功');
    } else {
      const firstMsg = failed[0]?.reason?.message || '删除失败';
      ElMessage.warning(`成功 ${results.length - failed.length} 条，失败 ${failed.length} 条：${firstMsg}`);
    }
    selectedRows.value = [];
    await fetchData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '批量删除失败');
    }
  }
}

const getStatusLabel = (status: string) => getProductStatusLabel(status);
const getStatusTagType = (status: string) => getProductStatusTag(status);

onMounted(() => {
  loadMeta();
  fetchCategories();
  fetchData();
});

async function loadMeta() {
  try {
    const { data } = await metaApi.getProductListMeta();
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
      })) as SchemaTableColumn<Product>[];
    if (normalizedSearchFields.length) searchFields.value = normalizedSearchFields;
    if (normalizedColumns.length) tableColumns.value = normalizedColumns;
  } catch (error) {
    console.warn('Failed to load product list meta, fallback to local schema', error);
  }
}
</script>

<style lang="scss" scoped>
.table-actions-spacer {
  width: 100%;
}
</style>
