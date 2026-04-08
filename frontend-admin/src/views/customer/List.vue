<template>
  <div class="customer-list">
    <ListPageScaffold
      :current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
    >
      <template #search>
        <SchemaSearchForm
          :model="searchForm as any"
          :fields="searchFields"
          @search="handleSearch"
          @reset="handleReset"
        />
      </template>

      <template #actions>
        <div class="left">
          <el-button type="primary" size="small" @click="openCreateDrawer">新增客户</el-button>
          <el-button size="small" @click="handleExport">导出</el-button>
        </div>
      </template>

      <template #footer-left>
        <BatchActionBar :count="selectedRows.length">
          <el-button size="small" type="danger" @click="handleBatchDeleteCustomers">批量删除</el-button>
          <el-button size="small" type="primary" plain @click="openBatchEditDialog">批量编辑</el-button>
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
        <template #cell-name="{ row }">
          <el-button link type="primary" @click="openDetailDrawer(row.id)">{{ row.name }}</el-button>
        </template>
        <template #cell-phone="{ row }">
          <el-button link type="primary" @click="openDetailDrawer(row.id)">{{ row.phone || '-' }}</el-button>
        </template>
        <template #cell-gender="{ row }">{{ getGenderLabel(row.gender) }}</template>
        <template #cell-level="{ row }">
          <el-tag :type="getLevelTagType(row.level)">{{ getLevelLabel(row.level) }}</el-tag>
        </template>
        <template #cell-status="{ row }">
          <el-tag>{{ getStatusLabel(row.status) }}</el-tag>
        </template>
        <template #cell-assignee="{ row }">{{ row.assignee?.name || '-' }}</template>
        <template #cell-lastActiveTime="{ row }">{{ formatDate(row.lastActiveTime) }}</template>
      </SchemaTable>
    </ListPageScaffold>

    <DetailDrawerLayout
      v-model="detailDrawerVisible"
      v-model:activeTab="detailActiveTab"
      :loading="detailLoading"
      size="50%"
      class="customer-detail-drawer"
    >
      <template #actions>
        <el-button type="primary" @click="openEditDrawer">编辑</el-button>
        <el-button @click="detailDrawerVisible = false">关闭</el-button>
      </template>

      <template #summary>
        <div v-if="fieldVisible('name')" class="summary-item">
          <span class="label">客户姓名</span>
          <span class="value">{{ detailCustomer?.name || '-' }}</span>
        </div>
        <div v-if="fieldVisible('phones')" class="summary-item">
          <span class="label">手机号码</span>
          <div class="phones-inline">
            <span v-for="phone in detailPhones" :key="phone.full" class="phone-pill">{{ phone.full }}</span>
            <span v-if="detailPhones.length === 0" class="value">-</span>
          </div>
        </div>
      </template>

      <el-tab-pane label="基本信息" name="basic">
              <el-descriptions :column="2" border>
                <el-descriptions-item v-if="fieldVisible('gender')" :label="fieldLabel('gender', '性别')">{{ getGenderLabel(detailCustomer?.gender) }}</el-descriptions-item>
                <el-descriptions-item v-if="fieldVisible('birthday')" :label="fieldLabel('birthday', '生日')">{{ detailCustomer?.birthday || '-' }}</el-descriptions-item>
                <el-descriptions-item label="年龄">{{ detailCustomer?.age ?? '-' }}</el-descriptions-item>
                <el-descriptions-item v-if="fieldVisible('level')" :label="fieldLabel('level', '等级')">{{ getLevelLabel(detailCustomer?.level) }}</el-descriptions-item>
                <el-descriptions-item v-if="fieldVisible('status')" :label="fieldLabel('status', '状态')">{{ getStatusLabel(detailCustomer?.status) }}</el-descriptions-item>
                <el-descriptions-item label="跟进人">{{ detailCustomer?.assignee?.name || '未分配' }}</el-descriptions-item>
                <el-descriptions-item v-if="fieldVisible('address')" :label="fieldLabel('address', '地址')" :span="2">{{ detailCustomer?.address || '-' }}</el-descriptions-item>
                <el-descriptions-item
                  v-for="item in visibleCustomerCustomFields"
                  :key="`custom-desc-${item.key}`"
                  :label="item.displayName"
                >
                  {{ formatCustomerCustomFieldValue(item) }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ formatDate(detailCustomer?.createdAt) }}</el-descriptions-item>
                <el-descriptions-item label="更新时间">{{ formatDate(detailCustomer?.updatedAt) }}</el-descriptions-item>
              </el-descriptions>
      </el-tab-pane>

      <el-tab-pane label="订单" name="orders">
        <el-table :data="detailOrders" v-loading="detailOrdersLoading" stripe>
          <el-table-column prop="orderNo" label="订单号" min-width="160" />
          <el-table-column prop="payAmount" label="实付金额" width="110">
            <template #default="{ row }">¥{{ ((row.payAmount || 0) / 100).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">{{ getOrderStatusLabel(row.status) }}</template>
          </el-table-column>
          <el-table-column prop="createdAt" label="下单时间" width="170">
            <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="社交" name="social">
        <div class="social-list">
          <div v-for="item in socialRows" :key="item.key" class="social-card">
            <div class="social-logo" :style="{ background: item.color }">{{ item.logo }}</div>
            <div class="social-content">
              <div class="social-platform">{{ item.label }}</div>
              <div v-if="item.bound" class="social-bound">
                <el-avatar :size="28" :src="item.avatar">{{ item.label[0] }}</el-avatar>
                <span>{{ item.name }}</span>
              </div>
              <div v-else class="social-unbound">未绑定</div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="行为轨迹" name="behaviors">
        <div v-loading="detailBehaviorsLoading">
          <BehaviorTimeline :items="detailBehaviors" />
        </div>
      </el-tab-pane>
    </DetailDrawerLayout>

    <SchemaDrawerForm
      ref="formRef"
      v-model="formDrawerVisible"
      class="customer-form-drawer"
      :title="formMode === 'create' ? '新增客户' : '编辑客户'"
      :model="formState as any"
      :rules="formRules"
      :fields="effectiveCustomerFormFields"
      :loading="formSubmitting"
      :before-close="handleFormDrawerBeforeClose"
      @cancel="requestCloseFormDrawer"
      @submit="submitForm"
    >
      <template #field-phones>
        <div class="phones-editor">
          <div v-for="(phone, index) in formState.phones" :key="index" class="phone-row">
            <el-input v-model="phone.prefix" class="phone-prefix-input" maxlength="5" placeholder="86">
              <template #prepend>+</template>
            </el-input>
            <el-input v-model="phone.number" class="phone-number-input" maxlength="20" placeholder="手机号" />
            <el-button v-if="formState.phones.length > 1" text type="danger" @click="removeFormPhone(index)">
              删除
            </el-button>
          </div>
          <div v-if="phoneInlineError" class="phone-inline-error">{{ phoneInlineError }}</div>
          <el-button text type="primary" @click="addFormPhone">+ 添加手机号</el-button>
        </div>
      </template>
      <template
        v-for="customField in customerCustomFormFields"
        :key="`field-custom-${customField.prop}`"
        #[`field-${customField.prop}`]="{ field }"
      >
        <el-input
          v-if="field.type === 'input'"
          v-model="formState.extraFields[field.prop]"
          :placeholder="field.placeholder"
          :maxlength="field.maxlength"
          :show-word-limit="field.showWordLimit"
          clearable
        />
        <el-input
          v-else-if="field.type === 'textarea'"
          v-model="formState.extraFields[field.prop]"
          type="textarea"
          :rows="field.rows || 3"
          :placeholder="field.placeholder"
        />
        <el-input-number
          v-else-if="field.type === 'number'"
          v-model="formState.extraFields[field.prop]"
          :min="0"
          class="w-100"
        />
        <el-date-picker
          v-else-if="field.type === 'date'"
          v-model="formState.extraFields[field.prop]"
          type="date"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          class="w-100"
        />
        <el-date-picker
          v-else-if="field.type === 'datetime'"
          v-model="formState.extraFields[field.prop]"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          format="YYYY-MM-DD HH:mm:ss"
          class="w-100"
        />
        <el-select
          v-else-if="field.type === 'select'"
          v-model="formState.extraFields[field.prop]"
          class="w-100"
          clearable
        >
          <el-option v-for="option in field.options || []" :key="String(option.value)" :label="option.label" :value="option.value" />
        </el-select>
        <el-radio-group v-else-if="field.type === 'radio'" v-model="formState.extraFields[field.prop]">
          <el-radio v-for="option in field.options || []" :key="String(option.value)" :label="option.value">{{ option.label }}</el-radio>
        </el-radio-group>
        <el-checkbox-group v-else-if="field.type === 'checkbox'" v-model="formState.extraFields[field.prop]">
          <el-checkbox v-for="option in field.options || []" :key="String(option.value)" :label="option.value">{{ option.label }}</el-checkbox>
        </el-checkbox-group>
      </template>
    </SchemaDrawerForm>

    <el-dialog v-model="batchEditVisible" title="批量编辑客户" width="620px" destroy-on-close>
      <div class="batch-edit-dialog">
        <el-form label-width="110px">
          <el-form-item label="选择字段">
            <el-checkbox-group v-model="batchEditFields">
              <el-checkbox v-for="field in batchEditableFields" :key="field.prop" :label="field.prop">
                {{ field.label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <SchemaFormRenderer
            v-if="batchEditSchemaFields.length"
            :model="batchEditValues"
            :fields="batchEditSchemaFields"
          />
        </el-form>
      </div>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="batchEditVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchEditCustomers">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onActivated, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox, type FormRules } from 'element-plus';
import { customerApi, metaApi, orderApi, systemApi } from '@/api';
import BatchActionBar from '@/components/common/BatchActionBar.vue';
import BehaviorTimeline from '@/components/common/BehaviorTimeline.vue';
import DetailDrawerLayout from '@/components/common/DetailDrawerLayout.vue';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import SchemaSearchForm, { type SchemaSearchField } from '@/components/common/SchemaSearchForm.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import SchemaFormRenderer, { type SchemaFormField } from '@/components/common/SchemaFormRenderer.vue';
import {
  getCustomerGenderLabel,
  getCustomerLevelLabel,
  getCustomerLevelTag,
  getCustomerStatusLabel,
  getOrderStatusLabel as getOrderStatusLabelFromDict
} from '@/constants/dictionaries';
import { formatDate } from '@/utils/format';
import {
  applyFieldConfigToSchemaFields,
  buildCustomSchemaFields,
  formatFieldConfigValue,
  getFieldLabel,
  isFieldVisible
} from '@/utils/fieldConfig';
import type { Customer, CustomerDetail } from '@/types';
import type { FieldConfigItem, FieldConfigSchema } from '@/types';

type PhoneRow = { prefix: string; number: string };
type FormMode = 'create' | 'edit';

const loading = ref(false);
const tableData = ref<Customer[]>([]);
const selectedRows = ref<Customer[]>([]);
const pagination = reactive({ page: 1, pageSize: 20, total: 0 });
const searchForm = reactive({ keyword: '', level: undefined as any, status: undefined as any });
const defaultSearchFields: SchemaSearchField[] = [
  { prop: 'keyword', label: '关键词', type: 'input', placeholder: '姓名/手机号' },
  {
    prop: 'level',
    label: '等级',
    type: 'select',
    options: [
      { label: '普通', value: 'REGULAR' },
      { label: 'VIP', value: 'VIP' },
      { label: 'SVIP', value: 'SVIP' }
    ]
  },
  {
    prop: 'status',
    label: '状态',
    type: 'select',
    options: [
      { label: '待跟进', value: 'PENDING_FOLLOW_UP' },
      { label: '跟进中', value: 'FOLLOWING' },
      { label: '已成单', value: 'DEAL' },
      { label: '复购', value: 'REPURCHASE' },
      { label: '无效', value: 'INVALID' },
      { label: '活跃', value: 'ACTIVE' },
      { label: '沉睡', value: 'INACTIVE' }
    ]
  }
];
const defaultTableColumns: SchemaTableColumn<Customer>[] = [
  { label: '客户姓名', minWidth: 140, slot: 'name', key: 'name' },
  { label: '手机号码', minWidth: 180, slot: 'phone', key: 'phone' },
  { label: '性别', width: 80, slot: 'gender', key: 'gender' },
  { label: '等级', width: 100, slot: 'level', key: 'level' },
  { label: '状态', width: 110, slot: 'status', key: 'status' },
  { label: '跟进人', minWidth: 100, slot: 'assignee', key: 'assignee' },
  { label: '最后活跃', width: 160, slot: 'lastActiveTime', key: 'lastActiveTime' }
];
const searchFields = ref<SchemaSearchField[]>(defaultSearchFields);
const tableColumns = ref<SchemaTableColumn<Customer>[]>(defaultTableColumns);
const defaultCustomerFormFields: SchemaDrawerField[] = [
  { prop: 'name', label: '姓名', type: 'input', maxlength: 50, showWordLimit: true, placeholder: '请输入客户姓名' },
  { prop: 'phones', label: '手机号码', type: 'custom' },
  { prop: 'birthday', label: '生日', type: 'date', placeholder: '请选择生日', className: 'w-100' },
  {
    prop: 'gender',
    label: '性别',
    type: 'radio',
    options: [
      { label: '男', value: 'MALE' },
      { label: '女', value: 'FEMALE' },
      { label: '未知', value: 'UNKNOWN' }
    ]
  },
  {
    prop: 'status',
    label: '状态',
    type: 'select',
    className: 'w-100',
    options: [
      { label: '待跟进', value: 'PENDING_FOLLOW_UP' },
      { label: '跟进中', value: 'FOLLOWING' },
      { label: '已成单', value: 'DEAL' },
      { label: '复购', value: 'REPURCHASE' },
      { label: '无效', value: 'INVALID' }
    ]
  },
  {
    prop: 'level',
    label: '等级',
    type: 'select',
    className: 'w-100',
    options: [
      { label: '普通', value: 'REGULAR' },
      { label: 'VIP', value: 'VIP' },
      { label: 'SVIP', value: 'SVIP' }
    ]
  },
  { prop: 'address', label: '地址', type: 'textarea', rows: 3, placeholder: '请输入联系地址' }
];
const customerFormFields = ref<SchemaDrawerField[]>(defaultCustomerFormFields);
const customerFieldConfig = ref<FieldConfigSchema | null>(null);

const detailDrawerVisible = ref(false);
const detailLoading = ref(false);
const detailCustomer = ref<CustomerDetail | null>(null);
const detailActiveTab = ref<'basic' | 'orders' | 'social' | 'behaviors'>('basic');
const detailOrders = ref<any[]>([]);
const detailOrdersLoading = ref(false);
const detailBehaviors = ref<any[]>([]);
const detailBehaviorsLoading = ref(false);

const formDrawerVisible = ref(false);
const formMode = ref<FormMode>('create');
const editingCustomerId = ref<string | null>(null);
const formSubmitting = ref(false);
const phoneInlineError = ref('');
const formRef = ref<SchemaDrawerFormExposed>();
const closingBySubmit = ref(false);
const pendingSaveOnClose = ref(false);
const formInitialSnapshot = ref('');

const formState = reactive({
  name: '',
  phones: [{ prefix: '86', number: '' }] as PhoneRow[],
  birthday: '',
  gender: 'UNKNOWN',
  status: 'PENDING_FOLLOW_UP',
  level: 'REGULAR',
  address: '',
  extraFields: {} as Record<string, any>
});

const defaultFormRules: FormRules = {
  name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }]
};
const formRules = ref<FormRules>(defaultFormRules);
const batchEditVisible = ref(false);
const batchEditFields = ref<string[]>([]);
const batchEditValues = reactive<Record<string, any>>({
  gender: 'UNKNOWN',
  status: '',
  level: '',
  birthday: '',
  address: ''
});
const baseBatchEditableFields = [
  { prop: 'gender', label: '性别' },
  { prop: 'status', label: '状态' },
  { prop: 'level', label: '等级' },
  { prop: 'birthday', label: '生日' },
  { prop: 'address', label: '地址' }
];
const batchEditableFields = computed(() => [
  ...baseBatchEditableFields,
  ...customerCustomFieldItems.value.map((item) => ({ prop: `custom__${item.key}`, label: item.displayName }))
]);

