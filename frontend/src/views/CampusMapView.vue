<template>
  <div class="p-6 lg:p-10 space-y-6 max-w-6xl mx-auto">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white tracking-tight">Campus Map</h1>
      <p class="text-slate-400 text-sm mt-1">Tap a dining hall to get walking directions from your current location.</p>
    </div>

    <!-- Map -->
    <CampusMap
      :halls="halls"
      :access-token="mapboxToken"
      map-height="500px"
      @hall-click="onHallClick"
    />

    <!-- Hall list under map -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <button
        v-for="hall in halls"
        :key="hall.id || hall.name"
        @click="onHallClick(hall)"
        class="flex items-center gap-3 p-3 rounded-xl border transition-all"
        :class="selectedHall?.name === hall.name
          ? 'border-red-500/40 bg-red-500/10 text-white'
          : 'border-white/5 bg-white/[0.02] text-slate-300 hover:bg-white/5 hover:border-white/10'"
      >
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8h2.5v8H21V2c-2.76 0-5 2.24-5 4z"/></svg>
        </div>
        <div class="text-left">
          <p class="text-sm font-medium">{{ hall.name }}</p>
          <p class="text-xs text-slate-500">{{ hall.campus_area || 'Campus' }}</p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CampusMap from '@/components/CampusMap.vue'
import { getDiningHalls } from '@/api'

const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN || ''
const halls = ref([])
const selectedHall = ref(null)

function onHallClick(hall) {
  selectedHall.value = hall
}

onMounted(async () => {
  try {
    const res = await getDiningHalls()
    halls.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load dining halls:', e)
    // Fallback hardcoded Cornell halls for demo
    halls.value = [
      { name: 'Okenshields', short_name: 'okenshields', location_lat: 42.4490, location_lng: -76.4837, campus_area: 'Central' },
      { name: 'North Star', short_name: 'north_star', location_lat: 42.4533, location_lng: -76.4782, campus_area: 'North' },
      { name: 'Morrison Dining', short_name: 'morrison', location_lat: 42.4467, location_lng: -76.4835, campus_area: 'West' },
      { name: 'Risley Dining', short_name: 'risley', location_lat: 42.4556, location_lng: -76.4794, campus_area: 'North' },
      { name: 'Becker House', short_name: 'becker', location_lat: 42.4456, location_lng: -76.4870, campus_area: 'West' },
      { name: 'Rose House', short_name: 'rose', location_lat: 42.4452, location_lng: -76.4880, campus_area: 'West' },
      { name: 'Keeton House', short_name: 'keeton', location_lat: 42.4447, location_lng: -76.4883, campus_area: 'West' },
      { name: 'Cook House', short_name: 'cook', location_lat: 42.4460, location_lng: -76.4868, campus_area: 'West' },
    ]
  }
})
</script>
