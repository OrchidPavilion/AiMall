import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/aimall/Login.vue'),
    meta: { hidden: true, requiresGuest: true, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/aimall/LayoutShell.vue'),
    redirect: '/mall/product-management/products',
    children: [
      {
        path: 'mall',
        name: 'Mall',
        meta: { title: '商城' },
        children: [
          {
            path: 'product-management',
            name: 'MallProductManagement',
            meta: { title: '商品管理' },
            children: [
              {
                path: 'products',
                name: 'MallProducts',
                component: () => import('@/views/aimall/mall/ProductsPage.vue'),
                meta: { title: '商品列表' }
              },
              {
                path: 'categories',
                name: 'MallCategories',
                component: () => import('@/views/aimall/mall/CategoriesPage.vue'),
                meta: { title: '类别列表' }
              },
              {
                path: 'recommendation',
                name: 'MallRecommendation',
                component: () => import('@/views/aimall/mall/RecommendationPage.vue'),
                meta: { title: '智能推荐' }
              },
              {
                path: 'preview',
                name: 'MallPreview',
                component: () => import('@/views/aimall/mall/PreviewPage.vue'),
                meta: { title: '线上预览' }
              }
            ]
          }
        ]
      },
      {
        path: 'recommendation-system',
        name: 'RecommendationSystem',
        meta: { title: '推荐系统' },
        children: [
          {
            path: 'intelligent',
            name: 'RecommendationIntelligent',
            component: () => import('@/views/aimall/mall/RecommendationPage.vue'),
            meta: { title: '智能推荐' }
          },
          {
            path: 'analytics',
            name: 'RecommendationAnalytics',
            component: () => import('@/views/aimall/recommendation/RecommendationAnalyticsPage.vue'),
            meta: { title: '数据分析' }
          },
          {
            path: 'settings',
            name: 'RecommendationSettings',
            component: () => import('@/views/aimall/recommendation/RecommendationSettingsPage.vue'),
            meta: { title: '推荐设置' }
          }
        ]
      },
      {
        path: 'customer',
        name: 'Customer',
        meta: { title: '客户' },
        children: [
          {
            path: 'customer-management',
            name: 'CustomerManagement',
            meta: { title: '客户管理' },
            children: [
              {
                path: 'list',
                name: 'CustomerList',
                component: () => import('@/views/aimall/customer/CustomerListPage.vue'),
                meta: { title: '客户列表' }
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/mall/product-management/products'
  }
];

export default routes;
