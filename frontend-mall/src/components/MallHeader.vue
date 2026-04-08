<template>
  <header class="mall-header apple-shell">
    <div class="header-inner">
      <button class="brand-btn" type="button" @click="$router.push('/')">
        <span class="brand-mark">●</span>
        <span class="brand-text">AiMall</span>
      </button>

      <nav class="main-nav" aria-label="主导航">
        <a href="javascript:void(0)" @click="$router.push('/')">首页</a>
        <a href="javascript:void(0)" @click="$router.push('/products')">商店</a>
      </nav>

      <form class="search" @submit.prevent="search">
        <input v-model="keywordInner" placeholder="搜索商品" aria-label="搜索商品" />
        <button type="submit">搜索</button>
      </form>

      <div class="header-actions">
        <button class="icon-btn" type="button" @click="$router.push('/cart')">购物车</button>
        <div class="avatar-wrap">
          <button class="avatar-btn" type="button" @click="goAuthOrHome">
            <img v-if="user?.avatar" :src="user.avatar" alt="avatar" />
            <span v-else>{{ avatarText }}</span>
          </button>
          <div class="avatar-pop">
            <template v-if="user">
              <div class="avatar-name">{{ user.name }}</div>
              <div class="avatar-phone">{{ user.phone }}</div>
              <button class="avatar-link" type="button" @click="logout">退出登录</button>
            </template>
            <template v-else>
              <div class="avatar-name">未登录</div>
              <button class="avatar-link" type="button" @click="$router.push('/auth')">去登录 / 注册</button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { clearMallUser, getMallUser } from '../auth'

const router = useRouter()
const props = defineProps<{ keyword?: string }>()
const emit = defineEmits<{ (e: 'search', value: string): void }>()
const keywordInner = ref(props.keyword || '')
const user = ref(getMallUser())
watch(() => props.keyword, (v) => { keywordInner.value = v || '' })

const avatarText = computed(() => (user.value?.name?.slice(0, 1) || '我'))

function search() { emit('search', keywordInner.value.trim()) }
function refreshUser() { user.value = getMallUser() }
function logout() {
  clearMallUser()
  router.push('/auth')
}
function goAuthOrHome() {
  if (!user.value) router.push('/auth')
}

onMounted(() => window.addEventListener('aimall-auth-changed', refreshUser))
onUnmounted(() => window.removeEventListener('aimall-auth-changed', refreshUser))
</script>
