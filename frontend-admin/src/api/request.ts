import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import { ElMessage } from 'element-plus';
import { useAuthStore } from '@/stores/auth.store';
import type { ApiResponse } from '@/types';

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    
    // 添加 Token
    if (authStore.token) {
      const rawToken = String(authStore.token).trim();
      const normalizedToken = rawToken.startsWith('Bearer ')
        ? rawToken
        : rawToken.startsWith('Bearer')
          ? `Bearer ${rawToken.slice('Bearer'.length).trim()}`
          : `Bearer ${rawToken}`;
      config.headers.Authorization = normalizedToken;
    }
    
    // 开发环境打印请求日志
    if (import.meta.env.DEV) {
      console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response;
    
    // 根据后端约定的响应码判断
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败');
      
      // Token 失效
      if (data.code === 1003 || data.code === 401) {
        const authStore = useAuthStore();
        authStore.logout();
      }
      
      return Promise.reject(new Error(data.message));
    }
    
    return data as any;
  },
  async (error) => {
    const { response } = error;
    
    if (response) {
      const { status, data } = response;
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录');
          useAuthStore().logout();
          break;
        case 403:
          ElMessage.error('无权限访问该资源');
          break;
        case 404:
          ElMessage.error('请求的资源不存在');
          break;
        case 500:
          ElMessage.error('服务器内部错误');
          break;
        default:
          ElMessage.error(data?.message || `HTTP ${status} 错误`);
      }
    } else {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络');
    }
    
    return Promise.reject(error);
  }
);

export default request;
