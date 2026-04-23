<template>
  <div class="min-h-screen bg-[#0f172a]">

    <!-- Search + Filter Bar (hall list only) -->
    <div v-if="!selectedHall" class="flex items-center gap-3 px-6 py-4 border-b border-white/10">
      <div class="flex-1 relative">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Search dining halls..."
          class="w-full bg-[#141e30] border border-slate-700 rounded-xl pl-11 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-slate-500" />
      </div>
      <select v-model="filterArea" class="bg-[#141e30] border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:border-slate-500 min-w-[140px]">
        <option value="all">All Areas</option>
        <option v-for="area in uniqueAreas" :key="area" :value="area">{{ area }}</option>
      </select>
    </div>

    <div class="px-6 py-6 max-w-7xl mx-auto">

      <!-- Dining Halls Grid -->
      <div v-if="!selectedHall" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div v-for="hall in filteredHalls" :key="hall.id"
             class="flex flex-col rounded-2xl bg-[#141e30] border border-slate-800 p-5 hover:border-slate-700 transition-all relative">

          <div class="flex items-start justify-between mb-3">
            <h2 class="text-[15px] font-semibold text-white leading-snug pr-4">{{ hall.name }}</h2>
            <button @click.stop="toggleHallFavorite(hall)" class="shrink-0 mt-0.5 text-slate-600 hover:text-[#B31B1B] transition-colors">
              <svg class="h-5 w-5" :fill="hallFavorites.has(hall.id) ? '#B31B1B' : 'none'" viewBox="0 0 24 24" stroke="currentColor" :stroke="hallFavorites.has(hall.id) ? '#B31B1B' : 'currentColor'" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </button>
          </div>

          <div class="mb-3">
            <span :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium', areaBadgeClass(hall.campus_area)]">
              {{ hall.campus_area ? hall.campus_area + ' Campus' : 'Campus' }}
            </span>
          </div>

          <div class="flex gap-2 mb-4">
            <span class="inline-flex items-center gap-1.5 bg-[#1e293b] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>
              </svg>
              Meal Swipe
            </span>
            <span class="inline-flex items-center gap-1.5 bg-[#1e293b] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="16" cy="12" r="2"/>
              </svg>
              BRB
            </span>
          </div>

          <button @click="openHall(hall)"
            class="w-full mt-auto rounded-xl bg-[#B31B1B] py-2.5 text-sm font-semibold text-white hover:bg-[#a01818] transition-colors">
            View Menu
          </button>
        </div>
      </div>

      <!-- Selected Hall: Menu View -->
      <div v-else class="max-w-5xl mx-auto">

        <!-- Header row -->
        <div class="flex items-start justify-between mb-6">
          <div>
            <button @click="selectedHall = null" class="mb-3 flex items-center gap-1.5 text-sm text-slate-500 hover:text-white transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              All dining halls
            </button>
            <h2 class="text-2xl font-bold text-white">{{ selectedHall.name }}</h2>
            <div class="flex items-center gap-2 mt-1.5">
              <span :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium', areaBadgeClass(selectedHall.campus_area)]">
                {{ selectedHall.campus_area ? selectedHall.campus_area + ' Campus' : 'Campus' }}
              </span>
              <span v-if="selectedHall.accepts_meal_swipe" class="text-xs text-slate-500">· Meal Swipe</span>
              <span v-if="selectedHall.accepts_brbs" class="text-xs text-slate-500">· BRB</span>
            </div>
          </div>

          <!-- Date picker -->
          <div class="flex items-center gap-1 bg-[#141e30] border border-slate-700 rounded-xl p-1">
            <button @click="setDate('today')"
              :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-all', selectedDateKey === 'today' ? 'bg-[#B31B1B] text-white' : 'text-slate-400 hover:text-white']">
              Today
            </button>
            <button @click="setDate('tomorrow')"
              :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-all', selectedDateKey === 'tomorrow' ? 'bg-[#B31B1B] text-white' : 'text-slate-400 hover:text-white']">
              Tomorrow
            </button>
          </div>
        </div>

        <!-- AI regen banner (shows when date changes to tomorrow) -->
        <transition enter-active-class="transition-all duration-200" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-150" leave-from-class="opacity-100" leave-to-class="opacity-0">
          <div v-if="showRegenBanner" class="mb-6 flex items-center justify-between rounded-xl bg-[#1e293b] border border-slate-700 px-5 py-3.5">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-[#B31B1B] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              <p class="text-sm text-slate-300">Viewing tomorrow's menu. Want to regenerate your AI meal plan for this date?</p>
            </div>
            <div class="flex items-center gap-2 ml-4 shrink-0">
              <button @click="showRegenBanner = false" class="text-xs text-slate-500 hover:text-slate-300 transition-colors px-2 py-1">Dismiss</button>
              <button @click="goToPlanner" class="px-4 py-1.5 rounded-lg bg-[#B31B1B] text-white text-xs font-semibold hover:bg-[#a01818] transition-colors">
                Regenerate
              </button>
            </div>
          </div>
        </transition>

        <!-- Loading -->
        <div v-if="loadingMenu" class="py-20 flex flex-col items-center gap-3 text-slate-500">
          <div class="h-8 w-8 rounded-full border-2 border-[#B31B1B] border-t-transparent animate-spin"></div>
          <span class="text-sm">Loading menu...</span>
        </div>

        <!-- Empty state -->
        <div v-else-if="menus.length === 0" class="py-20 flex flex-col items-center gap-4 text-center">
          <div class="h-14 w-14 rounded-2xl bg-[#141e30] border border-slate-700 flex items-center justify-center">
            <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3v7"/>
            </svg>
          </div>
          <div>
            <p class="text-white font-semibold">No menu available</p>
            <p class="text-slate-500 text-sm mt-1">Menu data for {{ selectedDateKey === 'tomorrow' ? 'tomorrow' : 'today' }} hasn't been loaded yet.</p>
          </div>
        </div>

        <!-- Menu periods -->
        <div v-else class="space-y-8">
          <div v-for="menu in menus" :key="menu.meal_period">
            <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-3">
              <span>{{ menu.meal_period }}</span>
              <span class="flex-1 h-px bg-slate-800"></span>
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div v-for="(item, idx) in menu.items" :key="idx"
                   class="flex items-start justify-between rounded-xl bg-[#141e30] border border-slate-800 p-4 hover:border-slate-700 transition-colors">
                <div class="flex-1 pr-3">
                  <h4 class="text-sm font-semibold text-white leading-snug">{{ item.name }}</h4>
                  <p v-if="item.station" class="text-[11px] text-slate-500 mt-0.5 uppercase tracking-wide">{{ item.station }}</p>
                  <div class="flex gap-1 mt-2 flex-wrap">
                    <span v-if="item.is_vegan" class="px-1.5 py-0.5 rounded bg-emerald-500/20 text-[10px] text-emerald-400 font-semibold">Vegan</span>
                    <span v-if="item.is_vegetarian && !item.is_vegan" class="px-1.5 py-0.5 rounded bg-lime-500/20 text-[10px] text-lime-400 font-semibold">Veg</span>
                    <span v-if="item.is_halal" class="px-1.5 py-0.5 rounded bg-blue-500/20 text-[10px] text-blue-400 font-semibold">Halal</span>
                    <span v-if="item.is_gluten_free" class="px-1.5 py-0.5 rounded bg-amber-500/20 text-[10px] text-amber-400 font-semibold">GF</span>
                  </div>
                  <div v-if="item.macros" class="flex gap-2 mt-2">
                    <span class="text-[11px] text-slate-500">{{ Math.round(item.macros.calories) }} cal</span>
                    <span class="text-[11px] text-slate-600">·</span>
                    <span class="text-[11px] text-slate-500">{{ Math.round(item.macros.protein_g) }}g protein</span>
                  </div>
                </div>
                <button @click="toggleFavorite(item.name)"
                  :class="['shrink-0 p-1.5 rounded-lg transition-all', isFavorite(item.name) ? 'text-[#B31B1B]' : 'text-slate-600 hover:text-[#B31B1B]']">
                  <svg class="h-4 w-4" :fill="isFavorite(item.name) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 translate-y-2">
      <div v-if="toast.visible" class="fixed bottom-6 right-6 z-50 rounded-xl bg-[#1e293b] border border-slate-700 px-4 py-2.5 text-sm font-medium text-white shadow-xl">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getDiningHalls, getDiningHallMenu, getProfile, toggleFavoriteMeal } from '@/api'

const router = useRouter()

const halls = ref([])
const loadingHalls = ref(false)
const hallFavorites = ref(new Set())
const selectedHall = ref(null)
const menus = ref([])
const loadingMenu = ref(false)
const favoriteMeals = ref(new Set())
const toast = ref({ visible: false, message: '' })
let toastTimer = null

const userLocation = ref(null)
const searchQuery = ref('')
const filterArea = ref('all')
const filterStatus = ref('all')

// Date state
const selectedDateKey = ref('today')
const showRegenBanner = ref(false)

function getDateStr(key) {
  const d = new Date()
  if (key === 'tomorrow') d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

function setDate(key) {
  selectedDateKey.value = key
}

watch(selectedDateKey, async (key) => {
  if (!selectedHall.value) return
  showRegenBanner.value = key === 'tomorrow'
  await loadMenu(selectedHall.value, getDateStr(key))
})

function areaBadgeClass(area) {
  if (!area) return 'bg-slate-700/50 text-slate-400'
  const a = area.toLowerCase()
  if (a.includes('north')) return 'bg-blue-500/20 text-blue-300'
  if (a.includes('west')) return 'bg-purple-500/20 text-purple-300'
  if (a.includes('central')) return 'bg-emerald-500/20 text-emerald-300'
  return 'bg-slate-700/50 text-slate-400'
}

function toggleHallFavorite(hall) {
  hallFavorites.value.has(hall.id)
    ? hallFavorites.value.delete(hall.id)
    : hallFavorites.value.add(hall.id)
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 3958.8
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function attachDistances() {
  if (!userLocation.value) return
  const { lat, lng } = userLocation.value
  halls.value.forEach(h => {
    h._distance = (h.location_lat && h.location_lng)
      ? haversine(lat, lng, h.location_lat, h.location_lng).toFixed(2)
      : null
  })
}

const uniqueAreas = computed(() => {
  const areas = new Set(halls.value.map(h => h.campus_area).filter(Boolean))
  return [...areas].sort()
})

const filteredHalls = computed(() => {
  const q = searchQuery.value.toLowerCase()
  let result = halls.value.filter(hall => {
    if (q && !hall.name.toLowerCase().includes(q)) return false
    if (filterStatus.value === 'open' && !isOpen(hall)) return false
    if (filterStatus.value === 'closed' && isOpen(hall)) return false
    if (filterArea.value !== 'all' && hall.campus_area !== filterArea.value) return false
    return true
  })
  if (userLocation.value) {
    result = result.slice().sort((a, b) => {
      const da = a._distance != null ? parseFloat(a._distance) : Infinity
      const db = b._distance != null ? parseFloat(b._distance) : Infinity
      return da - db
    })
  }
  return result
})

function isOpen(hall) {
  return !!hall.operating_hours && Object.keys(hall.operating_hours).length > 0
}

onMounted(async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        attachDistances()
      },
      () => {},
      { enableHighAccuracy: false, timeout: 8000 }
    )
  }
  loadingHalls.value = true
  try {
    const [hallsRes, profileRes] = await Promise.all([getDiningHalls(), getProfile()])
    halls.value = hallsRes.data
    attachDistances()
    favoriteMeals.value = new Set(profileRes.data.favorite_meals || [])
  } catch (e) {
    console.error(e)
  } finally {
    loadingHalls.value = false
  }
})

async function loadMenu(hall, dateStr) {
  loadingMenu.value = true
  menus.value = []
  try {
    const res = await getDiningHallMenu(hall.id, dateStr)
    menus.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loadingMenu.value = false
  }
}

async function openHall(hall) {
  selectedHall.value = hall
  selectedDateKey.value = 'today'
  showRegenBanner.value = false
  await loadMenu(hall, getDateStr('today'))
}

function goToPlanner() {
  showRegenBanner.value = false
  router.push({ path: '/planner', query: { date: getDateStr(selectedDateKey.value) } })
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
