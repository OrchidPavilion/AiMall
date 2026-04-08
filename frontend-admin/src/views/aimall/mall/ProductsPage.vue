<template>
  <div>
    <ListPageScaffold :show-pagination="false">
      <template #search>
        <SchemaSearchForm :model="searchForm" :fields="searchFields" @search="loadProducts" @reset="resetSearch">
          <template #field-categoryId>
            <el-select v-model="searchForm.categoryId" clearable placeholder="全部分类" style="width: 220px">
              <el-option v-for="opt in categoryOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </template>
        </SchemaSearchForm>
      </template>
      <template #actions>
        <el-button type="primary" size="small" @click="openCreate">新增商品</el-button>
      </template>
      <SchemaTable :data="rows" :columns="columns" v-loading="loading">
        <template #cell-image="{ row }">
          <img :src="row.image" alt="" class="thumb" />
        </template>
        <template #cell-price="{ row }">¥{{ row.price.toFixed(2) }}</template>
        <template #cell-actions="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="removeRow(row.id)">删除</el-button>
        </template>
      </SchemaTable>
    </ListPageScaffold>

    <SchemaDrawerForm
      ref="drawerRef"
      v-model="drawerVisible"
      :title="editingId ? '编辑商品' : '新增商品'"
      :model="form"
      :fields="formFields"
      :rules="rules"
      :loading="submitting"
      size="46%"
      :before-close="handleBeforeClose"
      @cancel="requestCloseDrawer"
      @submit="submit"
    >
      <template #field-categoryId>
        <el-select v-model="form.categoryId" clearable placeholder="请选择分类" class="w-100">
          <el-option v-for="opt in categoryOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
      </template>
      <template #field-image>
        <div class="upload-mock">
          <el-input v-model="form.image" placeholder="输入图片 URL 或上传图片" />
          <input type="file" accept="image/*" @change="onUploadFileChange" />
          <div class="upload-tip">已对接 Django 上传接口，可直接上传图片</div>
        </div>
      </template>
      <template #field-specs>
        <div class="sku-box">
          <div v-for="(sku, idx) in form.specs" :key="idx" class="sku-row">
            <el-input v-model="sku.name" placeholder="规格名，如 黑色/128G" />
            <el-input-number v-model="sku.price" :min="0" :precision="2" :step="1" />
            <el-button text type="danger" @click="removeSku(idx)">删除</el-button>
          </div>
          <el-button text type="primary" @click="form.specs.push({ name: '', price: 0 })">+ 新增规格</el-button>
        </div>
      </template>
    </SchemaDrawerForm>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox, type FormRules } from 'element-plus';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaSearchForm, { type SchemaSearchField } from '@/components/common/SchemaSearchForm.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import { aimallApi } from '@/api/aimall';

interface ProductRow {
  id: number;
  name: string;
  category: string;
  categoryId: number;
  image: string;
  defaultSpec: string;
  price: number;
  sales: number;
  views: number;
  status: string;
}

const drawerRef = ref<SchemaDrawerFormExposed>();
const drawerVisible = ref(false);
const editingId = ref<number | null>(null);
const submitting = ref(false);
const loading = ref(false);
const closingBySubmit = ref(false);
const initialSnapshot = ref('');

const rows = ref<ProductRow[]>([]);
const categoryOptions = ref<{ label: string; value: number }[]>([]);

const searchForm = reactive({ keyword: '', categoryId: undefined as number | undefined });
const searchFields: SchemaSearchField[] = [
  { prop: 'keyword', label: '关键词', type: 'input', placeholder: '商品名称' },
  { prop: 'categoryId', label: '分类', type: 'custom' },
];

const columns: SchemaTableColumn<ProductRow>[] = [
  { key: 'image', label: '图片', width: 90, slot: 'image' },
  { prop: 'name', label: '名称', minWidth: 180 },
  { prop: 'category', label: '分类', width: 180 },
  { prop: 'defaultSpec', label: '默认规格', width: 110 },
  { key: 'price', label: '价格', width: 100, slot: 'price' },
  { prop: 'sales', label: '销量', width: 90 },
  { prop: 'views', label: '浏览量', width: 90 },
  { prop: 'status', label: '状态', width: 100 },
  { key: 'actions', label: '操作', width: 130, fixed: 'right', slot: 'actions' }
];

const form = reactive({
  name: '',
  categoryId: undefined as number | undefined,
  image: '',
  price: 0,
  defaultSpec: '',
  specs: [{ name: '', price: 0 }]
});

const formFields: SchemaDrawerField[] = [
  { prop: 'name', label: '商品名称', type: 'input', placeholder: '请输入商品名称' },
  { prop: 'categoryId', label: '商品分类', type: 'custom' },
  { prop: 'image', label: '商品图片', type: 'custom' },
  { prop: 'defaultSpec', label: '默认规格', type: 'input', placeholder: '如：黑色' },
  { prop: 'price', label: '默认价格', type: 'number', min: 0, precision: 2, step: 1 },
  { prop: 'specs', label: '规格列表', type: 'custom' }
] as any;

const rules: FormRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择商品分类', trigger: 'change' }]
};

function resetSearch() {
  searchForm.keyword = '';
  searchForm.categoryId = undefined;
  loadProducts();
}

