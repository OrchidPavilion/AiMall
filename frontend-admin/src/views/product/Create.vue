<template>
  <div class="product-form">
    <el-page-header @back="handleBack" :title="isEdit ? '编辑商品' : '新增商品'" class="mb-16" />

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-card :title="fieldLabel('name', '基本信息')" class="mb-16">
        <SchemaFormRenderer :model="form as any" :fields="basicFields">
          <template #field-categoryId>
            <el-cascader
              v-model="form.categoryId"
              class="w-100"
              :options="categoryOptions"
              placeholder="请选择分类"
              :props="{ checkStrictly: true, emitPath: false, value: 'id', label: 'name', children: 'children' }"
              clearable
            />
          </template>
        </SchemaFormRenderer>
      </el-card>

      <el-card :title="fieldLabel('mainImage', '商品图片')" class="mb-16">
        <SchemaFormRenderer :model="form as any" :fields="mediaFields">
          <template #field-mainImage>
            <el-upload
              v-model:file-list="mainImageList"
              action="#"
              list-type="picture-card"
              :auto-upload="false"
              :on-preview="handlePreview"
              :on-remove="handleRemoveMain"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </template>

          <template #field-gallery>
            <el-upload
              v-model:file-list="galleryList"
              action="#"
              list-type="picture-card"
              :auto-upload="false"
              :on-preview="handlePreview"
              :on-remove="handleRemove"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
          </template>
        </SchemaFormRenderer>
      </el-card>

      <el-card v-if="showField('description')" :title="fieldLabel('description', '商品详情')" class="mb-16">
        <SchemaFormRenderer :model="form as any" :fields="detailFields" />
      </el-card>

      <el-card v-if="productCustomFormFields.length" title="自定义字段" class="mb-16">
        <SchemaFormRenderer :model="form.extraFields as any" :fields="productCustomFormFields" />
      </el-card>

      <el-card v-if="showField('skus')" :title="fieldLabel('skus', '商品规格')" class="mb-16">
        <div class="sku-list">
          <div v-for="(sku, index) in skuRows" :key="index" class="sku-row">
            <el-input v-model="sku.specName" placeholder="规格名称（如：重量）" class="sku-col" />
            <el-input v-model="sku.specValue" placeholder="规格值（如：10KG/对）" class="sku-col" />
            <el-input-number v-model="sku.price" :min="0" :precision="2" :step="0.01" class="sku-price" />
            <el-input-number v-model="sku.stock" :min="0" :precision="0" :step="1" class="sku-stock" />
            <el-button v-if="skuRows.length > 1" text type="danger" @click="removeSku(index)">删除</el-button>
          </div>
          <el-button text type="primary" @click="addSku">+ 添加规格</el-button>
        </div>
      </el-card>

      <div class="form-actions">
        <el-button @click="handleBack">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onActivated, onUnmounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { metaApi, productApi, storeApi, systemApi } from '@/api';
import SchemaFormRenderer, { type SchemaFormField } from '@/components/common/SchemaFormRenderer.vue';
import type { UploadFile, UploadUserFile } from 'element-plus';
import type { FieldConfigSchema, ProductForm, ProductCategory } from '@/types';
import { applyFieldConfigToSchemaFields, buildCustomSchemaFields, getFieldLabel, isFieldVisible } from '@/utils/fieldConfig';

const route = useRoute();
const router = useRouter();
const formRef = ref<FormInstance>();
const saving = ref(false);
const categories = ref<ProductCategory[]>([]);
const mainImageList = ref<UploadUserFile[]>([]);
const galleryList = ref<UploadUserFile[]>([]);
const productFieldConfig = ref<FieldConfigSchema | null>(null);
const skuRows = ref<Array<{ specName: string; specValue: string; price: number; stock: number }>>([
  { specName: '', specValue: '', price: 0, stock: 0 }
]);

const isEdit = computed(() => !!route.params.id);
const productId = computed(() => Number(route.params.id));

const form = reactive<ProductForm>({
  name: '',
  categoryId: undefined as any,
  price: 0,
  originalPrice: undefined,
  stock: 0,
  description: '',
  mainImage: '' as any,
  gallery: [],
  extraFields: {}
});

const defaultBasicFields: SchemaFormField[] = [
  { prop: 'name', label: '商品名称', type: 'input', placeholder: '请输入商品名称' },
  { prop: 'categoryId', label: '商品分类', type: 'custom' },
  { prop: 'price', label: '售价', type: 'number', min: 0, precision: 2, step: 0.01 },
  { prop: 'originalPrice', label: '原价', type: 'number', min: 0, precision: 2, step: 0.01 },
  { prop: 'stock', label: '库存', type: 'number', min: 0, precision: 0, step: 1 }
];

