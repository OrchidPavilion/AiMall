<template>
  <div class="permission-management">
    <el-card>
      <div class="table-actions">
        <el-button type="primary" size="small" @click="handleCreateRole">新增角色</el-button>
      </div>
      
      <el-table :data="roles" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column prop="dataScope" label="数据范围" width="120">
          <template #default="{ row }">
            {{ getDataScopeLabel(row.dataScope) }}
          </template>
        </el-table-column>
        <el-table-column label="权限数" width="100">
          <template #default="{ row }">
            {{ getTotalPermissions(row.permissions) }}
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">权限配置</el-button>
            <el-button link type="danger" @click="handleDelete(row)" :disabled="row.name === 'SUPER_ADMIN'">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 权限配置弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="角色权限配置"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="currentRole" label-width="100px">
        <el-form-item label="角色名称">
          <el-input v-model="currentRole.name" disabled />
        </el-form-item>
        <el-form-item label="权限配置">
          <el-tree
            ref="permissionTreeRef"
            :data="permissionTree"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            show-checkbox
            default-expand-all
            :check-strictly="false"
          />
        </el-form-item>
        <el-form-item label="数据范围">
          <el-radio-group v-model="currentRole.dataScope">
            <el-radio value="ALL">全部数据</el-radio>
            <el-radio value="ORG">所属机构</el-radio>
            <el-radio value="SELF_DEPT">本部门</el-radio>
            <el-radio value="SELF">仅个人</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { permissionApi } from '@/api';
import { formatBeijingDateTime } from '@/utils/time';
import type { Role, MenuItem } from '@/types';

const loading = ref(false);
const roles = ref<Role[]>([]);
const dialogVisible = ref(false);
const saving = ref(false);
const permissionTree = ref<MenuItem[]>([]);
const permissionTreeRef = ref();
const currentRole = reactive<Partial<Role>>({
  id: undefined,
  name: '',
  description: '',
  dataScope: 'SELF',
  permissions: []
});

const fetchRoles = async () => {
  loading.value = true;
  try {
    const { data } = await permissionApi.getRoles({ page: 1, pageSize: 100 });
    roles.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Failed to fetch roles:', error);
  } finally {
    loading.value = false;
  }
};

const fetchMenus = async () => {
  try {
    const { data } = await permissionApi.getMenus();
    permissionTree.value = data as any;
  } catch (error) {
    console.error('Failed to fetch menus:', error);
  }
};

const handleCreateRole = () => {
  ElMessage.info('新增角色功能待实现');
};

const handleEdit = async (row: Role) => {
  currentRole.id = row.id;
  currentRole.name = row.name;
  currentRole.description = row.description;
  currentRole.dataScope = row.dataScope;
  
  // 加载权限
  dialogVisible.value = true;
  await fetchMenus();
  
  // 设置已选中的权限节点
  const checkedKeys = convertPermissionsToKeys(row.permissions);
  permissionTreeRef.value?.setCheckedKeys(checkedKeys);
};

const handleDelete = async (row: Role) => {
  try {
    await ElMessageBox.confirm(`确定删除角色"${row.name}"吗？`, '警告', {
      type: 'warning'
    });
    
    await permissionApi.delete(row.id!);
    ElMessage.success('删除成功');
    await fetchRoles();
  } catch (error) {
    // 取消或失败
  }
};

const handleSavePermissions = async () => {
  if (!currentRole.id) return;
  
  saving.value = true;
  try {
    const checkedNodes = permissionTreeRef.value?.getCheckedNodes(true) as any[];
    const halfCheckedNodes = permissionTreeRef.value?.getHalfCheckedNodes(true) as any[];
    
    const permissions = combinePermissions(checkedNodes, halfCheckedNodes);
    
    await permissionApi.savePermissions(currentRole.id, {
      menuIds: [],
      permissions,
      dataScope: currentRole.dataScope
    });
    
    ElMessage.success('权限配置成功');
    dialogVisible.value = false;
    await fetchRoles();
  } catch (error) {
    console.error('Save permissions failed:', error);
  } finally {
    saving.value = false;
  }
};

const handleDialogClose = () => {
  permissionTreeRef.value?.setCheckedKeys([]);
};

const convertPermissionsToKeys = (permissions: Role['permissions']): number[] => {
  // 将权限数组转换为菜单节点ID数组
  const ids: number[] = [];
  permissions.forEach(p => {
    if (p.module) {
      // 假设 module 对应菜单ID（简化处理）
      ids.push(p.module as any);
    }
  });
  return ids;
};

const combinePermissions = (checkedNodes: any[], halfCheckedNodes: any[]) => {
  const permissions: Record<string, string[]> = {};
  
  const processNode = (node: any) => {
    const module = node.resource || node.name.toLowerCase();
    if (!permissions[module]) {
      permissions[module] = [];
    }
    // 这里简化处理，实际需要根据权限码添加 read/create/update/delete
    permissions[module].push('read');
  };
  
  checkedNodes.forEach(processNode);
  halfCheckedNodes.forEach(processNode);
  
  return permissions;
};

const getDataScopeLabel = (scope: string) => {
  const map: Record<string, string> = {
    ALL: '全部数据',
    ORG: '所属机构',
    SELF_DEPT: '本部门',
    SELF: '仅个人'
  };
  return map[scope] || scope;
};

const getTotalPermissions = (permissions: Role['permissions']) => {
  if (!permissions) return 0;
  return permissions.reduce((sum, p) => sum + (p.actions?.length || 0), 0);
};

const formatDate = (date: string) => {
  return formatBeijingDateTime(date) || '-';
};

onMounted(() => {
  fetchRoles();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.table-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: $spacing-md;
}

.mt-16 {
  margin-top: $spacing-md;
}
</style>
