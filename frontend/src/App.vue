<template>
  <div class="min-h-screen bg-slate-900 flex text-slate-200">
    <!-- Sidebar Navigation -->
    <aside v-if="!route.meta.hideNav" class="w-20 lg:w-64 flex-shrink-0 border-r border-white/10 bg-slate-900/50 flex flex-col justify-between backdrop-blur-md z-10 transition-all duration-300">
      <div class="p-4 lg:p-6">
        <div class="flex items-center gap-3 mb-10 justify-center lg:justify-start">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cornell-red to-cornell-800 shadow-lg shadow-cornell-red/20">
             <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="text-sm font-bold text-slate-900 dark:text-white hidden lg:block tracking-tight">Big Red Macro</span>
        </div>

        <nav class="space-y-2">
          <router-link to="/" class="flex items-center gap-3 px-3 py-3 rounded-xl transition-all text-slate-400 hover:text-white hover:bg-white/5 group" active-class="bg-gradient-to-r from-cornell-red/20 to-cornell-700/10 text-white border border-cornell-red/20 shadow-sm backdrop-blur-sm">
            <svg class="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            <span class="hidden lg:block font-medium">Dining Halls</span>
          </router-link>
          
          <router-link to="/planner" class="flex items-center gap-3 px-3 py-3 rounded-xl transition-all text-slate-400 hover:text-white hover:bg-white/5 group" active-class="bg-gradient-to-r from-cornell-red/20 to-cornell-700/10 text-white border border-cornell-red/20 shadow-sm backdrop-blur-sm">
            <svg class="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <span class="hidden lg:block font-medium">AI Planner</span>
          </router-link>

          <router-link to="/connect" class="flex items-center gap-3 px-3 py-3 rounded-xl transition-all text-slate-400 hover:text-white hover:bg-white/5 group" active-class="bg-gradient-to-r from-cornell-red/20 to-cornell-700/10 text-white border border-cornell-red/20 shadow-sm backdrop-blur-sm">
            <svg class="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            <span class="hidden lg:block font-medium">Settings</span>
          </router-link>
        </nav>
      </div>
      
      <!-- User Info + Logout at bottom -->
      <div class="p-4 lg:p-6 mb-4 space-y-3">
        <!-- User greeting -->
        <div v-if="auth.isAuthenticated && auth.userName" class="flex items-center gap-3 px-3 py-2">
          <img v-if="auth.userPicture" :src="auth.userPicture" class="w-8 h-8 rounded-full ring-2 ring-cornell-red/40 shrink-0" referrerpolicy="no-referrer" alt="avatar" />
          <div v-else class="w-8 h-8 rounded-full bg-gradient-to-br from-cornell-red to-cornell-800 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {{ auth.userName.charAt(0).toUpperCase() }}
          </div>
          <div class="hidden lg:block overflow-hidden">
            <p class="text-sm font-semibold text-white truncate">{{ auth.userName }}</p>
            <p class="text-[11px] text-slate-500 truncate">{{ auth.userEmail }}</p>
          </div>
        </div>

        <button v-if="auth.isAuthenticated" @click="doLogout" class="flex items-center gap-3 px-3 py-3 rounded-xl transition-all bg-transparent group w-full justify-center lg:justify-start text-red-400 hover:text-red-300 hover:bg-red-500/10">
          <svg class="w-6 h-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
          <span class="hidden lg:block font-medium">Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 min-h-screen overflow-y-auto relative">
      <div v-if="!route.meta.hideNav" class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-cornell-red/10 via-slate-900/0 to-cornell-red/5 pointer-events-none -z-10"></div>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'

const route = useRoute()
const { isDark, toggle } = useTheme()
</script>
