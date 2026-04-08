<template>
  <div class="ad-spaces">
    <el-alert title="功能说明" type="info" :closable="false" show-icon class="mb-16">
      管理 APP 内各广告位的物料投放，设置投放时间、展示次数、点击跳转链接等。
    </el-alert>
    
    <el-card>
      <div class="table-actions">
        <el-button type="primary" size="small" @click="handleUpdateAll">批量更新</el-button>
      </div>
      
      <el-table :data="adSpaces" v-loading="loading" stripe>
        <el-table-column prop="name" label="广告位名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            {{ getTypeLabel(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="position" label="位置" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="config" label="配置" min-width="200">
          <template #default="{ row }">
            <pre>{{ JSON.stringify(row.config, null, 2) }}</pre>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleTest(row)">测试</el-button>
            <el-button link type="primary" @click="handleToggle(row)">
              {{ row.enabled ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { storeApi } from '@/api';
import { formatDate } from '@/utils/format';
import type { Integration } from '@/types';

const loading = ref(false);
const adSpaces = ref<Integration[]>([]);

const fetchData = async () => {
  loading.value = true;
  try {
    const { data } = await storeApi.getAdSpaces();
    adSpaces.value = data;
  } catch (error) {
    console.error('Failed to fetch ad spaces:', error);
  } finally {
    loading.value = false;
  }
};

const handleEdit = (row: Integration) => {
  ElMessage.info(`编辑广告位: ${row.name}`);
};

const handleTest = async (row: Integration) => {
  try {
    await storeApi.testIntegration(row.id, { url: row.config.url, method: 'GET' });
    ElMessage.success('接口测试成功');
  } catch (error) {
    ElMessage.error('接口测试失败');
  }
};

const handleToggle = async (row: Integration) => {
  try {
    await storeApi.toggleIntegration(row.id, !row.enabled);
    ElMessage.success(row.enabled ? '已禁用' : '已启用');
    await fetchData();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleUpdateAll = () => {
  ElMessage.info('批量更新功能待实现');
};

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    BANNER: 'Banner广告',
    POPUP: '弹窗广告',
    FEED: '信息流广告',
    SPLASH: '开屏广告'
  };
  return map[type] || type;
};

onMounted(() => {
  fetchData();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.table-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: $spacing-md;
}

pre {
  margin: 0;
  font-size: $font-size-sm;
  color: $text-secondary;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>