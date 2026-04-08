<template>
  <div class="page-shell auth-page-wrap">
    <MallHeader />
    <main class="auth-page apple-shell">
      <div class="auth-card">
        <div class="auth-switch">
          <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <h1>{{ mode === 'login' ? '手机号登录' : '注册账户' }}</h1>
        <p class="soft">密码规则：至少 6 位纯数字</p>

        <form class="auth-form" @submit.prevent="submit">
          <label>
            手机号
            <input v-model.trim="form.phone" maxlength="11" placeholder="请输入手机号" />
          </label>
          <label v-if="mode === 'register'">
            用户名
            <input v-model.trim="form.name" maxlength="20" placeholder="可选，留空自动生成" />
          </label>
          <label>
            密码
            <input v-model.trim="form.password" type="password" maxlength="20" placeholder="至少6位纯数字" />
          </label>
          <button class="hero-btn primary auth-submit" type="submit" :disabled="submitting">{{ submitting ? '提交中...' : (mode === 'login' ? '登录' : '注册') }}</button>
        </form>

        <p v-if="errorMsg" class="auth-error">{{ errorMsg }}</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import MallHeader from '../components/MallHeader.vue'
import { mallApi } from '../api'
import { setMallUser } from '../auth'

const router = useRouter()
const mode = ref<'login' | 'register'>('login')
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({ phone: '', password: '', name: '' })

function localValidate() {
  if (!/^1\d{10}$/.test(form.phone)) return '请输入正确的11位手机号'
  if (!/^\d{6,}$/.test(form.password)) return '密码必须为至少6位纯数字'
  return ''
}

async function submit() {
  errorMsg.value = ''
  const v = localValidate()
  if (v) {
    errorMsg.value = v
    return
  }
  submitting.value = true
  try {
    const data = mode.value === 'login'
      ? await mallApi.mallLogin({ phone: form.phone, password: form.password })
      : await mallApi.mallRegister({ phone: form.phone, password: form.password, name: form.name })
    setMallUser({ id: data.user.id, name: data.user.name, phone: data.user.phone, avatar: data.user.avatar })
    router.replace('/')
  } catch (e: any) {
    errorMsg.value = e.message || '操作失败'
  } finally {
    submitting.value = false
  }
}
</script>
