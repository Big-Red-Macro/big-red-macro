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
        <p class="mb-8 text-sm text-slate-400">Log in with your Google Calendar to allow our AI to build a personalized, time-aware itinerary.</p>
        
        <button 
          @click="connectToGoogle" 
          class="flex w-full items-center justify-center gap-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/5 py-3.5 px-4 font-medium text-white transition-all hover:scale-[1.02] active:scale-[0.98] shadow-sm"
        >
          <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" class="h-5 w-5" />
          <span>Connect Google Calendar</span>
        </button>

        <p v-if="error" class="mt-4 text-xs font-medium text-red-400">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMainStore } from '../stores/mainStore'

const store = useMainStore()
const error = ref('')

const connectToGoogle = async () => {
  const url = await store.getConnectUrl()
  if (url) {
    window.location.href = url
  } else {
    error.value = store.currentError || 'An error occurred fetching the URL.'
  }
}
</script>
