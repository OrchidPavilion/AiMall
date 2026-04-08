import { useAuthStore } from '@/stores/auth.store';

const TOKEN_KEY = 'ghostfit_token';
const REFRESH_TOKEN_KEY = 'ghostfit_refresh_token';

/**
 * 存储 Token
 */
export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * 获取 Token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * 移除 Token
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function setRefreshToken(token: string) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function removeRefreshToken() {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * 清除认证信息
 */
export function clearAuth() {
  removeToken();
  removeRefreshToken();
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getToken();
}