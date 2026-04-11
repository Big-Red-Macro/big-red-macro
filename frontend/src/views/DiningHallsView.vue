<template>
  <div class="p-4 md:p-8">
    <div class="mx-auto max-w-6xl">
      <header class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-white mb-2">Today on Campus</h1>
          <p class="text-slate-400">Discover what's open and save your favorite meals.</p>
        </div>
        <div v-if="loadingHalls" class="text-red-400 text-sm animate-pulse flex items-center gap-2">
          <div class="h-4 w-4 rounded-full border-2 border-red-500 border-t-transparent animate-spin"></div>
          Syncing Menus...
        </div>
      </header>

      <!-- Filter Bar -->
      <div v-if="!selectedHall" class="mb-6 flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-1 backdrop-blur-xl">
          <button @click="filterStatus = 'all'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'all' ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-white']">All</button>
          <button @click="filterStatus = 'open'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'open' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400 hover:text-white']">Open Now</button>
          <button @click="filterStatus = 'closed'" :class="['px-4 py-1.5 rounded-lg text-sm font-medium transition-colors', filterStatus === 'closed' ? 'bg-red-500/20 text-red-400' : 'text-slate-400 hover:text-white']">Closed</button>
        </div>

        <select v-model="filterArea" class="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 backdrop-blur-xl focus:outline-none focus:border-red-500">
          <option value="all">All Areas</option>
          <option v-for="area in uniqueAreas" :key="area" :value="area">{{ area }}</option>
        </select>
      </div>

      <!-- Dining Halls Grid — skeleton loading state -->
      <div v-if="!selectedHall && loadingHalls" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div
          v-for="n in 8"
          :key="n"
          class="flex flex-col rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl animate-pulse"
        >
          <div class="h-5 w-3/4 rounded-lg bg-white/10 mb-2"></div>
          <div class="h-3 w-1/2 rounded-md bg-white/5 mb-6"></div>
          <div class="mt-auto h-6 w-20 rounded-full bg-white/10"></div>
        </div>
      </div>

      <!-- Dining Halls Grid — real data -->
      <div v-else-if="!selectedHall" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div v-for="hall in filteredHalls" :key="hall.id"
             @click="openHall(hall)"
             class="group cursor-pointer flex flex-col rounded-3xl border border-white/10 bg-white/5 p-6 hover:bg-white/10 backdrop-blur-xl transition-all hover:scale-[1.02] active:scale-95 shadow-lg relative overflow-hidden">

           <div class="absolute inset-0 bg-gradient-to-br from-red-500/10 to-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>

           <h2 class="text-lg font-bold text-white mb-1 z-10">{{ hall.name }}</h2>
           <p class="text-xs text-slate-400 mb-4 uppercase tracking-wider z-10">{{ hall.campus_area || 'Campus' }}</p>

           <div class="mt-auto z-10 flex items-center gap-2 flex-wrap">
             <span v-if="isOpen(hall)" class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2.5 py-1 text-xs font-bold text-emerald-400">
               <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
               Open Now
             </span>
             <span v-else class="inline-flex items-center gap-1.5 rounded-full bg-red-500/20 px-2.5 py-1 text-xs font-bold text-red-400">
               <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
               Closed
             </span>
             <!-- Closing Soon badge — shown when open but closing within 30 minutes -->
             <span v-if="isOpen(hall) && isClosingSoon(hall)" class="inline-flex items-center gap-1.5 rounded-full bg-amber-500/20 px-2.5 py-1 text-xs font-bold text-amber-400">
               <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
               Closing Soon
             </span>
           </div>
        </div>
      </div>

      <!-- Selected Hall View -->
      <div v-if="selectedHall" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <button @click="selectedHall = null" class="mb-6 flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-white transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
          Back to list
        </button>

        <div class="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
          <h2 class="text-3xl font-bold text-white mb-2">{{ selectedHall.name }}</h2>
          <div class="flex flex-wrap gap-2 mb-8">
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">Swipes: {{ selectedHall.accepts_meal_swipe ? 'Yes' : 'No' }}</span>
            <span class="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-slate-300">BRBs: {{ selectedHall.accepts_brbs ? 'Yes' : 'No' }}</span>
          </div>

          <!-- Menu skeleton loading state -->
          <div v-if="loadingMenu" class="space-y-10">
            <div v-for="n in 2" :key="n" class="space-y-4 animate-pulse">
              <div class="h-4 w-32 rounded-md bg-white/10 mb-4"></div>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="m in 6" :key="m" class="rounded-2xl bg-black/20 p-4 border border-white/5">
                  <div class="h-4 w-3/4 rounded-md bg-white/10 mb-2"></div>
                  <div class="h-3 w-1/3 rounded-sm bg-white/5 mb-3"></div>
                  <div class="flex gap-1">
                    <div class="h-3 w-10 rounded-sm bg-white/5"></div>
                    <div class="h-3 w-10 rounded-sm bg-white/5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="!menus.length" class="text-center py-12 text-slate-400">
            No menus available for today.
          </div>
          <div v-else class="space-y-10">
            <div v-for="menu in menus" :key="menu.meal_period" class="space-y-4">
              <h3 class="text-lg font-bold text-red-400 uppercase tracking-widest border-b border-white/10 pb-2">{{ menu.meal_period }}</h3>
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
                  <button @click="toggleFavorite(item.name)" class="shrink-0 p-2 rounded-full transition-all focus:outline-none" :class="isFavorite(item.name) ? 'text-red-500 hover:text-red-400 bg-red-500/10' : 'text-slate-600 hover:text-red-400 bg-white/5'">
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

    <!-- Toast notification -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="toast.visible"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-800/90 px-4 py-3 text-sm font-medium text-white shadow-2xl backdrop-blur-xl"
      >
        {{ toast.message }}
      </div>
    </transition>
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

