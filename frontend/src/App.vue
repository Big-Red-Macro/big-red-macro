<template>
  <div class="min-h-screen bg-slate-900 flex text-slate-200">
    <!-- Sidebar -->
    <aside v-if="!route.meta.hideNav" class="w-16 lg:w-56 flex-shrink-0 border-r border-slate-800 bg-slate-950 flex flex-col justify-between z-10">
      <div class="p-3 lg:p-5">
        <!-- Logo -->
        <div class="flex items-center gap-2.5 mb-8 px-1 justify-center lg:justify-start">
          <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-600">
            <svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="text-sm font-bold text-white hidden lg:block tracking-tight">Big Red Macro</span>
        </div>

        <nav class="space-y-1">
          <router-link
            to="/"
            class="flex items-center gap-3 px-2 py-2.5 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white hover:bg-slate-800"
            active-class="bg-slate-800 text-white"
          >
            <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <span class="hidden lg:block">Dining Halls</span>
          </router-link>

          <router-link
            to="/planner"
            class="flex items-center gap-3 px-2 py-2.5 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white hover:bg-slate-800"
            active-class="bg-slate-800 text-white"
          >
            <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <span class="hidden lg:block">AI Planner</span>
          </router-link>

          <router-link
            to="/connect"
            class="flex items-center gap-3 px-2 py-2.5 rounded-lg text-sm font-medium transition-colors text-slate-400 hover:text-white hover:bg-slate-800"
            active-class="bg-slate-800 text-white"
          >
            <svg class="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span class="hidden lg:block">Settings</span>
          </router-link>
        </nav>
      </div>

    </aside>

    <!-- Main Content -->
    <main class="flex-1 min-h-screen overflow-y-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>
