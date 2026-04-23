<template>
  <div class="min-h-screen bg-[#0f172a]">

    <!-- Search + Filter Bar -->
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

          <!-- Hall name + heart -->
          <div class="flex items-start justify-between mb-3">
            <h2 class="text-[15px] font-semibold text-white leading-snug pr-4">{{ hall.name }}</h2>
            <button @click.stop="toggleHallFavorite(hall)" class="shrink-0 mt-0.5 text-slate-600 hover:text-[#B31B1B] transition-colors">
              <svg class="h-5 w-5" :fill="hallFavorites.has(hall.id) ? '#B31B1B' : 'none'" viewBox="0 0 24 24" stroke="currentColor" :stroke="hallFavorites.has(hall.id) ? '#B31B1B' : 'currentColor'" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </button>
          </div>

          <!-- Area badge -->
          <div class="mb-3">
            <span :class="['inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium', areaBadgeClass(hall.campus_area)]">
              {{ hall.campus_area ? hall.campus_area + ' Campus' : 'Campus' }}
            </span>
          </div>

          <!-- Payment badges -->
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

          <!-- View Menu button -->
          <button @click="openHall(hall)"
            class="w-full mt-auto rounded-xl bg-[#B31B1B] py-2.5 text-sm font-semibold text-white hover:bg-[#a01818] transition-colors">
            View Menu
          </button>
        </div>
      </div>

      <!-- Selected Hall View -->
      <div v-else class="animate-fade-in max-w-5xl mx-auto">
        <button @click="selectedHall = null" class="mb-6 flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-white transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          Back to list
        </button>

        <div class="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl mb-6">
          <h2 class="text-3xl font-bold text-white mb-2">{{ selectedHall.name }}</h2>
          <div class="flex flex-wrap gap-2">
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">Swipes: {{ selectedHall.accepts_meal_swipe ? 'Yes' : 'No' }}</span>
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">BRBs: {{ selectedHall.accepts_brbs ? 'Yes' : 'No' }}</span>
            <span v-if="selectedHall._distance != null" class="rounded-full bg-cornell-red/20 px-3 py-1 text-xs font-bold text-cornell-300">{{ selectedHall._distance }} mi away</span>
          </div>
        </div>

        <div v-if="loadingMenu" class="py-12 flex justify-center">
          <div class="h-8 w-8 rounded-full border-4 border-cornell-red border-t-transparent animate-spin"></div>
        </div>

        <div v-else-if="menus.length === 0" class="text-center py-12 text-slate-400">
          No menu data available for today.
        </div>

        <div v-else class="space-y-10">
          <div v-for="menu in menus" :key="menu.meal_period" class="space-y-4">
            <h3 class="text-lg font-bold text-cornell-400 uppercase tracking-widest border-b border-white/10 pb-2">{{ menu.meal_period }}</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
              <div v-for="(item, idx) in menu.items" :key="idx" class="group flex items-start justify-between rounded-2xl bg-black/20 p-4 hover:bg-black/40 transition-colors border border-white/5">
                <div class="pr-4">
                  <h4 class="text-sm font-bold text-slate-200">{{ item.name }}</h4>
                  <p v-if="item.station" class="text-[10px] text-slate-500 uppercase mt-1">{{ item.station }}</p>
                  <div class="flex gap-1 mt-2 flex-wrap">
                    <span v-if="item.is_vegan" class="px-1.5 py-0.5 rounded-sm bg-emerald-500/20 text-[9px] text-emerald-400 font-bold uppercase tracking-wider">Vegan</span>
                    <span v-if="item.is_vegetarian && !item.is_vegan" class="px-1.5 py-0.5 rounded-sm bg-lime-500/20 text-[9px] text-lime-400 font-bold uppercase tracking-wider">Veg</span>
                    <span v-if="item.is_halal" class="px-1.5 py-0.5 rounded-sm bg-blue-500/20 text-[9px] text-blue-400 font-bold uppercase tracking-wider">Halal</span>
                    <span v-for="algo in item.allergens.slice(0, 2)" :key="algo" class="px-1.5 py-0.5 rounded-sm bg-red-500/20 text-[9px] text-red-400 font-bold uppercase tracking-wider">{{ algo }}</span>
                  </div>
                </div>
                <button @click="toggleFavorite(item.name)" class="shrink-0 p-2 rounded-full transition-all focus:outline-none" :class="isFavorite(item.name) ? 'text-cornell-red hover:text-cornell-400 bg-cornell-red/10' : 'text-slate-600 hover:text-cornell-400 bg-white/5'">
                  <svg class="h-5 w-5" :fill="isFavorite(item.name) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
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
        class="fixed bottom-6 right-6 z-50 rounded-xl bg-[#1e293b] border border-slate-700 px-4 py-2.5 text-sm font-medium text-white shadow-xl"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDiningHalls, getDiningHallMenu, getProfile, toggleFavoriteMeal } from '@/api'

