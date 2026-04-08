<template>
  <el-form :model="model" inline class="schema-search-form">
    <el-form-item v-for="field in fields" :key="field.prop" :label="field.label">
      <el-input
        v-if="field.type === 'input'"
        v-model="model[field.prop]"
        :placeholder="field.placeholder || `请输入${field.label}`"
        :clearable="field.clearable ?? true"
      />
      <el-select
        v-else-if="field.type === 'select'"
        v-model="model[field.prop]"
        :placeholder="field.placeholder || '全部'"
        :clearable="field.clearable ?? true"
        :class="field.className"
      >
        <el-option
          v-for="option in field.options || []"
          :key="String(option.value)"
          :label="option.label"
          :value="option.value"
        />
      </el-select>
      <slot
        v-else
        :name="`field-${field.prop}`"
        :field="field"
        :model="model"
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="$emit('search')">{{ searchText }}</el-button>
      <el-button @click="$emit('reset')">{{ resetText }}</el-button>
      <slot name="actions-after" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
export interface SchemaOption {
  label: string;
  value: string | number | boolean;
}

export interface SchemaSearchField {
  prop: string;
  label: string;
  type: 'input' | 'select' | 'custom';
  placeholder?: string;
  clearable?: boolean;
  className?: string;
  options?: SchemaOption[];
}

interface Props {
  model: Record<string, any>;
  fields: SchemaSearchField[];
  searchText?: string;
  resetText?: string;
}

withDefaults(defineProps<Props>(), {
  searchText: '查询',
  resetText: '重置'
});

defineEmits<{
  (e: 'search'): void;
  (e: 'reset'): void;
}>();
</script>

<style scoped lang="scss">
.schema-search-form {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}
</style>

