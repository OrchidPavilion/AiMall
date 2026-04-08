# GhostFit 管理后台 - 前端部署与运维手册

## 1. 环境要求

### 1.1 基础环境
| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18.x LTS 或 20.x LTS | 推荐使用 nvm 管理版本 |
| npm | 9.x 或 10.x | npm 随 Node.js 安装 |
| Git | 2.40+ | 版本控制 |

### 1.2 系统要求
- **操作系统**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+ / CentOS 8+)
- **内存**: 至少 4GB RAM (推荐 8GB+)
- **磁盘**: 至少 2GB 可用空间
- **网络**: 可访问 npm 仓库和后端 API

### 1.3 开发工具 (推荐)
- **IDE**: Visual Studio Code 1.80+
- **VSCode 插件**:
  - Volar (Vue 3) - 必装
  - TypeScript Vue Plugin
  - Prettier
  - ESLint
  - SCSS IntelliSense

---

## 2. 快速开始

### 2.1 克隆仓库 (如已有)
```bash
cd /Users/novation/Desktop/GhostFit/Dev-Frontend
```

### 2.2 检查 Node.js 版本
```bash
node -v  # 应显示 v18.x 或 v20.x
npm -v   # 应显示 9.x 或更高
```

如版本不符合，使用 nvm 切换：
```bash
nvm install 20
nvm use 20
```

### 2.3 安装依赖
```bash
# 国内推荐使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 安装项目依赖
npm ci

# 或使用 npm install
npm install
```
⚠️ **注意**: 使用 `npm ci` 可确保依赖版本与 `package-lock.json` 完全一致。

### 2.4 配置环境变量
创建 `.env.local` 文件（已包含在`.gitignore`中）：

```env
# API 地址
VITE_API_BASE_URL=http://localhost:8080

# 环境标识
VITE_APP_ENV=development

# 是否启用 Mock 数据 (仅开发环境)
VITE_USE_MOCK=false
```

---

## 3. 开发运行

### 3.1 启动开发服务器
```bash
npm run dev
```

**预期输出**:
```
  VITE v5.1.6  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### 3.2 访问应用
- 在浏览器打开: `http://localhost:3000`
- 首次访问会重定向到登录页 `/login`
- 登录账号密码请联系后端获取测试数据

### 3.3 开发服务器特性
- **热更新 (HMR)**: 修改代码自动刷新页面
- **代理配置**: `/api` 请求自动代理到后端
- **错误提示**: 编译错误在浏览器和终端都会显示
- **Source Map**: 支持调试

### 3.4 常用开发命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 (先运行类型检查) |
| `npm run preview` | 预览构建结果 (本地静态服务器) |
| `npm run lint` | 运行 ESLint 检查并自动修复 |
| `npm run format` | 运行 Prettier 格式化代码 |
| `npm run type-check` | 仅运行 TypeScript 类型检查 |

---

## 4. 项目结构与文件说明

### 4.1 目录树 (关键文件)

```
ghostfit-admin/
├── src/
│   ├── api/              # API 请求封装
│   ├── assets/           # 静态资源 (图片、字体)
│   ├── components/       # 全局可复用组件
│   ├── composables/      # Composition API 组合函数
│   ├── directives/       # 自定义指令
│   ├── locales/          # 国际化 (可选)
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   ├── styles/           # 全局样式 (SCSS)
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面视图
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── public/               # 静态文件 (直接复制到 dist)
├── index.html            # HTML 模板
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
├── .env.example          # 环境变量示例
├── .env.local            # 本地环境变量 (不提交)
├── package.json          # 依赖管理
├── package-lock.json     # 依赖版本锁定
└── dist/                 # 构建输出目录 (自动生成)
```

### 4.2 关键文件说明

