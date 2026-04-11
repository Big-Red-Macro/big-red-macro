<template>
  <div class="p-4 md:p-8">
    <div class="mx-auto max-w-6xl">

      <!-- Greeting header -->
      <header class="mb-8">
        <p class="text-sm font-semibold text-red-400 uppercase tracking-widest mb-1">{{ todayFormatted }}</p>
        <h1 class="text-3xl font-bold tracking-tight text-white">{{ greeting }}, Cornell!</h1>
      </header>

      <!-- Main Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- Left Col: Itinerary -->
        <div class="col-span-1 lg:col-span-2">

          <div v-if="!store.isConnectedToCalendar" class="rounded-3xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl">
             <h2 class="text-xl font-bold text-white mb-2">Connect Your Calendar</h2>
             <p class="text-slate-400 mb-6 text-sm">We need to read your schedule to generate a personalized meal itinerary.</p>
             <router-link to="/connect" class="inline-flex items-center justify-center rounded-xl bg-red-500 hover:bg-red-600 px-6 py-2.5 text-sm font-semibold text-white transition-all">Sign in with Google</router-link>
          </div>

          <div v-else class="space-y-4">
             <div class="flex justify-between items-center mb-2">
               <button @click="generatePlan" :disabled="store.isLoading" class="rounded-xl border border-white/10 bg-white/10 hover:bg-white/20 px-4 py-2 text-sm font-semibold text-white transition-all disabled:opacity-50">
                 {{ store.isLoading ? 'Generating Plan...' : 'Generate New Plan' }}
               </button>
             </div>

             <MealTimeline
               :date="store.itinerary?.itinerary_date"
               :meals="store.itinerary?.meals ?? []"
               :summary="store.itinerary?.daily_summary"
               :is-loading="store.isLoading"
               :plan-generated="!!store.itinerary"
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
               <span v-else class="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-bold text-red-400 uppercase tracking-wider">Offline</span>
             </div>
             <p class="mt-4 text-xs text-slate-400">Syncs daily events to find free meal gaps.</p>
          </div>

          <!-- Wait Times Widget -->
          <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xs font-bold tracking-widest text-slate-300 uppercase">Dining Hall Wait Times</h3>
              <button
                @click="refreshWaitTimes"
                :disabled="waitTimesRefreshing"
                class="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-semibold text-slate-300 hover:bg-white/10 transition-all disabled:opacity-50"
                title="Refresh wait times"
              >
                <svg
                  class="h-3.5 w-3.5"
                  :class="{ 'animate-spin': waitTimesRefreshing }"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
            </div>
            <WaitTimeWidget :wait-times="store.waitTimes" />
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/mainStore'
import MealTimeline from '../components/MealTimeline.vue'
import WaitTimeWidget from '../components/WaitTimeWidget.vue'

const store = useMainStore()
const waitTimesRefreshing = ref(false)

// Greeting based on current hour
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
})

// Nicely formatted today string e.g. "Saturday, April 11"
const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

onMounted(() => {
  store.fetchWaitTimes()
  if (store.isConnectedToCalendar && !store.itinerary) {
    store.generateMealPlan()
  }
})

const generatePlan = () => {
  store.generateMealPlan()
}

async function refreshWaitTimes() {
  waitTimesRefreshing.value = true
  try {
    await store.fetchWaitTimes()
  } finally {
    waitTimesRefreshing.value = false
  }
}
</script>
