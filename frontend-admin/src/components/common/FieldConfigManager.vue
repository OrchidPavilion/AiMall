<template>
  <div class="field-config-manager">
    <div class="toolbar">
      <div class="desc">基础字段支持显示开关与重命名；自定义字段支持新增、编辑、删除。</div>
      <el-button type="primary" size="small" @click="openCreate">新增自定义字段</el-button>
    </div>

    <el-table :data="tableRows" stripe border>
      <el-table-column label="字段来源" width="90">
        <template #default="{ row }">
          <el-tag size="small" :type="row.builtin ? 'info' : 'success'">{{ row.builtin ? '基础字段' : '自定义' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="key" label="字段Key" min-width="140" />
      <el-table-column prop="systemName" label="系统字段名" min-width="120" />
      <el-table-column prop="displayName" label="展示字段名" min-width="140" />
      <el-table-column prop="fieldType" label="字段类型" width="120" />
        <el-table-column label="显示" width="100">
          <template #default="{ row }">
          <el-switch v-model="row.visible" :disabled="isVisibilityLocked(row)" @change="save" />
          </template>
        </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openRename(row)">编辑</el-button>
          <el-button v-if="!row.builtin" link type="danger" @click="removeCustom(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="renameDialogVisible" title="编辑字段名称" width="520px">
      <el-form label-width="120px">
        <el-form-item label="系统字段名称">
          <el-input :model-value="renameTarget?.systemName || ''" disabled />
        </el-form-item>
        <el-form-item label="字段名称">
          <el-input v-model="renameForm.displayName" placeholder="请输入展示字段名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRename">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="customDialogVisible" :title="customMode === 'create' ? '新增自定义字段' : '编辑自定义字段'" width="640px">
      <el-form label-width="120px">
        <el-form-item label="字段名称" required>
          <el-input v-model="customForm.displayName" placeholder="请输入字段名称" />
        </el-form-item>
        <el-form-item label="字段类型" required>
          <el-select v-model="customForm.fieldType" class="w-100">
            <el-option v-for="item in fieldTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <template v-if="needsOptions(customForm.fieldType)">
          <el-form-item label="选项列表">
            <div class="option-editor">
              <div v-for="(opt, idx) in customForm.options" :key="idx" class="option-row">
                <el-input v-model="opt.label" placeholder="选项名称" />
                <el-button text type="danger" @click="customForm.options.splice(idx, 1)">删除</el-button>
              </div>
              <el-button text type="primary" @click="customForm.options.push({ label: '', value: '' })">+ 添加选项</el-button>
            </div>
          </el-form-item>
        </template>
        <el-form-item label="默认显示">
          <el-switch v-model="customForm.visible" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCustom">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { systemApi } from '@/api';
import type { FieldConfigItem, FieldConfigSchema } from '@/types';

const props = defineProps<{
  domain: 'customer' | 'product' | 'order';
}>();

const loading = ref(false);
const schema = ref<FieldConfigSchema>({ domain: props.domain, baseFields: [], customFields: [] });

const renameDialogVisible = ref(false);
const renameTarget = ref<FieldConfigItem | null>(null);
const renameForm = reactive({ displayName: '' });

const customDialogVisible = ref(false);
const customMode = ref<'create' | 'edit'>('create');
const customEditKey = ref<string>('');
const customForm = reactive<FieldConfigItem>({
  key: '',
  systemName: '',
  displayName: '',
  fieldType: 'TEXT',
  builtin: false,
  visible: true,
  options: []
});

const fieldTypeOptions = [
  { label: '文本', value: 'TEXT' },
  { label: '多行文本', value: 'TEXTAREA' },
  { label: '数字', value: 'NUMBER' },
  { label: '日期', value: 'DATE' },
  { label: '时间日期', value: 'DATETIME' },
  { label: '单选', value: 'RADIO' },
  { label: '多选', value: 'CHECKBOX' },
  { label: '下拉选择', value: 'SELECT' }
];

const tableRows = computed(() => [
  ...schema.value.baseFields,
  ...schema.value.customFields
]);

onMounted(load);

async function load() {
  loading.value = true;
  try {
    const { data } = await systemApi.getFieldConfig(props.domain);
    schema.value = normalizeSchema(data, props.domain);
  } catch (error) {
    ElMessage.error('加载字段配置失败');
  } finally {
    loading.value = false;
  }
}

function normalizeSchema(data: any, domain: FieldConfigSchema['domain']): FieldConfigSchema {
  return {
    domain,
    baseFields: Array.isArray(data?.baseFields) ? data.baseFields : [],
    customFields: Array.isArray(data?.customFields) ? data.customFields : []
  };
}

async function save() {
  try {
    const payload: FieldConfigSchema = {
      domain: props.domain,
      baseFields: schema.value.baseFields,
      customFields: schema.value.customFields
    };
    const { data } = await systemApi.updateFieldConfig(props.domain, payload);
    schema.value = normalizeSchema(data, props.domain);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('gf-field-config-changed', { detail: { domain: props.domain } }));
    }
    ElMessage.success('字段配置已保存');
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败');
  }
}