const detailPhones = computed(() => detailCustomer.value?.phones || []);
const customerCustomFieldItems = computed<FieldConfigItem[]>(() => customerFieldConfig.value?.customFields || []);
const customerCustomFormFields = computed<SchemaDrawerField[]>(() => buildCustomSchemaFields(customerFieldConfig.value));
const effectiveCustomerFormFields = computed<SchemaDrawerField[]>(() => [
  ...customerFormFields.value,
  ...customerCustomFormFields.value
]);
const visibleCustomerCustomFields = computed(() =>
  customerCustomFieldItems.value.filter((item) => item.visible !== false)
);
const batchEditSchemaFields = computed<SchemaFormField[]>(() =>
  batchEditFields.value
    .map((prop) => buildBatchEditField(prop))
    .filter((v): v is SchemaFormField => !!v)
);

const socialRows = computed(() => {
  const map = detailCustomer.value?.socialAccounts || {};
  return [
    { key: 'WECHAT', label: '微信', logo: '微', color: '#07c160', ...(map.WECHAT || {}) },
    { key: 'QQ', label: 'QQ', logo: 'Q', color: '#12b7f5', ...(map.QQ || {}) },
    { key: 'DOUYIN', label: '抖音', logo: '抖', color: '#111111', ...(map.DOUYIN || {}) },
    { key: 'KUAISHOU', label: '快手', logo: '快', color: '#ff6a00', ...(map.KUAISHOU || {}) }
  ].map((item) => ({ ...item, bound: !!item.name }));
});

