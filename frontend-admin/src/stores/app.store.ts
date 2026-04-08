import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRoute } from 'vue-router';

export const useAppStore = defineStore('app', () => {
  const route = useRoute();
  
  const sidebarCollapsed = ref(false);
  const isMobile = ref(false);
  const breadcrumbs = ref<Array<{ path: string; title: string }>>([]);
  
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  };

  const syncViewport = () => {
    if (typeof window === 'undefined') return;
    isMobile.value = window.innerWidth <= 768;
    if (isMobile.value) {
      // 手机端默认收起，仅显示图标
      sidebarCollapsed.value = true;
    }
  };
  
  const setBreadcrumbs = (matched: any[]) => {
    breadcrumbs.value = matched
      .filter(record => record.meta?.title)
      .map(record => ({
        path: record.path,
        title: record.meta.title as string
      }));
  };
  
  return {
    sidebarCollapsed,
    isMobile,
    breadcrumbs,
    toggleSidebar,
    setBreadcrumbs,
    syncViewport
  };
});
