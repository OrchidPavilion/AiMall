import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '@/api';
import { UserRole, type UserInfo } from '@/types';

const TOKEN_KEY = 'token';
const USER_INFO_KEY = 'userInfo';
const ROLES_KEY = 'roles';
const PERMISSIONS_KEY = 'permissions';

function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function normalizeBearerToken(input: string): string {
  const token = String(input || '').trim();
  if (!token) return '';
  if (token.startsWith('Bearer ')) return token;
  if (token.startsWith('Bearer')) return `Bearer ${token.slice('Bearer'.length).trim()}`;
  return `Bearer ${token}`;
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '');
  const userInfo = ref<UserInfo | null>(readJson<UserInfo | null>(USER_INFO_KEY, null));
  const roles = ref<UserRole[]>(readJson<UserRole[]>(ROLES_KEY, []));
  const permissions = ref<string[]>(readJson<string[]>(PERMISSIONS_KEY, []));
  const sessionValidated = ref(false);
  
  const isLoggedIn = computed(() => !!token.value);
  
  const isSuperAdmin = computed(() => 
    roles.value.includes(UserRole.SUPER_ADMIN)
  );
  
  // 登录
  async function login(credentials: { account: string; password: string }) {
    const { data } = await authApi.login(credentials);
    const resolvedToken = data.accessToken || data.token || '';
    if (!resolvedToken) {
      throw new Error('登录响应缺少访问令牌');
    }

    token.value = normalizeBearerToken(resolvedToken);
    userInfo.value = {
      ...data.user,
      status: data.user.status || 'ACTIVE'
    } as UserInfo;
    roles.value = (data.user.roles?.length ? data.user.roles : (data.user.role ? [data.user.role] : [])) as UserRole[];
    permissions.value = data.user.permissions || (roles.value.includes(UserRole.SUPER_ADMIN) ? ['*'] : []);

    localStorage.setItem(TOKEN_KEY, token.value);
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo.value));
    localStorage.setItem(ROLES_KEY, JSON.stringify(roles.value));
    localStorage.setItem(PERMISSIONS_KEY, JSON.stringify(permissions.value));
    sessionValidated.value = true;
  }
  
  // 获取用户信息
  async function fetchUserInfo(force = false) {
    if (!force && userInfo.value) {
      sessionValidated.value = true;
      return;
    }

    const { data } = await authApi.getUserInfo();
    userInfo.value = data;
    roles.value = (data.roles?.length ? data.roles : (data.role ? [data.role] : [])) as UserRole[];
    permissions.value = data.permissions || [];
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo.value));
    localStorage.setItem(ROLES_KEY, JSON.stringify(roles.value));
    localStorage.setItem(PERMISSIONS_KEY, JSON.stringify(permissions.value));
    sessionValidated.value = true;
  }
  
  // 登出
  function logout(redirect = true) {
    token.value = '';
    userInfo.value = null;
    roles.value = [];
    permissions.value = [];
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_INFO_KEY);
    localStorage.removeItem(ROLES_KEY);
    localStorage.removeItem(PERMISSIONS_KEY);
    sessionValidated.value = false;
    if (redirect) {
      router.push('/login');
    }
  }
  
  // 检查是否有权限
  function hasPermission(permission: string | undefined): boolean {
    if (!permission) return true;
    
    // 超级管理员拥有所有权限
    if (isSuperAdmin.value) return true;
    
    // 检查具体权限码
    return permissions.value.includes(permission) || permissions.value.includes('*');
  }
  
  return {
    token,
    userInfo,
    roles,
    permissions,
    sessionValidated,
    isLoggedIn,
    isSuperAdmin,
    login,
    fetchUserInfo,
    logout,
    hasPermission
  };
});
