<template>
  <div class="card" @click="$router.push(`/product/${item.id}`)">
    <div class="card-media">
      <img :src="item.image" alt="" />
    </div>
    <div class="card-body">
      <div class="card-title">{{ item.name }}</div>
      <div class="card-spec">{{ item.spec }}</div>
      <div class="card-footer">
        <div class="card-price">¥{{ item.price.toFixed(2) }}</div>
        <div class="card-meta">销量 {{ item.sales }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ item: { id: number; name: string; image: string; spec: string; price: number; sales: number; views: number } }>()
</script>
