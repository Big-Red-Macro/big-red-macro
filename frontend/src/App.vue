<template>
  <div class="min-h-screen bg-[#0f172a] text-slate-200 flex flex-col">

    <!-- Top Navigation -->
    <header v-if="!route.meta.hideNav" class="sticky top-0 z-50 flex items-center justify-between px-6 h-16 border-b border-white/10 bg-[#0f172a]/95 backdrop-blur-md">

      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#B31B1B] to-[#8a1515] shadow-lg shadow-[#B31B1B]/30 border border-white/10">
          <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3v7"/>
          </svg>
        </div>
        <span class="font-bold text-white text-[17px] tracking-tight">Big Red Macro</span>
      </div>

      <!-- Center nav -->
      <nav class="hidden md:flex items-center gap-8">
        <router-link to="/" class="text-sm font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-2" active-class="text-white !text-white">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
          Dashboard
        </router-link>
        <router-link to="/planner" class="text-sm font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-2" active-class="text-white !text-white">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          AI Planner
        </router-link>
        <router-link to="/map" class="text-sm font-semibold text-slate-400 hover:text-white transition-colors flex items-center gap-2" active-class="text-white !text-white">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
          Campus Map
        </router-link>
      </nav>

      <!-- Right: avatar & notifications -->
      <div class="flex items-center gap-5">
        <button class="relative text-slate-400 hover:text-white transition-colors">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
          <span class="absolute top-0 right-0 w-2 h-2 bg-[#B31B1B] rounded-full border-2 border-[#0f172a]"></span>
        </button>

        <div class="relative">
          <button @click="showDropdown = !showDropdown" class="flex items-center gap-2 focus:outline-none">
            <div class="h-10 w-10 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-sm font-bold text-white shadow-md border border-slate-600 hover:border-slate-400 transition-colors">
              {{ initials }}
            </div>
          </button>

          <!-- Dropdown -->
          <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
            <div v-if="showDropdown" class="absolute right-0 mt-2 w-48 rounded-xl shadow-lg bg-[#1e293b] ring-1 ring-black ring-opacity-5 divide-y divide-slate-700 border border-slate-700 focus:outline-none z-50">
              <div class="px-4 py-3">
                <p class="text-sm font-semibold text-white truncate">{{ auth.userName || 'User' }}</p>
                <p class="text-xs font-medium text-slate-400 truncate">{{ auth.userEmail || 'user@cornell.edu' }}</p>
              </div>
              <div class="py-1">
                <router-link @click="showDropdown = false" to="/connect" class="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white">
                  <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                  Profile Settings
                </router-link>
              </div>
              <div class="py-1">
                <button @click="doLogout" class="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-slate-700 hover:text-red-300">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                  Sign out
                </button>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 relative">
      <router-view />
    </main>

    <!-- Overlay to close dropdown -->
    <div v-if="showDropdown" @click="showDropdown = false" class="fixed inset-0 z-40"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showDropdown = ref(false)

const initials = computed(() => {
  if (!auth.userName) return 'U'
  return auth.userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function doLogout() {
  showDropdown.value = false
  auth.logout()
  router.push('/login')
}
</script>
