import request from '../request';
import type { PageResponse, UserDTO, UserCreateRequest, UserUpdateRequest } from '@/types';

export const userApi = {
  // 获取用户列表（分页）
  async getList(params: { page: number; pageSize: number; keyword?: string; roleId?: number; status?: number }) {
    const result = await request.post<PageResponse<any>>('/user/list', null, { params });
    return {
      ...result,
      data: {
        ...result.data,
        list: (result.data?.list || []).map(normalizeUser)
      }
    } as any;
  },
  
  // 获取用户详情
  async getDetail(id: number) {
    const result = await request.post<any>(`/user/${id}`);
    return { ...result, data: normalizeUser(result.data) } as any;
  },
  
  // 创建用户
  create(data: UserCreateRequest) {
    return request.post<{ id: number }>('/user', data);
  },
  
  // 更新用户
  update(id: number, data: UserUpdateRequest) {
    return request.put(`/user/${id}`, data);
  },
  
  // 删除用户
  delete(id: number) {
    return request.delete(`/user/${id}`);
  },
  
  // 重置密码
  resetPassword(id: number, password?: string) {
    return request.put(`/user/${id}/reset-password`, password ? { password } : {});
  }
};

function normalizeUser(user: any): any {
  if (!user) return user;
  return {
    ...user,
    role: user.roleCode || user.role || 'OPERATION_MANAGER',
    status: user.status === 1 || user.status === 'ACTIVE' ? 'ACTIVE' : 'DISABLED'
  };
}
