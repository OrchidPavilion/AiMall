<template>
  <div class="customer-detail">
    <el-page-header @back="handleBack" class="mb-16" />
    
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ customer.name }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ maskPhone(customer.phone) }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ getGenderLabel(customer.gender) }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ customer.age || '-' }}</el-descriptions-item>
            <el-descriptions-item label="等级">
              <el-tag :type="getLevelTagType(customer.level)">
                {{ getLevelLabel(customer.level) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag>{{ getStatusLabel(customer.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="跟进人">{{ customer.assignee?.name || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ customer.address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(customer.createdAt) }}</el-descriptions-item>
          </el-descriptions>
          
          <div class="mt-16">
            <el-button type="primary" size="small" @click="handleEdit">编辑</el-button>
            <el-button size="small" @click="handleAssign">分配跟进</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>最近订单</span>
          </template>
          <el-table :data="customer.orders || []" stripe>
            <el-table-column prop="orderNo" label="订单号" min-width="150" />
            <el-table-column prop="totalAmount" label="金额" width="100">
              <template #default="{ row }">
                <span class="text-primary">¥{{ (row.totalAmount / 100).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                {{ getOrderStatusLabel(row.status) }}
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="下单时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.createdAt) }}
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!customer.orders?.length" class="empty-state">
            <div class="empty-icon">📦</div>
            <div class="empty-text">暂无订单</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { customerApi } from '@/api';
import {
  getCustomerGenderLabel,
  getCustomerLevelLabel,
  getCustomerLevelTag,
  getCustomerStatusLabel,
  getOrderStatusLabel as getOrderStatusLabelFromDict
} from '@/constants/dictionaries';
import { formatDate, maskPhone } from '@/utils/format';
import type { CustomerDetail } from '@/types';

const route = useRoute();
const router = useRouter();
const customerId = Number(route.params.id);

const customer = ref<CustomerDetail>({} as any);

onMounted(async () => {
  try {
    const { data } = await customerApi.getDetail(customerId);
    customer.value = data;
  } catch (error) {
    ElMessage.error('获取客户信息失败');
    router.back();
  }
});

const handleBack = () => {
  router.back();
};

const handleEdit = () => {
  router.push(`/customer/edit/${customerId}`);
};

const handleAssign = () => {
  // 分配客户逻辑
};

const getGenderLabel = (gender: string) => getCustomerGenderLabel(gender);
const getLevelTagType = (level: string) => getCustomerLevelTag(level);
const getLevelLabel = (level: string) => getCustomerLevelLabel(level);
const getStatusLabel = (status: string) => getCustomerStatusLabel(status);
const getOrderStatusLabel = (status: string) => getOrderStatusLabelFromDict(status);
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.mt-16 {
  margin-top: $spacing-md;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xxl;
  color: $text-secondary;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: $spacing-sm;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: $font-size-base;
  }
}
</style>
