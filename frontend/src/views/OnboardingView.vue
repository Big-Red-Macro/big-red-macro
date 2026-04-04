<template>
  <div class="min-h-screen bg-slate-900 bg-[radial-gradient(circle_at_bottom_left,_var(--tw-gradient-stops))] from-slate-900 via-red-900/20 to-slate-900 p-6 flex items-center justify-center">
    <div class="w-full max-w-2xl bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold tracking-tight text-white">Welcome to Big Red Macro AI</h1>
        <p class="text-slate-400 mt-2">Let's set up your profile so we can personalize your dining experience.</p>
      </div>

      <form @submit.prevent="saveProfile" class="space-y-8">
        <!-- Macros -->
        <div class="space-y-4">
          <h2 class="text-lg font-semibold text-white flex items-center gap-2">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-red-500/20 text-xs text-red-400">1</span>
            Initial Macro Goals
          </h2>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Calories</label>
              <input v-model.number="form.macro_goals.calories" type="number" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-red-500 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Protein (g)</label>
              <input v-model.number="form.macro_goals.protein_g" type="number" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-red-500 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Carbs (g)</label>
              <input v-model.number="form.macro_goals.carbs_g" type="number" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-red-500 transition-colors" />
            </div>
            <div>
              <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Fat (g)</label>
              <input v-model.number="form.macro_goals.fat_g" type="number" class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-red-500 transition-colors" />
            </div>
          </div>
        </div>

        <!-- Dietary Needs -->
        <div class="space-y-4">
          <h2 class="text-lg font-semibold text-white flex items-center gap-2">
            <span class="flex h-6 w-6 items-center justify-center rounded-full bg-red-500/20 text-xs text-red-400">2</span>
            Dietary Preferences
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <label v-for="opt in dietaryOptions" :key="opt.value" 
                   :class="['cursor-pointer border rounded-xl p-3 text-center transition-all', form.dietary_restrictions.includes(opt.value) ? 'bg-red-600/20 border-red-500 text-white' : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10']">
              <input type="checkbox" :value="opt.value" v-model="form.dietary_restrictions" class="hidden" />
              <span class="text-sm font-medium">{{ opt.label }}</span>
            </label>
          </div>
        </div>

        <div class="pt-6 border-t border-white/10">
          <p v-if="errorMsg" class="text-red-400 text-sm mb-4 text-center">{{ errorMsg }}</p>
          <button type="submit" :disabled="saving" class="w-full rounded-xl bg-gradient-to-r from-red-500 to-red-600 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transition-all disabled:opacity-50">
            {{ saving ? 'Creating Profile...' : 'Complete Setup' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { updateProfile } from '@/api'

const router = useRouter()

const form = ref({
  macro_goals: { calories: 2000, protein_g: 150, carbs_g: 200, fat_g: 65 },
  dietary_restrictions: [],
  allergens: [],
  meal_plan_type: 'traditional'
})

const dietaryOptions = [
  { value: 'vegan', label: 'Vegan' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'halal', label: 'Halal' },
  { value: 'gluten_free', label: 'Gluten Free' }
]

const saving = ref(false)
const errorMsg = ref('')

async function saveProfile() {
  saving.value = true
  errorMsg.value = ''
  try {
    await updateProfile(form.value)
    router.push('/')
  } catch (e) {
    console.error(e)
    errorMsg.value = 'Failed to setup profile. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>
