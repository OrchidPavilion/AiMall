# AiMall（开发骨架）

当前已创建：
- `backend`（Django + DRF）
- `frontend-admin`（基于 GhostFit Dev-Frontend 复制并改造）
- `frontend-mall`（Vue3 + TS）

## 端口规划（避免与 GhostFit 冲突）
- AiMall 后端：`18080`
- AiMall 管理端：`3100`
- AiMall 商城端：`3101`

已知 GhostFit 使用：
- GhostFit 后端：`8080`
- GhostFit 管理端：`3000`

## 启动方式
### 一键脚本（根目录）
- `后端-启动.command`
- `后端-重启.command`
- `后端-停止.command`
- `前端-启动.command`（同时启动管理端 `3100` + 商城端 `3101`）
- `前端-重启.command`
- `前端-停止.command`

说明：
- 前端脚本当前使用 `vite preview` 启动 `dist` 产物（已为你构建完成，可直接用）
- 日志输出目录：`/Users/novation/Desktop/AiMall/logs`
- PID 文件目录：`/Users/novation/Desktop/AiMall/.run`

### 1. 后端（Django）
```bash
cd backend
./run_dev.sh
```

健康检查：`http://127.0.0.1:18080/api/v1/health`

### 2. 管理端（复用 GhostFit 资源）
```bash
cd frontend-admin
npm install
npm run dev
```
访问：`http://localhost:3100`
开发登录账号：`admin / 123456`

### 3. 商城端
```bash
cd frontend-mall
npm install
npm run dev
```
访问：`http://localhost:3101`

## 当前实现状态（骨架）
- 管理端：登录页、3级菜单结构、商品列表/分类列表/智能推荐/线上预览/客户列表页面骨架
- 商城端：首页（搜索/分类悬浮/推荐换一换/商品列表）、商品列表页、购物车页、商品详情页结构
- 后端：Django 工程、DRF、分页响应包装、健康检查接口、业务 apps 目录
