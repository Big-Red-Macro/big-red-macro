<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold">Good {{ greeting }}, Bear</h1>
      <p class="text-cornell-gray text-sm">{{ today }}</p>
    </div>

    <!-- Macro rings -->
    <div class="card" v-if="mealPlan.todaysPlan">
      <h2 class="font-semibold mb-4">Today's Macro Progress</h2>
      <div class="flex justify-around">
        <MacroRing
          label="Calories"
          :actual="Math.round(mealPlan.todaysPlan.total_macros.calories)"
          :goal="Math.round(mealPlan.todaysPlan.goal_macros.calories)"
          unit=" kcal"
          color="#B31B1B"
          :size="80"
        />
        <MacroRing
          label="Protein"
          :actual="Math.round(mealPlan.todaysPlan.total_macros.protein_g)"
          :goal="Math.round(mealPlan.todaysPlan.goal_macros.protein_g)"
          color="#2563EB"
        />
        <MacroRing
          label="Carbs"
          :actual="Math.round(mealPlan.todaysPlan.total_macros.carbs_g)"
          :goal="Math.round(mealPlan.todaysPlan.goal_macros.carbs_g)"
          color="#D97706"
        />
        <MacroRing
          label="Fat"
          :actual="Math.round(mealPlan.todaysPlan.total_macros.fat_g)"
          :goal="Math.round(mealPlan.todaysPlan.goal_macros.fat_g)"
          color="#059669"
        />
      </div>
    </div>

    <!-- No plan yet -->
    <div v-else class="card text-center py-8">
      <p class="text-cornell-gray mb-4">No meal plan generated yet for today.</p>
      <button @click="generate" class="btn-primary" :disabled="mealPlan.loading">
        {{ mealPlan.loading ? 'Generating…' : 'Generate My Meal Plan' }}
      </button>
      <p v-if="mealPlan.error" class="text-red-600 text-sm mt-2">{{ mealPlan.error }}</p>
    </div>

    <!-- Today's meals -->
    <div v-if="mealPlan.todaysPlan" class="space-y-3">
      <h2 class="font-semibold">Today's Itinerary</h2>
      <MealCard
        v-for="meal in mealPlan.todaysPlan.meals"
        :key="meal.period"
        :meal="meal"
      />
    </div>

    <!-- Quick wait times -->
    <div v-if="dining.halls.length">
      <h2 class="font-semibold mb-3">Current Wait Times</h2>
      <div class="space-y-2">
        <DiningHallCard
          v-for="hall in dining.halls.slice(0, 4)"
          :key="hall.id"
          :hall="hall"
          :waitMinutes="dining.waitForHall(hall.id)"
        />
      </div>
      <RouterLink to="/dining" class="text-sm text-cornell-red font-medium mt-2 inline-block">
        See all dining halls →
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useGeolocation } from '@vueuse/core'
import { useMealPlanStore } from '@/stores/mealPlan'
import { useDiningStore } from '@/stores/dining'
import MacroRing from '@/components/MacroRing.vue'
import MealCard from '@/components/MealCard.vue'
import DiningHallCard from '@/components/DiningHallCard.vue'

const mealPlan = useMealPlanStore()
const dining = useDiningStore()
const { coords } = useGeolocation()

const today = new Date().toLocaleDateString('en-US', {
  weekday: 'long', month: 'long', day: 'numeric'
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
})

async function generate() {
  const location = coords.value?.latitude
    ? { lat: coords.value.latitude, lng: coords.value.longitude }
    : null
  await mealPlan.generate(null, location)
}

onMounted(async () => {
  await dining.fetchHalls()
  await dining.fetchWaitTimes()
})
</script>
