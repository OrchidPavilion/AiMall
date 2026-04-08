<template>
  <div class="page-shell">
    <MallHeader :keyword="keyword" @search="search" />
    <main class="list-page mall-surface apple-shell block-shell">
      <div class="list-hero minimal-row">
        <div>
          <h2>商品列表</h2>
          <p>{{ keyword ? `关键词：${keyword}` : '全部商品' }}{{ categoryId ? ` · 分类 ${categoryId}` : '' }}</p>
        </div>
        <div class="tool-row">
          <select v-model="sortBy" aria-label="排序">
            <option value="default">默认排序</option>
            <option value="price_asc">价格从低到高</option>
            <option value="price_desc">价格从高到低</option>
            <option value="sales_desc">销量优先</option>
            <option value="views_desc">浏览优先</option>
          </select>
        </div>
      </div>

      <div class="list-bar">
        <div>{{ total }} 件商品</div>
        <div class="panel-chip">第 {{ page }} 页</div>
      </div>

      <div v-if="sortedProducts.length" class="grid grid-4">
        <ProductCard v-for="p in sortedProducts" :key="p.id" :item="p" />
      </div>
      <div v-else class="empty-block">没有找到匹配商品</div>

      <div class="load-more-wrap">
        <button class="load-more" :disabled="page * pageSize >= total" @click="nextPage">{{ page * pageSize >= total ? '没有更多了' : '继续加载' }}</button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MallHeader from '../components/MallHeader.vue'
import ProductCard from '../components/ProductCard.vue'
import { mallApi } from '../api'
import { getMallCustomerId } from '../auth'

const route = useRoute()
const router = useRouter()
const keyword = computed(() => String(route.query.keyword || ''))
const categoryId = computed(() => String(route.query.categoryId || ''))
const products = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const sortBy = ref<'default'|'price_asc'|'price_desc'|'sales_desc'|'views_desc'>('default')

const normalizeProduct = (x: any) => ({
  id: x.id,
  name: x.name,
  image: x.image || 'https://via.placeholder.com/240x180?text=No+Image',
  spec: x.default_spec || '默认规格',
  price: Number(x.price || 0),
  sales: x.sales || 0,
  views: x.views || 0,
})

const sortedProducts = computed(() => {
  const list = [...products.value]
  switch (sortBy.value) {
    case 'price_asc': return list.sort((a,b) => a.price - b.price)
    case 'price_desc': return list.sort((a,b) => b.price - a.price)
    case 'sales_desc': return list.sort((a,b) => b.sales - a.sales)
    case 'views_desc': return list.sort((a,b) => b.views - a.views)
    default: return list
  }
})

async function loadProducts(reset = true) {
  if (reset) {
    page.value = 1
    products.value = []
  }
  const data = await mallApi.getProducts({ keyword: keyword.value || undefined, categoryId: categoryId.value || undefined, page: page.value, pageSize })
  total.value = data.total || 0
  const rows = (data.list || []).map(normalizeProduct)
  products.value = reset ? rows : [...products.value, ...rows]
}

function search(v: string) {
  if (v) {
    const cid = getMallCustomerId()
    if (cid) void mallApi.trackBehavior({ customer_id: cid, behavior_type: 'SEARCH', target_type: 'KEYWORD', target_name: v, source_page: 'PRODUCT_LIST' }).catch(() => {})
  }
  router.push({ path: '/products', query: { ...route.query, keyword: v || undefined } })
}

function nextPage() {
  if (page.value * pageSize >= total.value) return
  page.value += 1
  void loadProducts(false)
}

watch(() => [keyword.value, categoryId.value], () => { void loadProducts(true) }, { immediate: true })
</script>
