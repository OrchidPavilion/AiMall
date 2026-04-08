<template>
  <div class="page-shell">
    <MallHeader @search="goSearch" />

    <section class="hero-wrap apple-shell">
      <div class="hero-card minimal">
        <p class="eyebrow">AiMall</p>
        <h1>更安静的商城体验</h1>
        <p class="hero-desc">基于浏览、搜索与加购行为的个性化推荐。信息更少，决策更快。</p>
        <div class="hero-actions">
          <button class="hero-btn primary" @click="$router.push('/products')">浏览商品</button>
          <button class="hero-btn" @click="refreshRecommend">换一换推荐</button>
        </div>
      </div>
    </section>

    <main class="home-main apple-shell">
      <aside class="category-panel">
        <div class="section-title-row">
          <h3>分类</h3>
          <span>{{ categories.length }}</span>
        </div>
        <div v-for="cat in categories" :key="cat.id" class="cat-item" @mouseenter="active = cat.id" @mouseleave="active = null">
          <div class="cat-name-row">
            <button class="cat-name-btn" type="button" @click="goCategory(cat.id, cat.name)">{{ cat.name }}</button>
            <span class="cat-arrow">›</span>
          </div>
          <div v-if="active === cat.id" class="cat-flyout">
            <div v-for="sub in cat.children || []" :key="sub.id" class="sub-block">
              <button class="sub-title" type="button" @click="goCategory(sub.id, sub.name)">{{ sub.name }}</button>
              <div class="sub-tags">
                <button v-for="leaf in sub.children || []" :key="leaf.id" type="button" @click="goCategory(leaf.id, leaf.name)">{{ leaf.name }}</button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <section class="content-panel">
        <section class="panel recommend-panel">
          <div class="panel-head compact">
            <h3>为你推荐</h3>
            <button class="link-btn" @click="refreshRecommend">换一换</button>
          </div>
          <div v-if="recommendProducts.length" class="grid grid-4">
            <ProductCard v-for="p in recommendProducts" :key="`r-${p.id}`" :item="p" />
          </div>
          <div v-else class="empty-block">暂无推荐数据</div>
        </section>

        <section class="panel">
          <div class="panel-head compact">
            <h3>商品</h3>
            <span class="panel-chip">{{ randomProducts.length }} 已加载</span>
          </div>
          <div class="grid grid-4">
            <ProductCard v-for="p in randomProducts" :key="p.id" :item="p" />
          </div>
          <div class="load-more-wrap">
            <button class="load-more" :disabled="!randomHasMore" @click="loadMore">{{ randomHasMore ? '加载更多' : '没有更多了' }}</button>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MallHeader from '../components/MallHeader.vue'
import ProductCard from '../components/ProductCard.vue'
import { mallApi } from '../api'
import { getMallCustomerId } from '../auth'

const router = useRouter()
const active = ref<number | null>(null)
const categories = ref<any[]>([])
const recommendProducts = ref<any[]>([])
const randomProducts = ref<any[]>([])
const randomCursor = ref(0)
const randomHasMore = ref(true)
const randomSeed = ref(Math.floor(Date.now() / 1000))
const recommendExcludeIds = ref<number[]>([])
let randomLoading = false

const normalizeProduct = (x: any) => ({
  id: x.id,
  name: x.name,
  image: x.image || x.main_image || 'https://via.placeholder.com/240x180?text=No+Image',
  spec: x.default_spec || x.default_spec_name || '默认规格',
  price: Number(x.price ?? ((x.default_price || 0) / 100)),
  sales: x.sales || x.sales_count || 0,
  views: x.views || x.view_count || 0,
})

async function loadHome() {
  const home = await mallApi.home()
  categories.value = home.categories || []
}

async function loadRecommend(reset = false) {
  if (reset) recommendExcludeIds.value = []
  const cid = getMallCustomerId()
  if (!cid) {
    recommendProducts.value = []
    return
  }
  const data = await mallApi.getRecommendations(cid, undefined, recommendExcludeIds.value)
  recommendProducts.value = (data || []).map(normalizeProduct)
  recommendExcludeIds.value = [...new Set([...recommendExcludeIds.value, ...recommendProducts.value.map((p: any) => p.id)])]
}

async function loadRandom(reset = false) {
  if (randomLoading) return
  if (reset) {
    randomCursor.value = 0
    randomHasMore.value = true
    randomProducts.value = []
    randomSeed.value = Math.floor(Date.now() / 1000)
  }
  if (!randomHasMore.value) return
  randomLoading = true
  try {
    const data = await mallApi.getRandomProducts(randomCursor.value, 20, randomSeed.value)
    randomProducts.value = [...randomProducts.value, ...(data.list || []).map(normalizeProduct)]
    randomCursor.value = data.cursor || randomCursor.value
    randomHasMore.value = !!data.has_more
  } finally {
    randomLoading = false
  }
}

function refreshRecommend() { void loadRecommend(false) }
function loadMore() { void loadRandom(false) }

function onWindowScroll() {
  const nearBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 180
  if (nearBottom && randomHasMore.value) void loadRandom(false)
}

function goSearch(keyword: string) {
  if (!keyword) return
  const cid = getMallCustomerId()
  if (cid) void mallApi.trackBehavior({ customer_id: cid, behavior_type: 'SEARCH', target_type: 'KEYWORD', target_name: keyword, source_page: 'HOME' }).catch(() => {})
  router.push({ path: '/products', query: { keyword } })
}

function goCategory(categoryId: number, categoryName: string) {
  const cid = getMallCustomerId()
  if (cid) void mallApi.trackBehavior({ customer_id: cid, behavior_type: 'CLICK_CATEGORY', target_type: 'CATEGORY', target_id: categoryId, target_name: categoryName, source_page: 'HOME' }).catch(() => {})
  router.push({ path: '/products', query: { categoryId } })
}

onMounted(async () => {
  window.addEventListener('scroll', onWindowScroll, { passive: true })
  await loadHome()
  await Promise.all([loadRecommend(true), loadRandom(true)])
})

onUnmounted(() => window.removeEventListener('scroll', onWindowScroll))
</script>
