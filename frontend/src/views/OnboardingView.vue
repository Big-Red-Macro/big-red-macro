<template>
  <div class="min-h-screen bg-[#0f172a] flex flex-col items-center justify-start pt-12 pb-16 px-4">

    <!-- Step Indicator -->
    <div class="flex items-center gap-0 mb-10">
      <div v-for="n in 3" :key="n" class="flex items-center">
        <div :class="[
          'h-10 w-10 rounded-full flex items-center justify-center text-sm font-bold transition-all',
          step > n  ? 'bg-[#B31B1B] text-white' :
          step === n ? 'bg-[#B31B1B] text-white' :
                       'bg-[#1e293b] text-slate-500 border border-slate-700'
        ]">
          <svg v-if="step > n" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
          <span v-else>{{ n }}</span>
        </div>
        <div v-if="n < 3" :class="['w-20 h-px transition-all', step > n ? 'bg-[#B31B1B]' : 'bg-slate-700']"></div>
      </div>
    </div>

    <!-- Step 1: Body Metrics -->
    <div v-if="step === 1" class="w-full max-w-xl">
      <div class="rounded-2xl bg-[#141e30] p-8">
        <h2 class="text-2xl font-bold text-white mb-1">Tell us about yourself</h2>
        <p class="text-slate-400 text-sm mb-8">We'll use this to calculate your personalized nutrition targets</p>

        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-white mb-2">Height (ft)</label>
            <input v-model.number="form.heightFt" type="number" min="1" max="8" placeholder="5"
              class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-[#B31B1B] text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-white mb-2">Inches</label>
            <input v-model.number="form.heightIn" type="number" min="0" max="11" placeholder="10"
              class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-[#B31B1B] text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-white mb-2">Weight (lbs)</label>
            <input v-model.number="form.weightLbs" type="number" min="50" max="600" placeholder="155"
              class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-[#B31B1B] text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-white mb-2">Age</label>
            <input v-model.number="form.age" type="number" min="14" max="100" placeholder="20"
              class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-[#B31B1B] text-sm" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-white mb-3">Sex</label>
          <div class="flex rounded-xl overflow-hidden border border-slate-700 w-fit">
            <button type="button" @click="form.sex = 'male'"
              :class="['px-8 py-2.5 text-sm font-medium transition-all', form.sex === 'male' ? 'bg-[#B31B1B] text-white' : 'bg-[#1e293b] text-slate-400 hover:text-white']">
              Male
            </button>
            <button type="button" @click="form.sex = 'female'"
              :class="['px-8 py-2.5 text-sm font-medium transition-all', form.sex === 'female' ? 'bg-[#B31B1B] text-white' : 'bg-[#1e293b] text-slate-400 hover:text-white']">
              Female
            </button>
          </div>
        </div>
      </div>

      <p v-if="errorMsg" class="mt-3 text-red-400 text-sm text-center">{{ errorMsg }}</p>
      <div class="flex justify-end mt-4">
        <button @click="nextStep" class="px-8 py-3 rounded-xl bg-[#B31B1B] text-white text-sm font-semibold hover:bg-[#a01818] transition-colors shadow-lg shadow-[#B31B1B]/30">
          Next
        </button>
      </div>
    </div>

    <!-- Step 2: Activity & Goals -->
    <div v-else-if="step === 2" class="w-full max-w-xl">
      <div class="rounded-2xl bg-[#141e30] p-8">
        <h2 class="text-2xl font-bold text-white mb-1">Activity &amp; Goals</h2>
        <p class="text-slate-400 text-sm mb-8">Help us personalize your nutrition plan</p>

        <!-- Activity Level -->
        <div class="mb-6">
          <label class="block text-sm font-semibold text-white mb-3">Activity Level</label>
          <div class="grid grid-cols-2 gap-3">
            <button v-for="opt in activityOptions" :key="opt.value" type="button"
              @click="form.activity_level = opt.value"
              :class="[
                'p-4 rounded-xl border text-left transition-all',
                form.activity_level === opt.value
                  ? 'border-[#B31B1B] bg-[#B31B1B]/15'
                  : 'border-slate-700 bg-[#1e293b] hover:border-slate-600'
              ]">
              <div class="text-2xl mb-2">{{ opt.icon }}</div>
              <div class="text-sm font-semibold text-white">{{ opt.label }}</div>
              <div class="text-xs text-slate-400 mt-0.5">{{ opt.desc }}</div>
            </button>
          </div>
        </div>

        <!-- Fitness Goal -->
        <div class="mb-6">
          <label class="block text-sm font-semibold text-white mb-3">Fitness Goal</label>
          <div class="grid grid-cols-3 gap-3">
            <button v-for="opt in goalOptions" :key="opt.value" type="button"
              @click="form.fitness_goal = opt.value"
              :class="[
                'p-4 rounded-xl border text-center transition-all',
                form.fitness_goal === opt.value
                  ? 'border-[#B31B1B] bg-[#B31B1B]/15'
                  : 'border-slate-700 bg-[#1e293b] hover:border-slate-600'
              ]">
              <div class="flex justify-center mb-2">
                <svg v-if="opt.value === 'lose'" class="h-5 w-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
                </svg>
                <svg v-else-if="opt.value === 'maintain'" class="h-5 w-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 12h4l3-9 4 18 3-9h4"/>
                </svg>
                <svg v-else class="h-5 w-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
                </svg>
              </div>
              <div class="text-sm font-medium text-white">{{ opt.label }}</div>
            </button>
          </div>
        </div>

        <!-- Dietary Restrictions -->
        <div>
          <label class="block text-sm font-semibold text-white mb-3">Dietary Restrictions</label>
          <div class="flex flex-wrap gap-2">
            <label v-for="opt in dietaryOptions" :key="opt.value"
              :class="[
                'cursor-pointer border rounded-full px-4 py-1.5 text-sm transition-all select-none',
                form.dietary_restrictions.includes(opt.value)
                  ? 'border-[#B31B1B] bg-[#B31B1B]/15 text-white'
                  : 'border-slate-700 bg-[#1e293b] text-slate-400 hover:border-slate-500'
              ]">
              <input type="checkbox" :value="opt.value" v-model="form.dietary_restrictions" class="hidden" />
              {{ opt.label }}
            </label>
          </div>
        </div>
      </div>

      <div class="flex justify-between mt-4">
        <button @click="step--" class="px-6 py-3 rounded-xl bg-[#1e293b] text-slate-300 text-sm font-medium hover:bg-[#243044] transition-colors">
          Back
        </button>
        <button @click="nextStep" class="px-8 py-3 rounded-xl bg-[#B31B1B] text-white text-sm font-semibold hover:bg-[#a01818] transition-colors shadow-lg shadow-[#B31B1B]/30">
          Next
        </button>
      </div>
    </div>

    <!-- Step 3: Macro Targets -->
    <div v-else-if="step === 3" class="w-full max-w-xl">
      <div class="rounded-2xl bg-[#141e30] p-8">
        <h2 class="text-2xl font-bold text-white mb-1">Your Daily Targets</h2>
        <p class="text-slate-400 text-sm mb-8">Based on your profile and goals</p>

        <!-- Big calorie number -->
        <div class="text-center mb-6">
          <div class="text-7xl font-bold text-white tracking-tight">{{ form.macro_goals.calories }}</div>
          <div class="text-slate-400 text-sm mt-1">calories per day</div>
          <div class="text-slate-600 text-xs mt-1">BMR-based calculation • Adjust below if needed</div>
        </div>

        <div class="border-t border-slate-700/60 mb-6"></div>

        <!-- Macro inputs -->
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Protein</label>
            <div class="relative">
              <input v-model.number="form.macro_goals.protein_g" type="number"
                class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-[#B31B1B] pr-8" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs">g</span>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Carbs</label>
            <div class="relative">
              <input v-model.number="form.macro_goals.carbs_g" type="number"
                class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-[#B31B1B] pr-8" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs">g</span>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Fat</label>
            <div class="relative">
              <input v-model.number="form.macro_goals.fat_g" type="number"
                class="w-full bg-[#1e293b] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-[#B31B1B] pr-8" />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs">g</span>
            </div>
          </div>
        </div>
      </div>

      <p v-if="errorMsg" class="mt-3 text-red-400 text-sm text-center">{{ errorMsg }}</p>
      <div class="flex justify-between mt-4">
        <button @click="step--" class="px-6 py-3 rounded-xl bg-[#1e293b] text-slate-300 text-sm font-medium hover:bg-[#243044] transition-colors">
          Back
        </button>
        <button @click="saveProfile" :disabled="saving"
          class="px-8 py-3 rounded-xl bg-[#B31B1B] text-white text-sm font-semibold hover:bg-[#a01818] transition-colors shadow-lg shadow-[#B31B1B]/30 disabled:opacity-50">
          {{ saving ? 'Saving...' : 'Get Started' }}
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
  macro_goals: { calories: 2000, protein_g: 150, carbs_g: 250, fat_g: 65 }
})

const activityOptions = [
  { value: 'sedentary', label: 'Sedentary', icon: '🪑', desc: 'Little to no exercise' },
  { value: 'lightly_active', label: 'Light', icon: '🚶', desc: 'Exercise 1-3 days/week' },
  { value: 'moderately_active', label: 'Moderate', icon: '🏃', desc: 'Exercise 3-5 days/week' },
  { value: 'very_active', label: 'Active', icon: '💪', desc: 'Exercise 6-7 days/week' }
]

const goalOptions = [
  { value: 'lose', label: 'Lose Weight' },
  { value: 'maintain', label: 'Maintain' },
  { value: 'gain', label: 'Gain Weight' }
]

const dietaryOptions = [
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'gluten_free', label: 'Gluten-Free' },
  { value: 'dairy_free', label: 'Dairy-Free' },
  { value: 'halal', label: 'Halal' },
  { value: 'kosher', label: 'Kosher' }
]

