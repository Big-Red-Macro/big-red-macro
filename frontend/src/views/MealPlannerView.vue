<template>
  <div class="p-4 md:p-8">
    <div class="mx-auto max-w-4xl">
      <header class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight text-white mb-2">AI Meal Planner</h1>
        <p class="text-slate-400">Generate a personalized daily itinerary strictly adhering to your macros and free time blocks.</p>
      </header>

      <div class="space-y-8">
        <!-- Calendar Setup -->
        <div v-if="!store.isConnectedToCalendar" class="rounded-3xl border border-white/10 bg-white/5 p-10 text-center backdrop-blur-xl">
           <div class="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-red-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20">
              <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
           </div>
           <h2 class="text-xl font-bold text-white mb-2">Sync Your Schedule</h2>
           <p class="text-slate-400 mb-6 text-sm max-w-md mx-auto">To intelligently slot your meals throughout the day, connect your Google Calendar to find your free time gaps between classes.</p>
           <button @click="connectCalendar" class="inline-flex items-center justify-center rounded-xl bg-red-500 hover:bg-red-600 px-8 py-3 text-sm font-bold text-white transition-all shadow-lg shadow-red-500/20">
              Connect Google Calendar
           </button>
        </div>

        <div v-else class="space-y-6">
           <div class="space-y-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-sm">
             <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
               <div>
                 <p class="text-xs font-bold uppercase tracking-widest text-slate-500">Plan Date</p>
                 <h2 class="mt-1 text-xl font-bold text-white">{{ selectedDateLabel }}</h2>
               </div>
               <input
                 v-model="selectedDate"
                 @change="generatePlan"
                 type="date"
                 class="w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2 text-sm font-semibold text-white outline-none transition focus:border-red-400 lg:w-auto"
               />
             </div>

             <div class="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">
               <button
                 v-for="day in dayOptions"
                 :key="day.value"
                 @click="selectDay(day.value)"
                 class="rounded-xl border px-3 py-3 text-left transition"
                 :class="day.value === selectedDate
                   ? 'border-red-400 bg-red-500/20 text-white'
                   : 'border-white/10 bg-slate-950/40 text-slate-300 hover:border-white/20 hover:bg-white/10'"
               >
                 <span class="block text-xs font-bold uppercase tracking-wide text-slate-400">{{ day.weekday }}</span>
                 <span class="mt-1 block text-sm font-bold">{{ day.label }}</span>
               </button>
             </div>
           </div>

           <div class="flex flex-col gap-4 p-6 rounded-3xl border border-emerald-500/20 bg-emerald-500/5 backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between">
             <div class="flex items-center gap-4">
               <div class="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                 <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
               </div>
               <div>
                  <h3 class="text-white font-bold">Calendar Connected</h3>
                  <p class="text-xs text-slate-400 mt-1">Reading free time slots for {{ selectedDateLabel }}.</p>
               </div>
             </div>
             
             <button @click="generatePlan" :disabled="store.isLoading" class="rounded-xl bg-gradient-to-r from-red-500 to-red-600 px-6 py-2.5 text-sm font-bold text-white transition-all disabled:opacity-50 shadow-lg shadow-red-500/20">
               {{ store.isLoading ? 'Analyzing menus...' : 'Generate Itinerary' }}
             </button>
           </div>
           
           <MealTimeline 
             v-if="store.itinerary"
             :date="store.itinerary?.itinerary_date"
             :meals="store.itinerary?.meals"
             :summary="store.itinerary?.daily_summary"
             :plan-generated="true"
             class="animate-in fade-in slide-in-from-bottom-4 duration-500"
           />
           <div v-else-if="store.isLoading" class="text-center py-12">
             <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-red-500 border-t-transparent mb-4"></div>
             <p class="text-slate-400 animate-pulse">Running RAG via Gemini 2.5 Flash...</p>
           </div>
           <div v-else-if="store.currentError" class="rounded-2xl border border-red-500/20 bg-red-500/10 p-5 text-sm text-red-200">
             <p class="font-bold text-red-100">Itinerary generation failed</p>
             <p class="mt-1 text-red-200/80">{{ store.currentError }}</p>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '../stores/mainStore'
import MealTimeline from '../components/MealTimeline.vue'

const store = useMainStore()
const route = useRoute()
const selectedDate = ref(route.query.date || toLocalDateInput(new Date()))

const dayOptions = computed(() => {
  const today = new Date()
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today)
    date.setDate(today.getDate() + index)
    return {
      value: toLocalDateInput(date),
      weekday: date.toLocaleDateString(undefined, { weekday: 'short' }),
      label: index === 0
        ? 'Today'
        : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    }
  })
})

const selectedDateLabel = computed(() => {
  const date = parseLocalDateInput(selectedDate.value)
  const today = toLocalDateInput(new Date())
  if (selectedDate.value === today) return 'Today'
  return date.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  })
})

onMounted(async () => {
  await store.checkCalendarStatus()
  if (store.isConnectedToCalendar && store.itinerary?.itinerary_date !== selectedDate.value) {
    store.generateMealPlan(selectedDate.value)
  }
})

const generatePlan = () => {
  store.generateMealPlan(selectedDate.value)
}

const selectDay = (date) => {
  selectedDate.value = date
  generatePlan()
}

const connectCalendar = async () => {
  const url = await store.getConnectUrl()
  if (url) {
    window.location.href = url
  }
}

function toLocalDateInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseLocalDateInput(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}
</script>
