<template>
  <div>
    <ListPageScaffold :show-pagination="false">
      <template #search>
        <SchemaSearchForm :model="searchForm" :fields="searchFields" @search="loadCustomers" @reset="resetSearch" />
      </template>
      <template #actions>
        <el-button type="primary" size="small" @click="openCreate">新增客户</el-button>
      </template>
      <SchemaTable :data="rows" :columns="columns" v-loading="loading">
        <template #cell-name="{ row }">
          <el-button link type="primary" @click="openDetail(row)">{{ row.name }}</el-button>
        </template>
        <template #cell-actions="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="removeRow(row.id)">删除</el-button>
        </template>
      </SchemaTable>
    </ListPageScaffold>

    <DetailDrawerLayout v-model="detailVisible" v-model:activeTab="activeTab" size="50%" :loading="detailLoading">
      <template #actions>
        <el-button type="primary" @click="detailRow && openEdit(detailRow)" :disabled="!detailRow">编辑</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
      <template #summary>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ detailRow?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detailRow?.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ detailRow?.age ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="爱好">{{ detailRow?.hobby || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">{{ detailRow?.address || '-' }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <el-tab-pane label="基本信息" name="basic">
        <div class="pane-pad">客户基础信息见顶部摘要。</div>
      </el-tab-pane>
      <el-tab-pane label="行为轨迹" name="behaviors">
        <div class="pane-pad">
          <BehaviorTimeline :items="behaviors" />
        </div>
      </el-tab-pane>
      <el-tab-pane label="智能推荐" name="recommendations">
        <div class="pane-pad">
          <div class="rec-head">
            <span>三种算法推荐对比</span>
            <el-button size="small" @click="detailRow && loadRecommendationCompare(detailRow.id)" :disabled="!detailRow" :loading="recCompareLoading">刷新对比</el-button>
          </div>
          <el-tabs v-model="activeRecAlgTab" class="rec-tabs">
            <el-tab-pane label="基于用户的协同过滤算法" name="USER_CF" />
            <el-tab-pane label="基于物品的协同过滤算法" name="ITEM_CF" />
            <el-tab-pane label="基于交替最小二乘的矩阵分解算法" name="ALS" />
          </el-tabs>
          <el-table :data="currentRecItems" border size="small" v-loading="recCompareLoading">
            <el-table-column prop="name" label="商品" min-width="180" />
            <el-table-column prop="default_spec" label="规格" width="140" />
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column prop="sales" label="销量" width="90" />
            <el-table-column prop="views" label="浏览量" width="90" />
            <el-table-column width="180">
              <template #header>
                <div class="score-header">
                  <span>推荐分数</span>
                  <el-popover placement="top" trigger="click" width="320">
                    <template #reference>
                      <el-button class="score-tip-btn" type="primary" text circle size="small">?</el-button>
                    </template>
                    <div class="score-tip-content">
                      这是把当前算法这一列结果按高低做了“0到100分”的换算，方便你一眼看出谁更靠前。
                      <br />
                      100分表示该算法这次推荐里最匹配的商品，0分表示在这批结果里相对靠后。
                      <br />
                      注意：这个分数主要用于当前算法内部排序展示，不适合直接拿来和其他算法的原始分数做绝对比较。
                    </div>
                  </el-popover>
                </div>
              </template>
              <template #default="{ row }">
                <div class="score-cell">
                  <span class="score-main">{{ Number(row.score_normalized ?? 0).toFixed(2) }}</span>
                  <span class="score-raw" :title="`原始分数（仅同算法内可比）：${Number(row.score ?? 0).toFixed(4)}`">
                    原始{{ Number(row.score ?? 0).toFixed(4) }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="推荐原因" min-width="240" />
          </el-table>
          <div v-if="!recCompareLoading && !currentRecItems.length" class="empty-tip">
            当前行为数据不足，暂时无法生成该客户的算法对比推荐。
          </div>
        </div>
      </el-tab-pane>
    </DetailDrawerLayout>

    <SchemaDrawerForm
      ref="drawerRef"
      v-model="formVisible"
      :title="editingId ? '编辑客户' : '新增客户'"
      :model="form"
      :fields="fields"
      :rules="rules"
      :before-close="handleBeforeClose"
      @cancel="requestCloseDrawer"
      @submit="save"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { ElMessage, ElMessageBox, type FormRules } from 'element-plus';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaSearchForm, { type SchemaSearchField } from '@/components/common/SchemaSearchForm.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import DetailDrawerLayout from '@/components/common/DetailDrawerLayout.vue';
import BehaviorTimeline from '@/components/common/BehaviorTimeline.vue';
import { aimallApi } from '@/api/aimall';

interface CustomerRow { id: number; name: string; phone: string; age: number; hobby: string; address: string }

const searchForm = reactive({ keyword: '' });
const searchFields: SchemaSearchField[] = [{ prop: 'keyword', label: '关键词', type: 'input', placeholder: '姓名/手机号' }];

const rows = ref<CustomerRow[]>([]);
const columns: SchemaTableColumn<CustomerRow>[] = [
  { key: 'name', label: '姓名', minWidth: 120, slot: 'name' },
  { prop: 'phone', label: '手机号', width: 150 },
  { prop: 'age', label: '年龄', width: 90 },
  { prop: 'hobby', label: '爱好', minWidth: 160 },
  { prop: 'address', label: '地址', minWidth: 220 },
  { key: 'actions', label: '操作', width: 120, slot: 'actions' }
];

const loading = ref(false);
const detailLoading = ref(false);
const detailVisible = ref(false);
const activeTab = ref('basic');
const detailRow = ref<CustomerRow | null>(null);
const behaviors = ref<any[]>([]);
const recCompareLoading = ref(false);
const recCompare = ref<Record<string, { items: any[]; label: string }>>({});
const activeRecAlgTab = ref<'USER_CF' | 'ITEM_CF' | 'ALS'>('USER_CF');
const currentRecItems = computed(() => recCompare.value?.[activeRecAlgTab.value]?.items || []);

const drawerRef = ref<SchemaDrawerFormExposed>();
const formVisible = ref(false);
const editingId = ref<number | null>(null);
const closingBySubmit = ref(false);
const initialSnapshot = ref('');
const form = reactive<CustomerRow>({ id: 0, name: '', phone: '', age: 18, hobby: '', address: '' });
const fields: SchemaDrawerField[] = [
  { prop: 'name', label: '姓名', type: 'input', placeholder: '请输入姓名' },
  { prop: 'phone', label: '手机号', type: 'input', placeholder: '请输入手机号' },
  { prop: 'age', label: '年龄', type: 'number', min: 0, precision: 0, step: 1 },
  { prop: 'hobby', label: '爱好', type: 'input', placeholder: '请输入爱好' },
  { prop: 'address', label: '地址', type: 'input', placeholder: '请输入地址' }
] as any;
const rules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
};