const hallFavorites = ref(new Set())
const halls = ref([])
const loadingHalls = ref(false)
const selectedHall = ref(null)
const menus = ref([])
const loadingMenu = ref(false)
const favoriteMeals = ref(new Set())
const toast = ref({ visible: false, message: '' })
let toastTimer = null

const userLocation = ref(null)
const searchQuery = ref('')

// Filters
const filterStatus = ref('all')
const filterArea = ref('all')

function areaBadgeClass(area) {
  if (!area) return 'bg-slate-700/50 text-slate-400'
  const a = area.toLowerCase()
  if (a.includes('north')) return 'bg-blue-500/20 text-blue-300'
  if (a.includes('west')) return 'bg-purple-500/20 text-purple-300'
  if (a.includes('central')) return 'bg-emerald-500/20 text-emerald-300'
  return 'bg-slate-700/50 text-slate-400'
}

function toggleHallFavorite(hall) {
  if (hallFavorites.value.has(hall.id)) {
    hallFavorites.value.delete(hall.id)
  } else {
    hallFavorites.value.add(hall.id)
  }
}

const regions = [
  { key: 'North', label: 'North Campus' },
  { key: 'Central', label: 'Central Campus' },
  { key: 'West', label: 'West Campus' },
]

// Haversine distance (miles)
function haversine(lat1, lon1, lat2, lon2) {
  const R = 3958.8 // Earth radius in miles
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
    if (h.location_lat && h.location_lng) {
      h._distance = haversine(lat, lng, h.location_lat, h.location_lng).toFixed(2)
    } else {
      h._distance = null
    }
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
    const open = isOpen(hall)
    if (filterStatus.value === 'open' && !open) return false
    if (filterStatus.value === 'closed' && open) return false
    if (filterArea.value !== 'all' && hall.campus_area !== filterArea.value) return false
    return true
  })

  // Sort by distance if location is available
  if (userLocation.value) {
    result = result.slice().sort((a, b) => {
      const da = a._distance != null ? parseFloat(a._distance) : Infinity
      const db = b._distance != null ? parseFloat(b._distance) : Infinity
      return da - db
    })
  }

  return result
})

onMounted(async () => {
  // Request geolocation in parallel with data fetching
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        attachDistances()
      },
      () => {
        // Permission denied — silently fall back to default order
        console.log('Geolocation denied, using default sort order.')
      },
      { enableHighAccuracy: false, timeout: 8000 }
    )
  }

  loadingHalls.value = true
  try {
    const [hallsRes, profileRes] = await Promise.all([getDiningHalls(), getProfile()])
    halls.value = hallsRes.data
    attachDistances()
    const favs = profileRes.data.favorite_meals || []
    favoriteMeals.value = new Set(favs)
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
  return !!hall.operating_hours && Object.keys(hall.operating_hours).length > 0;
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
    if (wasFav) {
      favoriteMeals.value.add(name)
    } else {
      favoriteMeals.value.delete(name)
    }
  }
}
</script>
