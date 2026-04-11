<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 px-4">
    <div class="w-full max-w-sm">

      <!-- Logo -->
      <div class="text-center mb-10">
        <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-red-600 mb-4">
          <svg class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight">Big Red Macro</h1>
        <p class="text-slate-400 text-sm mt-1">Cornell's intelligent dining planner</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-300 mb-1.5">NetID</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="ab123"
            required
            autocomplete="username"
            class="w-full rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="current-password"
            class="w-full rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
          />
        </div>

        <!-- Error -->
        <div v-if="errorMsg" class="rounded-xl bg-red-500/10 border border-red-500/30 px-4 py-3">
          <p class="text-sm text-red-400">{{ errorMsg }}</p>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 px-4 py-2.5 text-sm font-semibold text-white transition-colors mt-2"
        >
          <span v-if="loading" class="flex items-center justify-center gap-2">
            <svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Signing in...
          </span>
          <span v-else>Sign in</span>
        </button>
      </form>

      <p class="text-center text-xs text-slate-600 mt-8">Cornell University — Dining Services</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/')
  } catch (e) {
    const status = e.response?.status
    if (status === 401 || status === 400) {
      errorMsg.value = 'Incorrect NetID or password.'
    } else if (!e.response) {
      errorMsg.value = 'Cannot reach the server. Make sure the backend is running.'
    } else {
      errorMsg.value = `Server error (${status}). Please try again.`
    }
  } finally {
    loading.value = false
  }
}
</script>
