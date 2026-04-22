<template>
  <div class="min-h-screen bg-slate-900 bg-[radial-gradient(circle_at_bottom_left,_var(--tw-gradient-stops))] from-slate-900 via-red-900/20 to-slate-900 p-6 flex items-center justify-center">
    <div class="w-full max-w-2xl bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">

      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold tracking-tight text-white">Welcome to Big Red Macro</h1>
        <p class="text-slate-400 mt-2">Let's personalize your dining experience in 3 quick steps.</p>
      </div>

      <!-- Step indicator -->
      <div class="flex items-center justify-center gap-3 mb-10">
        <div v-for="n in 3" :key="n" class="flex items-center gap-3">
          <div :class="[
            'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold transition-all',
            step === n ? 'bg-red-500 text-white shadow-lg shadow-red-500/40' :
            step > n  ? 'bg-red-800/60 text-red-300' : 'bg-white/10 text-slate-500'
          ]">{{ n }}</div>
          <div v-if="n < 3" :class="['h-px w-8 transition-all', step > n ? 'bg-red-600' : 'bg-white/10']"></div>
        </div>
      </div>

      <!-- Step 1: Body Metrics -->
      <div v-if="step === 1" class="space-y-6">
        <h2 class="text-lg font-semibold text-white">Body Metrics</h2>

        <!-- Height -->
        <div>
          <label class="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Height</label>
          <div class="flex gap-3">
            <div class="flex-1">
              <input v-model.number="form.heightFt" type="number" min="1" max="8" placeholder="ft"
                class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-red-500 transition-colors" />
              <span class="text-xs text-slate-500 mt-1 block">feet</span>
            </div>
            <div class="flex-1">
              <input v-model.number="form.heightIn" type="number" min="0" max="11" placeholder="in"
                class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-red-500 transition-colors" />
              <span class="text-xs text-slate-500 mt-1 block">inches</span>
            </div>
          </div>
        </div>

        <!-- Weight -->
        <div>
          <label class="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Weight</label>
          <div class="flex gap-3 items-start">
            <div class="flex-1">
              <input v-model.number="form.weightLbs" type="number" min="50" max="600" placeholder="lbs"
                class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-red-500 transition-colors" />
              <span class="text-xs text-slate-500 mt-1 block">pounds</span>
            </div>
            <div class="flex-1"></div>
          </div>
        </div>

        <!-- Age -->
        <div>
          <label class="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Age</label>
          <input v-model.number="form.age" type="number" min="14" max="100" placeholder="e.g. 20"
            class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-red-500 transition-colors" />
        </div>

        <!-- Sex -->
        <div>
          <label class="block text-xs text-slate-400 mb-2 uppercase tracking-wider">Sex (for BMR calculation)</label>
          <div class="flex gap-3">
            <button v-for="opt in sexOptions" :key="opt.value" type="button"
              @click="form.sex = opt.value"
              :class="[
                'flex-1 py-3 rounded-xl border text-sm font-medium transition-all',
                form.sex === opt.value
                  ? 'bg-red-600/20 border-red-500 text-white'
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
              ]">
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Step 2: Goals & Diet -->
      <div v-else-if="step === 2" class="space-y-6">
        <h2 class="text-lg font-semibold text-white">Goals & Dietary Needs</h2>

        <!-- Activity Level -->
        <div>
          <label class="block text-xs text-slate-400 mb-3 uppercase tracking-wider">Activity Level</label>
          <div class="grid grid-cols-2 gap-3">
            <button v-for="opt in activityOptions" :key="opt.value" type="button"
              @click="form.activity_level = opt.value"
              :class="[
                'p-3 rounded-xl border text-left transition-all',
                form.activity_level === opt.value
                  ? 'bg-red-600/20 border-red-500'
                  : 'bg-white/5 border-white/10 hover:bg-white/10'
              ]">
              <div class="text-sm font-medium text-white">{{ opt.label }}</div>
              <div class="text-xs text-slate-400 mt-0.5">{{ opt.desc }}</div>
            </button>
          </div>
        </div>

        <!-- Fitness Goal -->
        <div>
          <label class="block text-xs text-slate-400 mb-3 uppercase tracking-wider">Fitness Goal</label>
          <div class="grid grid-cols-3 gap-3">
            <button v-for="opt in goalOptions" :key="opt.value" type="button"
              @click="form.fitness_goal = opt.value"
              :class="[
                'p-3 rounded-xl border text-center transition-all',
                form.fitness_goal === opt.value
                  ? 'bg-red-600/20 border-red-500'
                  : 'bg-white/5 border-white/10 hover:bg-white/10'
              ]">
              <div class="text-xl mb-1">{{ opt.icon }}</div>
              <div class="text-sm font-medium text-white">{{ opt.label }}</div>
            </button>
          </div>
        </div>

        <!-- Dietary Restrictions -->
        <div>
          <label class="block text-xs text-slate-400 mb-3 uppercase tracking-wider">Dietary Restrictions</label>
          <div class="flex flex-wrap gap-2">
            <label v-for="opt in dietaryOptions" :key="opt.value"
              :class="[
                'cursor-pointer border rounded-full px-4 py-1.5 text-sm transition-all',
                form.dietary_restrictions.includes(opt.value)
                  ? 'bg-red-600/20 border-red-500 text-white'
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
              ]">
              <input type="checkbox" :value="opt.value" v-model="form.dietary_restrictions" class="hidden" />
              {{ opt.label }}
            </label>
          </div>
        </div>

        <!-- Allergens -->
        <div>
          <label class="block text-xs text-slate-400 mb-3 uppercase tracking-wider">Allergens to Avoid</label>
          <div class="flex flex-wrap gap-2">
            <label v-for="opt in allergenOptions" :key="opt"
              :class="[
                'cursor-pointer border rounded-full px-4 py-1.5 text-sm transition-all',
                form.allergens.includes(opt)
                  ? 'bg-red-600/20 border-red-500 text-white'
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
              ]">
              <input type="checkbox" :value="opt" v-model="form.allergens" class="hidden" />
              {{ opt }}
            </label>
          </div>
        </div>
      </div>

      <!-- Step 3: Review Macros -->
      <div v-else-if="step === 3" class="space-y-6">
        <div>
          <h2 class="text-lg font-semibold text-white">Your Recommended Macros</h2>
          <p class="text-xs text-slate-400 mt-1">Calculated from your body metrics and goals. Adjust as needed.</p>
        </div>

        <div class="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-1 text-sm">
          <div class="flex justify-between text-slate-400">
            <span>Estimated Daily Calories (TDEE)</span>
            <span class="text-white font-medium">{{ Math.round(tdee) }} kcal</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Goal adjustment ({{ form.fitness_goal }})</span>
            <span :class="form.fitness_goal === 'lose' ? 'text-red-400' : form.fitness_goal === 'gain' ? 'text-green-400' : 'text-white'">
              {{ form.fitness_goal === 'lose' ? '−500' : form.fitness_goal === 'gain' ? '+300' : '±0' }} kcal
            </span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Calories</label>
            <input v-model.number="form.macro_goals.calories" type="number"
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Protein (g)</label>
            <input v-model.number="form.macro_goals.protein_g" type="number"
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Carbs (g)</label>
            <input v-model.number="form.macro_goals.carbs_g" type="number"
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 transition-colors" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1 uppercase tracking-wider">Fat (g)</label>
            <input v-model.number="form.macro_goals.fat_g" type="number"
              class="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 transition-colors" />
          </div>
        </div>

        <div class="flex gap-2 text-xs text-slate-500 bg-white/5 rounded-xl p-3">
          <span>These macros will be used by the AI meal planner to pick the best dining hall items for you each day.</span>
        </div>
      </div>

      <!-- Error -->
      <p v-if="errorMsg" class="mt-4 text-red-400 text-sm text-center">{{ errorMsg }}</p>

      <!-- Navigation buttons -->
      <div class="flex gap-3 mt-8 pt-6 border-t border-white/10">
        <button v-if="step > 1" type="button" @click="step--"
          class="flex-1 rounded-xl bg-white/10 border border-white/10 px-6 py-3 text-sm font-medium text-white hover:bg-white/20 transition-all">
          Back
        </button>
        <button v-if="step < 3" type="button" @click="nextStep"
          class="flex-1 rounded-xl bg-gradient-to-r from-red-500 to-red-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transition-all">
          Next
        </button>
        <button v-else type="button" @click="saveProfile" :disabled="saving"
          class="flex-1 rounded-xl bg-gradient-to-r from-red-500 to-red-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transition-all disabled:opacity-50">
          {{ saving ? 'Setting up...' : 'Complete Setup' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { updateProfile } from '@/api'

const router = useRouter()
const step = ref(1)
const saving = ref(false)
const errorMsg = ref('')

const form = ref({
  heightFt: null,
  heightIn: 0,
  weightLbs: null,
  age: null,
  sex: 'male',
  activity_level: 'moderately_active',
  fitness_goal: 'maintain',
  dietary_restrictions: [],
  allergens: [],
  macro_goals: { calories: 2000, protein_g: 150, carbs_g: 200, fat_g: 65 }
})

const sexOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' }
]

const activityOptions = [
  { value: 'sedentary', label: 'Sedentary', desc: 'Mostly sitting, little exercise' },
  { value: 'lightly_active', label: 'Lightly Active', desc: 'Light exercise 1–3 days/week' },
  { value: 'moderately_active', label: 'Moderately Active', desc: 'Moderate exercise 3–5 days/week' },
  { value: 'very_active', label: 'Very Active', desc: 'Hard exercise 6–7 days/week' }
]

const goalOptions = [
  { value: 'lose', label: 'Lose Weight', icon: '🔥' },
  { value: 'maintain', label: 'Maintain', icon: '⚖️' },
  { value: 'gain', label: 'Gain Muscle', icon: '💪' }
]

const dietaryOptions = [
  { value: 'vegan', label: 'Vegan' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'halal', label: 'Halal' },
  { value: 'gluten_free', label: 'Gluten Free' }
]

const allergenOptions = ['Nuts', 'Dairy', 'Soy', 'Eggs', 'Shellfish', 'Wheat']

const activityMultipliers = {
  sedentary: 1.2,
  lightly_active: 1.375,
  moderately_active: 1.55,
  very_active: 1.725
}

const heightCm = computed(() => {
  const ft = form.value.heightFt || 0
  const inches = form.value.heightIn || 0
  return ft * 30.48 + inches * 2.54
})

const weightKg = computed(() => {
  return (form.value.weightLbs || 0) * 0.453592
})

const bmr = computed(() => {
  const h = heightCm.value
  const w = weightKg.value
  const a = form.value.age || 20
  if (form.value.sex === 'female') {
    return 10 * w + 6.25 * h - 5 * a - 161
  }
  return 10 * w + 6.25 * h - 5 * a + 5
})

const tdee = computed(() => {
  const mult = activityMultipliers[form.value.activity_level] || 1.55
  return bmr.value * mult
})

const recommendedCalories = computed(() => {
  if (form.value.fitness_goal === 'lose') return tdee.value - 500
  if (form.value.fitness_goal === 'gain') return tdee.value + 300
  return tdee.value
})

// Auto-fill macros when entering step 3
watch(step, (newStep) => {
  if (newStep === 3 && heightCm.value > 0 && weightKg.value > 0) {
    const cals = Math.round(recommendedCalories.value)
    const proteinPerLb = form.value.fitness_goal === 'lose' ? 1.0 : form.value.fitness_goal === 'gain' ? 1.2 : 0.8
    const protein = Math.round((form.value.weightLbs || 150) * proteinPerLb)
    const fat = Math.round(cals * 0.25 / 9)
    const carbs = Math.round((cals - protein * 4 - fat * 9) / 4)
    form.value.macro_goals = { calories: cals, protein_g: protein, carbs_g: carbs, fat_g: fat }
  }
})

function nextStep() {
  errorMsg.value = ''
  if (step.value === 1) {
    if (!form.value.heightFt || !form.value.weightLbs || !form.value.age) {
      errorMsg.value = 'Please fill in all body metric fields.'
      return
    }
  }
  step.value++
}

async function saveProfile() {
  saving.value = true
  errorMsg.value = ''
  try {
    await updateProfile({
      height_cm: heightCm.value,
      weight_kg: weightKg.value,
      age: form.value.age,
      sex: form.value.sex,
      activity_level: form.value.activity_level,
      fitness_goal: form.value.fitness_goal,
      dietary_restrictions: form.value.dietary_restrictions,
      allergens: form.value.allergens,
      macro_goals: {
        ...form.value.macro_goals,
        fiber_g: 0,
        sodium_mg: 0
      },
      onboarding_complete: true
    })
    router.push('/')
  } catch (e) {
    console.error(e)
    errorMsg.value = 'Failed to save profile. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>
