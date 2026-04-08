import type { UserRole } from './common';

// 登录凭证
export interface LoginCredentials {
  account?: string;  // 手机号或账号
  phone?: string;    // 手机号 (与account互斥)
  password: string;
}

// 登录响应
export interface LoginResponse {
  token?: string;
  accessToken?: string;
  expiresIn: number;
  refreshToken: string;
  tokenType?: string;
  user: UserInfo;
}

// 用户信息
export interface UserInfo {
  id: number;
  username: string;
  realName: string;
  phone: string;
  role?: UserRole;
  roles?: UserRole[];       // 多角色支持
  avatar?: string;
  permissions?: string[];   // 权限码列表
  status?: 'ACTIVE' | 'DISABLED';
  lastLoginAt?: string;
  lastLoginIp?: string;
  createdAt?: string;
}

// Token 刷新请求
export interface RefreshTokenRequest {
  refreshToken: string;
}

// 用户权限
export interface UserPermission {
  id: number;
  code: string;
  name: string;
  type: 'MENU' | 'ACTION' | 'DATA';
  resource?: string;
}

// 菜单项
export interface MenuItem {
  id: number;
  name: string;
  path?: string;
  icon?: string;
  permission?: string;
  children: MenuItem[];
  visible: boolean;
  sort: number;
}
