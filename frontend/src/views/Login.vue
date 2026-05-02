<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-cornell-900 via-cornell-800 to-slate-900 px-4 relative overflow-hidden">
    <!-- Animated background shapes -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-cornell-red/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-cornell-red/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cornell-red/5 rounded-full blur-3xl"></div>
    </div>

    <div class="w-full max-w-md relative z-10">
      <!-- Logo + Title -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-cornell-red to-cornell-700 shadow-2xl shadow-cornell-red/30 mb-6">
          <svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-white tracking-tight mb-2">Big Red Macro</h1>
        <p class="text-slate-400 text-base">Cornell's intelligent dining planner</p>
      </div>

      <!-- Login Card -->
      <div class="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-2xl p-8 shadow-2xl">
        <div class="text-center mb-6">
          <h2 class="text-xl font-semibold text-white mb-1">Welcome Back</h2>
          <p class="text-sm text-slate-400">Sign in with your Google account to continue</p>
        </div>

        <div class="flex justify-center mb-6">
          <GoogleLogin
            v-if="googleClientId"
            :client-id="googleClientId"
            :callback="onGoogleSuccess"
            :error="onGoogleError"
            prompt
            auto-login
          />
          <p v-else class="text-sm text-red-400 text-center bg-red-500/10 rounded-xl px-4 py-2">
            Google sign-in is not configured.
          </p>
        </div>

        <p v-if="errorMsg" class="text-sm text-red-400 text-center bg-red-500/10 rounded-xl px-4 py-2 mt-4">{{ errorMsg }}</p>

        <div v-if="loading" class="flex justify-center mt-4">
          <div class="h-6 w-6 rounded-full border-2 border-cornell-red border-t-transparent animate-spin"></div>
        </div>

        <div class="mt-8 pt-6 border-t border-white/10">
          <p class="text-xs text-slate-500 text-center leading-relaxed">
            By signing in, you agree to let Big Red Macro access your Cornell dining preferences.
            We never store your Google password.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-slate-600 mt-8">© 2026 Big Red Macro · Cornell University</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { GoogleLogin } from 'vue3-google-login'

const auth = useAuthStore()
const router = useRouter()

const loading = ref(false)
const errorMsg = ref('')
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

async function onGoogleSuccess(response) {
  if (!response?.credential) {
    errorMsg.value = 'Google did not return a sign-in credential.'
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    await auth.loginGoogle(response.credential)
    router.push('/')
  } catch (e) {
    console.error('Google login failed:', e)
    errorMsg.value = e.response?.data?.detail || 'Sign-in failed. Please try again.'
  } finally {
    loading.value = false
  }
}

function onGoogleError() {
  errorMsg.value = 'Google sign-in was cancelled or failed.'
}
</script>