const formDirty = computed(() => JSON.stringify(normalizeFormForCompare()) !== formInitialSnapshot.value);

watch(
  () => detailDrawerVisible.value,
  (visible) => {
    if (!visible) {
      detailActiveTab.value = 'basic';
    }
  }
);

watch(
  () => formState.phones.map((p) => `${p.prefix}|${p.number}`).join(','),
  () => {
    phoneInlineError.value = '';
  }
);

async function fetchData() {
  loading.value = true;
  try {
    const { data } = await customerApi.getList({
      ...searchForm,
      page: pagination.page,
      pageSize: pagination.pageSize
    } as any);
    tableData.value = data.list || [];
    pagination.total = data.total || 0;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  fetchData();
}

function handleReset() {
  searchForm.keyword = '';
  searchForm.level = undefined;
  searchForm.status = undefined;
  handleSearch();
}

function handlePageChange(page: number) {
  pagination.page = page;
  fetchData();
}

function handleSelectionChange(rows: Customer[]) {
  selectedRows.value = rows || [];
}

function handleSizeChange(size: number) {
  pagination.pageSize = size;
  pagination.page = 1;
  fetchData();
}

async function handleExport() {
  await customerApi.exportList(searchForm as any);
}

async function handleBatchDeleteCustomers() {
  if (selectedRows.value.length < 2) return;
  try {
    await ElMessageBox.confirm(`确认删除已选 ${selectedRows.value.length} 个客户？`, '批量删除', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消'
    });
    const results = await Promise.allSettled(selectedRows.value.map((row) => customerApi.delete(String(row.id))));
    const failed = results.filter((r): r is PromiseRejectedResult => r.status === 'rejected');
    if (failed.length === 0) {
      ElMessage.success('批量删除成功');
    } else {
      ElMessage.warning(`成功 ${results.length - failed.length} 条，失败 ${failed.length} 条`);
    }
    selectedRows.value = [];
    await fetchData();
  } catch (error) {
    // cancel
  }
}

