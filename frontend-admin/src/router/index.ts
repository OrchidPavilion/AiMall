import { createRouter, createWebHistory } from 'vue-router';
import routes from './routes';
import { setupRouterGuards } from './guards';

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

setupRouterGuards(router);

router.afterEach((to) => {
  const pageTitle = typeof to.meta?.title === 'string' ? to.meta.title : '';
  document.title = pageTitle ? `AiMall 管理后台 - ${pageTitle}` : 'AiMall 管理后台';
});

export default router;
