<template>
  <div v-if="count > 1" class="batch-action-bar">
    <span class="count-text">已选择 {{ count }} 条</span>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  count: number;
}>();
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.batch-action-bar {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.count-text {
  color: $text-secondary;
  font-size: 13px;
}
</style>