function openBatchEditDialog() {
  if (selectedRows.value.length < 2) return;
  batchEditFields.value = [];
  batchEditValues.gender = 'UNKNOWN';
  batchEditValues.status = '';
  batchEditValues.level = '';
  batchEditValues.birthday = '';
  batchEditValues.address = '';
  Object.keys(batchEditValues)
    .filter((k) => k.startsWith('custom__'))
    .forEach((k) => delete batchEditValues[k]);
  for (const item of customerCustomFieldItems.value) {
    batchEditValues[`custom__${item.key}`] = item.fieldType === 'CHECKBOX' ? [] : '';
  }
  batchEditVisible.value = true;
}

async function submitBatchEditCustomers() {
  if (batchEditFields.value.length === 0) {
    ElMessage.warning('请先选择至少一个字段');
    return;
  }
  const payload: any = {};
  if (batchEditFields.value.includes('gender')) payload.gender = mapGenderToBackend(batchEditValues.gender || 'UNKNOWN');
  if (batchEditFields.value.includes('status')) payload.status = batchEditValues.status || undefined;
  if (batchEditFields.value.includes('level')) payload.level = batchEditValues.level || undefined;
  if (batchEditFields.value.includes('birthday')) payload.birthday = batchEditValues.birthday || null;
  if (batchEditFields.value.includes('address')) payload.address = (batchEditValues.address || '').trim() || '';
  const customExtra: Record<string, any> = {};
  for (const fieldKey of batchEditFields.value) {
    if (!fieldKey.startsWith('custom__')) continue;
    const customKey = fieldKey.replace(/^custom__/, '');
    const value = batchEditValues[fieldKey];
    if (Array.isArray(value)) {
      customExtra[customKey] = value.filter((v) => v !== '' && v != null);
    } else {
      customExtra[customKey] = value;
    }
  }
  if (Object.keys(customExtra).length) {
    payload.extraFields = customExtra;
  }

  try {
    await ElMessageBox.confirm(`确认批量更新 ${selectedRows.value.length} 个客户？`, '批量编辑', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消'
    });
    const results = await Promise.allSettled(
      selectedRows.value.map((row) => customerApi.update(String(row.id), payload))
    );
    const failed = results.filter((r): r is PromiseRejectedResult => r.status === 'rejected');
    if (failed.length === 0) {
      ElMessage.success('批量编辑成功');
    } else {
      const firstMsg = failed[0]?.reason?.message || '批量编辑失败';
      ElMessage.warning(`成功 ${results.length - failed.length} 条，失败 ${failed.length} 条：${firstMsg}`);
    }
    batchEditVisible.value = false;
    selectedRows.value = [];
    await fetchData();
  } catch (error) {
    // cancel
  }
}

