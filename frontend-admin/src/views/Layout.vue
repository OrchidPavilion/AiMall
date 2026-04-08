<template>
  <div class="layout-container" :class="{ mobile: appStore.isMobile }">
    <Sidebar />
    
    <div class="layout-main" :class="{ collapsed: appStore.sidebarCollapsed }">
      <Header />
      <MainContent>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </MainContent>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/stores/app.store';
import { usePermissionStore } from '@/stores/permission.store';
import { permissionApi } from '@/api';
import { Sidebar, Header, MainContent } from '@/components/layout';

const route = useRoute();
const appStore = useAppStore();
const permissionStore = usePermissionStore();

onMounted(async () => {
  appStore.syncViewport();
  window.addEventListener('resize', appStore.syncViewport);
  // 加载权限菜单
  if (permissionStore.menus.length === 0) {
    try {
      const { data: menus } = await permissionApi.getMenus();
      permissionStore.setMenus(menus);
    } catch (error) {
      console.error('Failed to load menus:', error);
    }
  }
  
  // 设置面包屑
  appStore.setBreadcrumbs(route.matched);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', appStore.syncViewport);
});
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.layout-container {
  display: flex;
  height: 100vh;
  
  .layout-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin-left: $sidebar-width;
    transition: margin-left 0.3s;
    
    &.collapsed {
      margin-left: $sidebar-collapsed-width;
    }
  }
}

@media (max-width: 768px) {
  .layout-container {
    .layout-main {
      margin-left: $sidebar-collapsed-width !important;
    }
  }
}
</style>
