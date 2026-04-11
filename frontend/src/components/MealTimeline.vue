<template>
  <div class="rounded-2xl border border-slate-700 bg-slate-800 p-6">

    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-base font-bold text-white tracking-tight">Daily Meal Itinerary</h2>
        <p class="text-xs text-slate-500 mt-0.5">{{ date || 'Today' }}</p>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="isLoading" class="relative pl-4 border-l border-slate-700 ml-4 py-2 space-y-6 animate-pulse">
      <div v-for="n in 3" :key="n" class="ml-6 rounded-xl border border-slate-700 bg-slate-700/50 p-4">
        <div class="h-3 w-20 rounded bg-slate-600 mb-3"></div>
        <div class="h-4 w-3/4 rounded bg-slate-600 mb-2"></div>
        <div class="h-4 w-1/2 rounded bg-slate-600 mb-4"></div>
        <div class="h-3 w-full rounded bg-slate-700"></div>
      </div>
    </div>

    <!-- Timeline -->
    <div v-else-if="meals.length > 0" class="relative pl-4 border-l border-slate-700 ml-4 py-2 space-y-8">
      <div v-for="(meal, index) in meals" :key="index" class="relative group">
        <div class="absolute -left-[21px] top-4 h-2.5 w-2.5 rounded-full border-2 border-slate-900 bg-red-500"></div>
        <div class="absolute -left-10 top-3 text-xs font-semibold text-slate-500 w-6 text-right">
          {{ meal.meal_time?.split(' ')[0] }}
        </div>

        <div class="ml-6 rounded-xl border border-slate-700 bg-slate-700/30 p-4 hover:bg-slate-700/50 transition-colors">
          <h4 class="text-xs font-bold tracking-widest text-red-400 uppercase mb-2">{{ meal.dining_hall_name }}</h4>
          <ul class="text-sm text-slate-200 space-y-0.5">
            <li v-for="item in meal.suggested_items" :key="item" class="flex items-start gap-1.5">
              <span class="text-slate-600 mt-0.5">–</span>{{ item }}
            </li>
          </ul>
          <div class="flex justify-between items-end mt-3">
            <p class="text-xs text-slate-500 w-3/4 pr-4">{{ meal.reasoning }}</p>
            <span class="rounded-lg bg-slate-900 px-2 py-1 text-xs font-semibold text-red-400">
              {{ meal.estimated_macros?.calories || '---' }} kcal
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty: generated but no meals -->
    <div v-else-if="planGenerated" class="py-10 flex flex-col items-center gap-2 text-slate-500">
      <svg class="h-8 w-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm">No meals scheduled — try generating a new plan.</p>
    </div>

    <!-- Empty: not yet generated -->
    <div v-else class="py-10 flex flex-col items-center gap-2 text-slate-500">
      <svg class="h-8 w-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm">Hit "Generate New Plan" to get started.</p>
    </div>

    <div v-if="summary" class="mt-6 rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-300">
      {{ summary }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  date: { type: String, default: '' },
  meals: { type: Array, default: () => [] },
  summary: { type: String, default: '' },
  isLoading: { type: Boolean, default: false },
  planGenerated: { type: Boolean, default: false }
})
</script>
