<template>
  <div class="dashboard">
    <div class="page-title">数据概览</div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="mb-16">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in stats" :key="stat.key">
        <div class="stat-card" :class="`stat-${stat.key}`">
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-icon">
            <component :is="stat.icon" />
          </div>
        </div>
      </el-col>
    </el-row>

    <TrendDashboardPanel
      v-model="trendQueryState"
      class="mb-16"
      :loading="trendLoading"
      :data="trendData"
      @search="handleTrendSearch"
    />
    
    <!-- 快捷操作 -->
    <el-card class="mb-16">
      <template #header>
        <span>快捷操作</span>
      </template>
      <div class="quick-actions">
        <div
          v-for="action in quickActions"
          :key="action.name"
          class="action-item"
          @click="handleAction(action)"
        >
          <div class="action-icon">{{ action.icon }}</div>
          <div class="action-label">{{ action.label }}</div>
        </div>
      </div>
    </el-card>
    
    <!-- 临时提示 -->
    <el-alert
      title="系统说明"
      type="info"
      :closable="false"
      show-icon
    >
      <template #default>
        <p>欢迎使用 GhostFit 管理后台！</p>
        <p style="margin-top: 8px; font-size: 13px; color: #8c8c8c;">
          当前版本: 1.0.0 | 后端接口待联调，部分功能可能暂不可用
        </p>
      </template>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { User, ShoppingCart, Money, TrendCharts } from '@element-plus/icons-vue';
import { dashboardApi } from '@/api';
import TrendDashboardPanel from '@/components/common/TrendDashboardPanel.vue';

const router = useRouter();

const stats = ref([
  { key: 'customers', label: '总客户数', value: '1,234', icon: User },
  { key: 'orders', label: '今日订单', value: '56', icon: ShoppingCart },
  { key: 'revenue', label: '本月收入', value: '¥128,500', icon: Money },
  { key: 'active', label: '活跃用户', value: '892', icon: TrendCharts }
]);

const quickActions = [
  { name: 'order', label: '创建订单', icon: '📦', path: '/order/create' },
  { name: 'customer', label: '客户管理', icon: '👥', path: '/customer/list' },
  { name: 'product', label: '商品上架', icon: '📦', path: '/product/create' },
  { name: 'store', label: '商城配置', icon: '⚙️', path: '/store/layout' }
];

const handleAction = (action: any) => {
  if (action.path) {
    router.push(action.path);
  }
};

const trendLoading = ref(false);
const trendData = ref<any>(null);
const trendQueryState = ref<{ rangeType: any; dateRange: [string, string] | [] }>({
  rangeType: 'TODAY',
  dateRange: []
});

function resolveTrendPayload(state: { rangeType: string; dateRange: [string, string] | [] }) {
  if (state.rangeType === 'CUSTOM' && state.dateRange.length === 2) {
    return {
      startDate: state.dateRange[0],
      endDate: state.dateRange[1]
    };
  }
  if (state.rangeType === 'TODAY') {
    return { days: 1 };
  }
  return { days: Number(state.rangeType) || 1 };
}

async function handleTrendSearch(state = trendQueryState.value) {
  trendLoading.value = true;
  try {
    const { data } = await dashboardApi.getTrend(resolveTrendPayload(state));
    trendData.value = data;
  } catch (error) {
    console.error('Failed to load dashboard trend:', error);
  } finally {
    trendLoading.value = false;
  }
}

onMounted(() => {
  handleTrendSearch();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.dashboard {
  .stat-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    background: $white;
    border-radius: $border-radius-base;
    box-shadow: $shadow-sm;
    border-left: 4px solid;
    
    &.stat-customers { border-left-color: $primary-color; }
    &.stat-orders { border-left-color: $success-color; }
    &.stat-revenue { border-left-color: $warning-color; }
    &.stat-active { border-left-color: $info-color; }
    
    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: $text-primary;
      font-family: $font-family-code;
    }
    
    .stat-label {
      margin-top: 8px;
      font-size: 14px;
      color: $text-secondary;
    }
    
    .stat-icon {
      font-size: 48px;
      opacity: 0.3;
    }
  }
  
  .quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    
    .action-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: $bg-page;
      border-radius: $border-radius-base;
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid transparent;
      
      &:hover {
        background: $bg-hover;
        border-color: $primary-color;
        transform: translateY(-2px);
      }
      
      .action-icon {
        font-size: 32px;
        margin-bottom: 8px;
      }
      
      .action-label {
        font-size: 14px;
        color: $text-regular;
      }
    }
  }
}
</style>
