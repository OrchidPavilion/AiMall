<template>
  <div class="sidebar" :class="{ collapsed }">
    <div class="logo">
      <span v-if="!collapsed" class="logo-full">GhostFit</span>
      <span v-else class="logo-sm">GF</span>
    </div>
    
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :collapse-transition="false"
      router
    >
      <template v-for="menu in accessibleMenus" :key="menu.id">
        <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.path || ''">
          <template #title>
            <el-icon v-if="resolveMenuIcon(menu.icon)">
              <component :is="resolveMenuIcon(menu.icon)" />
            </el-icon>
            <span>{{ menu.name }}</span>
          </template>

          <template v-for="child in menu.children" :key="child.id">
            <el-sub-menu v-if="child.children && child.children.length > 0" :index="child.path || `sub-${child.id}`">
              <template #title>
                <el-icon v-if="resolveMenuIcon(child.icon)">
                  <component :is="resolveMenuIcon(child.icon)" />
                </el-icon>
                <span>{{ child.name }}</span>
              </template>
              <el-menu-item
                v-for="grand in child.children"
                :key="grand.id"
                :index="grand.path || ''"
              >
                <el-icon v-if="resolveMenuIcon(grand.icon)">
                  <component :is="resolveMenuIcon(grand.icon)" />
                </el-icon>
                <span>{{ grand.name }}</span>
              </el-menu-item>
            </el-sub-menu>

            <el-menu-item
              v-else
              :index="child.path || ''"
            >
              <el-icon v-if="resolveMenuIcon(child.icon)">
                <component :is="resolveMenuIcon(child.icon)" />
              </el-icon>
              <span>{{ child.name }}</span>
            </el-menu-item>
          </template>
        </el-sub-menu>
        
        <el-menu-item v-else :index="menu.path || ''">
          <el-icon v-if="resolveMenuIcon(menu.icon)">
            <component :is="resolveMenuIcon(menu.icon)" />
          </el-icon>
          <template #title>{{ menu.name }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import {
  HomeFilled,
  User,
  ShoppingBag,
  Tickets,
  Shop,
  Setting,
  List as ListIcon,
  Grid,
  DataBoard,
  Connection,
  Bell,
  Document,
  Collection,
  Picture,
  Monitor,
  UserFilled
} from '@element-plus/icons-vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/stores/app.store';
import { usePermissionStore } from '@/stores/permission.store';

const route = useRoute();
const appStore = useAppStore();
const permissionStore = usePermissionStore();

const collapsed = computed(() => appStore.sidebarCollapsed);
const accessibleMenus = computed(() => permissionStore.accessibleMenus);

const activeMenu = computed(() => {
  const { path } = route;
  return path;
});

const iconMap: Record<string, any> = {
  dashboard: HomeFilled,
  user: User,
  users: UserFilled,
  goods: ShoppingBag,
  order: Tickets,
  store: Shop,
  setting: Setting,
  config: Setting,
  list: ListIcon,
  category: Grid,
  layout: DataBoard,
  permission: Collection,
  link: Connection,
  ad: Picture,
  detail: Document,
  pool: Monitor
};

function resolveMenuIcon(name?: string) {
  if (!name) return null;
  return iconMap[String(name).toLowerCase()] || null;
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
  width: $sidebar-width;
  height: 100vh;
  background: $white;
  border-right: 1px solid $border-color-lighter;
  transition: width 0.3s;
  overflow: hidden;
  
  &.collapsed {
    width: $sidebar-collapsed-width;
  }
  
  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: $header-height;
    border-bottom: 1px solid $border-color-lighter;
    
    .logo-full {
      font-size: 20px;
      font-weight: 600;
      color: $primary-color;
    }
    
    .logo-sm {
      font-size: 18px;
      font-weight: 600;
      color: $primary-color;
    }
  }
  
  .el-menu {
    border-right: none;
    height: calc(100vh - #{$header-height});
    overflow-y: auto;
    
    &:not(.el-menu--collapse) {
      width: $sidebar-width;
    }
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: $sidebar-collapsed-width;
    .el-menu:not(.el-menu--collapse) {
      width: $sidebar-collapsed-width !important;
    }
  }
}
</style>
