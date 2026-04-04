<template>
  <div class="min-h-screen bg-slate-900 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-indigo-900/10 to-rose-900/10 p-4 md:p-8">
    <div class="mx-auto max-w-6xl">
      
      <!-- Top nav/header -->
      <header class="mb-8 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-rose-500 to-indigo-600 shadow-lg shadow-rose-500/20">
             <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 class="text-xl font-bold tracking-tight text-white hidden sm:block">Campus Kitchen AI</h1>
        </div>

        <nav class="flex gap-4">
          <router-link to="/" class="text-sm font-semibold text-white border-b-2 border-rose-500 pb-1">Dashboard</router-link>
          <a href="#" class="text-sm font-medium text-slate-400 hover:text-white transition-colors pb-1">Settings</a>
        </nav>
      </header>

      <!-- Main Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left Col: Itinerary -->
        <div class="col-span-1 lg:col-span-2">
          
          <div v-if="!store.isConnectedToCalendar" class="rounded-3xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl">
             <h2 class="text-xl font-bold text-white mb-2">Connect Your Calendar</h2>
             <p class="text-slate-400 mb-6 text-sm">We need to read your schedule to generate a personalized meal itinerary.</p>
             <router-link to="/connect" class="inline-flex items-center justify-center rounded-xl bg-indigo-500 hover:bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white transition-all">Sign in with Google</router-link>
          </div>

          <div v-else class="space-y-4">
             <div class="flex justify-between items-center mb-2">
               <button @click="generatePlan" :disabled="store.isLoading" class="rounded-xl border border-white/10 bg-white/10 hover:bg-white/20 px-4 py-2 text-sm font-semibold text-white transition-all disabled:opacity-50">
                 {{ store.isLoading ? 'Generating Plan...' : 'Generate New Plan' }}
               </button>
             </div>
             
             <!-- RAG Output display -->
             <MealTimeline 
               :date="store.itinerary?.itinerary_date"
               :meals="store.itinerary?.meals"
               :summary="store.itinerary?.daily_summary"
             />
          </div>

        </div>

        <!-- Right Col: Widgets -->
        <div class="col-span-1 space-y-8">
          
          <!-- Connection Status Widget -->
          <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">
             <div class="flex items-center justify-between">
               <h3 class="text-xs font-bold tracking-widest text-slate-300 uppercase">Google Calendar</h3>
               <span v-if="store.isConnectedToCalendar" class="rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Connected</span>
               <span v-else class="rounded-full bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400 uppercase tracking-wider">Offline</span>
             </div>
             <p class="mt-4 text-xs text-slate-400">Syncs daily events to find free meal gaps.</p>
          </div>

          <!-- Wait Times Widget -->
          <WaitTimeWidget :wait-times="store.waitTimes" />

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useMainStore } from '../stores/mainStore'
import MealTimeline from '../components/MealTimeline.vue'
import WaitTimeWidget from '../components/WaitTimeWidget.vue'

const store = useMainStore()

onMounted(() => {
  store.fetchWaitTimes()
  if (store.isConnectedToCalendar && !store.itinerary) {
    store.generateMealPlan()
  }
})

const generatePlan = () => {
  store.generateMealPlan()
}
</script>
