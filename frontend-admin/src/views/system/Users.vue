<template>
  <div class="user-management">
    <ListPageScaffold
      :current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      @current-change="setPage"
      @size-change="setPageSize"
    >
      <template #actions>
        <el-button type="primary" size="small" @click="handleCreate">新增用户</el-button>
      </template>

      <SchemaTable :data="tableData" :columns="columns" :loading="loading">
        <template #cell-status="{ row }">
          <el-tag :type="getUserStatusTag(row.status)">
            {{ getUserStatusLabel(row.status) }}
          </el-tag>
        </template>
        <template #cell-lastLoginAt="{ row }">
          {{ row.lastLoginAt ? formatDateText(row.lastLoginAt) : '-' }}
        </template>
        <template #cell-actions="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="handleResetPassword(row)">重置密码</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </SchemaTable>
    </ListPageScaffold>

    <SchemaDrawerForm
      ref="drawerRef"
      v-model="drawerVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      :model="formModel"
      :fields="drawerFields"
      :rules="drawerRules"
      :size="drawerSize"
      :loading="submitLoading"
      :before-close="handleBeforeClose"
      @submit="handleSubmit"
      @cancel="handleCancel"
    >
      <template #field-phone="{ field }">
        <el-input v-model="formModel.phone" :disabled="isEdit" :placeholder="field.placeholder || '请输入手机号'" />
      </template>
      <template #field-roleId>
        <el-select v-model="formModel.roleId" placeholder="请选择角色" style="width: 100%">
          <el-option v-for="role in roleOptions" :key="role.value" :label="role.label" :value="role.value" />
        </el-select>
      </template>
      <template #field-status>
        <el-radio-group v-model="formModel.status">
          <el-radio label="ACTIVE">启用</el-radio>
          <el-radio label="DISABLED">禁用</el-radio>
        </el-radio-group>
      </template>
    </SchemaDrawerForm>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import type { FormRules } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';
import { metaApi, permissionApi, userApi } from '@/api';
import ListPageScaffold from '@/components/common/ListPageScaffold.vue';
import SchemaTable, { type SchemaTableColumn } from '@/components/common/SchemaTable.vue';
import SchemaDrawerForm, { type SchemaDrawerField, type SchemaDrawerFormExposed } from '@/components/common/SchemaDrawerForm.vue';
import { usePagedList } from '@/composables/usePagedList';
import { getUserStatusLabel, getUserStatusTag } from '@/constants/dictionaries';
import type { User, UserCreateRequest, UserUpdateRequest } from '@/types';
import { formatBeijingDateTime } from '@/utils/time';

const {
  loading,
  tableData,
  pagination,
  fetchData,
  setPage,
  setPageSize
} = usePagedList<Record<string, never>, User>({
  initialQuery: {},
  fetcher: async (params) => {
    const { data } = await userApi.getList(params as any);
    return data;
  },
  onError: (error) => {
    console.error('Failed to fetch users:', error);
  }
});

const defaultColumns: SchemaTableColumn<User>[] = [
  { prop: 'id', label: 'ID', width: 80 },
  { prop: 'username', label: '用户名', minWidth: 120 },
  { prop: 'realName', label: '姓名', minWidth: 100 },
  { prop: 'phone', label: '手机号', width: 120 },
  { prop: 'role', label: '角色', width: 120 },
  { label: '状态', width: 100, slot: 'status', key: 'status' },
  { label: '最后登录', width: 160, slot: 'lastLoginAt', key: 'lastLoginAt' },
  { label: '操作', width: 220, fixed: 'right', slot: 'actions', key: 'actions' }
];
const columns = ref<SchemaTableColumn<User>[]>(defaultColumns);
const drawerRef = ref<SchemaDrawerFormExposed>();
const drawerVisible = ref(false);
const submitLoading = ref(false);
const isEdit = ref(false);
const editingId = ref<number | null>(null);
const roleOptions = ref<Array<{ label: string; value: number }>>([]);
const formModel = ref<any>(createEmptyForm());
const formSnapshot = ref('');

const drawerSize = computed(() => (window.innerWidth <= 768 ? '92%' : '36%'));
const drawerFields = computed<SchemaDrawerField[]>(() => {
  const fields: SchemaDrawerField[] = [
    { prop: 'username', label: '用户名', type: 'input', placeholder: '请输入用户名' },
    { prop: 'realName', label: '姓名', type: 'input', placeholder: '请输入姓名' },
    { prop: 'phone', label: '手机号', type: 'custom', placeholder: '请输入手机号' },
    { prop: 'roleId', label: '角色', type: 'custom' },
    { prop: 'status', label: '状态', type: 'custom' }
  ];
  if (!isEdit.value) {
    fields.splice(1, 0, { prop: 'password', label: '密码', type: 'input', inputType: 'password', placeholder: '至少8位' } as any);
  }
  return fields;
});

const drawerRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 8, message: '密码至少8位', trigger: 'blur' }],
  realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  roleId: [{ required: true, message: '请选择角色', trigger: 'change' }]
};

const handleCreate = () => {
  isEdit.value = false;
  editingId.value = null;
  formModel.value = createEmptyForm();
  formSnapshot.value = JSON.stringify(formModel.value);
  drawerVisible.value = true;
};

const handleEdit = async (row: User) => {
  try {
    const { data } = await userApi.getDetail(row.id);
    isEdit.value = true;
    editingId.value = row.id;
    formModel.value = {
      username: data.username,
      realName: data.realName,
      phone: data.phone,
      roleId: data.roleId,
      status: data.status
    };
    formSnapshot.value = JSON.stringify(formModel.value);
    drawerVisible.value = true;
  } catch (error: any) {
    ElMessage.error(error?.message || '加载用户详情失败');
  }
};

const handleResetPassword = async (row: User) => {
  try {
    await ElMessageBox.confirm(`确定重置用户 ${row.username} 的密码吗？`, '提示', {
      type: 'warning'
    });
    
    const { data } = await userApi.resetPassword(row.id);
    ElMessage.success(`新密码: ${data.newPassword} (请告知用户)`);
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('重置失败');
  }
};

const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm(`确定删除用户 ${row.username} 吗？`, '警告', {
      type: 'warning'
    });
    
    await userApi.delete(row.id);
    ElMessage.success('删除成功');
    await fetchData();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
};

const formatDateText = (date: string) => {
  return formatBeijingDateTime(date);
};

onMounted(() => {
  loadRoles();
  loadMeta();
  fetchData();
});

async function loadMeta() {
  try {
    const { data } = await metaApi.getUserListMeta();
    const remoteColumns = Array.isArray(data?.columns) ? data.columns : [];
    const normalized = remoteColumns
      .filter((c: any) => c && typeof c.label === 'string')
      .map((c: any) => ({
        key: c.key,
        prop: c.prop,
        label: c.label,
        width: c.width,
        minWidth: c.minWidth,
        fixed: c.fixed,
        slot: c.slot
      })) as SchemaTableColumn<User>[];
    if (normalized.length) {
      columns.value = normalized;
    }
  } catch (error) {
    console.warn('Failed to load user list meta, fallback to local schema', error);
  }
}

async function loadRoles() {
  try {
    const { data } = await permissionApi.getRoles({ page: 1, pageSize: 200 });
    const list = Array.isArray(data) ? data : (data?.list || []);
    roleOptions.value = list.map((r: any) => ({ label: r.name || r.code || `角色${r.id}`, value: Number(r.id) }));
  } catch (error) {
    console.warn('Failed to load roles', error);
    roleOptions.value = [];
  }
}

function createEmptyForm() {
  return {
    username: '',
    password: '',
    realName: '',
    phone: '',
    roleId: undefined,
    status: 'ACTIVE'
  };
}

function isFormDirty() {
  return JSON.stringify(formModel.value) !== formSnapshot.value;
}

function handleBeforeClose(done: () => void) {
  if (!isFormDirty()) {
    done();
    return;
  }
  ElMessageBox.confirm('当前填写资料未保存，是否取消？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(() => done()).catch(() => undefined);
}

function handleCancel() {
  handleBeforeClose(() => {
    drawerVisible.value = false;
  });
}

async function handleSubmit() {
  try {
    await drawerRef.value?.validate();
    submitLoading.value = true;
    if (isEdit.value && editingId.value) {
      const payload: UserUpdateRequest = {
        realName: formModel.value.realName,
        roleId: formModel.value.roleId,
        status: formModel.value.status
      };
      await userApi.update(editingId.value, payload);
      ElMessage.success('更新成功');
    } else {
      const payload: UserCreateRequest = {
        username: formModel.value.username,
        password: formModel.value.password,
        realName: formModel.value.realName,
        phone: formModel.value.phone,
        roleId: Number(formModel.value.roleId),
        status: formModel.value.status
      };
      await userApi.create(payload);
      ElMessage.success('创建成功');
    }
    drawerVisible.value = false;
    await fetchData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || (isEdit.value ? '更新失败' : '创建失败'));
    }
  } finally {
    submitLoading.value = false;
  }
}
</script>

<style lang="scss" scoped>
</style>
