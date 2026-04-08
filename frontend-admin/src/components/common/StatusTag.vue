<template>
  <el-tag :type="tagType" :size="size">
    <slot>{{ label }}</slot>
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  value?: string;
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'large' | 'default' | 'small';
  options?: Record<string, { label: string; type: string }>;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  size: 'default'
});

const label = computed(() => {
  if (props.options && props.value) {
    const option = props.options[props.value];
    return option?.label || props.value;
  }
  return props.value || '';
});

const tagType = computed(() => {
  if (props.options && props.value) {
    const option = props.options[props.value];
    return (option?.type || 'info') as any;
  }
  return props.type;
});
</script>