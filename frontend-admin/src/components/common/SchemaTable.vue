<template>
  <el-table
    :data="data"
    :row-key="rowKey"
    :stripe="stripe"
    :border="border"
    :default-expand-all="defaultExpandAll"
    v-loading="loading"
    v-bind="$attrs"
    @selection-change="onSelectionChange"
  >
    <el-table-column
      v-if="selection"
      type="selection"
      :width="selectionWidth"
      :fixed="selectionFixed"
      :selectable="selectable"
      reserve-selection
    />
    <el-table-column
      v-for="column in columns"
      :key="column.key || column.prop || column.label"
      :prop="column.prop"
      :label="column.label"
      :width="column.width"
      :min-width="column.minWidth"
      :fixed="column.fixed"
      :align="column.align"
      :show-overflow-tooltip="column.showOverflowTooltip"
    >
      <template v-if="column.slot" #default="{ row, $index }">
        <slot :name="`cell-${column.slot}`" :row="row" :column="column" :index="$index" />
      </template>
      <template v-else-if="column.formatter" #default="{ row, $index }">
        {{ column.formatter(row, $index) }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
export interface SchemaTableColumn<T = any> {
  key?: string;
  prop?: string;
  label: string;
  width?: string | number;
  minWidth?: string | number;
  fixed?: 'left' | 'right' | boolean;
  align?: 'left' | 'center' | 'right';
  showOverflowTooltip?: boolean;
  slot?: string;
  formatter?: (row: T, index: number) => string | number;
}

interface Props<T = any> {
  data: T[];
  columns: SchemaTableColumn<T>[];
  loading?: boolean;
  stripe?: boolean;
  border?: boolean;
  rowKey?: string;
  defaultExpandAll?: boolean;
  selection?: boolean;
  selectionWidth?: number;
  selectionFixed?: 'left' | 'right' | boolean;
  selectable?: (row: T, index: number) => boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  stripe: true,
  border: false,
  rowKey: undefined,
  defaultExpandAll: false,
  selection: false,
  selectionWidth: 52,
  selectionFixed: 'left',
  selectable: undefined
});

const emit = defineEmits<{
  (e: 'selection-change', value: any[]): void;
}>();

function onSelectionChange(rows: any[]) {
  emit('selection-change', rows);
}
</script>