function resetForm() {
  form.name = '';
  form.categoryId = undefined;
  form.image = '';
  form.price = 0;
  form.defaultSpec = '';
  form.specs = [{ name: '', price: 0 }];
  drawerRef.value?.clearValidate();
}

function snapshotForm() {
  initialSnapshot.value = JSON.stringify({
    name: form.name,
    categoryId: form.categoryId,
    image: form.image,
    price: form.price,
    defaultSpec: form.defaultSpec,
    specs: form.specs.map((s) => ({ ...s })),
  });
}

function isDirty() {
  return JSON.stringify({
    name: form.name,
    categoryId: form.categoryId,
    image: form.image,
    price: form.price,
    defaultSpec: form.defaultSpec,
    specs: form.specs.map((s) => ({ ...s })),
  }) !== initialSnapshot.value;
}

function removeSku(idx: number) {
  if (form.specs.length === 1) {
    form.specs[0] = { name: '', price: 0 };
    return;
  }
  form.specs.splice(idx, 1);
}

function openCreate() {
  editingId.value = null;
  resetForm();
  snapshotForm();
  drawerVisible.value = true;
}

function openEdit(row: ProductRow) {
  editingId.value = row.id;
  form.name = row.name;
  form.categoryId = row.categoryId;
  form.image = row.image;
  form.price = row.price;
  form.defaultSpec = row.defaultSpec;
  form.specs = [{ name: row.defaultSpec || '默认规格', price: row.price }];
  snapshotForm();
  drawerVisible.value = true;
}

async function removeRow(id: number) {
  try {
    await aimallApi.deleteAdminProduct(id);
    ElMessage.success('删除成功');
    await loadProducts();
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败');
  }
}

async function onUploadFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  try {
    const data = await aimallApi.uploadImage(file);
    form.image = data.url;
    ElMessage.success('上传成功');
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败');
  } finally {
    (event.target as HTMLInputElement).value = '';
  }
}

async function submit() {
  try {
    await drawerRef.value?.validate();
    submitting.value = true;
    const payload = {
      name: form.name,
      category_id: form.categoryId,
      main_image: form.image,
      default_spec_name: form.defaultSpec || form.specs[0]?.name || '默认规格',
      default_price: Math.round(Number(form.price || form.specs[0]?.price || 0) * 100),
      status: 'ON_SHELF',
      skus: form.specs.filter((s) => s.name.trim()).map((s, idx) => ({
        spec_values: { 规格: s.name.trim() },
        spec_name_text: s.name.trim(),
        price: Math.round(Number(s.price || 0) * 100),
        stock: 999,
        is_default: idx === 0,
        status: true,
      })),
      images: form.image ? [{ image_url: form.image, sort: 1 }] : [],
    };
    if (editingId.value) {
      await aimallApi.updateAdminProduct(editingId.value, payload);
      ElMessage.success('更新成功');
    } else {
      await aimallApi.createAdminProduct(payload);
      ElMessage.success('创建成功');
    }
    closingBySubmit.value = true;
    drawerVisible.value = false;
    await loadProducts();
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败');
  } finally {
    submitting.value = false;
  }
}

async function requestCloseDrawer() {
  if (!isDirty()) {
    drawerVisible.value = false;
    return;
  }
  try {
    await ElMessageBox.confirm('当前商品信息已修改但未保存，确认取消吗？', '提示', { type: 'warning' });
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
    await ElMessageBox.confirm('当前商品信息已修改但未保存，确认关闭吗？', '提示', { type: 'warning' });
    done();
  } catch {}
}

async function loadCategoryOptions() {
  const tree = await aimallApi.getAdminCategoryTree();
  const flat: { label: string; value: number }[] = [];
  const walk = (nodes: any[], prefix = '') => {
    for (const n of nodes || []) {
      const label = prefix ? `${prefix} / ${n.name}` : n.name;
      if ((n.level || 1) >= 3 || !(n.children || []).length) flat.push({ label, value: n.id });
      walk(n.children || [], label);
    }
  };
  walk(tree);
  categoryOptions.value = flat;
}

async function loadProducts() {
  try {
    loading.value = true;
    const data = await aimallApi.getAdminProducts({
      page: 1,
      page_size: 200,
      keyword: searchForm.keyword || undefined,
      category_id: searchForm.categoryId || undefined,
    });
    rows.value = (data.list || []).map((x: any) => ({
      id: x.id,
      name: x.name,
      category: x.category_name,
      categoryId: x.category_id ?? 0,
      image: x.image,
      defaultSpec: x.default_spec,
      price: Number(x.price || 0),
      sales: x.sales || 0,
      views: x.views || 0,
      status: x.status,
    }));
  } catch (e: any) {
    ElMessage.error(e.message || '加载商品失败');
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadCategoryOptions();
  await loadProducts();
});
</script>

<style scoped lang="scss">
.thumb { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; border: 1px solid #dbeafe; }
.upload-tip { margin-top: 6px; font-size: 12px; color: #64748b; }
.sku-box { display: flex; flex-direction: column; gap: 8px; }
.sku-row { display: grid; grid-template-columns: 1fr 140px 56px; gap: 8px; align-items: center; }
.w-100 { width: 100%; }
</style>