function resetSearch() { searchForm.keyword = ''; loadCustomers(); }
function resetForm() {
  form.id = 0; form.name = ''; form.phone = ''; form.age = 18; form.hobby = ''; form.address = '';
  drawerRef.value?.clearValidate();
}

function snapshotForm() {
  initialSnapshot.value = JSON.stringify({
    id: form.id,
    name: form.name,
    phone: form.phone,
    age: form.age,
    hobby: form.hobby,
    address: form.address,
  });
}

function isDirty() {
  return JSON.stringify({
    id: form.id,
    name: form.name,
    phone: form.phone,
    age: form.age,
    hobby: form.hobby,
    address: form.address,
  }) !== initialSnapshot.value;
}

async function loadCustomers() {
  loading.value = true;
  try {
    const data = await aimallApi.getAdminCustomers({ page: 1, page_size: 200, keyword: searchForm.keyword || undefined });
    rows.value = data.list || [];
  } catch (e: any) {
    ElMessage.error(e.message || '加载客户失败');
  } finally {
    loading.value = false;
  }
}

async function openDetail(row: CustomerRow) {
  detailRow.value = row;
  activeTab.value = 'basic';
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    behaviors.value = await aimallApi.getAdminCustomerBehaviors(row.id);
    await loadRecommendationCompare(row.id);
  } catch (e: any) {
    ElMessage.error(e.message || '加载行为轨迹失败');
  } finally {
    detailLoading.value = false;
  }
}

async function loadRecommendationCompare(customerId: number) {
  recCompareLoading.value = true;
  try {
    const data = await aimallApi.getCustomerRecommendationCompare(customerId, 5);
    recCompare.value = data.algorithms || {};
  } catch (e: any) {
    recCompare.value = {};
    ElMessage.error(e.message || '加载推荐对比失败');
  } finally {
    recCompareLoading.value = false;
  }
}

function openCreate() {
  editingId.value = null;
  resetForm();
  snapshotForm();
  formVisible.value = true;
}
function openEdit(row: CustomerRow) {
  editingId.value = row.id;
  Object.assign(form, row);
  snapshotForm();
  formVisible.value = true;
}

async function removeRow(id: number) {
  try {
    await aimallApi.deleteAdminCustomer(id);
    ElMessage.success('删除成功');
    if (detailRow.value?.id === id) detailVisible.value = false;
    await loadCustomers();
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败');
  }
}

async function save() {
  try {
    await drawerRef.value?.validate();
    const payload = { name: form.name, phone: form.phone, age: form.age, hobby: form.hobby, address: form.address };
    if (editingId.value) {
      await aimallApi.updateAdminCustomer(editingId.value, payload);
      ElMessage.success('更新成功');
    } else {
      await aimallApi.createAdminCustomer(payload);
      ElMessage.success('创建成功');
    }
    closingBySubmit.value = true;
    formVisible.value = false;
    await loadCustomers();
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败');
  }
}

async function requestCloseDrawer() {
  if (!isDirty()) {
    formVisible.value = false;
    return;
  }
  try {
    await ElMessageBox.confirm('当前客户资料已修改但未保存，确认取消吗？', '提示', { type: 'warning' });
    formVisible.value = false;
  } catch {}
}

async function handleBeforeClose(done: () => void) {
  if (closingBySubmit.value) {
    closingBySubmit.value = false;
    done();
    return;
  }
  if (!isDirty()) {
    done();
    return;
  }
  try {
    await ElMessageBox.confirm('当前客户资料已修改但未保存，确认关闭吗？', '提示', { type: 'warning' });
    done();
  } catch {}
}

loadCustomers();

watch(detailVisible, (v) => {
  if (!v) {
    recCompare.value = {};
    activeRecAlgTab.value = 'USER_CF';
  }
});
</script>

<style scoped>
.pane-pad { padding: 8px 4px; }
.rec-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  color: #475569;
}
.rec-tabs {
  margin-bottom: 8px;
}
.empty-tip {
  padding: 10px 0 2px;
  color: #94a3b8;
}
.score-cell {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.score-header {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.score-tip-btn {
  width: 16px;
  height: 16px;
  min-height: 16px;
  padding: 0;
  border-radius: 50%;
  font-weight: 700;
}
.score-tip-content {
  color: #475569;
  line-height: 1.6;
  font-size: 13px;
}
.score-main {
  font-weight: 600;
  color: var(--el-color-primary);
}
.score-raw {
  color: #94a3b8;
  font-size: 12px;
}
</style>
