<template>
  <div class="category-list">
    <el-card>
      <div class="table-actions">
        <el-button type="primary" size="small" @click="handleCreate">新增分类</el-button>
      </div>
      
      <el-table :data="treeData" row-key="id" default-expand-all border>
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="icon" label="图标" width="100">
          <template #default="{ row }">
            <span v-if="row.icon">🖼️</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="productCount" label="商品数" width="80" />
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleAddChild(row)">添加子分类</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { storeApi } from '@/api';
import type { ProductCategory } from '@/types';

const treeData = ref<ProductCategory[]>([]);

const fetchData = async () => {
  try {
    const { data } = await storeApi.getCategoryTree();
    treeData.value = data;
  } catch (error) {
    console.error('Failed to fetch categories:', error);
  }
};

const handleCreate = () => {
  // 新增顶层分类
  ElMessage.info('新增分类功能待实现');
};

const handleAddChild = (row: ProductCategory) => {
  ElMessage.info(`添加 ${row.name} 的子分类`);
};

const handleEdit = (row: ProductCategory) => {
  ElMessage.info(`编辑分类 ${row.name}`);
};

const handleDelete = async (row: ProductCategory) => {
  try {
    await storeApi.deleteCategory(row.id);
    ElMessage.success('删除成功');
    await fetchData();
  } catch (error) {
    console.error('Delete failed:', error);
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.table-actions {
  margin-bottom: $spacing-md;
}
</style>