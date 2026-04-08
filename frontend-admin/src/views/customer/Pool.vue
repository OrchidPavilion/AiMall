<template>
  <div class="customer-pool">
    <el-alert title="公海客户管理" type="warning" :closable="false" show-icon class="mb-16">
      公海客户是指未分配或超过跟进期限自动回收的客户。您可以在此领取客户进行跟进。
    </el-alert>
    
    <ListPageScaffold :show-pagination="false">
      <template #search>
        <el-form :model="searchForm" inline>
          <el-form-item label="关键词">
            <el-input v-model="searchForm.keyword" placeholder="姓名/手机号" clearable />
          </el-form-item>
          <el-form-item label="等级">
            <el-select v-model="searchForm.level" placeholder="全部" clearable>
              <el-option label="普通" value="REGULAR" />
              <el-option label="VIP" value="VIP" />
              <el-option label="SVIP" value="SVIP" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </template>
      
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="phone" label="手机号" min-width="120">
          <template #default="{ row }">
            <span class="phone-masked">{{ maskPhone(row.phone) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)">
              {{ getLevelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag>{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastActiveTime" label="最后活跃" width="160">
          <template #default="{ row }">
            {{ formatDate(row.lastActiveTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleClaim(row)">领取</el-button>
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ListPageScaffold>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { customerApi } from '@/api';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import { usePagedList } from '@/composables/usePagedList';
import { getCustomerLevelLabel, getCustomerLevelTag, getCustomerStatusLabel } from '@/constants/dictionaries';
import { formatDate, maskPhone } from '@/utils/format';
import type { Customer } from '@/types';

const router = useRouter();
const {
  loading,
  tableData,
  query: searchForm,
  fetchData,
  search,
  reset
} = usePagedList<{ keyword: string; level: any }, Customer>({
  initialQuery: {
    keyword: '',
    level: undefined
  },
  fetcher: async (params) => {
    const { data } = await customerApi.getPublicSeaList(params as any);
    return data;
  },
  onError: (error) => {
    console.error('Failed to fetch pool customers:', error);
  }
});

const handleSearch = () => {
  search();
};

const handleReset = () => {
  reset();
};

const handleClaim = async (row: Customer) => {
  try {
    await ElMessageBox.confirm(`确定领取客户"${row.name}"吗？`, '提示', {
      type: 'info'
    });
    // 调用领取接口
    ElMessage.success('领取成功');
    await fetchData();
  } catch (error) {
    // 取消
  }
};

const handleView = (row: Customer) => {
  router.push(`/customer/detail/${row.id}`);
};

const getLevelTagType = (level: string) => getCustomerLevelTag(level);
const getLevelLabel = (level: string) => getCustomerLevelLabel(level);
const getStatusLabel = (status: string) => getCustomerStatusLabel(status);

onMounted(() => {
  fetchData();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.phone-masked {
  font-family: monospace;
  letter-spacing: 1px;
}
</style>