const defaultMediaFields: SchemaFormField[] = [
  { prop: 'mainImage', label: '主图', type: 'custom' },
  { prop: 'gallery', label: '商品图集', type: 'custom' }
];

const defaultDetailFields: SchemaFormField[] = [
  { prop: 'description', label: '商品描述', type: 'textarea', rows: 6, placeholder: '请输入商品描述' }
];

const basicFields = ref<SchemaFormField[]>(defaultBasicFields);
const mediaFields = ref<SchemaFormField[]>(defaultMediaFields);
const detailFields = ref<SchemaFormField[]>(defaultDetailFields);
const productCustomFormFields = computed<SchemaFormField[]>(() => buildCustomSchemaFields(productFieldConfig.value));

const defaultRules: FormRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  mainImage: [{ required: true, message: '请上传商品主图', trigger: 'change' }]
};
const rules = ref<FormRules>(defaultRules);
const categoryOptions = computed(() => categories.value as any[]);

const fetchCategories = async () => {
  try {
    const { data } = await storeApi.getCategoryTree();
    categories.value = data;
  } catch (error: any) {
    console.error('Failed to fetch categories:', error);
  }
};

const fetchProduct = async (id: number) => {
  try {
    const { data } = await productApi.getDetail(id);
    form.name = data.name;
    form.categoryId = data.categoryId;
    form.price = data.price / 100;
    form.originalPrice = data.originalPrice ? data.originalPrice / 100 : undefined;
    form.stock = data.stock ?? 0;
    form.description = data.description || '';
    form.extraFields = { ...((data as any).extraFields || {}) };
    skuRows.value = Array.isArray((data as any).skus) && (data as any).skus.length
      ? (data as any).skus.map((sku: any) => {
          const [specName, specValue] = Object.entries(sku.spec || {})[0] || ['', ''];
          return {
            specName: String(specName),
            specValue: String(specValue),
            price: Number(sku.price || 0) / 100,
            stock: Number(sku.stock || 0)
          };
        })
      : [{ specName: '', specValue: '', price: 0, stock: 0 }];

    if (data.mainImage) {
      mainImageList.value = [{ name: 'main', url: data.mainImage }];
    }

    if (data.gallery) {
      galleryList.value = data.gallery.map((url: string, index: number) => ({
        name: `gallery-${index}`,
        url
      }));
    }
  } catch (error) {
    ElMessage.error('获取商品信息失败');
    router.back();
  }
};

const handleBack = () => {
  router.back();
};

const handleSave = async () => {
  try {
    await formRef.value?.validate();
    saving.value = true;

    const mainImageFile = mainImageList.value[0]?.raw as File | undefined;
    if (mainImageFile) {
      form.mainImage = mainImageFile;
    } else if (mainImageList.value[0]?.url) {
      form.mainImage = mainImageList.value[0].url;
    } else {
      form.mainImage = '' as any;
    }

    if (!form.mainImage) {
      ElMessage.warning('请上传商品主图');
      return;
    }

    if (galleryList.value.length > 0) {
      const rawFiles = galleryList.value.filter((f) => f.raw).map((f) => f.raw as File);
      const urlFiles = galleryList.value.filter((f) => !f.raw && typeof f.url === 'string').map((f) => f.url as string);
      form.gallery = [...urlFiles, ...rawFiles] as any;
    } else {
      form.gallery = [];
    }

    form.skus = skuRows.value
      .filter((sku) => sku.specName.trim() && sku.specValue.trim())
      .map((sku) => ({
        spec: { [sku.specName.trim()]: sku.specValue.trim() },
        price: Number(sku.price || 0),
        stock: Number(sku.stock || 0)
      }));

    if (isEdit.value) {
      await productApi.update(productId.value, form);
      ElMessage.success('商品更新成功');
    } else {
      await productApi.create(form);
      ElMessage.success('商品创建成功');
    }

    router.push('/product/list');
  } catch (error: any) {
    console.error('Save failed:', error);
    ElMessage.error(error?.message || '商品保存失败');
  } finally {
    saving.value = false;
  }
};

const handlePreview = (_file: UploadFile) => {
  // 图片预览逻辑待后续接入
};

const handleRemoveMain = () => {
  mainImageList.value = [];
};

const handleRemove = (file: UploadFile) => {
  galleryList.value = galleryList.value.filter((f) => f.uid !== file.uid);
};

