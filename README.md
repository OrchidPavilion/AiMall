# AiMall

AiMall 是一个包含管理后台、商城前台和 Django 后端的电商推荐实验项目，支持真实业务链路下的个性化推荐与论文实验数据采集。

当前已经实现并接入系统的核心能力：
- 基于用户的协同过滤推荐 `USER_CF`
- 基于物品的协同过滤推荐 `ITEM_CF`
- 基于交替最小二乘的矩阵分解推荐 `ALS`
- 后台切换线上推荐算法、`TopN`、行为权重
- 商城真实访问行为采集与推荐实验记录
- 一键清空旧行为并重建论文实验样本

## 项目结构

```text
AiMall/
├── backend/          Django + DRF 后端
├── frontend-admin/   Vue 3 + TypeScript 管理端
├── frontend-mall/    Vue 3 + TypeScript 商城端
├── .aimall_ctl.sh    启停脚本
├── start-backend.sh
├── start-admin.sh
└── start-mall.sh
```

## 技术栈

- 后端：Django、Django REST framework、SQLite（默认）
- 管理端：Vue 3、TypeScript、Vite、Element Plus、Pinia
- 商城端：Vue 3、TypeScript、Vite
- 推荐算法：UserCF、ItemCF、ALS

## 环境要求

- Python `3.12`
- Node.js `>= 18`
- npm

## 端口说明

- 后端：`18080`
- 管理端：`3100`
- 商城端：`3101`

## 快速启动

### 方式一：用根目录脚本

后端：

```bash
./start-backend.sh
```

前端：

```bash
./start-admin.sh
./start-mall.sh
```

或者使用统一控制脚本：

```bash
./.aimall_ctl.sh backend_start
./.aimall_ctl.sh frontend_start
```

停止服务：

```bash
./.aimall_ctl.sh backend_stop
./.aimall_ctl.sh frontend_stop
```

### 方式二：手动启动

后端：

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:18080 --noreload
```

管理端：

```bash
cd frontend-admin
npm install
npm run build
npm run preview -- --host 127.0.0.1 --port 3100
```

商城端：

```bash
cd frontend-mall
npm install
npm run build
npm run preview -- --host 127.0.0.1 --port 3101
```

## 默认访问地址

- 管理端：[http://127.0.0.1:3100](http://127.0.0.1:3100)
- 商城端：[http://127.0.0.1:3101](http://127.0.0.1:3101)
- 后端健康检查：[http://127.0.0.1:18080/api/v1/health](http://127.0.0.1:18080/api/v1/health)

管理端默认账号：

- 用户名：`admin`
- 密码：`123456`

## 推荐系统说明

### 后台可配置项

管理端“推荐设置”页支持配置：

- 线上推荐算法
- `TopN`
- 邻居数 `K`
- ALS 因子数、迭代次数、Alpha、正则化
- 行为权重：浏览、加购、购买、搜索

这些配置会真实影响商城推荐接口，不是展示用假开关。

### 真实行为采集

以下行为已经接入推荐建模链路：

- 搜索
- 点击分类
- 浏览商品详情
- 加入购物车
- 购买商品

商城用户自然访问后，系统会记录行为并参与推荐计算。

## 论文实验

项目内置论文实验样本生成与三算法对比命令：

```bash
backend/.venv/bin/python backend/manage.py recommendation_thesis_lab \
  --customers 36 \
  --actions 40 \
  --seed 20260408 \
  --clear-all-behaviors
```

这条命令会依次完成：

1. 清空旧行为轨迹、购物车和推荐实验数据
2. 重新生成论文实验样本用户与访问行为
3. 验证后台“线上推荐算法”切换是否真实生效
4. 执行 `USER_CF / ITEM_CF / ALS` 三算法实验
5. 保存实验记录，供管理端“数据分析”页查看

如果只想跑实验，不重新生成数据：

```bash
backend/.venv/bin/python backend/manage.py recommendation_thesis_lab --skip-seed
```

## 测试与构建

后端测试：

```bash
backend/.venv/bin/python backend/manage.py test apps.recommendations
```

管理端构建：

```bash
cd frontend-admin
npm run build
```

商城端构建：

```bash
cd frontend-mall
npm run build
```

## 运行日志

- 日志目录：`./logs`
- PID 目录：`./.run`

## 说明

- 默认数据库是 SQLite，配置见 `backend/.env.example`
- 根目录 `.gitignore` 已排除虚拟环境、数据库、构建产物和本地工作区状态文件
- 如果用于论文提交，建议固定随机种子并保留每次实验的参数、指标截图与实验记录编号
