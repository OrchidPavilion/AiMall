<template>
  <div class="page-shell">
    <MallHeader @search="goSearch" />
    <main class="detail-page mall-surface apple-shell block-shell" v-if="detail">
      <div class="detail-top">
        <div class="gallery clean">
          <img class="main-img" :src="activeImage || detail.main_image" alt="" />
          <div class="thumbs">
            <img
              v-for="img in detail.images || []"
              :key="img.id || img.image_url"
              :src="img.image_url"
              alt=""
              :class="{ active: activeImage === img.image_url }"
              @click="activeImage = img.image_url"
            />
          </div>
        </div>

        <div class="detail-info clean">
          <h1>{{ detail.name }}</h1>
          <p class="soft">{{ detail.category_name }} · 浏览 {{ detail.view_count || 0 }}</p>
          <div class="price">¥{{ currentPrice }}</div>

          <div class="spec-box clean">
            <div class="spec-title">规格</div>
            <div class="spec-placeholder">
              <button v-for="sku in detail.skus || []" :key="sku.id" class="sku-chip" :class="{ active: selectedSku?.id === sku.id }" @click="selectedSku = sku">
                {{ sku.spec_name_text }}
              </button>
            </div>
            <div class="qty-picker">
              <span>数量</span>
              <button @click="quantity = Math.max(1, quantity - 1)">-</button>
              <strong>{{ quantity }}</strong>
              <button @click="quantity += 1">+</button>
            </div>
          </div>

          <div class="detail-actions">
            <button class="hero-btn primary" @click="addToCart">加入购物车</button>
            <button class="hero-btn" @click="buyNow">立即购买</button>
          </div>

          <p class="intro">{{ detail.summary || '暂无商品简介' }}</p>
        </div>
      </div>

      <section class="detail-content clean">
        <div class="panel-head compact"><h3>详情</h3></div>
        <div class="content-placeholder" v-html="detail.detail_content || '<p>图文详情区域占位（后续实现）</p>'"></div>
      </section>
    </main>
    <main class="detail-page mall-surface apple-shell block-shell" v-else>
      <div class="empty-block">加载中...</div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MallHeader from '../components/MallHeader.vue'
import { mallApi } from '../api'
import { ensureMallCustomerId, getMallCustomerId } from '../auth'

const route = useRoute()
const router = useRouter()
const detail = ref<any>(null)
const selectedSku = ref<any>(null)
const activeImage = ref('')
const quantity = ref(1)

const currentPrice = computed(() => ((selectedSku.value?.price ?? detail.value?.default_price ?? 0) / 100).toFixed(2))

async function loadDetail() {
  const id = route.params.id as string
  detail.value = await mallApi.getProductDetail(id)
  selectedSku.value = (detail.value.skus || [])[0] || null
  activeImage.value = detail.value.main_image || ''
  const cid = getMallCustomerId()
  if (cid) void mallApi.trackBehavior({ customer_id: cid, behavior_type: 'VIEW_PRODUCT', target_type: 'PRODUCT', target_id: Number(id), target_name: detail.value.name, source_page: 'PRODUCT_DETAIL' }).catch(() => {})
}

async function addToCart() {
  if (!detail.value || !selectedSku.value) return
  try {
    const cid = ensureMallCustomerId()
    await mallApi.addCartItem({ customer_id: cid, sku_id: selectedSku.value.id, quantity: quantity.value })
    void mallApi.trackBehavior({ customer_id: cid, behavior_type: 'ADD_TO_CART', target_type: 'PRODUCT', target_id: detail.value.id, target_name: detail.value.name, source_page: 'PRODUCT_DETAIL' }).catch(() => {})
    alert('已加入购物车')
  } catch {
    router.push('/auth')
  }
}

async function buyNow() { await addToCart(); router.push('/cart') }
function goSearch(keyword: string) { router.push({ path: '/products', query: { keyword } }) }
onMounted(() => { void loadDetail() })
</script>
