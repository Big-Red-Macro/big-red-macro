<template>
  <div class="min-h-screen flex items-center justify-center bg-[#0f172a]">
    <div class="w-full max-w-md mx-4">
      <div class="rounded-2xl bg-[#1c1528] p-10 flex flex-col items-center text-center shadow-2xl">

        <!-- Icon -->
        <div class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#B31B1B] shadow-lg shadow-[#B31B1B]/30">
          <svg class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3v7"/>
          </svg>
        </div>

        <!-- Title -->
        <h1 class="text-2xl font-bold text-white mb-2 tracking-tight">Big Red Macro</h1>
        <p class="text-slate-400 text-sm mb-8 leading-relaxed">AI-powered nutrition planning for Cornell dining</p>

        <!-- Google Sign In -->
        <div class="w-full flex justify-center">
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