function buildBatchEditField(prop: string): SchemaFormField | null {
  switch (prop) {
    case 'gender':
      return {
        prop,
        label: '性别',
        type: 'radio',
        options: [
          { label: '未知', value: 'UNKNOWN' },
          { label: '男', value: 'MALE' },
          { label: '女', value: 'FEMALE' }
        ]
      };
    case 'status':
      return {
        prop,
        label: '状态',
        type: 'select',
        className: 'w-100',
        options: [
          { label: '待跟进', value: 'PENDING_FOLLOW_UP' },
          { label: '跟进中', value: 'FOLLOWING' },
          { label: '已成单', value: 'DEAL' },
          { label: '复购', value: 'REPURCHASE' },
          { label: '无效', value: 'INVALID' }
        ]
      };
    case 'level':
      return {
        prop,
        label: '等级',
        type: 'select',
        className: 'w-100',
        options: [
          { label: '普通', value: 'REGULAR' },
          { label: 'VIP', value: 'VIP' },
          { label: 'SVIP', value: 'SVIP' }
        ]
      };
    case 'birthday':
      return {
        prop,
        label: '生日',
        type: 'date',
        className: 'w-100',
        valueFormat: 'YYYY-MM-DD',
        format: 'YYYY-MM-DD'
      };
    case 'address':
      return {
        prop,
        label: '地址',
        type: 'textarea',
        rows: 3,
        placeholder: '请输入地址'
      };
    default:
      if (prop.startsWith('custom__')) {
        const key = prop.replace(/^custom__/, '');
        const item = customerCustomFieldItems.value.find((x) => x.key === key);
        if (!item) return null;
        return mapCustomFieldToBatchSchema(item);
      }
      return null;
  }
}

function mapCustomFieldToBatchSchema(item: FieldConfigItem): SchemaFormField {
  const prop = `custom__${item.key}`;
  const options = (item.options || []).map((o: any) => ({ label: o.label, value: o.value }));
  switch (item.fieldType) {
    case 'TEXTAREA':
      return { prop, label: item.displayName, type: 'textarea', rows: 3, placeholder: `请输入${item.displayName}` };
    case 'NUMBER':
      return { prop, label: item.displayName, type: 'number', className: 'w-100', min: 0 };
    case 'DATE':
      return { prop, label: item.displayName, type: 'date', className: 'w-100' };
    case 'DATETIME':
      return { prop, label: item.displayName, type: 'datetime', className: 'w-100' };
    case 'RADIO':
      return { prop, label: item.displayName, type: 'radio', options };
    case 'CHECKBOX':
      return { prop, label: item.displayName, type: 'checkbox', options };
    case 'SELECT':
      return { prop, label: item.displayName, type: 'select', className: 'w-100', options };
    default:
      return { prop, label: item.displayName, type: 'input', placeholder: `请输入${item.displayName}` };
  }
}

