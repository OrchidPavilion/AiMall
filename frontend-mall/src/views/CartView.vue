<template>
  <div class="page-shell">
    <MallHeader @search="goSearch" />
    <main class="cart-page mall-surface apple-shell block-shell">
      <div class="cart-head minimal-row">
        <div>
          <h2>购物车</h2>
          <p class="soft">已选 {{ checkedCount }} 件</p>
        </div>
        <div class="cart-tools">
          <label><input type="checkbox" :checked="allChecked" @change="toggleAll(($event.target as HTMLInputElement).checked)" /> 全选</label>
          <button class="ghost-btn" @click="removeChecked" :disabled="!checkedCount">删除已选</button>
        </div>
      </div>

      <div v-if="items.length" class="cart-list clean">
        <label v-for="item in items" :key="item.id" class="cart-row minimal">
          <input type="checkbox" :checked="item.checked" @change="toggleCheck(item, ($event.target as HTMLInputElement).checked)" />
          <img :src="item.product_image" alt="" />
          <div class="info">
            <div class="name">{{ item.product_name }}</div>
            <div class="meta">{{ item.spec_name }}</div>
            <button class="text-danger" @click.prevent="removeItem(item.id)">移除</button>
          </div>
          <div class="price-cell">¥{{ (item.unit_price / 100).toFixed(2) }}</div>
          <div class="qty-cell">
            <button @click.prevent="changeQty(item, item.quantity - 1)">-</button>
            <span>{{ item.quantity }}</span>
            <button @click.prevent="changeQty(item, item.quantity + 1)">+</button>
          </div>
          <div class="price-cell">¥{{ (item.line_total / 100).toFixed(2) }}</div>
        </label>
      </div>
      <div v-else class="empty-block">购物车为空</div>

      <div class="cart-footer sticky-footer slim">
        <div>合计 <strong class="price-strong">¥{{ (total / 100).toFixed(2) }}</strong></div>
        <button class="checkout" @click="checkout" :disabled="!checkedCount">结算</button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MallHeader from '../components/MallHeader.vue'
import { mallApi } from '../api'
import { ensureMallCustomerId } from '../auth'

const router = useRouter()
const items = ref<any[]>([])
const total = computed(() => items.value.filter(i => i.checked).reduce((s, i) => s + (i.line_total || 0), 0))
const checkedCount = computed(() => items.value.filter(i => i.checked).length)
const allChecked = computed(() => items.value.length > 0 && items.value.every(i => i.checked))

async function loadCart() {
  const cid = ensureMallCustomerId()
  items.value = await mallApi.getCartItems(cid)
}
async function toggleCheck(item: any, checked: boolean) { Object.assign(item, await mallApi.updateCartItem(item.id, { checked })) }
async function toggleAll(checked: boolean) { await Promise.all(items.value.map(i => mallApi.updateCartItem(i.id, { checked }))); await loadCart() }
async function changeQty(item: any, quantity: number) { if (quantity < 1) return; Object.assign(item, await mallApi.updateCartItem(item.id, { quantity })) }
async function removeItem(id: number) { await mallApi.deleteCartItem(id); await loadCart() }
async function removeChecked() { await Promise.all(items.value.filter(i => i.checked).map(i => mallApi.deleteCartItem(i.id))); await loadCart() }
async function checkout() {
  const checkedItems = items.value.filter(i => i.checked)
  const checkedIds = checkedItems.map(i => i.id)
  const productIds = checkedItems.map((i: any) => i.product).filter(Boolean)
  const cid = ensureMallCustomerId()
  const data = await mallApi.settlementPreview({ customer_id: cid, item_ids: checkedIds })
  const itemNames = checkedItems.map((i: any) => i.product_name).filter(Boolean)
  if (itemNames.length) {
    await mallApi.trackBehavior({
      customer_id: cid,
      behavior_type: 'PURCHASE',
      target_type: 'PRODUCT',
      target_id: productIds.length === 1 ? productIds[0] : undefined,
      target_name: itemNames.join('、'),
      source_page: 'CART',
      extra_data: {
        item_ids: productIds,
        item_names: itemNames,
        item_count: data.item_count,
        total_amount: data.total_amount,
      },
    }).catch(() => {})
  }
  alert(`结算预览：${(data.total_amount / 100).toFixed(2)} 元（${data.item_count} 件）`)
}
function goSearch(keyword: string) { router.push({ path: '/products', query: { keyword } }) }
onMounted(() => {
  if (!localStorage.getItem('aimall_mall_user')) {
    router.push('/auth')
    return
  }
  void loadCart().catch(() => router.push('/auth'))
})
</script>
