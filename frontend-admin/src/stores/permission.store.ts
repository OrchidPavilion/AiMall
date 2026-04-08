import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { MenuItem } from '@/types';

export const usePermissionStore = defineStore('permission', () => {
  const menus = ref<MenuItem[]>([]);
  const permissionsMap = ref<Map<string, boolean>>(new Map());

  function buildMenuTree(menuList: any[]): MenuItem[] {
    const enabledMenus = menuList
      .filter(item => item && item.type !== 2 && item.enabled !== 0)
      .filter(item => item.path !== '/customer/detail')
      .map((item) => ({
        ...item,
        visible: item.visible ?? item.enabled !== 0,
        children: [] as any[]
      }));

    const nodeMap = new Map<number, any>();
    enabledMenus.forEach((item) => {
      nodeMap.set(Number(item.id), item);
    });

    const roots: any[] = [];
    enabledMenus.forEach((item) => {
      const parentId = Number(item.parentId ?? 0);
      if (parentId > 0 && nodeMap.has(parentId)) {
        nodeMap.get(parentId).children.push(item);
      } else {
        roots.push(item);
      }
    });

    const sortRecursively = (items: any[]): any[] => {
      items.sort((a, b) => (a.sort ?? 0) - (b.sort ?? 0));
      items.forEach((item) => sortRecursively(item.children || []));
      return items;
    };

    return transformMenuStructure(sortRecursively(roots)) as MenuItem[];
  }

  function transformMenuStructure(roots: any[]): any[] {
    const clone = JSON.parse(JSON.stringify(roots || []));
    const findByPath = (path: string) => clone.find((item: any) => item.path === path);

    const storeRoot = findByPath('/store');
    const productRoot = findByPath('/product');
    const orderRoot = findByPath('/order');

    if (storeRoot) {
      const ensureGroup = (name: string, path: string, icon: string, sort: number, id: number) => {
        let node = (storeRoot.children || []).find((c: any) => c.path === path);
        if (!node) {
          node = { id, name, path, icon, permission: '', visible: true, sort, children: [] };
          storeRoot.children = [...(storeRoot.children || []), node];
        }
        return node;
      };

      const storeProductGroup = ensureGroup('商品管理', '/store/product', 'goods', 10, -3001);
      const storeOrderGroup = ensureGroup('订单管理', '/store/order', 'order', 11, -3002);

      if (productRoot) {
        const movedChildren = (productRoot.children || []).map((c: any) => ({ ...c }));
        const categoryNode = (storeRoot.children || []).find((c: any) => c.path === '/store/categories');
        const normalized = movedChildren
          .filter((c: any) => c.path !== '/product/category');
        if (categoryNode) {
          normalized.push({
            ...categoryNode,
            name: '分类管理',
            path: '/store/categories'
          });
          storeRoot.children = (storeRoot.children || []).filter((c: any) => c.path !== '/store/categories');
        }
        storeProductGroup.children = normalized.sort((a: any, b: any) => (a.sort ?? 0) - (b.sort ?? 0));
      }

      if (orderRoot) {
        storeOrderGroup.children = (orderRoot.children || []).map((c: any) => ({ ...c }));
      }

      storeRoot.children = (storeRoot.children || []).sort((a: any, b: any) => (a.sort ?? 0) - (b.sort ?? 0));
    }

    return clone.filter((item: any) => !['/product', '/order'].includes(item.path));
  }
  
  // 设置菜单
  function setMenus(menuList: MenuItem[] | unknown) {
    if (!Array.isArray(menuList)) {
      console.warn('Invalid menu payload, expected array:', menuList);
      menus.value = [];
      return;
    }
    menus.value = buildMenuTree(menuList as any[]);
  }
  
  // 设置权限列表
  function setPermissions(permissions: string[]) {
    permissionsMap.value.clear();
    permissions.forEach(p => {
      permissionsMap.value.set(p, true);
    });
  }
  
  // 检查是否有权限
  function hasPermission(permission: string | undefined): boolean {
    if (!permission) return true;
    
    // 先检查具体权限码
    if (permissionsMap.value.has(permission)) {
      return true;
    }
    
    // 通配符权限
    if (permissionsMap.value.has('*')) {
      return true;
    }
    
    // 检查模块级通配符，如 "customer:*"
    const [module, action] = permission.split(':');
    if (module && action) {
      const moduleWildcard = `${module}:*`;
      if (permissionsMap.value.has(moduleWildcard)) {
        return true;
      }
    }
    
    return false;
  }
  
  // 获取可访问的菜单
  const accessibleMenus = computed(() => {
    const filterMenus = (items: MenuItem[]): MenuItem[] => {
      return items.filter(item => {
        if (item.permission && !hasPermission(item.permission)) {
          return false;
        }
        if (item.children && item.children.length > 0) {
          item.children = filterMenus(item.children);
        }
        return true;
      });
    };
    
    return Array.isArray(menus.value) ? filterMenus(menus.value) : [];
  });
  
  return {
    menus,
    permissionsMap,
    setMenus,
    setPermissions,
    hasPermission,
    accessibleMenus
  };
});
