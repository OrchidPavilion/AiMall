import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import 'nprogress/nprogress.css';
import '@/styles/index.scss';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(ElementPlus);

// 全局错误处理
app.config.errorHandler = (error, instance, info) => {
  console.error('Vue global error:', error, info);
  // TODO: 上报错误监控系统
};

app.mount('#app');