async function openDetailDrawer(id: number | string) {
  detailDrawerVisible.value = true;
  detailLoading.value = true;
  detailCustomer.value = null;
  try {
    const { data } = await customerApi.getDetail(id);
    detailCustomer.value = data;
    await Promise.all([fetchDetailOrders(), fetchDetailBehaviors()]);
  } catch {
    ElMessage.error('获取客户详情失败');
  } finally {
    detailLoading.value = false;
  }
}

async function fetchDetailOrders() {
  if (!detailCustomer.value) return;
  detailOrdersLoading.value = true;
  try {
    const primaryPhone = detailCustomer.value.phones?.[0]?.full;
    const { data } = await orderApi.getList({
      page: 1,
      pageSize: 20,
      customerName: detailCustomer.value.name,
      customerPhone: primaryPhone
    } as any);
    detailOrders.value = data.list || [];
  } catch {
    detailOrders.value = [];
  } finally {
    detailOrdersLoading.value = false;
  }
}

async function fetchDetailBehaviors() {
  if (!detailCustomer.value) return;
  detailBehaviorsLoading.value = true;
  try {
    const { data } = await customerApi.getBehaviors(detailCustomer.value.id);
    detailBehaviors.value = Array.isArray(data) ? data : [];
  } catch {
    detailBehaviors.value = [];
  } finally {
    detailBehaviorsLoading.value = false;
  }
}

function resetFormState() {
  formState.name = '';
  formState.phones = [{ prefix: '86', number: '' }];
  formState.birthday = '';
  formState.gender = 'UNKNOWN';
  formState.status = 'PENDING_FOLLOW_UP';
  formState.level = 'REGULAR';
  formState.address = '';
  formState.extraFields = {};
  ensureCustomerExtraFieldDefaults();
  phoneInlineError.value = '';
  formRef.value?.clearValidate();
}

function snapshotForm() {
  formInitialSnapshot.value = JSON.stringify(normalizeFormForCompare());
}

function normalizeFormForCompare() {
  return {
    name: formState.name.trim(),
    phones: formState.phones
      .map((p) => ({ prefix: String(p.prefix || '').trim(), number: String(p.number || '').trim() }))
      .filter((p) => p.prefix || p.number),
    birthday: formState.birthday || '',
    gender: formState.gender,
    status: formState.status,
    level: formState.level,
    address: formState.address.trim(),
    extraFields: normalizeExtraFieldsForCompare()
  };
}

function openCreateDrawer() {
  formMode.value = 'create';
  editingCustomerId.value = null;
  resetFormState();
  snapshotForm();
  formDrawerVisible.value = true;
}

function openEditDrawer() {
  if (!detailCustomer.value) return;
  formMode.value = 'edit';
  editingCustomerId.value = String(detailCustomer.value.id);
  fillFormFromCustomer(detailCustomer.value);
  snapshotForm();
  formDrawerVisible.value = true;
}

function fillFormFromCustomer(customer: CustomerDetail) {
  formState.name = customer.name || '';
  formState.phones = (customer.phones?.length ? customer.phones : [{ prefix: '86', number: '' }]).map((p) => ({
    prefix: p.prefix || '86',
    number: p.number || ''
  }));
  formState.birthday = customer.birthday || '';
  formState.gender = customer.gender || 'UNKNOWN';
  formState.status = customer.status || 'PENDING_FOLLOW_UP';
  formState.level = customer.level || 'REGULAR';
  formState.address = customer.address || '';
  formState.extraFields = { ...(customer.extraFields || {}) };
  ensureCustomerExtraFieldDefaults();
}

function addFormPhone() {
  formState.phones.push({ prefix: '86', number: '' });
}

function removeFormPhone(index: number) {
  formState.phones.splice(index, 1);
  if (formState.phones.length === 0) {
    formState.phones.push({ prefix: '86', number: '' });
  }
}

function getGenderLabel(gender?: string) {
  return getCustomerGenderLabel(gender);
}

function getLevelTagType(level?: string) {
  return getCustomerLevelTag(level);
}

function getLevelLabel(level?: string) {
  return getCustomerLevelLabel(level);
}

function getStatusLabel(status?: string) {
  return getCustomerStatusLabel(status);
}

function getOrderStatusLabel(status?: string) {
  return getOrderStatusLabelFromDict(status);
}

function fieldLabel(key: string, fallback: string) {
  return getFieldLabel(customerFieldConfig.value, key, fallback);
}

function fieldVisible(key: string) {
  return isFieldVisible(customerFieldConfig.value, key, true);
}

function ensureCustomerExtraFieldDefaults() {
  const next = { ...(formState.extraFields || {}) };
  for (const item of customerCustomFieldItems.value) {
    if (next[item.key] === undefined) {
      next[item.key] = item.fieldType === 'CHECKBOX' ? [] : '';
    }
  }
  formState.extraFields = next;
}

