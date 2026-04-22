<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-red-900/20 to-red-900/20 p-6">
    <div class="relative w-full max-w-md overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl">
      <div class="absolute -top-32 -right-32 h-64 w-64 rounded-full bg-red-500/20 blur-[80px]"></div>
      <div class="absolute -bottom-32 -left-32 h-64 w-64 rounded-full bg-red-500/20 blur-[80px]"></div>

      <div class="relative z-10 flex flex-col items-center text-center">
        <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500 to-red-600 shadow-lg shadow-red-500/30">
          <svg class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>

        <h1 class="mb-2 text-3xl font-bold tracking-tight text-white">Big Red Macro</h1>
        <p class="mb-8 text-sm text-slate-400">Your AI-powered Cornell dining planner. Sign in with Google to get started.</p>

        <div class="flex justify-center w-full">
          <GoogleLogin :callback="onGoogleLogin" />
        </div>

        <p v-if="error" class="mt-4 text-xs font-medium text-red-400">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { GoogleLogin } from 'vue3-google-login'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getProfile } from '@/api'

const router = useRouter()
const auth = useAuthStore()
const error = ref('')

async function onGoogleLogin(response) {
  try {
    await auth.loginGoogle(response.credential)
  } catch (e) {
    console.error(e)
    error.value = 'Sign in failed. Please try again.'
    return
  }
  try {
    const profileRes = await getProfile()
    if (!profileRes.data.onboarding_complete) {
      router.push('/onboarding')
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error(e)
    router.push('/onboarding')
  }
}
</script>
