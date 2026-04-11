<template>
  <div class="p-6 md:p-8 max-w-6xl mx-auto">

    <header class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Today on Campus</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Discover what's open and save your favorite meals.</p>
      </div>
      <div v-if="loadingHalls" class="flex items-center gap-2 text-xs text-slate-400">
        <div class="h-3.5 w-3.5 rounded-full border-2 border-red-500 border-t-transparent animate-spin"></div>
        Syncing...
      </div>
    </header>

    <!-- Filter Bar -->
    <div v-if="!selectedHall" class="mb-6 flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-1">
        <button
          @click="filterStatus = 'all'"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'all' ? 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white']"
        >All</button>
        <button
          @click="filterStatus = 'open'"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'open' ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white']"
        >Open Now</button>
        <button
          @click="filterStatus = 'closed'"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'closed' ? 'bg-red-500/20 text-red-600 dark:text-red-400' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white']"
        >Closed</button>
      </div>

      <select
        v-model="filterArea"
        class="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 focus:outline-none focus:border-red-500 transition-colors"
      >
        <option value="all">All Areas</option>
        <option value="North">North Campus</option>
        <option value="Central">Central Campus</option>
        <option value="West">West Campus</option>
      </select>
    </div>

    <!-- Skeleton -->
    <div v-if="!selectedHall && loadingHalls" class="space-y-8">
      <div v-for="n in 3" :key="n">
        <div class="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700 mb-4 animate-pulse"></div>
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div
            v-for="m in 4" :key="m"
            class="flex flex-col rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 animate-pulse"
          >
            <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-700 mb-2"></div>
            <div class="h-3 w-1/2 rounded bg-slate-100 dark:bg-slate-700/60 mb-6"></div>
            <div class="mt-auto h-5 w-20 rounded-full bg-slate-200 dark:bg-slate-700"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Halls: grouped by region when "All Areas" selected -->
    <div v-else-if="!selectedHall && filterArea === 'all'" class="space-y-10">
      <div v-for="region in regions" :key="region.key">
        <div v-if="hallsByRegion(region.key).length > 0">
          <h2 class="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
            <span class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></span>
            {{ region.label }}
            <span class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></span>
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <HallCard
              v-for="hall in hallsByRegion(region.key)"
              :key="hall.id"
              :hall="hall"
              :is-open="isOpen(hall)"
              :is-closing-soon="isClosingSoon(hall)"
              @click="openHall(hall)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Halls: flat list when specific area selected -->
    <div v-else-if="!selectedHall" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <HallCard
        v-for="hall in filteredHalls"
        :key="hall.id"
        :hall="hall"
        :is-open="isOpen(hall)"
        :is-closing-soon="isClosingSoon(hall)"
        @click="openHall(hall)"
      />
      <div v-if="filteredHalls.length === 0" class="col-span-full py-12 text-center text-slate-400 dark:text-slate-500 text-sm">
        No dining halls found for this area.
      </div>
    </div>

    <!-- Selected Hall -->
    <div v-if="selectedHall">
      <button @click="selectedHall = null" class="mb-6 flex items-center gap-2 text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        Back
      </button>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6">
        <div class="mb-6">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-3">{{ selectedHall.name }}</h2>
          <div class="flex flex-wrap gap-2">
            <span class="rounded-lg bg-slate-100 dark:bg-slate-700 px-3 py-1 text-xs font-medium text-slate-600 dark:text-slate-300">
              Swipes: {{ selectedHall.accepts_meal_swipe ? 'Yes' : 'No' }}
            </span>
            <span class="rounded-lg bg-slate-100 dark:bg-slate-700 px-3 py-1 text-xs font-medium text-slate-600 dark:text-slate-300">
              BRBs: {{ selectedHall.accepts_brbs ? 'Yes' : 'No' }}
            </span>
          </div>
        </div>

        <!-- Menu skeleton -->
        <div v-if="loadingMenu" class="space-y-8 animate-pulse">
          <div v-for="n in 2" :key="n" class="space-y-3">
            <div class="h-3 w-28 rounded bg-slate-200 dark:bg-slate-700"></div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div v-for="m in 6" :key="m" class="rounded-xl bg-slate-50 dark:bg-slate-700/50 p-4 border border-slate-200 dark:border-slate-700">
                <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-700 mb-2"></div>
                <div class="h-3 w-1/3 rounded bg-slate-100 dark:bg-slate-700/60 mb-3"></div>
                <div class="flex gap-1">
                  <div class="h-3 w-10 rounded bg-slate-100 dark:bg-slate-700/60"></div>
                  <div class="h-3 w-10 rounded bg-slate-100 dark:bg-slate-700/60"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!menus.length" class="py-10 text-center text-slate-400 dark:text-slate-500 text-sm">
          No menus available for today.
        </div>

        <div v-else class="space-y-8">
          <div v-for="menu in menus" :key="menu.meal_period">
            <h3 class="text-xs font-bold text-red-600 dark:text-red-400 uppercase tracking-widest border-b border-slate-200 dark:border-slate-700 pb-2 mb-4">
              {{ menu.meal_period }}
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div
                v-for="(item, idx) in menu.items"
                :key="idx"
                class="flex items-start justify-between rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/30 hover:bg-slate-100 dark:hover:bg-slate-700/60 p-4 transition-colors"
              >
                <div class="pr-3 min-w-0">
                  <h4 class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ item.name }}</h4>
                  <p v-if="item.station" class="text-[10px] text-slate-400 dark:text-slate-500 uppercase mt-0.5">{{ item.station }}</p>
                  <div class="flex gap-1 mt-2 flex-wrap">
                    <span v-if="item.is_vegan" class="px-1.5 py-0.5 rounded bg-emerald-500/20 text-[9px] text-emerald-600 dark:text-emerald-400 font-semibold uppercase">Vegan</span>
                    <span v-if="item.is_vegetarian && !item.is_vegan" class="px-1.5 py-0.5 rounded bg-lime-500/20 text-[9px] text-lime-600 dark:text-lime-400 font-semibold uppercase">Veg</span>
                    <span v-if="item.is_halal" class="px-1.5 py-0.5 rounded bg-blue-500/20 text-[9px] text-blue-600 dark:text-blue-400 font-semibold uppercase">Halal</span>
                    <span v-for="alg in item.allergens?.slice(0, 2)" :key="alg" class="px-1.5 py-0.5 rounded bg-red-500/20 text-[9px] text-red-600 dark:text-red-400 font-semibold uppercase">{{ alg }}</span>
                  </div>
                </div>
                <button
                  @click.stop="toggleFavorite(item.name)"
                  class="shrink-0 p-1.5 rounded-lg transition-colors"
                  :class="isFavorite(item.name) ? 'text-red-500 bg-red-500/10 hover:bg-red-500/20' : 'text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 bg-slate-100 dark:bg-slate-700/50'"
                >
                  <svg class="h-4 w-4" :fill="isFavorite(item.name) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="toast.visible"
        class="fixed bottom-6 right-6 z-50 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm font-medium text-slate-900 dark:text-white shadow-xl"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDiningHalls, getDiningHallMenu, getProfile, toggleFavoriteMeal } from '@/api'

