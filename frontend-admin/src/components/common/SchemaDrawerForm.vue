<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :direction="direction"
    :size="size"
    :before-close="beforeClose"
    :destroy-on-close="destroyOnClose"
    v-bind="$attrs"
  >
    <template #header>
      <slot name="header">
        <div class="drawer-title">{{ title }}</div>
      </slot>
    </template>

    <div class="drawer-body">
      <el-form ref="innerFormRef" :model="model" :rules="rules" :label-width="labelWidth">
        <SchemaFormRenderer :model="model" :fields="fields">
          <template v-for="field in fields" :key="field.prop" #[`field-${field.prop}`]="slotProps">
            <slot :name="`field-${field.prop}`" v-bind="slotProps" />
          </template>
        </SchemaFormRenderer>
      </el-form>
    </div>

    <template #footer>
      <slot name="footer">
        <div class="drawer-footer">
          <el-button @click="$emit('cancel')">{{ cancelText }}</el-button>
          <el-button type="primary" :loading="loading" @click="$emit('submit')">{{ submitText }}</el-button>
        </div>
      </slot>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import SchemaFormRenderer, { type SchemaFormField, type SchemaFormOption } from './SchemaFormRenderer.vue';

export type SchemaDrawerOption = SchemaFormOption;
export type SchemaDrawerField = SchemaFormField;

export interface SchemaDrawerFormExposed {
  validate: () => Promise<void>;
  clearValidate: () => void;
}

interface Props {
  modelValue: boolean;
  title: string;
  model: Record<string, any>;
  rules?: FormRules;
  fields: SchemaDrawerField[];
  labelWidth?: string | number;
  size?: string | number;
  direction?: 'rtl' | 'ltr' | 'ttb' | 'btt';
  destroyOnClose?: boolean;
  loading?: boolean;
  submitText?: string;
  cancelText?: string;
  beforeClose?: (done: () => void) => void;
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: 88,
  size: '30%',
  direction: 'rtl',
  destroyOnClose: true,
  loading: false,
  submitText: '保存',
  cancelText: '取消',
  beforeClose: undefined
});

defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'submit'): void;
  (e: 'cancel'): void;
}>();

const innerFormRef = ref<FormInstance>();

async function validate() {
  await innerFormRef.value?.validate();
}

function clearValidate() {
  innerFormRef.value?.clearValidate();
}

defineExpose<SchemaDrawerFormExposed>({
  validate,
  clearValidate
});
</script>

<style scoped lang="scss">
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
  gap: 8px;
}
</style>
