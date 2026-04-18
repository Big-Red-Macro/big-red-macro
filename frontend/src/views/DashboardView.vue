<template>
  <div class="p-6 md:p-8 max-w-5xl mx-auto">

    <header class="mb-8">
      <p class="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-widest mb-1">{{ todayFormatted }}</p>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{{ greeting }}, Cornell!</h1>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Left: Itinerary -->
      <div class="col-span-1 lg:col-span-2">
        <div v-if="!store.isConnectedToCalendar" class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-8 text-center">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Connect Your Calendar</h2>
          <p class="text-slate-500 dark:text-slate-400 mb-6 text-sm">We need to read your schedule to generate a personalized meal itinerary.</p>
          <router-link to="/connect" class="inline-flex items-center justify-center rounded-xl bg-red-600 hover:bg-red-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors">
            Sign in with Google
          </router-link>
        </div>

        <div v-else class="space-y-4">
          <div class="flex items-center justify-between mb-2">
            <button
              @click="generatePlan"
              :disabled="store.isLoading"
              class="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-800 dark:text-white transition-colors disabled:opacity-50"
            >
              {{ store.isLoading ? 'Generating...' : 'Generate New Plan' }}
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

      <!-- Right: Widgets -->
      <div class="col-span-1 space-y-4">

        <!-- Google Calendar status -->
        <div class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <div class="flex items-center justify-between">
            <p class="text-xs font-bold tracking-widest text-slate-400 dark:text-slate-400 uppercase">Google Calendar</p>
            <span v-if="store.isConnectedToCalendar" class="rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Connected</span>
            <span v-else class="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">Offline</span>
          </div>
          <p class="mt-3 text-xs text-slate-400 dark:text-slate-500">Syncs daily events to find free meal gaps.</p>
        </div>

        <!-- Wait Times -->
        <div class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <div class="flex items-center justify-between mb-4">
            <p class="text-xs font-bold tracking-widest text-slate-400 uppercase">Wait Times</p>
            <button
              @click="refreshWaitTimes"
              :disabled="waitTimesRefreshing"
              class="flex items-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 px-2.5 py-1 text-xs font-medium text-slate-600 dark:text-slate-300 transition-colors disabled:opacity-50"
            >
              <svg class="h-3 w-3" :class="{ 'animate-spin': waitTimesRefreshing }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/mainStore'
import MealTimeline from '../components/MealTimeline.vue'
import WaitTimeWidget from '../components/WaitTimeWidget.vue'

const store = useMainStore()
const waitTimesRefreshing = ref(false)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
})

const todayFormatted = computed(() =>
  new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
)

onMounted(() => {
  store.fetchWaitTimes()
  if (store.isConnectedToCalendar && !store.itinerary) {
    store.generateMealPlan()
  }
})

const generatePlan = () => store.generateMealPlan()

async function refreshWaitTimes() {
  waitTimesRefreshing.value = true
  try {
    await store.fetchWaitTimes()
  } finally {
    waitTimesRefreshing.value = false
  }
}
</script>
