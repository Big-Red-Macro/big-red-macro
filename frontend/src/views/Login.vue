<template>
  <div class="min-h-screen flex items-center justify-center bg-cornell-light px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-cornell-red">🐻 Big Red Macro</h1>
        <p class="text-cornell-gray mt-1 text-sm">Cornell's intelligent dining planner</p>
      </div>

      <form @submit.prevent="handleLogin" class="card space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">NetID</label>
          <input v-model="form.username" type="text" class="input" placeholder="ab123" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input v-model="form.password" type="password" class="input" placeholder="••••••••" required />
        </div>
        <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
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
  } catch {
    errorMsg.value = 'Invalid NetID or password.'
  } finally {
    loading.value = false
  }
}
</script>
