<template>
  <div class="login-page">
    <div class="login-card">
      <h1>AiMall 管理后台</h1>
      <p>开发账号：admin / 123456</p>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" class="w-100" @click="submit">登录</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { aimallApi } from '@/api/aimall';

const router = useRouter();
const route = useRoute();
const form = reactive({ username: 'admin', password: '123456' });

async function submit() {
  try {
    const data = await aimallApi.adminLogin({ username: form.username, password: form.password });
    localStorage.setItem('aimall_admin_token', data.token);
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/mall/product-management/products';
    router.replace(redirect);
    ElMessage.success('登录成功');
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败');
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(160deg, #eff6ff 0%, #dbeafe 45%, #f8fbff 100%);
}
.login-card {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 18px 40px rgba(30, 64, 175, 0.12);
  border: 1px solid #dbeafe;
}
.login-card h1 {
  margin: 0 0 8px;
  color: #1d4ed8;
}
.login-card p {
  margin: 0 0 20px;
  color: #64748b;
}
.w-100 { width: 100%; }
</style>