const activityMultipliers = {
  sedentary: 1.2, lightly_active: 1.375, moderately_active: 1.55, very_active: 1.725
}

const heightCm = computed(() => (form.value.heightFt || 0) * 30.48 + (form.value.heightIn || 0) * 2.54)
const weightKg = computed(() => (form.value.weightLbs || 0) * 0.453592)

const bmr = computed(() => {
  const h = heightCm.value, w = weightKg.value, a = form.value.age || 20
  return form.value.sex === 'female'
    ? 10 * w + 6.25 * h - 5 * a - 161
    : 10 * w + 6.25 * h - 5 * a + 5
})

const tdee = computed(() => bmr.value * (activityMultipliers[form.value.activity_level] || 1.55))

watch(step, (newStep) => {
  if (newStep === 3 && heightCm.value > 0 && weightKg.value > 0) {
    const goal = form.value.fitness_goal
    const cals = Math.round(goal === 'lose' ? tdee.value - 500 : goal === 'gain' ? tdee.value + 300 : tdee.value)
    const lbs = form.value.weightLbs || 150
    const proteinPerLb = goal === 'lose' ? 1.0 : goal === 'gain' ? 1.2 : 0.8
    const protein = Math.round(lbs * proteinPerLb)
    const fat = Math.round(cals * 0.25 / 9)
    const carbs = Math.round((cals - protein * 4 - fat * 9) / 4)
    form.value.macro_goals = { calories: cals, protein_g: protein, carbs_g: carbs, fat_g: fat }
  }
})

function nextStep() {
  errorMsg.value = ''
  if (step.value === 1 && (!form.value.heightFt || !form.value.weightLbs || !form.value.age)) {
    errorMsg.value = 'Please fill in all fields.'
    return
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
      macro_goals: { ...form.value.macro_goals, fiber_g: 0, sodium_mg: 0 },
      onboarding_complete: true
    })
    router.push('/')
  } catch (e) {
    console.error(e)
    errorMsg.value = 'Failed to save. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>