| 文件 | 用途 | 是否可编辑 |
|------|------|-----------|
| `vite.config.ts` | Vite 构建配置 | ✅ 是 |
| `tsconfig.json` | TypeScript 配置 | ✅ 是 |
| `.env.local` | 本地环境变量 | ✅ 是 (不提交) |
| `src/styles/variables.scss` | SCSS 主题变量 | ✅ 是 |
| `src/router/routes.ts` | 路由定义 | ✅ 是 |
| `src/api/modules/` | API 模块 | ✅ 是 |
| `src/views/` | 页面组件 | ✅ 是 |
| `src/stores/` | 状态管理 | ✅ 是 |
| `public/` | 静态资源 (如 favicon) | ✅ 是 |
| `index.html` | HTML 模板 | ✅ 是 |

---

## 5. 构建打包

### 5.1 生产构建
```bash
npm run build
```

**构建过程**:
1. 运行 TypeScript 类型检查 (`vue-tsc --noEmit`)
2. 执行 Vite 构建 (`vite build`)
3. 输出到 `dist/` 目录

### 5.2 构建产物结构
```
dist/
├── index.html           # HTML 入口
├── assets/
│   ├── index-xxxx.css   # CSS 文件 (带 hash)
│   ├── index-xxxx.js    # JS 文件 (带 hash)
│   └── ...
└── favicon.ico          # 图标 (如有)
```

### 5.3 构建配置说明

**vite.config.ts 关键配置**:
```typescript
build: {
  outDir: 'dist',
  sourcemap: true,        // 生产 source map (便于调试)
  minify: 'terser',       // 代码压缩
  terserOptions: {
    compress: {
      drop_console: true  // 移除 console 语句
    }
  },
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['vue', 'vue-router', 'pinia'],
        element: ['element-plus', '@element-plus/icons-vue']
      }
    }
  }
}
```

### 5.4 构建常见问题

**Q: 构建失败，提示"类型错误"**
```bash
# 运行类型检查查看详细信息
npm run type-check

# 或直接运行 vue-tsc
npx vue-tsc --noEmit
```

**Q: 构建后样式丢失**
- 确认 `main.ts` 中引入了全局样式: `import '@/styles/index.scss'`
- 检查 `vite.config.ts` 中的 `css.preprocessorOptions` 配置

**Q: 构建文件过大**
- 配置 `manualChunks` 进行代码分割
- 使用 `element-plus/dist/index.full.js` 而非完整版
- 按需引入 Element Plus 组件

---

## 6. 部署指南

### 6.1 部署架构

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
┌──────▼─────────────────────────┐
│         Nginx (80/443)         │
│  + Static File Serving         │
│  + API Proxy (/api → backend)  │
└──────┬─────────────────────────┘
       │
┌──────▼─────────────────────────┐
│        dist/ static files      │
│  index.html + assets/          │
└────────────────────────────────┘