function normalizeExtraFieldsForCompare() {
  const result: Record<string, any> = {};
  for (const item of customerCustomFieldItems.value) {
    const value = formState.extraFields?.[item.key];
    result[item.key] = Array.isArray(value) ? [...value].sort() : (value ?? '');
  }
  return result;
}

function sanitizeExtraFieldsForSubmit() {
  const result: Record<string, any> = {};
  for (const item of customerCustomFieldItems.value) {
    const value = formState.extraFields?.[item.key];
    if (item.fieldType === 'CHECKBOX') {
      const arr = Array.isArray(value) ? value.filter((v) => v !== '' && v != null) : [];
      if (arr.length) result[item.key] = arr;
      continue;
    }
    if (value !== '' && value != null) {
      result[item.key] = value;
    }
  }
  return result;
}

function formatCustomerCustomFieldValue(item: FieldConfigItem) {
  return formatFieldConfigValue(item, detailCustomer.value?.extraFields?.[item.key]);
}

function mapGenderToBackend(gender: string) {
  const map: Record<string, number> = { UNKNOWN: 0, MALE: 1, FEMALE: 2 };
  return map[gender] ?? 0;
}

function normalizePhonesPayload() {
  phoneInlineError.value = '';
  const rows = formState.phones
    .map((p) => ({
      prefix: String(p.prefix || '').replace(/[^\d]/g, '') || '86',
      number: String(p.number || '').replace(/[^\d]/g, '')
    }))
    .filter((p) => p.number);

  const seen = new Set<string>();
  for (const row of rows) {
    if (!/^\d+$/.test(row.prefix)) throw new Error('手机号前缀格式不正确');
    if (!/^\d{5,20}$/.test(row.number)) throw new Error('手机号格式不正确');
    const key = `${row.prefix}-${row.number}`;
    if (seen.has(key)) {
      phoneInlineError.value = '手机号已存在，请勿重复填写';
      throw new Error('__LOCAL_PHONE_DUPLICATE__');
    }
    seen.add(key);
  }
  return rows;
}

async function submitForm() {
  try {
    await formRef.value?.validate();
    const phones = normalizePhonesPayload();
    formSubmitting.value = true;
    const payload: any = {
      name: formState.name.trim(),
      phones,
      birthday: formState.birthday || undefined,
      gender: mapGenderToBackend(formState.gender),
      status: formState.status,
      level: formState.level,
      address: formState.address.trim() || undefined,
      extraFields: sanitizeExtraFieldsForSubmit()
    };
    if (formMode.value === 'create') {
      await customerApi.addCustomer(payload);
      ElMessage.success('客户创建成功');
    } else {
      await customerApi.update(editingCustomerId.value!, payload);
      ElMessage.success('客户更新成功');
    }

    closingBySubmit.value = true;
    formDrawerVisible.value = false;
    await fetchData();

    if (formMode.value === 'edit' && detailCustomer.value && editingCustomerId.value) {
      await openDetailDrawer(editingCustomerId.value);
    }
  } catch (error: any) {
    if (error?.message === '__LOCAL_PHONE_DUPLICATE__') {
      return;
    }
    if (error?.message && !String(error.message).includes('Request failed')) {
      ElMessage.error(error.message);
    }
  } finally {
    formSubmitting.value = false;
    pendingSaveOnClose.value = false;
  }
}

async function requestCloseFormDrawer() {
  if (!formDirty.value) {
    formDrawerVisible.value = false;
    return;
  }

  try {
    await ElMessageBox.confirm('当前填写资料未保存，是否取消？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    });
    formDrawerVisible.value = false;
  } catch {
    // stay open
  }
}

async function handleFormDrawerBeforeClose(done: () => void) {
  if (closingBySubmit.value) {
    closingBySubmit.value = false;
    done();
    return;
  }
  if (!formDirty.value) {
    done();
    return;
  }
  try {
    await ElMessageBox.confirm('当前填写资料未保存，是否取消？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    });
    done();
  } catch {
    // keep open
  }
}

fetchData();
loadMeta();
loadCustomerFieldConfig();
loadCustomerFormMeta();
if (typeof window !== 'undefined') {
  window.addEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
}
onActivated(() => {
  loadCustomerFieldConfig();
  loadCustomerFormMeta();
});
onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
  }
});

async function loadMeta() {
  try {
    const { data } = await metaApi.getCustomerListMeta();
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
      })) as SchemaTableColumn<Customer>[];

    if (normalizedSearchFields.length) {
      searchFields.value = normalizedSearchFields;
    }
    if (normalizedColumns.length) {
      tableColumns.value = normalizedColumns;
    }
  } catch (error) {
    console.warn('Failed to load customer list meta, fallback to local schema', error);
  }
}

