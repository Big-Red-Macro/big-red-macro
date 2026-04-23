<template>
  <div class="min-h-screen bg-[#0f172a] text-slate-200 flex flex-col">

    <!-- Top Navigation -->
    <header v-if="!route.meta.hideNav" class="sticky top-0 z-50 flex items-center justify-between px-6 h-14 border-b border-white/10 bg-[#0f172a]/95 backdrop-blur-md">

      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#B31B1B] shadow-lg shadow-[#B31B1B]/30">
          <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3v7"/>
          </svg>
        </div>
        <span class="font-bold text-white text-[15px] tracking-tight">Big Red Macro</span>
      </div>

      <!-- Center nav -->
      <nav class="flex items-center gap-8">
        <router-link to="/" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">Dining Halls</router-link>
        <router-link to="/planner" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">AI Planner</router-link>
        <router-link to="/map" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">Campus Map</router-link>
      </nav>

      <!-- Right: avatar -->
      <div class="flex items-center gap-3">
        <router-link to="/connect">
          <div class="h-9 w-9 rounded-full bg-[#B31B1B] flex items-center justify-center text-sm font-bold text-white shadow-md shadow-[#B31B1B]/30 cursor-pointer hover:opacity-90 transition-opacity">
            {{ initials }}
          </div>
        </router-link>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const initials = computed(() => {
  if (!auth.userName) return 'U'
  return auth.userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function doLogout() {
  auth.logout()
  router.push('/login')
}
</script>
