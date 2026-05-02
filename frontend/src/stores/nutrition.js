import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getNutritionLog, updateNutritionLog } from '@/api'

const emptyMacros = () => ({ calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 })
const STORAGE_KEY = 'brm_nutrition_log_v2'

function todayKey() {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function cleanMacros(macros = {}) {
  return {
    calories: Number(macros.calories) || 0,
    protein_g: Number(macros.protein_g) || 0,
    carbs_g: Number(macros.carbs_g) || 0,
    fat_g: Number(macros.fat_g) || 0,
  }
}

function addMacros(a, b) {
  return {
    calories: a.calories + b.calories,
    protein_g: a.protein_g + b.protein_g,
    carbs_g: a.carbs_g + b.carbs_g,
    fat_g: a.fat_g + b.fat_g,
  }
}

function roundMacros(macros) {
  return {
    calories: Math.round(macros.calories),
    protein_g: Math.round(macros.protein_g),
    carbs_g: Math.round(macros.carbs_g),
    fat_g: Math.round(macros.fat_g),
  }
}

function loadState() {
  localStorage.removeItem('brm_nutrition_log_v1')
  return {}
}

export const useNutritionStore = defineStore('nutrition', () => {
  const byDate = ref(loadState())
  const activeDate = ref(todayKey())
  const loading = ref(false)
  const error = ref(null)

  const activeDay = computed(() => getDay(activeDate.value))
  const eatenMeals = computed(() =>
    Object.values(activeDay.value.meals).filter((meal) => meal.checked)
  )
  const consumedMacros = computed(() => {
    const mealsTotal = eatenMeals.value.reduce(
      (total, meal) => addMacros(total, cleanMacros(meal.macros)),
      emptyMacros()
    )
    return roundMacros(addMacros(mealsTotal, activeDay.value.manual))
  })

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(byDate.value))
  }

  async function syncDay(date = activeDate.value) {
    const day = getDay(date)
    try {
      await updateNutritionLog({
        date,
        meals: day.meals,
        manual: day.manual,
      })
    } catch (e) {
      console.error(e)
      error.value = 'Failed to save nutrition log.'
    }
  }

  async function loadDay(date = activeDate.value) {
    loading.value = true
    error.value = null
    try {
      const { data } = await getNutritionLog(date)
      byDate.value[date] = {
        meals: data.meals || {},
        manual: cleanMacros(data.manual),
      }
      persist()
      return byDate.value[date]
    } catch (e) {
      console.error(e)
      error.value = 'Failed to load nutrition log.'
      return getDay(date)
    } finally {
      loading.value = false
    }
  }

  function getDay(date = activeDate.value) {
    if (!byDate.value[date]) {
      byDate.value[date] = { meals: {}, manual: emptyMacros() }
      persist()
    }
    return byDate.value[date]
  }

  async function setActiveDate(date) {
    activeDate.value = date || todayKey()
    getDay(activeDate.value)
    await loadDay(activeDate.value)
  }

  function mealKey(meal, index = 0) {
    return [
      index,
      meal.meal_period || 'meal',
      meal.meal_time || index,
      meal.dining_hall_name || 'dining',
      (meal.suggested_items || []).join(','),
    ].join('|')
  }

  function getMealEntry(date, key, meal) {
    const day = getDay(date)
    if (!day.meals[key]) {
      day.meals[key] = {
        checked: false,
        title: meal.meal_period || meal.meal_time || 'Meal',
        dining_hall_name: meal.dining_hall_name || '',
        macros: cleanMacros(meal.estimated_macros),
      }
      persist()
    }
    return day.meals[key]
  }

  async function setMealChecked(date, key, meal, checked) {
    const entry = getMealEntry(date, key, meal)
    entry.checked = checked
    entry.title = meal.meal_period || meal.meal_time || 'Meal'
    entry.dining_hall_name = meal.dining_hall_name || ''
    persist()
    await syncDay(date)
  }

  async function updateMealMacros(date, key, meal, macros) {
    const entry = getMealEntry(date, key, meal)
    entry.macros = cleanMacros(macros)
    persist()
    await syncDay(date)
  }

  async function setManualMacros(date, macros) {
    getDay(date).manual = cleanMacros(macros)
    persist()
    await syncDay(date)
  }

  async function clearDay(date = activeDate.value) {
    byDate.value[date] = { meals: {}, manual: emptyMacros() }
    persist()
    await syncDay(date)
  }

  return {
    byDate,
    activeDate,
    loading,
    error,
    activeDay,
    eatenMeals,
    consumedMacros,
    loadDay,
    setActiveDate,
    mealKey,
    getMealEntry,
    setMealChecked,
    updateMealMacros,
    setManualMacros,
    clearDay,
  }
})
