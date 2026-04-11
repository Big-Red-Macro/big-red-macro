<template>
  <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl relative overflow-hidden">
    <!-- Subtle glow background -->
    <div class="absolute -top-40 -left-40 h-80 w-80 rounded-full bg-red-500/10 blur-[100px] pointer-events-none"></div>

    <div class="mb-8 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-white tracking-tight">DAILY MEAL ITINERARY</h2>
        <p class="text-sm text-slate-400 mt-1">{{ date }}</p>
      </div>
      <div class="flex gap-2">
        <button class="h-8 w-8 rounded-full border border-white/10 bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors text-white">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <button class="h-8 w-8 rounded-full border border-white/10 bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors text-white">
           <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>

    <!-- Skeleton loading state — shown while AI plan is being generated -->
    <div v-if="isLoading" class="relative pl-4 border-l border-white/10 ml-4 py-2 space-y-8 animate-pulse">
      <div v-for="n in 3" :key="n" class="ml-8 rounded-2xl border border-white/5 bg-white/5 p-4">
        <div class="h-3 w-24 rounded-md bg-white/10 mb-3"></div>
        <div class="h-4 w-3/4 rounded-md bg-white/10 mb-2"></div>
        <div class="h-4 w-1/2 rounded-md bg-white/10 mb-4"></div>
        <div class="h-3 w-full rounded-md bg-white/5"></div>
      </div>
    </div>

    <!-- Timeline — meals present -->
    <div v-else-if="meals.length > 0" class="relative pl-4 border-l border-white/10 ml-4 py-2 space-y-10">
      <div v-for="(meal, index) in meals" :key="index" class="relative group">
        <!-- Dot -->
        <div class="absolute -left-[21px] top-4 h-3 w-3 rounded-full border-2 border-slate-900 bg-red-400 shadow-[0_0_10px_rgba(129,140,248,0.5)] group-hover:bg-red-400 transition-colors"></div>
        <div class="absolute -left-12 top-3 text-sm font-semibold text-slate-300 w-8 text-right">{{ meal.meal_time.split(' ')[0] }}</div>

        <!-- Card -->
        <div class="ml-8 rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:-translate-y-1 hover:shadow-lg">
          <div class="flex flex-col gap-2">
            <h4 class="text-xs font-bold tracking-widest text-red-400 uppercase">{{ meal.dining_hall_name }}</h4>
            <ul class="text-sm text-white font-medium list-disc list-inside">
              <li v-for="item in meal.suggested_items" :key="item">{{ item }}</li>
            </ul>
            <div class="flex justify-between items-end mt-2">
              <p class="text-xs text-slate-400 w-3/4 pr-4">{{ meal.reasoning }}</p>
              <div class="rounded-lg bg-slate-900/50 px-2 py-1 text-xs font-semibold text-red-300">
                {{ meal.estimated_macros?.calories || '---' }} kcal
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state: plan was generated but returned no meals -->
    <div v-else-if="planGenerated" class="ml-8 py-10 flex flex-col items-center gap-3 text-slate-400">
      <svg class="h-10 w-10 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm italic opacity-60">No meals were scheduled — try generating a new plan.</p>
    </div>

    <!-- Empty state: plan has not been generated yet -->
    <div v-else class="ml-8 py-10 flex flex-col items-center gap-3 text-slate-400">
      <svg class="h-10 w-10 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm italic opacity-60">No plan generated yet — hit "Generate New Plan" to get started.</p>
    </div>

    <div v-if="summary" class="mt-8 rounded-xl bg-red-500/10 p-4 border border-red-500/20 text-sm text-red-200">
      {{ summary }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  date: {
    type: String,
    default: 'Today'
  },
  meals: {
    type: Array,
    default: () => []
  },
  summary: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  planGenerated: {
    type: Boolean,
    default: false
  }
})
</script>
