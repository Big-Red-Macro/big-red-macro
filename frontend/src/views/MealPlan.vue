<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Meal Plan</h1>
      <input type="date" v-model="selectedDate" class="input w-auto text-sm" />
    </div>

    <button
      @click="generate"
      class="btn-primary w-full"
      :disabled="mealPlan.loading"
    >
      {{ mealPlan.loading ? 'Generating…' : `Generate Plan for ${selectedDate}` }}
    </button>

    <p v-if="mealPlan.error" class="text-red-600 text-sm">{{ mealPlan.error }}</p>

    <div v-if="mealPlan.todaysPlan" class="space-y-4">
      <!-- Macro summary -->
      <div class="card">
        <h2 class="font-semibold mb-3">Daily Summary</h2>
        <div class="grid grid-cols-4 gap-2 text-center text-sm">
          <div v-for="macro in macroRows" :key="macro.label">
            <p class="font-bold text-base">{{ macro.actual }}</p>
            <p class="text-cornell-gray text-xs">/ {{ macro.goal }} {{ macro.unit }}</p>
            <p class="text-xs mt-0.5 font-medium" :class="macro.color">{{ macro.label }}</p>
          </div>
        </div>
      </div>

      <!-- Meal cards -->
      <MealCard
        v-for="meal in mealPlan.todaysPlan.meals"
        :key="meal.period"
        :meal="meal"
      />
    </div>

    <!-- History -->
    <div v-if="mealPlan.history.length">
      <h2 class="font-semibold mb-3">Recent Plans</h2>
      <div class="space-y-2">
        <div
          v-for="plan in mealPlan.history"
          :key="plan.id"
          class="card flex items-center justify-between cursor-pointer hover:bg-gray-50"
          @click="mealPlan.todaysPlan = plan"
        >
          <span class="font-medium">{{ plan.date }}</span>
          <span class="text-sm text-cornell-gray">
            {{ Math.round(plan.total_macros.calories) }} kcal ·
            {{ Math.round(plan.total_macros.protein_g) }}g protein
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGeolocation } from '@vueuse/core'
import { useMealPlanStore } from '@/stores/mealPlan'
import MealCard from '@/components/MealCard.vue'

const mealPlan = useMealPlanStore()
const { coords } = useGeolocation()

const selectedDate = ref(new Date().toISOString().slice(0, 10))

async function generate() {
  const location = coords.value?.latitude
    ? { lat: coords.value.latitude, lng: coords.value.longitude }
    : null
  await mealPlan.generate(selectedDate.value, location)
}

const macroRows = computed(() => {
  if (!mealPlan.todaysPlan) return []
  const { total_macros: t, goal_macros: g } = mealPlan.todaysPlan
  return [
    { label: 'Calories', actual: Math.round(t.calories), goal: Math.round(g.calories), unit: 'kcal', color: 'text-cornell-red' },
    { label: 'Protein', actual: Math.round(t.protein_g), goal: Math.round(g.protein_g), unit: 'g', color: 'text-blue-600' },
    { label: 'Carbs', actual: Math.round(t.carbs_g), goal: Math.round(g.carbs_g), unit: 'g', color: 'text-yellow-600' },
    { label: 'Fat', actual: Math.round(t.fat_g), goal: Math.round(g.fat_g), unit: 'g', color: 'text-green-600' },
  ]
})

onMounted(() => mealPlan.loadHistory())
</script>
