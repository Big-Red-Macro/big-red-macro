<template>
  <div class="p-4 md:p-8">
    <div class="mx-auto max-w-6xl">
      <header class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-white mb-2">Today on Campus</h1>
          <p class="text-slate-400">Discover what's open and save your favorite meals.</p>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="userLocation" class="hidden md:inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-400">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" /></svg>
            Sorted by distance
          </span>
          <div v-if="loadingHalls" class="text-cornell-red text-sm animate-pulse flex items-center gap-2">
            <div class="h-4 w-4 rounded-full border-2 border-cornell-red border-t-transparent animate-spin"></div>
            Syncing Menus...
          </div>
        </div>
      </header>

      <!-- Filter Bar -->
      <div v-if="!selectedHall" class="mb-6 flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-1 backdrop-blur-xl">
          <button @click="filterStatus = 'all'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'all' ? 'bg-cornell-red/20 text-cornell-300' : 'text-slate-400 hover:text-white']">All</button>
          <button @click="filterStatus = 'open'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'open' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400 hover:text-white']">Open Now</button>
          <button @click="filterStatus = 'closed'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'closed' ? 'bg-red-500/20 text-red-400' : 'text-slate-400 hover:text-white']">Closed</button>
        </div>
        
        <select v-model="filterArea" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 backdrop-blur-xl focus:outline-none focus:border-cornell-red">
          <option value="all">All Areas</option>
          <option v-for="area in uniqueAreas" :key="area" :value="area">{{ area }}</option>
        </select>
      </div>

      <!-- Dining Halls Grid -->
      <div v-if="!selectedHall" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="hall in filteredHalls" :key="hall.id" 
             @click="openHall(hall)"
             class="group cursor-pointer flex flex-col rounded-3xl border border-white/10 bg-white/5 p-6 hover:bg-white/10 backdrop-blur-xl transition-all hover:scale-[1.02] active:scale-95 shadow-lg relative overflow-hidden">
             
           <div class="absolute inset-0 bg-gradient-to-br from-cornell-red/10 to-cornell-red/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
           
           <h2 class="text-lg font-bold text-white mb-1 z-10">{{ hall.name }}</h2>
           <p class="text-xs text-slate-400 mb-3 uppercase tracking-wider z-10">{{ hall.campus_area || 'Campus' }}</p>
           
           <!-- Distance badge -->
           <p v-if="hall._distance != null" class="text-xs text-cornell-300 mb-3 z-10 flex items-center gap-1">
             <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
             {{ hall._distance }} mi away
           </p>

           <div class="mt-auto z-10 flex items-center gap-2">
             <span v-if="isOpen(hall)" class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2.5 py-1 text-xs font-bold text-emerald-400">
               <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
               Open Now
             </span>
             <span v-else class="inline-flex items-center gap-1.5 rounded-full bg-red-500/20 px-2.5 py-1 text-xs font-bold text-red-400">
               <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
               Closed
             </span>
           </div>
        </div>
      </div>

      <!-- Selected Hall View -->
      <div v-else class="animate-fade-in">
        <button @click="selectedHall = null" class="mb-6 flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-white transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          Back to list
        </button>

        <div class="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
          <h2 class="text-3xl font-bold text-white mb-2">{{ selectedHall.name }}</h2>
          <div class="flex flex-wrap gap-2 mb-8">
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">Swipes: {{ selectedHall.accepts_meal_swipe ? 'Yes' : 'No' }}</span>
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">BRBs: {{ selectedHall.accepts_brbs ? 'Yes' : 'No' }}</span>
            <span v-if="selectedHall._distance != null" class="rounded-full bg-cornell-red/20 px-3 py-1 text-xs font-bold text-cornell-300">{{ selectedHall._distance }} mi away</span>
          </div>

          <div v-if="loadingMenu" class="py-12 flex justify-center">
            <div class="h-8 w-8 rounded-full border-4 border-cornell-red border-t-transparent animate-spin"></div>
          </div>
          <div v-else-if="!menus.length" class="text-center py-12 text-slate-400">
            No menus available for today.
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDiningHalls, getDiningHallMenu, getProfile, toggleFavoriteMeal } from '@/api'

const halls = ref([])
const loadingHalls = ref(false)

const selectedHall = ref(null)
const menus = ref([])
const loadingMenu = ref(false)

const favoriteMeals = ref(new Set())

const userLocation = ref(null)

// Filters
const filterStatus = ref('all') // 'all', 'open', 'closed'
const filterArea = ref('all')

const uniqueAreas = computed(() => {
  const areas = new Set(halls.value.map(h => h.campus_area).filter(a => a))
  return Array.from(areas).sort()
})

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

const filteredHalls = computed(() => {
  let result = halls.value.filter(hall => {
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
    const [hallsRes, profileRes] = await Promise.all([
      getDiningHalls(),
      getProfile()
    ])
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

function isFavorite(name) {
  return favoriteMeals.value.has(name)
}

async function toggleFavorite(name) {
  const isFav = isFavorite(name)
  if (isFav) {
    favoriteMeals.value.delete(name)
  } else {
    favoriteMeals.value.add(name)
  }
  
  try {
    const res = await toggleFavoriteMeal(name)
    favoriteMeals.value = new Set(res.data.favorite_meals)
  } catch (e) {
    console.error(e)
    if (isFav) {
      favoriteMeals.value.add(name)
    } else {
      favoriteMeals.value.delete(name)
    }
  }
}
</script>
