<template>
  <div class="store-categories">
    <el-alert title="分类管理" type="info" :closable="false" show-icon class="mb-16">
      支持最多 3 级商品分类。新增/编辑时通过层级选择器选择父分类。
    </el-alert>

    <el-card>
      <div class="table-actions">
        <el-button type="primary" size="small" @click="openCreate()">新增分类</el-button>
      </div>

      <el-table :data="treeData" row-key="id" default-expand-all border stripe v-loading="loading">
        <el-table-column prop="name" label="分类名称" min-width="180" />
        <el-table-column label="层级" width="90">
          <template #default="{ row }">{{ row.level || 1 }}级</template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="100" />
        <el-table-column prop="sort" label="排序" width="90" />
        <el-table-column prop="productCount" label="商品数量" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" :disabled="(row.level || 1) >= 3" @click="openCreate(row)">添加子分类</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <SchemaDrawerForm
      ref="drawerRef"
      v-model="drawerVisible"
      class="category-form-drawer"
      :title="drawerMode === 'create' ? '新增分类' : '编辑分类'"
      :model="form as any"
      :rules="rules"
      :fields="fields"
      :before-close="handleBeforeClose"
      :loading="submitting"
      @cancel="requestClose"
      @submit="submitForm"
    >
      <template #field-parentPath>
        <el-cascader
          v-model="form.parentPath"
          :options="cascaderOptions"
          clearable
          class="w-100"
          placeholder="请选择父分类（留空为一级分类）"
          :props="{ checkStrictly: true, emitPath: true, value: 'id', label: 'name', children: 'children' }"
        />
      </template>
    </SchemaDrawerForm>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox, type FormRules } from 'element-plus';
import { storeApi } from '@/api';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import type { ProductCategory } from '@/types';

type Mode = 'create' | 'edit';
type CategoryRow = ProductCategory & { level?: number };

const loading = ref(false);
const treeData = ref<CategoryRow[]>([]);
const drawerVisible = ref(false);
const drawerMode = ref<Mode>('create');
const submitting = ref(false);
const drawerRef = ref<SchemaDrawerFormExposed>();
const editingId = ref<number | null>(null);
const initialSnapshot = ref('');
const closingBySubmit = ref(false);

const form = reactive({
  name: '',
  icon: '',
  sort: 0,
  enabled: true,
  parentPath: [] as number[]
});

const fields: SchemaDrawerField[] = [
  { prop: 'name', label: '分类名称', type: 'input', placeholder: '请输入分类名称' },
  { prop: 'parentPath', label: '父级分类', type: 'custom', className: 'w-100' },
  { prop: 'icon', label: '图标', type: 'input', placeholder: '图标/Emoji/URL（可选）' },
  { prop: 'sort', label: '排序', type: 'number', min: 0, precision: 0, step: 1 },
  { prop: 'enabled', label: '启用', type: 'switch' as any }
];

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
};

const cascaderOptions = computed(() => buildCascaderOptions(treeData.value, editingId.value));

fetchData();

async function fetchData() {
  loading.value = true;
  try {
    const { data } = await storeApi.getCategoryTree();
    treeData.value = markLevels((data || []) as any, 1);
  } finally {
    loading.value = false;
  }
}

function markLevels(nodes: CategoryRow[], level: number): CategoryRow[] {
  return (nodes || []).map((n) => ({
    ...n,
    level,
    children: markLevels((n.children || []) as any, level + 1)
  }));
}

function openCreate(parent?: CategoryRow) {
  drawerMode.value = 'create';
  editingId.value = null;
  resetForm();
  if (parent) {
    form.parentPath = getNodePath(parent.id, treeData.value) || [parent.id];
  }
  snapshot();
  drawerVisible.value = true;
}

function openEdit(row: CategoryRow) {
  drawerMode.value = 'edit';
  editingId.value = row.id;
  form.name = row.name || '';
  form.icon = row.icon || '';
  form.sort = row.sort || 0;
  form.enabled = !!row.enabled;
  form.parentPath = row.parentId && row.parentId > 0 ? (getNodePath(row.parentId, treeData.value) || [row.parentId]) : [];
  snapshot();
  drawerVisible.value = true;
}

async function handleDelete(row: CategoryRow) {
  try {
    await ElMessageBox.confirm(`确定删除分类“${row.name}”吗？`, '提示', { type: 'warning' });
    await storeApi.deleteCategory(row.id);
    ElMessage.success('删除成功');
    await fetchData();
  } catch {
    // ignore
  }
}

async function submitForm() {
  try {
    await drawerRef.value?.validate();
    submitting.value = true;
    const parentId = form.parentPath.length ? form.parentPath[form.parentPath.length - 1] : null;
    const payload = {
      name: form.name.trim(),
      parentId,
      icon: form.icon.trim() || undefined,
      sort: Number(form.sort || 0),
      enabled: !!form.enabled
    };
    if (drawerMode.value === 'create') {
      await storeApi.createCategory(payload);
      ElMessage.success('分类创建成功');
    } else {
      await storeApi.updateCategory(editingId.value!, payload);
      ElMessage.success('分类更新成功');
    }
    closingBySubmit.value = true;
    drawerVisible.value = false;
    await fetchData();
  } catch (error: any) {
    if (error?.message) ElMessage.error(error.message);
  } finally {
    submitting.value = false;
  }
}

async function requestClose() {
  if (!isDirty()) {
    drawerVisible.value = false;
    return;
  }
  try {
    await ElMessageBox.confirm('当前填写资料未保存，是否取消？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    });
    drawerVisible.value = false;
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
    await ElMessageBox.confirm('当前填写资料未保存，是否取消？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    });
    done();
  } catch {}
}

function resetForm() {
  form.name = '';
  form.icon = '';
  form.sort = 0;
  form.enabled = true;
  form.parentPath = [];
  drawerRef.value?.clearValidate();
}

function snapshot() {
  initialSnapshot.value = JSON.stringify({
    ...form,
    parentPath: [...form.parentPath]
  });
}

function isDirty() {
  return JSON.stringify({ ...form, parentPath: [...form.parentPath] }) !== initialSnapshot.value;
}

function getNodePath(id: number, nodes: CategoryRow[], path: number[] = []): number[] | null {
  for (const node of nodes) {
    const nextPath = [...path, node.id];
    if (node.id === id) return nextPath;
    const child = getNodePath(id, (node.children || []) as any, nextPath);
    if (child) return child;
  }
  return null;
}

function buildCascaderOptions(nodes: CategoryRow[], excludeId: number | null): any[] {
  return (nodes || [])
    .filter((n) => n.id !== excludeId)
    .map((n) => ({
      id: n.id,
      name: n.name,
      disabled: (n.level || 1) >= 3,
      children: buildCascaderOptions((n.children || []) as any, excludeId)
    }));
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.table-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: $spacing-md;
}

.w-100 {
  width: 100%;
}

:deep(.category-form-drawer .el-drawer.rtl) {
  top: 20vh;
  height: 60vh;
  max-height: 60vh;
  border-radius: 12px 0 0 12px;
}
</style>