Backend API: http://backend-server:8080
```

### 6.2 Nginx 配置示例

```nginx
# /etc/nginx/sites-available/ghostfit-admin
server {
    listen 80;
    server_name admin.ghostfit.com;
    
    # 根目录指向 dist/
    root /var/www/ghostfit-admin/dist;
    index index.html;
    
    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API 代理到后端
    location /api {
        proxy_pass http://localhost:8080;  # 修改为实际后端地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # SPA 路由 fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

### 6.3 HTTPS 配置 (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d admin.ghostfit.com

# 自动续期测试
sudo certbot renew --dry-run
```

Nginx 会自动更新为监听 443 并配置 SSL。

### 6.4 部署步骤

1. **准备服务器**:
   ```bash
   ssh user@server
   sudo apt update && sudo apt install nginx nodejs npm -y
   ```

2. **上传构建文件** (本地执行):
   ```bash
   npm run build
   scp -r dist/* user@server:/var/www/ghostfit-admin/
   ```

3. **配置 Nginx** (服务器):
   ```bash
   sudo cp ghostfit-admin.nginx.conf /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/ghostfit-admin /etc/nginx/sites-enabled/
   sudo nginx -t  # 测试配置
   sudo systemctl reload nginx
   ```

4. **验证部署**:
   - 访问 `http://admin.ghostfit.com`
   - 检查开发者工具 Network 面板，静态文件应返回 200
   - API 请求应正确代理到后端

---

## 7. 环境配置

### 7.1 多环境配置

项目支持以下环境：
- `development`: 开发环境 (默认)
- `staging`: 预发布环境
- `production`: 生产环境

### 7.2 环境变量文件

```
.env                # 所有环境都会加载 (不要敏感信息)
.env.local          # 本地覆盖 (已 .gitignore)
.env.development    # 开发环境
.env.staging        # 预发布环境
.env.production     # 生产环境
```

**示例 `.env.development`**:
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_ENV=development
VITE_USE_MOCK=true
```

**示例 `.env.production`**:
```env
VITE_API_BASE_URL=https://api.ghostfit.com
VITE_APP_ENV=production
VITE_USE_MOCK=false
```

### 7.3 环境变量使用

```typescript
// 在代码中访问
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const isDev = import.meta.env.DEV; // boolean
const isProd = import.meta.env.PROD; // boolean
```

---

## 8. 常用操作指南

### 8.1 添加新页面

1. **创建页面文件**: `src/views/Customer/NewPage.vue`
2. **配置路由**: 在 `src/router/routes.ts` 添加路由记录
3. **添加到菜单**: 更新路由元信息 `meta` 中的 `title`、`icon`、`permission`
4. **导航访问**: 左侧菜单会自动读取路由配置生成

### 8.2 添加新 API 接口

1. **定义类型**: 在 `src/types/` 添加对应 TypeScript 接口
2. **实现 API**: 在 `src/api/modules/` 创建或更新对应的 API 文件
3. **调用**: 在页面组件中 `import { moduleApi } from '@/api/modules/module'`

示例:
```typescript
// src/api/modules/customer.ts
export const customerApi = {
  getList(params: CustomerQueryParams) {
    return request.get<PageResponse<Customer>>('/customers', { params });
  },
  getDetail(id: number) {
    return request.get<Customer>(`/customers/${id}`);
  }
};
```

### 8.3 添加新状态 (Pinia Store)

1. **创建 Store**: `src/stores/custom.store.ts`
2. **导出**: 在 `src/stores/index.ts` 中统一导出
3. **使用**: `const customStore = useCustomStore()`

示例:
```typescript
export const useCustomStore = defineStore('custom', {
  state: () => ({ value: '' }),
  getters: {},
  actions: {
    setValue(val: string) {
      this.value = val;
    }
  }
});
```

### 8.4 按需引入 Element Plus

默认已配置按需引入。如需要手动引入组件:

```typescript
import { ElButton, ElTable } from 'element-plus';
// 或使用自动导入 (推荐)
// 在组件中直接使用 <el-button> 标签即可
```

Vite 配置已包含插件 `unplugin-vue-components` 和 `unplugin-auto-import`。

---

## 9. 代码规范与 Commit

### 9.1 代码规范

- **命名**: 
  - 组件文件: `PascalCase` (e.g., `CustomerList.vue`)
  - 函数/变量: `camelCase`
  - 常量: `UPPER_SNAKE_CASE`
  - 类型/接口: `PascalCase` + 以 `Type` 或 `Info` 结尾

- **组件结构顺序**:
  1. `<script setup>` imports
  2. Props/Emits 定义
  3. 响应式数据 `ref/reactive`
  4. 计算属性 `computed`
  5. 生命周期钩子
  6. 方法定义
  7. 样式 (`.scss` 或 `<style>`)

- **API 设计**: 使用 `Noun` + `Verb` 结构，如 `customerApi.getList()`、`orderApi.ship()`

### 9.2 提交规范 (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: bug 修复
- `docs`: 文档变更
- `style`: 代码格式调整 (不影响功能)
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具变更

**示例**:
```
feat(customer): 添加客户分配功能

- 实现客户分配API调用
- 新增分配弹窗组件
- 更新权限校验逻辑

Closes #123
```

### 9.3 Git Hooks

Husky 已配置，在 `git commit` 时会自动运行:
1. `lint-staged`: ESLint 检查 + 自动修复
2. `prettier`: 代码格式化

如有问题，会阻止提交并显示错误信息。

---

## 10. 故障排查

### 10.1 开发环境问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| `npm ci` 失败，网络超时 | npm 镜像慢 | 更换为淘宝镜像: `npm config set registry https://registry.npmmirror.com` |
| 开发服务器无法启动，端口被占用 | 3000 端口已被使用 | 修改 `vite.config.ts` 中 `server.port` 或使用 `PORT=3001 npm run dev` |
| 热更新失效 | 缓存问题 | 清除 `node_modules/.vite` 或重启开发服务器 |
| 样式未生效 | SCSS 变量未生效 | 检查 `vite.config.ts` 中的 `css.preprocessorOptions` 配置 |
| 组件无法识别 | 需要引入 Element Plus | 检查 `main.ts` 中是否 `app.use(ElementPlus)` |

### 10.2 构建问题

| 问题 | 解决方案 |
|------|----------|
| `npm run build` 失败，类型错误 | 运行 `npm run type-check` 查看错误详情 |
| 构建后页面空白 | 检查 `index.html` 中 `div#app` 存在，且 `main.ts` 正确挂载 |
| 字体/图片资源 404 | 使用相对路径 `/src/assets/...` 而非绝对路径 |
| 路由刷新 404 | Nginx 配置了 `try_files $uri $uri/ /index.html` |

### 10.3 运行时问题

| 问题 | 解决方案 |
|------|----------|
| API 请求 401 未授权 | 检查 Token 是否存在于 localStorage，或重新登录 |
| 跨域错误 | 后端未配置 CORS 或开发代理未生效 |
| 表单验证不触发 | 确认 `<el-form>` 有 `ref` 并在 JS 中调用 `validate()` |
| 权限按钮不显示 | 确认用户有对应权限码，且 `permission` 指令正确绑定 |

---

## 11. 性能调优

### 11.1 开发环境
- 使用 `import { User } from '@element-plus/icons-vue'` 按需引入图标
- 避免在 `created` 中执行大量计算
- 表格数据量大时使用虚拟滚动 (Element Plus 的 `virtual-scroll`)

### 11.2 生产环境
- 使用 CDN 托管 Element Plus 和图标资源
- 图片懒加载: `<el-image loading="lazy">`
- 路由懒加载已默认配置
- 开启 Gzip/Brotli 压缩 (Nginx: `gzip on;`)

---

## 12. 监控与日志

### 12.1 错误监控

建议接入 Sentry 或阿里云日志服务:

```typescript
// src/utils/error.ts
import * as Sentry from '@sentry/vue';

export const initSentry = () => {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_APP_ENV,
    release: `ghostfit-admin@${import.meta.env.VITE_APP_VERSION}`
  });
};
```

### 12.2 性能监控

使用 Web Vitals:

```typescript
import { getCLS, getFID, getLCP } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getLCP(console.log);
```

---

## 13. 更新依赖

```bash
# 检查过时依赖
npm outdated

# 更新所有依赖 (谨慎使用)
npm update

# 更新特定依赖
npm install element-plus@latest

# 更新后重新安装
rm -rf node_modules
npm ci
```

---

## 14. 联系与支持

- **技术文档**: [产品设计文档](../Product-Design/)
- **API 文档**: [接口契约](../Product-Design/接口契约.md)
- **后端 API 地址**: 请联系后端团队获取
- **问题反馈**: 在项目仓库提交 Issue

---

**文档版本**: v1.0  
**维护团队**: GhostFit 前端组  
**最后更新**: 2025-02-20