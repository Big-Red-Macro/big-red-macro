<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">My Profile</h1>

    <form @submit.prevent="save" class="space-y-5">
      <!-- Macro Goals -->
      <div class="card space-y-3">
        <h2 class="font-semibold">Daily Macro Goals</h2>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium mb-1">Calories (kcal)</label>
            <input v-model.number="form.macro_goals.calories" type="number" class="input" min="0" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Protein (g)</label>
            <input v-model.number="form.macro_goals.protein_g" type="number" class="input" min="0" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Carbs (g)</label>
            <input v-model.number="form.macro_goals.carbs_g" type="number" class="input" min="0" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Fat (g)</label>
            <input v-model.number="form.macro_goals.fat_g" type="number" class="input" min="0" />
          </div>
        </div>
      </div>

      <!-- Meal Plan Type -->
      <div class="card">
        <h2 class="font-semibold mb-2">Meal Plan</h2>
        <select v-model="form.meal_plan_type" class="input">
          <option value="traditional">Traditional</option>
          <option value="west_campus">West Campus House</option>
          <option value="bear_necessities">Bear Necessities</option>
          <option value="none">No Meal Plan</option>
        </select>
      </div>

      <!-- Dietary Restrictions -->
      <div class="card">
        <h2 class="font-semibold mb-3">Dietary Restrictions</h2>
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="opt in dietaryOptions"
            :key="opt.value"
            class="flex items-center gap-2 cursor-pointer"
          >
            <input
              type="checkbox"
              :value="opt.value"
              v-model="form.dietary_restrictions"
              class="accent-cornell-red"
            />
            <span class="text-sm">{{ opt.label }}</span>
          </label>
        </div>
      </div>

      <!-- Allergens -->
      <div class="card">
        <h2 class="font-semibold mb-3">Allergens to Exclude</h2>
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="allergen in allergenOptions"
            :key="allergen.value"
            class="flex items-center gap-2 cursor-pointer"
          >
            <input
              type="checkbox"
              :value="allergen.value"
              v-model="form.allergens"
              class="accent-cornell-red"
            />
            <span class="text-sm">{{ allergen.label }}</span>
          </label>
        </div>
      </div>



      <p v-if="successMsg" class="text-green-600 text-sm">{{ successMsg }}</p>
      <p v-if="errorMsg" class="text-red-600 text-sm">{{ errorMsg }}</p>

      <button type="submit" class="btn-primary w-full" :disabled="saving">
        {{ saving ? 'Saving…' : 'Save Profile' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProfile, updateProfile } from '@/api'

import { useMainStore } from '@/stores/mainStore'

const mainStore = useMainStore()

const form = ref({
  macro_goals: { calories: 2000, protein_g: 150, carbs_g: 200, fat_g: 65 },
  meal_plan_type: 'traditional',
  dietary_restrictions: [],
  allergens: [],
})

const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const dietaryOptions = [
  { value: 'vegan', label: 'Vegan' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'halal', label: 'Halal' },
  { value: 'gluten_free', label: 'Gluten Free' },
]

const allergenOptions = [
  { value: 'peanuts', label: 'Peanuts' },
  { value: 'tree_nuts', label: 'Tree Nuts' },
  { value: 'dairy', label: 'Dairy' },
  { value: 'eggs', label: 'Eggs' },
  { value: 'shellfish', label: 'Shellfish' },
  { value: 'soy', label: 'Soy' },
  { value: 'wheat', label: 'Wheat' },
]

async function save() {
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await updateProfile(form.value)
    successMsg.value = 'Profile saved!'
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Failed to save profile.'
  } finally {
    saving.value = false
  }
}



onMounted(async () => {
  try {
    const { data } = await getProfile()
    form.value = {
      macro_goals: data.macro_goals || form.value.macro_goals,
      meal_plan_type: data.meal_plan_type || 'traditional',
      dietary_restrictions: data.dietary_restrictions || [],
      allergens: data.allergens || [],
    }
  } catch {
    // Profile not yet created — use defaults
  }
})
</script>
