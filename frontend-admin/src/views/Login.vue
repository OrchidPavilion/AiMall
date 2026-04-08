<template>
  <div class="login-container">
    <div class="bg-overlay"></div>
    <div class="fitness-ring ring-1"></div>
    <div class="fitness-ring ring-2"></div>
    <div class="fitness-line line-1"></div>
    <div class="fitness-line line-2"></div>
    <div class="fitness-line line-3"></div>

    <div class="login-card">
      <div class="logo-area">
        <img src="@/assets/images/logo.svg" alt="GhostFit" class="logo" />
        <h1 class="title">GhostFit管理后台</h1>
        <p class="subtitle">欢迎登录管理后台</p>
      </div>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="账号" prop="account">
          <el-input
            v-model="form.account"
            placeholder="请输入手机号或账号"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="submit-btn"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        <p>© 2025 GhostFit · 健身业务管理系统</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { useAuthStore } from '@/stores/auth.store';
import { authApi } from '@/api';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const formRef = ref();
const loading = ref(false);
const rememberMe = ref(false);

const form = reactive({
  account: '',
  password: ''
});

const rules = {
  account: [
    { required: true, message: '请输入手机号或账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  try {
    await formRef.value.validate();
    loading.value = true;
    
    await authStore.login(form);
    ElMessage.success('登录成功');
    const redirect = typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
      ? route.query.redirect
      : '/dashboard';
    await router.replace(redirect);
  } catch (error: any) {
    console.error('Login failed:', error);
    ElMessage.error(error?.message || '登录失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.login-container {
  --bg-ink: rgba(108, 146, 204, 0.18);
  --bg-ink-strong: rgba(108, 146, 204, 0.28);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background:
    radial-gradient(circle at 50% 48%, rgba(255, 255, 255, 0.98) 0%, rgba(248, 251, 255, 0.95) 32%, rgba(234, 241, 251, 0.92) 58%, rgba(223, 233, 247, 0.96) 100%),
    linear-gradient(180deg, #eef4fb 0%, #e6eef8 100%);

  .bg-overlay {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
      radial-gradient(circle at 8% 18%, rgba(114, 149, 205, 0.12) 0 120px, transparent 121px),
      radial-gradient(circle at 92% 26%, rgba(114, 149, 205, 0.12) 0 120px, transparent 121px),
      radial-gradient(circle at 18% 78%, rgba(114, 149, 205, 0.10) 0 90px, transparent 91px),
      radial-gradient(circle at 86% 80%, rgba(114, 149, 205, 0.10) 0 110px, transparent 111px);
    opacity: 0.9;
  }

  .fitness-ring {
    position: absolute;
    border: 2px solid var(--bg-ink);
    border-radius: 50%;
    pointer-events: none;
    filter: blur(0.2px);
  }

  .ring-1 {
    width: min(86vw, 1180px);
    height: min(66vw, 760px);
    border-color: rgba(123, 157, 210, 0.12);
  }

  .ring-2 {
    width: min(74vw, 980px);
    height: min(54vw, 620px);
    border-color: rgba(123, 157, 210, 0.15);
  }

  .fitness-line {
    position: absolute;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--bg-ink-strong), transparent);
    transform-origin: center;
    pointer-events: none;
    opacity: 0.65;
  }

  .line-1 {
    width: 260px;
    top: 14%;
    left: 8%;
    transform: rotate(-24deg);
  }

  .line-2 {
    width: 320px;
    right: 10%;
    top: 19%;
    transform: rotate(18deg);
  }

  .line-3 {
    width: 340px;
    right: 14%;
    bottom: 16%;
    transform: rotate(-24deg);
  }

  .login-card {
    position: relative;
    z-index: 1;
    width: min(420px, 100%);
    padding: 34px 30px 24px;
    background: rgba(255, 255, 255, 0.84);
    border: 1px solid rgba(146, 171, 212, 0.32);
    border-radius: 22px;
    box-shadow:
      0 22px 48px rgba(73, 100, 144, 0.18),
      inset 0 1px 0 rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);

    .logo-area {
      text-align: center;
      margin-bottom: 26px;

      .logo {
        width: 66px;
        height: 66px;
        margin-bottom: 12px;
        padding: 10px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(146, 171, 212, 0.25);
        box-shadow: 0 8px 18px rgba(86, 118, 171, 0.12);
      }

      .title {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #2f4367;
      }

      .subtitle {
        margin: 8px 0 0;
        font-size: 13px;
        color: #7287ad;
      }
    }

    :deep(.el-form-item__label) {
      color: #425a86;
      font-weight: 600;
      padding-bottom: 8px;
    }

    .el-form-item {
      margin-bottom: 18px;
    }

    :deep(.el-input__wrapper) {
      border-radius: 12px;
      min-height: 44px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow:
        0 0 0 1px rgba(151, 174, 211, 0.22) inset,
        0 3px 10px rgba(121, 147, 190, 0.06);
      transition: box-shadow 0.2s ease;
    }

    :deep(.el-input__wrapper.is-focus) {
      box-shadow:
        0 0 0 1px rgba(89, 132, 210, 0.52) inset,
        0 0 0 4px rgba(101, 143, 216, 0.12);
    }

    :deep(.el-checkbox__label) {
      color: #5f739b;
    }

    .submit-btn {
      width: 100%;
      height: 46px;
      border: none;
      border-radius: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      background: linear-gradient(90deg, #6a95de 0%, #7ca6ee 100%);
      box-shadow: 0 10px 20px rgba(82, 123, 197, 0.25);
    }

    :deep(.el-button.submit-btn:hover) {
      opacity: 0.96;
    }

    .footer {
      margin-top: 18px;
      text-align: center;
      color: #8091b3;
      font-size: 12px;
      line-height: 1.5;
    }
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 16px;

    .line-1,
    .line-2,
    .line-3,
    .ring-2 {
      display: none;
    }

    .login-card {
      width: 100%;
      max-width: 420px;
      padding: 26px 18px 18px;

      .logo-area {
        margin-bottom: 20px;

        .title {
          font-size: 22px;
        }
      }
    }
  }
}
</style>
