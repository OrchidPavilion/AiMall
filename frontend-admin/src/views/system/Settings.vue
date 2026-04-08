<template>
  <div class="system-settings">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础设置" name="basic">
          <el-form :model="config" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="config.systemName" />
            </el-form-item>
            <el-form-item label="系统LOGO">
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleLogoChange"
              >
                <img v-if="config.logoUrl" :src="config.logoUrl" class="logo-preview" />
                <el-button v-else type="primary">上传LOGO</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="主题色">
              <el-color-picker v-model="config.themeColor" />
            </el-form-item>
            <el-form-item label="会话超时">
              <el-input-number v-model="config.sessionTimeout" :min="3600" :max="86400" />
              <span class="unit">秒</span>
            </el-form-item>
            <el-form-item label="允许注册">
              <el-switch v-model="config.registrationEnabled" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSave" :loading="saving">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="安全设置" name="security">
          <el-form :model="config.passwordPolicy" label-width="150px">
            <el-form-item label="密码最小长度">
              <el-input-number v-model="config.passwordPolicy.minLength" :min="6" :max="32" />
            </el-form-item>
            <el-form-item label="要求大写字母">
              <el-switch v-model="config.passwordPolicy.requireUppercase" />
            </el-form-item>
            <el-form-item label="要求数字">
              <el-switch v-model="config.passwordPolicy.requireNumber" />
            </el-form-item>
            <el-form-item label="密码过期天数">
              <el-input-number v-model="config.passwordPolicy.expireDays" :min="0" />
              <span class="unit">天 (0表示永不过期)</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveSecurity">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="字段配置" name="field-config">
          <el-tabs v-model="fieldConfigTab">
            <el-tab-pane label="客户字段" name="customer">
              <FieldConfigManager domain="customer" />
            </el-tab-pane>
            <el-tab-pane label="订单字段" name="order">
              <FieldConfigManager domain="order" />
            </el-tab-pane>
            <el-tab-pane label="商品字段" name="product">
              <FieldConfigManager domain="product" />
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { systemApi } from '@/api';
import FieldConfigManager from '@/components/common/FieldConfigManager.vue';
import type { SystemConfig } from '@/types';

const activeTab = ref('basic');
const fieldConfigTab = ref<'customer' | 'order' | 'product'>('customer');
const saving = ref(false);
const config = reactive<SystemConfig>({
  id: 0,
  systemName: 'GhostFit 管理后台',
  logoUrl: '',
  themeColor: '#1890ff',
  passwordPolicy: {
    minLength: 8,
    requireUppercase: true,
    requireNumber: true,
    requireSpecialChar: false,
    expireDays: 90
  },
  sessionTimeout: 86400,
  registrationEnabled: false,
  contactEmail: '',
  contactPhone: '',
  updatedAt: ''
});

const fetchConfig = async () => {
  try {
    const { data } = await systemApi.getConfig();
    Object.assign(config, data);
  } catch (error) {
    console.error('Failed to fetch config:', error);
  }
};

const handleLogoChange = (file: any) => {
  config.logoUrl = URL.createObjectURL(file.raw);
};

const handleSave = async () => {
  saving.value = true;
  try {
    await systemApi.updateConfig(config as any);
    ElMessage.success('配置已保存');
  } catch (error) {
    console.error('Save failed:', error);
  } finally {
    saving.value = false;
  }
};

const handleSaveSecurity = async () => {
  await handleSave();
};

onMounted(() => {
  fetchConfig();
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.unit {
  margin-left: $spacing-sm;
  color: $text-secondary;
}

.logo-preview {
  width: 100px;
  height: 100px;
  object-fit: contain;
  border: 1px solid $border-color-lighter;
  border-radius: $border-radius-base;
}
</style>
