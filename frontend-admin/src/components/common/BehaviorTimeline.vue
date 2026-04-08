<template>
  <div class="behavior-timeline">
    <div v-if="items.length === 0" class="empty">暂无行为记录</div>
    <div v-for="(item, index) in items" :key="item.id ?? index" class="behavior-row">
      <div class="dot"></div>
      <div class="line" v-if="index !== items.length - 1"></div>
      <div class="content">
        <div class="main">
          <template v-if="isAiMallBehavior(item)">
            <span class="time">[{{ formatDate(item.createdAt) || '-' }}]</span>
            <span class="sep"> </span>
            <template v-if="item.behavior_type === 'VIEW_PRODUCT' || item.behavior_type === 'ADD_TO_CART'">
              <span v-if="item.behavior_type === 'VIEW_PRODUCT'" class="desc">点击了商品详情 </span>
              <span v-else class="desc">将 </span>
              <button class="link-text" type="button" @click="openMallProduct(item.relatedProductId)">{{ item.target_name || item.productName || `商品#${item.relatedProductId}` }}</button>
              <span v-if="item.behavior_type === 'ADD_TO_CART'" class="desc"> 加入购物车</span>
            </template>
            <span v-else class="desc">{{ item.description || '-' }}</span>
          </template>
          <template v-else>
            <span class="time">[{{ formatDate(item.createdAt) || '-' }}]</span>
            <span class="sep">--</span>
            <span class="actor">{{ item.executorName || item.customerName || '系统' }}</span>
            <span class="sep">--</span>
            <span class="verb">{{ humanizeVerb(item.type) }}</span>
            <span class="sep">--</span>
            <span class="desc">{{ item.description || '-' }}</span>
          </template>
        </div>
        <div class="meta" v-if="showMeta(item)">
          <el-tag size="small" type="info">{{ item.behaviorTypeLabel || typeLabel(item.type) }}</el-tag>
          <el-tag v-if="item.relatedOrderId" size="small">订单#{{ item.relatedOrderId }}</el-tag>
          <el-tag v-if="item.relatedProductId && (item.behavior_type === 'VIEW_PRODUCT' || item.behavior_type === 'ADD_TO_CART')" size="small" type="success">
            <button class="tag-link-btn" type="button" @click="openMallProduct(item.relatedProductId)">{{ item.target_name || item.productName || `商品#${item.relatedProductId}` }}</button>
          </el-tag>
          <el-tag v-else-if="item.relatedProductId" size="small">商品ID#{{ item.relatedProductId }}</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '@/utils/format';

interface BehaviorItem {
  id?: string | number;
  type?: string;
  behavior_type?: string;
  behaviorTypeLabel?: string;
  description?: string;
  createdAt?: string;
  executorName?: string;
  customerName?: string;
  target_name?: string;
  productName?: string;
  relatedOrderId?: number;
  relatedProductId?: number;
}

defineProps<{ items: BehaviorItem[] }>();

function humanizeVerb(type?: string) {
  const map: Record<string, string> = {
    VIEW: '访问了',
    VIEW_PAGE: '访问了',
    VIEW_PRODUCT: '访问了',
    PLACE_ORDER: '下单了',
    ORDER: '下单了',
    AUTHORIZE: '授权了',
    CANCEL: '取消了',
    PUBLISH: '发布了',
    APP_ACTION: '执行了',
    FOLLOW_UP: '跟进了'
  };
  return map[type || ''] || '执行了';
}

function typeLabel(type?: string) {
  const map: Record<string, string> = {
    SEARCH: '搜索',
    CLICK_CATEGORY: '点击分类',
    VIEW_PRODUCT: '浏览商品详情',
    ADD_TO_CART: '加入购物车',
    PURCHASE: '购买',
  };
  return map[type || ''] || type || '操作';
}

function isAiMallBehavior(item: BehaviorItem) {
  return !!(item.behavior_type || item.behaviorTypeLabel);
}

function showMeta(item: BehaviorItem) {
  return !!(item.behavior_type || item.type || item.relatedOrderId || item.relatedProductId);
}

function openMallProduct(productId?: number) {
  if (!productId) return;
  const { protocol, hostname, port } = window.location;
  const mallPort = port === '3100' ? '3101' : port;
  const base = `${protocol}//${hostname}${mallPort ? `:${mallPort}` : ''}`;
  window.open(`${base}/product/${productId}`, '_blank');
}
</script>

<style scoped lang="scss">
.behavior-timeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty {
  color: var(--el-text-color-secondary);
  text-align: center;
  padding: 24px 0;
}

.behavior-row {
  position: relative;
  padding-left: 22px;
}

.dot {
  position: absolute;
  left: 0;
  top: 5px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--el-color-primary);
}

.line {
  position: absolute;
  left: 4px;
  top: 18px;
  width: 2px;
  bottom: -16px;
  background: var(--el-border-color);
}

.content {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 10px 12px;
  background: #fff;
}

.main {
  line-height: 1.6;
  word-break: break-word;
}

.time {
  color: var(--el-text-color-secondary);
}

.actor,
.verb {
  font-weight: 600;
}

.sep {
  margin: 0 4px;
  color: var(--el-text-color-secondary);
}
.link-text {
  border: 0;
  background: transparent;
  color: var(--el-color-primary);
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}
.link-text:hover { opacity: .85; }

.meta {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.tag-link-btn {
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0;
  cursor: pointer;
}
</style>