// Inline hall card component to avoid extra file
const HallCard = {
  props: ['hall', 'isOpen', 'isClosingSoon'],
  emits: ['click'],
  template: `
    <div
      @click="$emit('click')"
      class="group cursor-pointer flex flex-col rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 p-5 transition-colors active:scale-95"
    >
      <h2 class="text-sm font-semibold text-slate-900 dark:text-white mb-1">{{ hall.name }}</h2>
      <p class="text-xs text-slate-400 dark:text-slate-500 mb-4 uppercase tracking-wider">{{ hall.campus_area || 'Campus' }}</p>
      <div class="mt-auto flex items-center gap-2 flex-wrap">
        <span v-if="isOpen" class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse"></span>
          Open
        </span>
        <span v-else class="inline-flex items-center gap-1.5 rounded-full bg-slate-100 dark:bg-slate-700 px-2.5 py-1 text-xs font-semibold text-slate-400 dark:text-slate-500">
          <span class="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-500"></span>
          Closed
        </span>
        <span v-if="isOpen && isClosingSoon" class="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-600 dark:text-amber-400">
          Closing Soon
        </span>
      </div>
    </div>
  `
}

const halls = ref([])
const loadingHalls = ref(false)
const selectedHall = ref(null)
const menus = ref([])
const loadingMenu = ref(false)
const favoriteMeals = ref(new Set())
const toast = ref({ visible: false, message: '' })
let toastTimer = null

