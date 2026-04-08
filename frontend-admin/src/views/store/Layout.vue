<template>
  <div class="store-layout">
    <el-alert title="功能说明" type="info" :closable="false" show-icon class="mb-16">
      配置 APP 首页的模块展示顺序和内容。支持拖拽排序，配置完成后需保存并发布。
    </el-alert>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>首页模块配置</span>
          <div>
            <el-button type="primary" size="small" @click="handleSave">保存配置</el-button>
            <el-button type="success" size="small" @click="handlePublish" v-if="!published">发布</el-button>
          </div>
        </div>
      </template>
      
      <div class="module-list">
        <div
          v-for="(module, index) in modules"
          :key="module.id"
          class="module-item"
          draggable
          @dragstart="handleDragStart($event, index)"
          @dragover.prevent
          @drop="handleDrop($event, index)"
        >
          <div class="module-drag-handle">⋮⋮</div>
          <div class="module-info">
            <div class="module-name">{{ getModuleTypeName(module.type) }}</div>
            <div class="module-desc">{{ module.config.title || '默认标题' }}</div>
          </div>
          <div class="module-actions">
            <el-switch
              v-model="module.enabled"
              @change="handleToggleModule(module)"
            />
            <el-button link type="primary" @click="handleEdit(module)">配置</el-button>
          </div>
        </div>
      </div>
      
      <div v-if="modules.length === 0" class="empty-state">
        <div class="empty-icon">📱</div>
        <div class="empty-text">暂无模块配置</div>
        <el-button type="primary" class="mt-16" @click="handleAdd">添加模块</el-button>
      </div>
    </el-card>

    <el-card class="mt-16">
      <template #header>
        <div class="card-header">
          <span>APP验收预览（使用当前后台账号）</span>
          <div class="preview-actions">
            <el-switch v-model="hideTabBar" active-text="隐藏底部菜单" />
            <el-button size="small" @click="refreshPreviewContext">刷新上下文</el-button>
            <el-button type="primary" size="small" @click="previewDialogVisible = true">9:16预览</el-button>
          </div>
        </div>
      </template>
      <div class="preview-meta" v-if="previewContext">
        <el-tag type="info">后台账号：{{ previewContext.adminRealName || previewContext.adminUsername || '-' }}</el-tag>
        <el-tag :type="previewContext.linkedToCustomer ? 'success' : 'warning'">
          {{ previewContext.linkedToCustomer ? `客户映射：${previewContext.customerName || previewContext.customerPhone}` : '未映射客户（行为轨迹不会关联到客户详情）' }}
        </el-tag>
      </div>
      <div class="preview-layout">
        <div class="preview-canvas">
          <iframe v-if="previewSrc" :src="previewSrc" class="preview-iframe" />
          <el-empty v-else description="暂无预览地址，请先配置 H5 预览服务" />
        </div>
        <div class="preview-trail">
          <div class="preview-trail-head">
            <span>商城APP行为轨迹</span>
            <el-button size="small" @click="fetchBehaviors">刷新</el-button>
          </div>
          <BehaviorTimeline :items="previewBehaviors" />
        </div>
      </div>
    </el-card>

    <el-dialog v-model="previewDialogVisible" title="APP 预览（9:16）" width="70%" top="5vh">
      <div class="phone-preview-shell">
        <div class="phone-preview-frame">
          <iframe v-if="previewSrc" :src="previewSrc" class="phone-preview-iframe" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { storeApi } from '@/api';
import BehaviorTimeline from '@/components/common/BehaviorTimeline.vue';
import type { StoreModule } from '@/types';

const modules = ref<StoreModule[]>([]);
const published = ref(false);
const hideTabBar = ref(false);
const previewDialogVisible = ref(false);
const previewContext = ref<any>(null);
const previewBehaviors = ref<any[]>([]);

const previewSrc = computed(() => {
  const base = previewContext.value?.h5PreviewUrl;
  if (!base) return '';
  try {
    const url = new URL(base);
    const adminToken = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
    url.searchParams.set('gfPreview', '1');
    if (previewContext.value?.customerId) url.searchParams.set('customerId', String(previewContext.value.customerId));
    if (previewContext.value?.customerPhone) url.searchParams.set('customerPhone', String(previewContext.value.customerPhone));
    if (adminToken) url.searchParams.set('adminToken', adminToken);
    if (hideTabBar.value) url.searchParams.set('hideTabBar', '1');
    // H5 preview should land on the app home tab directly to avoid login route bootstrap mismatch.
    url.hash = '#/pages/home/index';
    return url.toString();
  } catch {
    return '';
  }
});

const fetchData = async () => {
  try {
    const { data } = await storeApi.getLayout();
    modules.value = data.modules;
    published.value = !!data.publishedAt;
  } catch (error) {
    console.error('Failed to fetch layout:', error);
  }
};

