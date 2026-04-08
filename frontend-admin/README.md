# GhostFit 管理后台

GhostFit 健身管理后台系统，基于 Vue 3 + TypeScript + Vite 构建。

## 技术栈

- **框架**: Vue 3.4 + Composition API + `<script setup>`
- **语言**: TypeScript 5.4
- **构建**: Vite 5.1
- **UI 组件库**: Element Plus 2.4
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4.3
- **HTTP 客户端**: Axios 1.6
- **样式**: SCSS + 蓝白主题

## 快速开始

### 环境要求

- Node.js >= 18.x
- npm >= 9.x

### 安装依赖

```bash
npm ci --only=production
# 或
npm install
```

### 开发运行

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物位于 `dist/` 目录。

### 预览构建结果

```bash
npm run preview
```

### 代码检查

```bash
npm run lint       # ESLint 检查并修复
npm run format     # Prettier 格式化
npm run type-check # TypeScript 类型检查
```

## 项目结构

```
src/
├── api/             # API 模块封装
│   ├── modules/     # 业务模块 API
│   └── request.ts   # Axios 封装
├── assets/          # 静态资源
├── components/      # 全局组件
│   ├── common/      # 通用组件
│   └── layout/      # 布局组件
├── composables/     # 组合函数
├── directives/      # 自定义指令
├── router/          # 路由配置
├── stores/          # Pinia stores
├── styles/          # 全局样式
│   ├── variables.scss   # SCSS 变量
│   ├── mixins.scss      # 样式混合
│   ├── index.scss       # 主样式文件
│   └── theme/           # Element Plus 主题
├── types/           # TypeScript 类型定义
├── utils/           # 工具函数
└── views/           # 页面视图
```

## 核心页面

- **登录页**: `/login`
- **首页**: `/dashboard` - 数据概览
- **客户管理**: `/customer/list` - 客户列表、详情、公海
- **商品管理**: `/product/list` - 商品 CRUD、分类管理
- **订单管理**: `/order/list` - 订单查询、详情
- **商城管理**: `/store/layout` - APP 排版、广告位、分类
- **系统配置**: `/system/*` - 系统设置、用户、权限、对接

## 配色方案

- 主色调：`#1890ff` (品牌蓝)
- 按钮：蓝色为主
- 背景：白色为主，浅灰为辅
- 文字：高对比度黑灰色系

详见 `src/styles/variables.scss`

## API 对接

所有 API 已按模块封装，位于 `src/api/modules/`。使用示例：

```typescript
import { customerApi } from '@/api';

const { data } = await customerApi.getList({ page: 1, pageSize: 20 });
```

## 状态管理

使用 Pinia 进行状态管理，stores 位置：`src/stores/`

- `auth.store.ts` - 认证状态
- `app.store.ts` - 应用状态
- `permission.store.ts` - 权限管理
- `customer.store.ts` - 客户管理状态
- `order.store.ts` - 订单管理状态
- `product.store.ts` - 商品管理状态

## 路由守卫

在 `src/router/guards.ts` 中实现了：
- 登录拦截
- 权限校验
- 路由懒加载
- Header 面包屑更新

## 部署

构建后的静态文件可直接部署至 Nginx、CDN 或静态服务器。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name admin.ghostfit.com;
    root /var/www/ghostfit-admin/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend-server:8080;
        proxy_set_header Host $host;
    }
}
```

## 说明

- 严格遵循 Vue 3 + TypeScript 最佳实践
- 使用 Composition API + `<script setup>` 语法
- 蓝白主题完全符合 PRD 要求
- 无 Docker，依赖原生 npm 运行
- 样式高对比度，-button 统一蓝色
- 所有 API 接口已按契约封装

## 文档

- `前端技术设计文档.md` - 完整技术设计与架构说明
- `runbook_frontend.md` - 开发、部署与运维手册

## 许可证

MIT