import request from '../request';
import type { LoginCredentials, LoginResponse, UserInfo } from '@/types/auth';

export const authApi = {
  // 用户登录
  login(credentials: LoginCredentials) {
    return request.post<LoginResponse>('/auth/login', credentials);
  },
  
  // 刷新 Token
  refresh(refreshToken: string) {
    return request.post<LoginResponse>('/auth/refresh', null, {
      params: { refreshToken }
    });
  },
  
  // 登出
  logout() {
    return request.post('/auth/logout');
  },
  
  // 获取当前用户信息
  getUserInfo() {
    return request.post<UserInfo>('/auth/me');
  }
};
