import type { Router } from 'vue-router';
import NProgress from 'nprogress';

NProgress.configure({ showSpinner: false });

const whiteList = ['/login'];

export function setupRouterGuards(router: Router) {
  router.beforeEach((to, _from, next) => {
    NProgress.start();
    const token = localStorage.getItem('aimall_admin_token');

    if (whiteList.includes(to.path)) {
      if (token && to.path === '/login') {
        next('/mall/product-management/products');
      } else {
        next();
      }
      NProgress.done();
      return;
    }

    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } });
      NProgress.done();
      return;
    }

    next();
    NProgress.done();
  });

  router.afterEach(() => {
    NProgress.done();
  });
}
