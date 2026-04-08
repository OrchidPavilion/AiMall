<template>
  <main class="main-content">
    <div class="content-wrapper">
      <slot />
    </div>
  </main>
</template>

<script setup lang="ts">
// 主内容容器
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;
@use '@/styles/mixins.scss' as *;

.main-content {
  flex: 1;
  margin-top: $header-height;
  padding: $spacing-lg;
  overflow-y: auto;
  @include scrollbar();
  
  .content-wrapper {
    min-height: calc(100vh - #{$header-height});
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: $spacing-sm;
    .content-wrapper {
      min-height: calc(100vh - #{$header-height} - #{$spacing-sm});
    }
  }
}
</style>