function openRename(row: FieldConfigItem) {
  if (row.builtin) {
    renameTarget.value = row;
    renameForm.displayName = row.displayName || row.systemName;
    renameDialogVisible.value = true;
    return;
  }
  openEditCustom(row);
}

function submitRename() {
  if (!renameTarget.value) return;
  const target = schema.value.baseFields.find((f) => f.key === renameTarget.value!.key);
  if (!target) return;
  target.displayName = renameForm.displayName.trim() || target.systemName;
  renameDialogVisible.value = false;
  save();
}

function openCreate() {
  customMode.value = 'create';
  customEditKey.value = '';
  resetCustomForm();
  customDialogVisible.value = true;
}

function openEditCustom(row: FieldConfigItem) {
  customMode.value = 'edit';
  customEditKey.value = row.key;
  customForm.key = row.key;
  customForm.systemName = row.systemName;
  customForm.displayName = row.displayName;
  customForm.fieldType = row.fieldType;
  customForm.builtin = false;
  customForm.visible = !!row.visible;
  customForm.options = Array.isArray(row.options) ? row.options.map((o) => ({ ...o })) : [];
  customDialogVisible.value = true;
}

async function removeCustom(row: FieldConfigItem) {
  try {
    await ElMessageBox.confirm(`确定删除自定义字段“${row.displayName}”吗？`, '提示', { type: 'warning' });
    schema.value.customFields = schema.value.customFields.filter((f) => f.key !== row.key);
    await save();
  } catch {
    // ignore
  }
}

function submitCustom() {
  if (!customForm.displayName.trim()) {
    ElMessage.warning('请输入字段名称');
    return;
  }
  if (needsOptions(customForm.fieldType)) {
    const validOptions = (customForm.options || []).filter((o) => o.label?.trim());
    if (!validOptions.length) {
      ElMessage.warning('请至少添加一个选项');
      return;
    }
    customForm.options = validOptions;
  }
  const item: FieldConfigItem = {
    key: customMode.value === 'create' ? `custom_${Date.now()}` : customEditKey.value,
    systemName: customMode.value === 'create' ? customForm.displayName.trim() : (customForm.systemName || customForm.displayName.trim()),
    displayName: customForm.displayName.trim(),
    fieldType: customForm.fieldType,
    builtin: false,
    visible: !!customForm.visible,
    options: (customForm.options || []).map((o) => {
      const label = o.label.trim();
      return { label, value: label };
    })
  };
  if (customMode.value === 'create') {
    schema.value.customFields.push(item);
  } else {
    const idx = schema.value.customFields.findIndex((f) => f.key === customEditKey.value);
    if (idx >= 0) schema.value.customFields[idx] = item;
  }
  customDialogVisible.value = false;
  save();
}

function resetCustomForm() {
  customForm.key = '';
  customForm.systemName = '';
  customForm.displayName = '';
  customForm.fieldType = 'TEXT';
  customForm.builtin = false;
  customForm.visible = true;
  customForm.options = [];
}

function needsOptions(type?: string) {
  return ['RADIO', 'CHECKBOX', 'SELECT'].includes(type || '');
}

function isVisibilityLocked(row: FieldConfigItem) {
  return props.domain === 'customer' && row.builtin && ['name', 'phones'].includes(row.key);
}
</script>

<style scoped lang="scss">
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.w-100 {
  width: 100%;
}

.option-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
}
</style>