function addSku() {
  skuRows.value.push({ specName: '', specValue: '', price: 0, stock: 0 });
}

function removeSku(index: number) {
  skuRows.value.splice(index, 1);
  if (!skuRows.value.length) addSku();
}

onMounted(() => {
  fetchCategories();
  loadProductFieldConfig();
  loadProductFormMeta();
  if (isEdit.value) {
    fetchProduct(productId.value);
  }
});

if (typeof window !== 'undefined') {
  window.addEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
}
onActivated(() => {
  loadProductFieldConfig();
  loadProductFormMeta();
});
onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('gf-field-config-changed', handleFieldConfigChanged as EventListener);
  }
});

watch(
  () => productCustomFormFields.value,
  () => {
    const next = { ...(form.extraFields || {}) } as Record<string, any>;
    for (const f of productCustomFormFields.value) {
      if (next[f.prop] === undefined) {
        next[f.prop] = f.type === 'checkbox' ? [] : '';
      }
    }
    form.extraFields = next;
  },
  { immediate: true }
);

async function loadProductFormMeta() {
  try {
    const { data } = await metaApi.getProductFormMeta();
    const normalizedBasic = normalizeSchemaFields(data?.basicFields);
    const normalizedMedia = normalizeSchemaFields(data?.mediaFields);
    const normalizedDetail = normalizeSchemaFields(data?.detailFields);
    if (normalizedBasic.length) basicFields.value = applyFieldConfigToSchemaFields(normalizedBasic, productFieldConfig.value);
    if (normalizedMedia.length) mediaFields.value = applyFieldConfigToSchemaFields(normalizedMedia, productFieldConfig.value);
    if (normalizedDetail.length) detailFields.value = applyFieldConfigToSchemaFields(normalizedDetail, productFieldConfig.value);
    if (data?.rules && typeof data.rules === 'object') {
      rules.value = data.rules as FormRules;
    }
  } catch (error) {
    console.warn('Failed to load product form meta, fallback to local schema', error);
    basicFields.value = applyFieldConfigToSchemaFields(defaultBasicFields, productFieldConfig.value);
    mediaFields.value = applyFieldConfigToSchemaFields(defaultMediaFields, productFieldConfig.value);
    detailFields.value = applyFieldConfigToSchemaFields(defaultDetailFields, productFieldConfig.value);
  }
}

async function loadProductFieldConfig() {
  try {
    const { data } = await systemApi.getFieldConfig('product');
    productFieldConfig.value = data;
  } catch (error) {
    console.warn('Failed to load product field config', error);
  } finally {
    basicFields.value = applyFieldConfigToSchemaFields(basicFields.value, productFieldConfig.value);
    mediaFields.value = applyFieldConfigToSchemaFields(mediaFields.value, productFieldConfig.value);
    detailFields.value = applyFieldConfigToSchemaFields(detailFields.value, productFieldConfig.value);
  }
}

function fieldLabel(key: string, fallback: string) {
  return getFieldLabel(productFieldConfig.value, key, fallback);
}

function showField(key: string) {
  return isFieldVisible(productFieldConfig.value, key, true);
}

function normalizeSchemaFields(raw: any): SchemaFormField[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((f) => f && typeof f.prop === 'string' && typeof f.label === 'string' && typeof f.type === 'string')
    .map((f) => ({
      prop: f.prop,
      label: f.label,
      type: f.type,
      placeholder: f.placeholder,
      className: f.className,
      clearable: f.clearable,
      maxlength: f.maxlength,
      showWordLimit: f.showWordLimit,
      rows: f.rows,
      format: f.format,
      valueFormat: f.valueFormat,
      options: Array.isArray(f.options) ? f.options : undefined,
      min: typeof f.min === 'number' ? f.min : undefined,
      max: typeof f.max === 'number' ? f.max : undefined,
      step: typeof f.step === 'number' ? f.step : undefined,
      precision: typeof f.precision === 'number' ? f.precision : undefined,
      controls: typeof f.controls === 'boolean' ? f.controls : undefined
    })) as SchemaFormField[];
}

function handleFieldConfigChanged(event: Event) {
  const domain = (event as CustomEvent<{ domain?: string }>).detail?.domain;
  if (!domain || domain === 'product') {
    loadProductFieldConfig();
    loadProductFormMeta();
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.w-100 {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
}

.sku-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.sku-row {
  display: grid;
  grid-template-columns: 1fr 1.2fr 140px 120px auto;
  gap: $spacing-sm;
  align-items: center;
}
</style>
