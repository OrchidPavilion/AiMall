<template>
  <span :class="['amount', { positive: isPositive, negative: isNegative }]">
    <template v-if="showSymbol">{{ symbol }}</template>
    {{ formattedAmount }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatAmount } from '@/utils/format';

interface Props {
  value: number | null | undefined;
  precision?: number;
  showSymbol?: boolean;
  symbol?: string;
}

const props = withDefaults(defineProps<Props>(), {
  precision: 2,
  showSymbol: true,
  symbol: '¥'
});

const isPositive = computed(() => {
  return props.value !== null && props.value !== undefined && props.value >= 0;
});

const isNegative = computed(() => {
  return props.value !== null && props.value !== undefined && props.value < 0;
});

const formattedAmount = computed(() => {
  return formatAmount(props.value, !props.showSymbol);
});
</script>