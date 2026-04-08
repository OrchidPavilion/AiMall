import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/HomeView.vue') },
    { path: '/auth', component: () => import('../views/AuthView.vue') },
    { path: '/products', component: () => import('../views/ProductListView.vue') },
    { path: '/cart', component: () => import('../views/CartView.vue') },
    { path: '/product/:id', component: () => import('../views/ProductDetailView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  const titleMap: Record<string, string> = {
    '/': 'AiMall 商城',
    '/auth': 'AiMall 登录注册',
    '/products': 'AiMall 商品列表',
    '/cart': 'AiMall 购物车',
  }
  if (to.path.startsWith('/product/')) {
    document.title = 'AiMall 商品详情'
    return
  }
  document.title = titleMap[to.path] || 'AiMall 商城'
})

export default router
