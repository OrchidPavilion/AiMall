<template>
  <el-card>
    <h3>线上预览</h3>
    <p>商城端开发地址：<code>{{ mallUrl }}</code></p>
    <el-space>
      <el-button type="primary" @click="openMall">打开商城</el-button>
      <el-button @click="copyHint">复制地址（手动）</el-button>
    </el-space>
  </el-card>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';
const mallUrl = 'http://localhost:3101';
function openMall() { window.open(mallUrl, '_blank'); }
function copyHint() { ElMessage.info(`请复制地址：${mallUrl}`); }
</script>