const handleDragStart = (event: DragEvent, index: number) => {
  event.dataTransfer?.setData('text/plain', String(index));
};

const handleDrop = (event: DragEvent, targetIndex: number) => {
  const sourceIndex = Number(event.dataTransfer?.getData('text/plain'));
  if (sourceIndex === targetIndex) return;
  
  const item = modules.value.splice(sourceIndex, 1)[0];
  modules.value.splice(targetIndex, 0, item);
};

const handleToggleModule = (module: StoreModule) => {
  console.log('Toggle module:', module.id, module.enabled);
};

const handleEdit = (module: StoreModule) => {
  ElMessage.info(`编辑模块 ${module.id}`);
};

const handleAdd = () => {
  ElMessage.info('添加模块功能待实现');
};

const handleSave = async () => {
  try {
    await storeApi.updateLayout({ modules: modules.value, publish: false });
    ElMessage.success('保存成功');
  } catch (error) {
    console.error('Save failed:', error);
  }
};

const handlePublish = async () => {
  try {
    await storeApi.updateLayout({ modules: modules.value, publish: true });
    ElMessage.success('发布成功');
    published.value = true;
  } catch (error) {
    console.error('Publish failed:', error);
  }
};

const getModuleTypeName = (type: string) => {
  const map: Record<string, string> = {
    BANNER: '轮播Banner',
    PRODUCT_RECOMMEND: '商品推荐',
    CATEGORY_ENTRANCE: '分类入口',
    ADVERTISEMENT: '广告位',
    NOTICE: '公告栏'
  };
  return map[type] || type;
};

onMounted(() => {
  fetchData();
  refreshPreviewContext();
});

watch(hideTabBar, () => {
  // trigger iframe reload through computed src
});

async function refreshPreviewContext() {
  try {
    const { data } = await storeApi.getAppPreviewContext();
    previewContext.value = data;
    await fetchBehaviors();
  } catch (error) {
    console.error('Failed to load app preview context', error);
    ElMessage.error('加载APP预览上下文失败');
  }
}

async function fetchBehaviors() {
  if (!previewContext.value?.customerId) {
    previewBehaviors.value = [];
    return;
  }
  try {
    const { data } = await storeApi.getAppPreviewBehaviors(previewContext.value.customerId);
    previewBehaviors.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Failed to fetch preview behaviors', error);
    previewBehaviors.value = [];
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.mb-16 {
  margin-bottom: $spacing-md;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.module-list {
  .module-item {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    padding: $spacing-md;
    margin-bottom: $spacing-sm;
    background: $bg-page;
    border: 1px solid $border-color-lighter;
    border-radius: $border-radius-base;
    cursor: move;
    transition: all 0.2s;
    
    &:hover {
      background: $bg-hover;
      border-color: $primary-color;
    }
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .module-drag-handle {
      color: $text-disabled;
      cursor: grab;
      font-size: 18px;
      padding: 0 $spacing-sm;
    }
    
    .module-info {
      flex: 1;
      
      .module-name {
        font-weight: 600;
        color: $text-primary;
        margin-bottom: 4px;
      }
      
      .module-desc {
        font-size: $font-size-sm;
        color: $text-secondary;
      }
    }
    
    .module-actions {
      display: flex;
      align-items: center;
      gap: $spacing-md;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 48px;
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: $spacing-md;
    opacity: 0.3;
  }
  
  .empty-text {
    color: $text-secondary;
  }
}

.mt-16 {
  margin-top: $spacing-md;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.preview-meta {
  margin-bottom: $spacing-md;
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.preview-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr);
  gap: $spacing-md;
}

.preview-canvas {
  min-height: 640px;
  border: 1px solid $border-color-lighter;
  border-radius: $border-radius-base;
  overflow: hidden;
  background: #fff;
}

.preview-iframe {
  width: 100%;
  height: 640px;
  border: none;
}

.preview-trail {
  border: 1px solid $border-color-lighter;
  border-radius: $border-radius-base;
  padding: $spacing-md;
  background: $bg-page;
  max-height: 640px;
  overflow: auto;
}

.preview-trail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  font-weight: 600;
}

.phone-preview-shell {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.phone-preview-frame {
  width: min(420px, 90%);
  aspect-ratio: 9 / 16;
  border-radius: 24px;
  overflow: hidden;
  border: 8px solid #111827;
  background: #111827;
  box-shadow: 0 10px 30px rgba(0,0,0,.16);
}

.phone-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

@media (max-width: 1200px) {
  .preview-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .card-header {
    align-items: flex-start;
    gap: $spacing-sm;
    flex-direction: column;
  }

  .preview-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .preview-canvas,
  .preview-iframe,
  .preview-trail {
    min-height: 420px;
    max-height: 420px;
    height: 420px;
  }

  .phone-preview-frame {
    width: 94%;
    border-width: 6px;
    border-radius: 18px;
  }
}
</style>
