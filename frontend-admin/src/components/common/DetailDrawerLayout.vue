<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :direction="direction"
    :size="size"
    :with-header="false"
    v-bind="$attrs"
  >
    <div v-loading="loading" class="detail-drawer-body">
      <div class="detail-top">
        <div class="detail-top-actions">
          <slot name="actions" />
        </div>
        <div class="detail-top-summary">
          <slot name="summary" />
        </div>
      </div>

      <div class="detail-tabs">
        <el-tabs :model-value="activeTab" @update:model-value="$emit('update:activeTab', $event as string)">
          <slot />
        </el-tabs>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean;
  activeTab: string;
  loading?: boolean;
  size?: string | number;
  direction?: 'rtl' | 'ltr' | 'ttb' | 'btt';
}

withDefaults(defineProps<Props>(), {
  loading: false,
  size: '50%',
  direction: 'rtl'
});

defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'update:activeTab', value: string): void;
}>();
</script>

<style scoped lang="scss">
.detail-drawer-body {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-top {
  min-height: 30%;
  display: flex;
  flex-direction: column;
}

.detail-top-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-top-summary {
  flex: 1;
}

.detail-tabs {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.detail-tabs :deep(.el-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-tabs :deep(.el-tabs__content) {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
</style>