async function loadCustomerFormMeta() {
  try {
    const { data } = await metaApi.getCustomerFormMeta();
    const remoteFields = Array.isArray(data?.fields) ? data.fields : [];
    const remoteRules = (data?.rules && typeof data.rules === 'object') ? data.rules : {};

    const normalizedFields = remoteFields
      .filter((f: any) => f && typeof f.prop === 'string' && typeof f.label === 'string' && typeof f.type === 'string')
      .map((f: any) => ({
        prop: f.prop,
        label: f.label,
        type: f.type,
        placeholder: f.placeholder,
        className: f.className,
        clearable: f.clearable,
        maxlength: typeof f.maxlength === 'number' ? f.maxlength : undefined,
        showWordLimit: typeof f.showWordLimit === 'boolean' ? f.showWordLimit : undefined,
        rows: typeof f.rows === 'number' ? f.rows : undefined,
        format: f.format,
        valueFormat: f.valueFormat,
        options: Array.isArray(f.options) ? f.options : undefined
      })) as SchemaDrawerField[];

    if (normalizedFields.length) {
      customerFormFields.value = applyFieldConfigToSchemaFields(normalizedFields, customerFieldConfig.value);
    }

    const normalizedRules: FormRules = {};
    Object.entries(remoteRules).forEach(([prop, rules]) => {
      if (Array.isArray(rules)) {
        normalizedRules[prop] = rules
          .filter((r: any) => r && typeof r === 'object')
          .map((r: any) => ({
            required: !!r.required,
            message: typeof r.message === 'string' ? r.message : undefined,
            trigger: typeof r.trigger === 'string' ? r.trigger : undefined,
            min: typeof r.min === 'number' ? r.min : undefined,
            max: typeof r.max === 'number' ? r.max : undefined
          }));
      }
    });
    if (Object.keys(normalizedRules).length) {
      formRules.value = normalizedRules;
    }
  } catch (error) {
    console.warn('Failed to load customer form meta, fallback to local schema', error);
    customerFormFields.value = applyFieldConfigToSchemaFields(defaultCustomerFormFields, customerFieldConfig.value);
  }
}

async function loadCustomerFieldConfig() {
  try {
    const { data } = await systemApi.getFieldConfig('customer');
    customerFieldConfig.value = data;
  } catch (error) {
    console.warn('Failed to load customer field config', error);
  } finally {
    customerFormFields.value = applyFieldConfigToSchemaFields(customerFormFields.value, customerFieldConfig.value);
    ensureCustomerExtraFieldDefaults();
  }
}

function handleFieldConfigChanged(event: Event) {
  const domain = (event as CustomEvent<{ domain?: string }>).detail?.domain;
  if (!domain || domain === 'customer') {
    loadCustomerFieldConfig();
    loadCustomerFormMeta();
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.search-area {
  margin-bottom: $spacing-md;
  .el-form-item {
    margin-bottom: 0;
  }
}

.table-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.mt-16 {
  margin-top: $spacing-md;
}

.drawer-title {
  font-weight: 600;
  font-size: 16px;
}

.drawer-body {
  height: 100%;
  overflow-y: auto;
}

.drawer-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
}

.w-100 {
  width: 100%;
}

.phones-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.phone-inline-error {
  color: var(--el-color-danger);
  font-size: 12px;
  text-align: center;
  line-height: 1.2;
  margin-top: -2px;
}

.phone-row {
  display: flex;
  gap: $spacing-sm;
  align-items: center;
}

.phone-prefix-input {
  width: 120px;
  flex: 0 0 120px;
}

.phone-number-input {
  flex: 1;
}

.detail-drawer-body {
  height: 60vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-top {
  height: 30%;
  min-height: 150px;
  border-bottom: 1px solid $border-color-light;
  padding: $spacing-md;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.detail-top-actions {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
}

.detail-top-summary {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-lg;
  align-items: flex-start;
  padding-left: 20%;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  .label {
    color: $text-secondary;
  }
  .value {
    color: $text-primary;
    font-weight: 600;
  }
}

.phones-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.phone-pill {
  padding: 2px 8px;
  border-radius: 999px;
  background: $gray-2;
  border: 1px solid $gray-3;
  font-family: monospace;
  font-size: 12px;
}

.detail-tabs {
  height: 70%;
  overflow: hidden;
  padding: $spacing-md;
  :deep(.el-tabs) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  :deep(.el-tabs__content) {
    flex: 1;
    overflow: auto;
  }
}

.social-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: $spacing-md;
}

.social-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-md;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  background: $white;
}

.social-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: $white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.social-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.social-platform {
  font-weight: 600;
}

.social-bound {
  display: flex;
  align-items: center;
  gap: 8px;
}

.social-unbound {
  color: $text-secondary;
}

:deep(.customer-form-drawer .el-drawer.rtl) {
  top: 20vh;
  height: 60vh;
  max-height: 60vh;
  border-radius: 12px 0 0 12px;
}

:deep(.customer-detail-drawer .el-drawer.rtl) {
  top: 20vh;
  height: 60vh;
  max-height: 60vh;
  border-radius: 12px 0 0 12px;
}

@media (max-width: 1200px) {
  .social-list {
    grid-template-columns: 1fr;
  }
  .detail-top-summary {
    padding-left: 0;
  }
}
</style>
