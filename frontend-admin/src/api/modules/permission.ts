import request from '../request';
import type { MenuItem, Role } from '@/types';

export const permissionApi = {
  // 获取权限菜单树
  getMenus() {
    return request.post<MenuItem[]>('/permission/menus');
  },
  
  // 获取角色列表
  getRoles(params: { page: number; pageSize: number }) {
    return request.post<Role[]>('/permission/roles/list', null, { params });
  },
  
  // 获取角色详情
  getRoleDetail(id: number) {
    return request.post<Role>(`/permission/roles/${id}`);
  },
  
  // 创建角色
  create(data: Partial<Role>) {
    return request.post<{ roleId: number }>('/permission/roles', data);
  },
  
  // 更新角色
  update(id: number, data: Partial<Role>) {
    return request.put(`/permission/roles/${id}`, data);
  },
  
  // 删除角色
  delete(id: number) {
    return request.delete(`/permission/roles/${id}`);
  },
  
  // 保存角色权限
  savePermissions(roleId: number, permissions: {
    menuIds: number[];
    permissions: Record<string, string[]>;
    dataScope: string;
  }) {
    return request.put(`/permission/roles/${roleId}/permissions`, {
      permissionIds: permissions.menuIds || []
    });
  },
  
  // 获取权限模板列表
  getTemplates() {
    return request.post<Array<{ id: number; name: string; description: string }>>('/permission/templates');
  }
};
