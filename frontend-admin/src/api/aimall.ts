import axios from 'axios';

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('aimall_admin_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (resp) => {
    const payload = resp.data;
    if (payload?.code === 0) return payload.data;
    throw new Error(payload?.message || '请求失败');
  },
  (error) => {
    throw new Error(error?.response?.data?.message || error?.message || '网络错误');
  }
);

export const aimallApi = {
  adminLogin: (data: { username: string; password: string }) => http.post('/admin/auth/login', data),
  getAdminProducts: (params: any) => http.get('/admin/products', { params }),
  createAdminProduct: (data: any) => http.post('/admin/products', data),
  updateAdminProduct: (id: number, data: any) => http.put(`/admin/products/${id}`, data),
  deleteAdminProduct: (id: number) => http.delete(`/admin/products/${id}`),
  uploadImage: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return http.post('/admin/upload/image', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  },

  getAdminCategoryTree: () => http.get('/admin/categories/tree'),
  createAdminCategory: (data: any) => http.post('/admin/categories', data),
  updateAdminCategory: (id: number, data: any) => http.put(`/admin/categories/${id}`, data),
  deleteAdminCategory: (id: number) => http.delete(`/admin/categories/${id}`),

  getAdminCustomers: (params: any) => http.get('/admin/customers', { params }),
  createAdminCustomer: (data: any) => http.post('/admin/customers', data),
  updateAdminCustomer: (id: number, data: any) => http.put(`/admin/customers/${id}`, data),
  deleteAdminCustomer: (id: number) => http.delete(`/admin/customers/${id}`),
  getAdminCustomerBehaviors: (id: number) => http.get(`/admin/customers/${id}/behaviors`),

  getAdminRecommendations: (params?: any) => http.get('/admin/recommendations', { params }),
  refreshAdminRecommendations: (data?: any) => http.post('/admin/recommendations/refresh', data || {}),
  getRecommendationSettings: () => http.get('/admin/recommendation-settings'),
  updateRecommendationSettings: (data: any) => http.put('/admin/recommendation-settings', data),
  getRecommendationAnalysis: () => http.get('/admin/recommendations/analysis'),
  runRecommendationExperiment: (data?: any) => http.post('/admin/recommendations/experiments', data || {}),
  getRecommendationExperiments: () => http.get('/admin/recommendations/experiments'),
  clearRecommendationExperiments: () => http.delete('/admin/recommendations/experiments'),
  getRecommendationExperimentDetail: (id: number) => http.get(`/admin/recommendations/experiments/${id}`),
  exportRecommendationExperiment: (id: number) => http.post(`/admin/recommendations/experiments/${id}/export`, {}),
  generateRecommendationBehaviorReplay: (data?: any) => http.post('/admin/recommendations/behavior-replay', data || {}),
  resetRecommendationBehaviors: (params?: any) => http.delete('/admin/recommendations/behavior-reset', { params }),
  getCustomerRecommendationCompare: (id: number, top_n = 5) => http.get(`/admin/customers/${id}/recommendation-compare`, { params: { top_n } }),
};
