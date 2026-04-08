<template>
  <div class="integration-management">
    <el-alert title="集成管理说明" type="info" :closable="false" show-icon class="mb-16">
      配置第三方系统接口，如支付网关、物流追踪、短信服务等。配置前请确保对接方已就绪。
    </el-alert>
    
    <el-card>
      <div class="table-actions">
        <el-button type="primary" size="small" @click="handleAdd">新增集成</el-button>
      </div>
      
      <el-table :data="integrations" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="集成名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="config" label="配置" min-width="150">
          <template #default="{ row }">
            <el-text type="info" line-clamp="2">
              {{ JSON.stringify(row.config) }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastTestResult" label="测试结果" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.lastTestResult" :type="row.lastTestResult === 'SUCCESS' ? 'success' : 'danger'">
              {{ row.lastTestResult === 'SUCCESS' ? '成功' : '失败' }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">配置</el-button>
            <el-button link type="primary" @click="handleTest(row)">测试</el-button>
            <el-button link type="primary" @click="handleToggle(row)">
              {{ row.enabled ? '禁用' : '启用' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { systemApi } from '@/api';
import { formatDate } from '@/utils/format';
import type { Integration } from '@/types';

const loading = ref(false);
const integrations = ref<Integration[]>([]);

const fetchData = async () => {
  loading.value = true;
  try {
    const { data } = await systemApi.getIntegrations();
    integrations.value = data;
  } catch (error) {
    console.error('Failed to fetch integrations:', error);
  } finally {
    loading.value = false;
  }
};

const handleAdd = () => {
  ElMessage.info('新增集成功能待实现');
};

const handleEdit = (row: Integration) => {
  ElMessage.info(`配置集成: ${row.name}`);
};

const handleTest = async (row: Integration) => {
  try {
    ElMessage.info('正在测试接口连通性...');
    await systemApi.testIntegration(row.id, {
      url: row.config.url || '',
      method: 'GET'
    });
    ElMessage.success('接口测试成功');
    await fetchData();
  } catch (error) {
    ElMessage.error('接口测试失败，请检查配置');
  }
};

const handleToggle = async (row: Integration) => {
  try {
    await systemApi.toggleIntegration(row.id, !row.enabled);
    ElMessage.success(row.enabled ? '已禁用' : '已启用');
    await fetchData();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleDelete = async (row: Integration) => {
  try {
    await ElMessageBox.confirm(`确定删除集成"${row.name}"吗？`, '警告', {
      type: 'warning'
    });
    ElMessage.success('删除成功');
    await fetchData();
  } catch (error) {
    // 取消或失败
  }
};

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    PAYMENT: '支付网关',
    LOGISTICS: '物流追踪',
    SMS: '短信服务',
    EMAIL: '邮件服务',
    ANALYTICS: '数据分析'
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
</style>