<template>
  <div>
    <el-alert title="类别列表（3级分类）" type="info" :closable="false" show-icon class="mb-12">
      数据已与 Django 后端分类树同步，支持 3 级分类 CRUD。
    </el-alert>
    <el-card>
      <div class="actions"><el-button type="primary" size="small" @click="addRoot">新增分类</el-button></div>
      <el-table :data="rows" row-key="id" default-expand-all border v-loading="loading">
        <el-table-column prop="name" label="分类名称" min-width="180" />
        <el-table-column prop="level" label="层级" width="90" />
        <el-table-column prop="sort" label="排序" width="90" />
        <el-table-column prop="product_count" label="商品数" width="90" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="editRow(row)">编辑</el-button>
            <el-button link type="primary" :disabled="row.level >= 3" @click="addChild(row)">添加子类</el-button>
            <el-button link type="danger" @click="delRow(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <SchemaDrawerForm
      ref="drawerRef"
      v-model="drawerVisible"
      :title="editingId ? '编辑分类' : '新增分类'"
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
import { reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormRules } from 'element-plus';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import { aimallApi } from '@/api/aimall';

interface CategoryRow {
  id: number;
  name: string;
  level: number;
  sort: number;
  parent_id: number | null;
  product_count?: number;
  children?: CategoryRow[];
}

const drawerRef = ref<SchemaDrawerFormExposed>();
const drawerVisible = ref(false);
const editingId = ref<number | null>(null);
const pendingParentId = ref<number | null>(null);
const rows = ref<CategoryRow[]>([]);
const loading = ref(false);
const closingBySubmit = ref(false);
const initialSnapshot = ref('');

const form = reactive({ name: '', sort: 0, icon: '' });
const fields: SchemaDrawerField[] = [
  { prop: 'name', label: '分类名称', type: 'input', placeholder: '请输入分类名称' },
  { prop: 'sort', label: '排序', type: 'number', min: 0, precision: 0, step: 1 },
  { prop: 'icon', label: '图标', type: 'input', placeholder: '可选' },
] as any;
const rules: FormRules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] };

function resetForm() {
  form.name = '';
  form.sort = 0;
  form.icon = '';
  drawerRef.value?.clearValidate();
}

function snapshotForm() {
  initialSnapshot.value = JSON.stringify({ ...form });
}

function isDirty() {
  return JSON.stringify({ ...form }) !== initialSnapshot.value;
}

function addRoot() {
  editingId.value = null;
  pendingParentId.value = null;
  resetForm();
  snapshotForm();
  drawerVisible.value = true;
}
function addChild(row: CategoryRow) {
  editingId.value = null;
  pendingParentId.value = row.id;
  resetForm();
  snapshotForm();
  drawerVisible.value = true;
}
function editRow(row: CategoryRow) {
  editingId.value = row.id;
  pendingParentId.value = row.parent_id;
  form.name = row.name;
  form.sort = row.sort;
  form.icon = '';
  snapshotForm();
  drawerVisible.value = true;
}

async function delRow(id: number) {
  try {
    await aimallApi.deleteAdminCategory(id);
    ElMessage.success('删除成功');
    await loadTree();
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败');
  }
}

async function save() {
  try {
    await drawerRef.value?.validate();
    const payload = {
      name: form.name,
      sort: form.sort,
      icon: form.icon,
      parent_id: pendingParentId.value,
      enabled: true,
    };
    if (editingId.value) {
      await aimallApi.updateAdminCategory(editingId.value, payload);
      ElMessage.success('更新成功');
    } else {
      await aimallApi.createAdminCategory(payload);
      ElMessage.success('创建成功');
    }
    closingBySubmit.value = true;
    drawerVisible.value = false;
    await loadTree();
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败');
  }
}

async function requestCloseDrawer() {
  if (!isDirty()) {
    drawerVisible.value = false;
    return;
  }
  try {
    await ElMessageBox.confirm('当前分类信息已修改但未保存，确认取消吗？', '提示', { type: 'warning' });
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
    await ElMessageBox.confirm('当前分类信息已修改但未保存，确认关闭吗？', '提示', { type: 'warning' });
    done();
  } catch {}
}

async function loadTree() {
  loading.value = true;
  try {
    rows.value = await aimallApi.getAdminCategoryTree();
  } finally {
    loading.value = false;
  }
}

loadTree();
</script>

<style scoped>
.actions { margin-bottom: 12px; }
.mb-12 { margin-bottom: 12px; }
</style>
