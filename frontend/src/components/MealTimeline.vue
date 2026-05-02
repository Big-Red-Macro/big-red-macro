<template>
  <div class="rounded-2xl border border-white/10 bg-[#111827] p-6 shadow-2xl shadow-black/20">

    <div class="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight">Daily Meal Itinerary</h2>
        <p class="text-xs text-slate-400 mt-1">{{ date || 'Today' }}</p>
      </div>
      <div v-if="meals.length" class="text-xs font-semibold text-emerald-300">
        {{ meals.length }} optimized stops
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="isLoading" class="relative pl-4 border-l border-slate-200 dark:border-slate-700 ml-4 py-2 space-y-6 animate-pulse">
      <div v-for="n in 3" :key="n" class="ml-6 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/50 p-4">
        <div class="h-3 w-20 rounded bg-slate-200 dark:bg-slate-600 mb-3"></div>
        <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-600 mb-2"></div>
        <div class="h-4 w-1/2 rounded bg-slate-200 dark:bg-slate-600 mb-4"></div>
        <div class="h-3 w-full rounded bg-slate-100 dark:bg-slate-700"></div>
      </div>
    </div>

    <!-- Timeline -->
    <div v-else-if="meals.length > 0" class="relative pl-4 border-l border-white/10 ml-4 py-2 space-y-8">
      <div v-for="(meal, index) in meals" :key="mealKey(meal, index)" class="relative group">
        <div class="absolute -left-[21px] top-4 h-2.5 w-2.5 rounded-full border-2 border-[#111827] bg-red-500"></div>
        <div class="absolute -left-12 top-2 text-xs font-semibold text-slate-400 w-8 text-right">
          {{ meal.meal_time?.split(' ')[0] }}
        </div>

        <div class="ml-6 rounded-xl border border-white/10 bg-white/[0.04] p-5 transition-colors hover:bg-white/[0.07]">
          <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-widest text-red-300">{{ meal.meal_period || meal.meal_time }}</p>
              <h4 class="mt-1 text-lg font-bold text-white">{{ meal.dining_hall_name }}</h4>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <label
                class="flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-bold transition"
                :class="mealEntry(meal, index).checked ? 'border-emerald-400/40 bg-emerald-500/15 text-emerald-200' : 'border-white/10 bg-slate-950/40 text-slate-300 hover:border-white/20'"
              >
                <input
                  type="checkbox"
                  class="h-4 w-4 accent-emerald-500"
                  :checked="mealEntry(meal, index).checked"
                  @change="setEaten(meal, index, $event.target.checked)"
                />
                Eaten
              </label>
              <span class="w-fit rounded-lg bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-200">
                {{ meal.meal_time }}
              </span>
            </div>
          </div>

          <ul class="grid gap-2 text-sm text-slate-100 sm:grid-cols-2">
            <li v-for="item in meal.suggested_items" :key="item" class="flex items-start gap-1.5">
              <span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400"></span>
              <span>{{ item }}</span>
            </li>
          </ul>

          <div class="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <div class="rounded-lg bg-slate-950/50 px-3 py-2">
              <p class="text-[11px] font-semibold uppercase text-slate-500">Calories</p>
              <input
                :value="mealEntry(meal, index).macros.calories"
                @change="updateMacro(meal, index, 'calories', $event.target.value)"
                type="number"
                min="0"
                class="mt-1 w-full rounded-md border border-white/10 bg-transparent px-2 py-1 text-sm font-bold text-white outline-none focus:border-red-300"
              />
            </div>
            <div class="rounded-lg bg-slate-950/50 px-3 py-2">
              <p class="text-[11px] font-semibold uppercase text-slate-500">Protein</p>
              <input
                :value="mealEntry(meal, index).macros.protein_g"
                @change="updateMacro(meal, index, 'protein_g', $event.target.value)"
                type="number"
                min="0"
                class="mt-1 w-full rounded-md border border-white/10 bg-transparent px-2 py-1 text-sm font-bold text-white outline-none focus:border-red-300"
              />
            </div>
            <div class="rounded-lg bg-slate-950/50 px-3 py-2">
              <p class="text-[11px] font-semibold uppercase text-slate-500">Carbs</p>
              <input
                :value="mealEntry(meal, index).macros.carbs_g"
                @change="updateMacro(meal, index, 'carbs_g', $event.target.value)"
                type="number"
                min="0"
                class="mt-1 w-full rounded-md border border-white/10 bg-transparent px-2 py-1 text-sm font-bold text-white outline-none focus:border-red-300"
              />
            </div>
            <div class="rounded-lg bg-slate-950/50 px-3 py-2">
              <p class="text-[11px] font-semibold uppercase text-slate-500">Fat</p>
              <input
                :value="mealEntry(meal, index).macros.fat_g"
                @change="updateMacro(meal, index, 'fat_g', $event.target.value)"
                type="number"
                min="0"
                class="mt-1 w-full rounded-md border border-white/10 bg-transparent px-2 py-1 text-sm font-bold text-white outline-none focus:border-red-300"
              />
            </div>
          </div>

          <p class="mt-4 text-sm leading-relaxed text-slate-400">{{ meal.reasoning }}</p>
        </div>
      </div>
    </div>

    <!-- Empty: generated but no meals -->
    <div v-else-if="planGenerated" class="py-10 flex flex-col items-center gap-2 text-slate-400 dark:text-slate-500">
      <svg class="h-8 w-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm">No dining stops were returned. Generate again to rebuild the itinerary.</p>
    </div>

    <!-- Empty: not yet generated -->
    <div v-else class="py-10 flex flex-col items-center gap-2 text-slate-400 dark:text-slate-500">
      <svg class="h-8 w-8 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-sm">Hit "Generate New Plan" to get started.</p>
    </div>

    <div v-if="summary" class="mt-6 rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-200">
      {{ summary }}
    </div>
  </div>
</template>

<script setup>
import { useNutritionStore } from '@/stores/nutrition'

const nutrition = useNutritionStore()

const props = defineProps({
  date: { type: String, default: '' },
  meals: { type: Array, default: () => [] },
  summary: { type: String, default: '' },
  isLoading: { type: Boolean, default: false },
  planGenerated: { type: Boolean, default: false }
})

function activeDate() {
  return props.date || new Date().toISOString().slice(0, 10)
}

function mealKey(meal, index) {
  return nutrition.mealKey(meal, index)
}

function mealEntry(meal, index) {
  return nutrition.getMealEntry(activeDate(), mealKey(meal, index), meal)
}

function setEaten(meal, index, checked) {
  nutrition.setMealChecked(activeDate(), mealKey(meal, index), meal, checked)
}

function updateMacro(meal, index, field, value) {
  const entry = mealEntry(meal, index)
  nutrition.updateMealMacros(activeDate(), mealKey(meal, index), meal, {
    ...entry.macros,
    [field]: Number(value) || 0,
  })
}
</script>
