<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="head">
        <div class="title-box">
          <span>智能推荐（按用户展示）</span>
          <el-tag size="small" type="primary">线上算法：{{ currentAlgorithmLabel }}</el-tag>
        </div>
        <el-space>
          <el-button @click="loadRows">刷新列表</el-button>
          <el-button type="primary" size="small" @click="refreshAndLoad">刷新推荐</el-button>
        </el-space>
      </div>
    </template>
    <el-table :data="rows" border>
      <el-table-column prop="customerName" label="客户" width="140" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column prop="products" label="推荐商品" min-width="320">
        <template #default="{ row }">
          <el-tag v-for="p in row.products" :key="p" class="mr-6">{{ p }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="推荐原因" min-width="220" />
      <el-table-column prop="score" label="分值" width="90" />
    </el-table>
    <div class="tip">
      查看单个客户三种算法推荐结果与推荐原因，请前往「客户管理 → 客户列表」，点击客户名，在详情抽屉的“智能推荐”Tab中查看。
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { aimallApi } from '@/api/aimall';

const rows = ref<any[]>([]);
const loading = ref(false);
const currentAlgorithmLabel = ref('ALS');

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await aimallApi.getAdminRecommendations();
    const setting = await aimallApi.getRecommendationSettings();
    currentAlgorithmLabel.value =
      ({
        USER_CF: '基于用户的协同过滤',
        ITEM_CF: '基于物品的协同过滤',
        ALS: 'ALS矩阵分解',
      } as any)[setting.online_algorithm] || setting.online_algorithm || 'ALS';
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败');
  } finally {
    loading.value = false;
  }
}

async function refreshAndLoad() {
  loading.value = true;
  try {
    await aimallApi.refreshAdminRecommendations({});
    await loadRows();
    ElMessage.success('推荐已刷新');
  } catch (e: any) {
    ElMessage.error(e.message || '刷新失败');
  } finally {
    loading.value = false;
  }
}

loadRows();
</script>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; }
.title-box { display: flex; align-items: center; gap: 8px; }
.mr-6 { margin-right: 6px; }
.tip { margin-top: 10px; color: #64748b; font-size: 12px; }
</style>
