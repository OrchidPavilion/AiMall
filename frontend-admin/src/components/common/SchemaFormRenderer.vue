<template>
  <template v-for="field in fields" :key="field.prop">
    <el-form-item :label="field.label" :prop="field.prop">
      <el-input
        v-if="field.type === 'input'"
        v-model="model[field.prop]"
        :maxlength="field.maxlength"
        :show-word-limit="field.showWordLimit"
        :placeholder="field.placeholder"
        :class="field.className"
        :clearable="field.clearable ?? true"
      />

      <el-input
        v-else-if="field.type === 'textarea'"
        v-model="model[field.prop]"
        type="textarea"
        :rows="field.rows || 3"
        :maxlength="field.maxlength"
        :show-word-limit="field.showWordLimit"
        :placeholder="field.placeholder"
        :class="field.className"
      />

      <el-select
        v-else-if="field.type === 'select'"
        v-model="model[field.prop]"
        :placeholder="field.placeholder || '请选择'"
        :class="field.className"
        :clearable="field.clearable ?? true"
      >
        <el-option
          v-for="option in field.options || []"
          :key="String(option.value)"
          :label="option.label"
          :value="option.value"
        />
      </el-select>

      <el-radio-group
        v-else-if="field.type === 'radio'"
        v-model="model[field.prop]"
        :class="field.className"
      >
        <el-radio v-for="option in field.options || []" :key="String(option.value)" :label="option.value">
          {{ option.label }}
        </el-radio>
      </el-radio-group>

      <el-checkbox-group
        v-else-if="field.type === 'checkbox'"
        v-model="model[field.prop]"
        :class="field.className"
      >
        <el-checkbox v-for="option in field.options || []" :key="String(option.value)" :label="option.value">
          {{ option.label }}
        </el-checkbox>
      </el-checkbox-group>

      <el-date-picker
        v-else-if="field.type === 'date'"
        v-model="model[field.prop]"
        type="date"
        :value-format="field.valueFormat || 'YYYY-MM-DD'"
        :format="field.format || 'YYYY-MM-DD'"
        :placeholder="field.placeholder || '请选择日期'"
        :class="field.className"
      />

      <el-date-picker
        v-else-if="field.type === 'datetime'"
        v-model="model[field.prop]"
        type="datetime"
        :value-format="field.valueFormat || 'YYYY-MM-DD HH:mm:ss'"
        :format="field.format || 'YYYY-MM-DD HH:mm:ss'"
        :placeholder="field.placeholder || '请选择日期时间'"
        :class="field.className"
      />

      <el-input-number
        v-else-if="field.type === 'number'"
        v-model="model[field.prop]"
        :min="field.min"
        :max="field.max"
        :step="field.step"
        :precision="field.precision"
        :controls="field.controls ?? true"
        :class="field.className"
      />

      <el-switch
        v-else-if="field.type === 'switch'"
        v-model="model[field.prop]"
        :class="field.className"
      />

      <slot
        v-else
        :name="`field-${field.prop}`"
        :field="field"
        :model="model"
      />
    </el-form-item>
  </template>
</template>

<script setup lang="ts">
export interface SchemaFormOption {
  label: string;
  value: string | number | boolean;
}

export interface SchemaFormField {
  prop: string;
  label: string;
  type: 'input' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'date' | 'datetime' | 'number' | 'switch' | 'custom';
  placeholder?: string;
  className?: string;
  clearable?: boolean;
  maxlength?: number;
  showWordLimit?: boolean;
  rows?: number;
  format?: string;
  valueFormat?: string;
  options?: SchemaFormOption[];
  min?: number;
  max?: number;
  step?: number;
  precision?: number;
  controls?: boolean;
}

interface Props {
  model: Record<string, any>;
  fields: SchemaFormField[];
}

defineProps<Props>();
</script>
