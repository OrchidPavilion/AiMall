<template>
  <el-card>
    <div v-if="$slots.search" class="search-area">
      <slot name="search" />
    </div>

    <div v-if="$slots.actions" class="table-actions">
      <slot name="actions" />
    </div>

    <slot />

    <div v-if="showPagination || $slots['footer-left']" class="footer-row mt-16">
      <div class="footer-left">
        <slot name="footer-left" />
      </div>
      <el-pagination
        v-if="showPagination"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        :page-sizes="pageSizes"
        :layout="layout"
        @update:current-page="$emit('update:currentPage', $event)"
        @update:page-size="$emit('update:pageSize', $event)"
        @current-change="$emit('current-change', $event)"
        @size-change="$emit('size-change', $event)"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  showPagination?: boolean;
  currentPage?: number;
  pageSize?: number;
  total?: number;
  pageSizes?: number[];
  layout?: string;
}

withDefaults(defineProps<Props>(), {
  showPagination: true,
  currentPage: 1,
  pageSize: 20,
  total: 0,
  pageSizes: () => [20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper'
});

defineEmits<{
  (e: 'update:currentPage', value: number): void;
  (e: 'update:pageSize', value: number): void;
  (e: 'current-change', value: number): void;
  (e: 'size-change', value: number): void;
}>();
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.search-area {
  margin-bottom: $spacing-md;

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.table-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.mt-16 {
  margin-top: $spacing-md;
}

.footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacing-md;
}

.footer-left {
  min-height: 32px;
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .footer-row {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-left {
    justify-content: flex-start;
  }
}
</style>
