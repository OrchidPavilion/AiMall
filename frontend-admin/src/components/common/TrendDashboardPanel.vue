<template>
  <el-card class="trend-dashboard-panel">
    <template #header>
      <div class="panel-header">
        <div class="title">增量趋势仪表盘</div>
        <div class="filters">
          <el-select v-model="rangeType" style="width: 140px" @change="handleRangeTypeChange">
            <el-option
              v-for="item in rangeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            clearable
            @change="handleDateRangeChange"
          />
          <el-button type="primary" @click="emitSearch">查询</el-button>
        </div>
      </div>
      <div class="quick-ranges">
        <el-button
          v-for="item in quickButtons"
          :key="item.days"
          size="small"
          :type="rangeType === item.value ? 'primary' : 'default'"
          plain
          @click="pickQuick(item.value)"
        >
          {{ item.label }}
        </el-button>
      </div>
    </template>

    <div v-loading="loading">
      <el-row :gutter="16" class="summary-cards">
        <el-col :xs="24" :sm="12">
          <div class="summary-card card-customer">
            <div class="label">客户增量数据</div>
            <div class="value">{{ data?.customerIncrementTotal ?? 0 }}</div>
            <div class="sub">{{ currentRangeLabel }}</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="summary-card card-order">
            <div class="label">订单增量数据</div>
            <div class="value">{{ data?.orderIncrementTotal ?? 0 }}</div>
            <div class="sub">{{ currentRangeLabel }}</div>
          </div>
        </el-col>
      </el-row>

      <el-table :data="data?.points || []" stripe size="small" class="trend-table">
        <el-table-column prop="date" label="日期" min-width="120" />
        <el-table-column prop="customerIncrement" label="客户增量" min-width="100" />
        <el-table-column prop="orderIncrement" label="订单增量" min-width="100" />
      </el-table>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { DashboardTrendData } from '@/api/modules/dashboard';

type RangeType =
  | 'TODAY'
  | '3'
  | '5'
  | '7'
  | '15'
  | '30'
  | '180'
  | '365'
  | 'CUSTOM';

const props = defineProps<{
  loading?: boolean;
  data?: DashboardTrendData | null;
  modelValue?: {
    rangeType: RangeType;
    dateRange: [string, string] | [];
  };
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: { rangeType: RangeType; dateRange: [string, string] | [] }): void;
  (e: 'search', value: { rangeType: RangeType; dateRange: [string, string] | [] }): void;
}>();

const rangeOptions = [
  { label: '当日', value: 'TODAY' },
  { label: '3天', value: '3' },
  { label: '5天', value: '5' },
  { label: '7天', value: '7' },
  { label: '15天', value: '15' },
  { label: '30天', value: '30' },
  { label: '180天', value: '180' },
  { label: '365天', value: '365' },
  { label: '自定义', value: 'CUSTOM' }
] as const;

const quickButtons = rangeOptions.filter((item) => item.value !== 'CUSTOM');

const rangeType = ref<RangeType>(props.modelValue?.rangeType ?? 'TODAY');
const dateRange = ref<[string, string] | []>(props.modelValue?.dateRange ?? []);

watch(
  () => props.modelValue,
  (value) => {
    if (!value) return;
    rangeType.value = value.rangeType;
    dateRange.value = value.dateRange;
  },
  { deep: true }
);

function syncModel() {
  emit('update:modelValue', { rangeType: rangeType.value, dateRange: dateRange.value });
}

function pickQuick(value: RangeType) {
  rangeType.value = value;
  if (value !== 'CUSTOM') {
    dateRange.value = [];
  }
  syncModel();
  emitSearch();
}

function handleRangeTypeChange() {
  if (rangeType.value !== 'CUSTOM') {
    dateRange.value = [];
  }
  syncModel();
}

function handleDateRangeChange() {
  if (dateRange.value && dateRange.value.length === 2) {
    rangeType.value = 'CUSTOM';
  }
  syncModel();
}

function emitSearch() {
  emit('search', { rangeType: rangeType.value, dateRange: dateRange.value });
}

const currentRangeLabel = computed(() => {
  if (props.data?.startDate && props.data?.endDate) {
    return `${props.data.startDate} 至 ${props.data.endDate}`;
  }
  return '当前周期';
});
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-md;
  flex-wrap: wrap;
}

.title {
  font-weight: 700;
}

.filters {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.quick-ranges {
  margin-top: $spacing-sm;
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.summary-cards {
  margin-bottom: $spacing-md;
}

.summary-card {
  border-radius: $border-radius-base;
  padding: $spacing-md;
  background: $bg-page;
  border: 1px solid $border-color-lighter;

  .label {
    color: $text-secondary;
    font-size: $font-size-sm;
  }
  .value {
    margin-top: 8px;
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
  }
  .sub {
    margin-top: 6px;
    font-size: 12px;
    color: $text-secondary;
  }

  &.card-customer {
    border-left: 4px solid $primary-color;
  }
  &.card-order {
    border-left: 4px solid $success-color;
  }
}

.trend-table {
  width: 100%;
}
</style>

