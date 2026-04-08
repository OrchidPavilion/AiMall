<template>
  <header class="header" :class="{ collapsed, mobile: appStore.isMobile }">
    <div class="left-actions">
      <el-button
        class="collapse-btn"
        link
        @click="handleToggleSidebar"
      >
        <el-icon :size="20">
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>
      
      <Breadcrumb class="breadcrumb" />
    </div>
    
    <div class="right-actions">
      <!-- 搜索 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索..."
        clearable
        :prefix-icon="Search"
        class="search-input"
      />
      
      <!-- 全屏 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-button link @click="toggleFullscreen">
          <el-icon :size="18">
            <FullScreen />
          </el-icon>
        </el-button>
      </el-tooltip>
      
      <!-- 用户信息 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <el-avatar :size="32" :src="userInfo?.avatar">
            {{ userInfo?.realName?.charAt(0) || 'U' }}
          </el-avatar>
          <span class="username">{{ userInfo?.realName }}</span>
          <el-icon class="arrow"><ArrowDown /></el-icon>
        </div>
        
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              个人设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { Search, Fold, Expand, FullScreen, ArrowDown } from '@element-plus/icons-vue';
import { useAuthStore } from '@/stores/auth.store';
import { useAppStore } from '@/stores/app.store';
import Breadcrumb from './Breadcrumb.vue';

const router = useRouter();
const authStore = useAuthStore();
const appStore = useAppStore();

const collapsed = computed(() => appStore.sidebarCollapsed);
const userInfo = computed(() => authStore.userInfo);
const searchKeyword = ref('');

const handleToggleSidebar = () => {
  appStore.toggleSidebar();
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile');
      break;
    case 'settings':
      router.push('/settings');
      break;
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        authStore.logout();
      } catch {
        // 取消退出
      }
      break;
  }
};
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.header {
  position: fixed;
  top: 0;
  left: $sidebar-width;
  right: 0;
  z-index: 99;
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-md;
  background: $white;
  border-bottom: 1px solid $border-color-lighter;
  transition: left 0.3s;
  
  &.collapsed {
    left: $sidebar-collapsed-width;
  }
  
  .left-actions {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    
    .collapse-btn {
      padding: 4px;
    }
    
    .breadcrumb {
      margin-left: $spacing-sm;
    }
  }
  
  .right-actions {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    
    .search-input {
      width: 240px;
      
      :deep(.el-input__wrapper) {
        padding: 0 12px;
        border-radius: $border-radius-base;
      }
    }
    
    .user-dropdown {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      cursor: pointer;
      padding: $spacing-xs $spacing-sm;
      border-radius: $border-radius-base;
      transition: background-color 0.2s;
      
      &:hover {
        background-color: $bg-hover;
      }
      
      .username {
        font-size: $font-size-sm;
        color: $text-primary;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .arrow {
        font-size: 12px;
        color: $text-secondary;
      }
    }
  }
}

@media (max-width: 768px) {
  .header {
    left: $sidebar-collapsed-width !important;
    padding: 0 $spacing-sm;

    .left-actions {
      gap: $spacing-sm;
      .breadcrumb {
        display: none;
      }
    }

    .right-actions {
      gap: $spacing-sm;

      .search-input {
        display: none;
      }

      .user-dropdown {
        .username,
        .arrow {
          display: none;
        }
      }
    }
  }
}
</style>