// Toast state
const toast = ref({ visible: false, message: '' })
let toastTimer = null

function showToast(message) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { visible: true, message }
  toastTimer = setTimeout(() => {
    toast.value.visible = false
  }, 2000)
}

// Filters
const filterStatus = ref('all') // 'all', 'open', 'closed'
const filterArea = ref('all')

const uniqueAreas = computed(() => {
  const areas = new Set(halls.value.map(h => h.campus_area).filter(a => a))
  return Array.from(areas).sort()
})

const filteredHalls = computed(() => {
  return halls.value.filter(hall => {
    const open = isOpen(hall)
    if (filterStatus.value === 'open' && !open) return false
    if (filterStatus.value === 'closed' && open) return false
    if (filterArea.value !== 'all' && hall.campus_area !== filterArea.value) return false
    return true
  })
})

onMounted(async () => {
  loadingHalls.value = true
  try {
    const [hallsRes, profileRes] = await Promise.all([
      getDiningHalls(),
      getProfile()
    ])
    halls.value = hallsRes.data
    const favs = profileRes.data.favorite_meals || []
    favoriteMeals.value = new Set(favs)
  } catch (e) {
    console.error(e)
  } finally {
    loadingHalls.value = false
  }
})

// Parses "HH:MM" into a Date object set to today
function parseTimeToday(timeStr) {
  const [hours, minutes] = timeStr.split(':').map(Number)
  const d = new Date()
  d.setHours(hours, minutes, 0, 0)
  return d
}

// Returns the day name that matches the keys in operating_hours
function getTodayName() {
  return new Date().toLocaleDateString('en-US', { weekday: 'long' })
}

function isOpen(hall) {
  if (!hall.operating_hours || typeof hall.operating_hours !== 'object') return false
  const todayName = getTodayName()
  const todayHours = hall.operating_hours[todayName]
  if (!todayHours || !todayHours.open || !todayHours.close) return false
  const now = new Date()
  const openTime = parseTimeToday(todayHours.open)
  const closeTime = parseTimeToday(todayHours.close)
  return now >= openTime && now < closeTime
}

function isClosingSoon(hall) {
  if (!hall.operating_hours || typeof hall.operating_hours !== 'object') return false
  const todayName = getTodayName()
  const todayHours = hall.operating_hours[todayName]
  if (!todayHours || !todayHours.close) return false
  const now = new Date()
  const closeTime = parseTimeToday(todayHours.close)
  const diffMs = closeTime - now
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

function isFavorite(name) {
  return favoriteMeals.value.has(name)
}

async function toggleFavorite(name) {
  const wasFav = isFavorite(name)
  if (wasFav) {
    favoriteMeals.value.delete(name)
    showToast('Removed from favorites')
  } else {
    favoriteMeals.value.add(name)
    showToast('Added to favorites')
  }

  try {
    const res = await toggleFavoriteMeal(name)
    favoriteMeals.value = new Set(res.data.favorite_meals)
  } catch (e) {
    console.error(e)
    // Revert optimistic update on failure
    if (wasFav) {
      favoriteMeals.value.add(name)
    } else {
      favoriteMeals.value.delete(name)
    }
  }
}
</script>