const filterStatus = ref('all')
const filterArea = ref('all')

const regions = [
  { key: 'North', label: 'North Campus' },
  { key: 'Central', label: 'Central Campus' },
  { key: 'West', label: 'West Campus' },
]

function hallsByRegion(regionKey) {
  return halls.value.filter(hall => {
    const area = (hall.campus_area || '').toLowerCase()
    const key = regionKey.toLowerCase()
    if (!area.includes(key)) return false
    const open = isOpen(hall)
    if (filterStatus.value === 'open' && !open) return false
    if (filterStatus.value === 'closed' && open) return false
    return true
  })
}

const filteredHalls = computed(() =>
  halls.value.filter(hall => {
    const open = isOpen(hall)
    if (filterStatus.value === 'open' && !open) return false
    if (filterStatus.value === 'closed' && open) return false
    const area = (hall.campus_area || '').toLowerCase()
    const selected = filterArea.value.toLowerCase()
    if (filterArea.value !== 'all' && !area.includes(selected)) return false
    return true
  })
)

onMounted(async () => {
  loadingHalls.value = true
  try {
    const [hallsRes, profileRes] = await Promise.all([getDiningHalls(), getProfile()])
    halls.value = hallsRes.data
    favoriteMeals.value = new Set(profileRes.data.favorite_meals || [])
  } catch (e) {
    console.error(e)
  } finally {
    loadingHalls.value = false
  }
})

function parseTimeToday(timeStr) {
  const [hours, minutes] = timeStr.split(':').map(Number)
  const d = new Date()
  d.setHours(hours, minutes, 0, 0)
  return d
}

function getTodayName() {
  return new Date().toLocaleDateString('en-US', { weekday: 'long' })
}

function isOpen(hall) {
  if (!hall.operating_hours || typeof hall.operating_hours !== 'object') return false
  const todayHours = hall.operating_hours[getTodayName()]
  if (!todayHours?.open || !todayHours?.close) return false
  const now = new Date()
  return now >= parseTimeToday(todayHours.open) && now < parseTimeToday(todayHours.close)
}

function isClosingSoon(hall) {
  if (!hall.operating_hours || typeof hall.operating_hours !== 'object') return false
  const todayHours = hall.operating_hours[getTodayName()]
  if (!todayHours?.close) return false
  const diffMs = parseTimeToday(todayHours.close) - new Date()
  return diffMs > 0 && diffMs <= 30 * 60 * 1000
}

async function openHall(hall) {
  selectedHall.value = hall
  loadingMenu.value = true
  menus.value = []
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await getDiningHallMenu(hall.id, today)
    menus.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loadingMenu.value = false
  }
}

function isFavorite(name) { return favoriteMeals.value.has(name) }

function showToast(message) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { visible: true, message }
  toastTimer = setTimeout(() => { toast.value.visible = false }, 2000)
}

async function toggleFavorite(name) {
  const wasFav = isFavorite(name)
  wasFav ? favoriteMeals.value.delete(name) : favoriteMeals.value.add(name)
  showToast(wasFav ? 'Removed from favorites' : 'Added to favorites')
  try {
    const res = await toggleFavoriteMeal(name)
    favoriteMeals.value = new Set(res.data.favorite_meals)
  } catch (e) {
    console.error(e)
    wasFav ? favoriteMeals.value.add(name) : favoriteMeals.value.delete(name)
  }
}
</script>
