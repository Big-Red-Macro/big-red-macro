import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateMealPlan, getMealPlanHistory } from '@/api'

export const useMealPlanStore = defineStore('mealPlan', () => {
  const todaysPlan = ref(null)
  const history = ref([])
  const loading = ref(false)
  const error = ref(null)

  const macroProgress = computed(() => {
    if (!todaysPlan.value) return null
    const { total_macros, goal_macros } = todaysPlan.value
    return {
      calories: pct(total_macros.calories, goal_macros.calories),
      protein: pct(total_macros.protein_g, goal_macros.protein_g),
      carbs: pct(total_macros.carbs_g, goal_macros.carbs_g),
      fat: pct(total_macros.fat_g, goal_macros.fat_g),
    }
  })

  function pct(actual, goal) {
    if (!goal) return 0
    return Math.min(Math.round((actual / goal) * 100), 100)
  }

  async function generate(date, location) {
    loading.value = true
    error.value = null
    try {
      const today = date || new Date().toISOString().slice(0, 10)
      const { data } = await generateMealPlan(today, location)
      todaysPlan.value = data
      return data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to generate meal plan.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadHistory() {
    const { data } = await getMealPlanHistory()
    history.value = data
  }

  return { todaysPlan, history, loading, error, macroProgress, generate, loadHistory }
})
