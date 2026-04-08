<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">AiMall Admin</div>
      <div class="menu-group">
        <div class="menu-l1">商城</div>
        <div class="menu-l2">商品管理</div>
        <RouterLink class="menu-l3" to="/mall/product-management/products">商品列表</RouterLink>
        <RouterLink class="menu-l3" to="/mall/product-management/categories">类别列表</RouterLink>
        <RouterLink class="menu-l3" to="/mall/product-management/recommendation">智能推荐</RouterLink>
        <RouterLink class="menu-l3" to="/mall/product-management/preview">线上预览</RouterLink>
      </div>
      <div class="menu-group">
        <div class="menu-l1">客户</div>
        <div class="menu-l2">客户管理</div>
        <RouterLink class="menu-l3" to="/customer/customer-management/list">客户列表</RouterLink>
      </div>
      <div class="menu-group">
        <div class="menu-l1">推荐系统</div>
        <RouterLink class="menu-l3" to="/recommendation-system/intelligent">智能推荐</RouterLink>
        <RouterLink class="menu-l3" to="/recommendation-system/analytics">数据分析</RouterLink>
        <RouterLink class="menu-l3" to="/recommendation-system/settings">推荐设置</RouterLink>
      </div>
    </aside>
    <main class="main">
      <header class="topbar">
        <div class="title">{{ pageTitle }}</div>
        <el-button text type="primary" @click="logout">退出登录</el-button>
      </header>
      <section class="content">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router';

const route = useRoute();
const router = useRouter();

const pageTitle = computed(() => (route.meta?.title as string) || 'AiMall');

function logout() {
  localStorage.removeItem('aimall_admin_token');
  router.replace('/login');
}
</script>

<style scoped lang="scss">
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px 1fr;
  background: #f4f8ff;
}
.sidebar {
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border-right: 1px solid #dbeafe;
  padding: 16px 14px;
}
.brand {
  font-weight: 700;
  color: #1d4ed8;
  padding: 10px 12px;
  border-radius: 10px;
  background: #eff6ff;
  margin-bottom: 14px;
}
.menu-group { margin-bottom: 14px; }
.menu-l1, .menu-l2, .menu-l3 {
  display: block;
  border-radius: 8px;
  margin: 4px 0;
  text-decoration: none;
}
.menu-l1 { padding: 8px 10px; font-weight: 700; color: #0f172a; }
.menu-l2 { padding: 8px 10px 8px 18px; color: #334155; background: #f8fbff; }
.menu-l3 { padding: 8px 10px 8px 28px; color: #475569; }
.menu-l3.router-link-active { background: #dbeafe; color: #1d4ed8; font-weight: 600; }
.main { display: flex; flex-direction: column; min-width: 0; }
.topbar {
  height: 56px;
  border-bottom: 1px solid #dbeafe;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}
.title { font-weight: 600; color: #1e3a8a; }
.content { padding: 16px; }
@media (max-width: 980px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { border-right: 0; border-bottom: 1px solid #dbeafe; }
}
</style>
