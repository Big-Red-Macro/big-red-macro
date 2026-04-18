<template>
  <div class="relative w-full rounded-2xl overflow-hidden border border-white/10 shadow-lg">
    <div ref="mapContainer" class="w-full" :style="{ height: mapHeight }"></div>
    
    <!-- Route info overlay -->
    <transition name="fade">
      <div v-if="routeInfo" class="absolute bottom-4 left-4 right-4 bg-slate-900/90 backdrop-blur-md rounded-xl border border-white/10 p-4 flex items-center justify-between">
        <div>
          <p class="text-white font-semibold text-sm">{{ routeInfo.hallName }}</p>
          <p class="text-slate-400 text-xs mt-0.5">
            🚶 {{ routeInfo.walkMinutes }} min walk · {{ routeInfo.distanceMi }} mi
          </p>
        </div>
        <button @click="clearRoute" class="text-slate-400 hover:text-white transition-colors text-xs px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10">
          Clear
        </button>
      </div>
    </transition>

    <!-- Loading overlay -->
    <div v-if="loadingRoute" class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-10">
      <div class="flex items-center gap-2 text-white text-sm">
        <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        Finding route…
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

const props = defineProps({
  halls: { type: Array, default: () => [] },
  mapHeight: { type: String, default: '400px' },
  accessToken: { type: String, required: true },
})

const emit = defineEmits(['hallClick'])

const mapContainer = ref(null)
const routeInfo = ref(null)
const loadingRoute = ref(false)

let map = null
let userMarker = null
let markers = []

// Cornell campus center
const CORNELL_CENTER = [-76.4735, 42.4534]

function initMap() {
  mapboxgl.accessToken = props.accessToken

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/dark-v11',
    center: CORNELL_CENTER,
    zoom: 14.5,
    pitch: 30,
  })

  map.addControl(new mapboxgl.NavigationControl(), 'top-right')

  const geolocate = new mapboxgl.GeolocateControl({
    positionOptions: { enableHighAccuracy: true },
    trackUserLocation: true,
    showUserHeading: true,
  })
  map.addControl(geolocate, 'top-right')

  map.on('load', () => {
    addHallMarkers()
    
    // Add empty route source
    map.addSource('route', {
      type: 'geojson',
      data: { type: 'Feature', geometry: { type: 'LineString', coordinates: [] } },
    })
    map.addLayer({
      id: 'route-line',
      type: 'line',
      source: 'route',
      layout: { 'line-join': 'round', 'line-cap': 'round' },
      paint: {
        'line-color': '#ef4444',
        'line-width': 4,
        'line-opacity': 0.8,
      },
    })

    // Try to trigger geolocation
    geolocate.trigger()
  })

  // Track user position
  geolocate.on('geolocate', (e) => {
    if (!userMarker) {
      userMarker = { lng: e.coords.longitude, lat: e.coords.latitude }
    } else {
      userMarker.lng = e.coords.longitude
      userMarker.lat = e.coords.latitude
    }
  })
}

function addHallMarkers() {
  // Clear existing
  markers.forEach((m) => m.remove())
  markers = []

  props.halls.forEach((hall) => {
    if (!hall.location_lat || !hall.location_lng) return

    const el = document.createElement('div')
    el.className = 'hall-marker'
    el.innerHTML = `
      <div style="
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.3);
        display: flex; align-items: center; justify-content: center;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(220,38,38,0.4);
        transition: transform 0.2s;
      ">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
          <path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8h2.5v8H21V2c-2.76 0-5 2.24-5 4z"/>
        </svg>
      </div>
    `
    el.addEventListener('mouseenter', () => {
      el.firstElementChild.style.transform = 'scale(1.2)'
    })
    el.addEventListener('mouseleave', () => {
      el.firstElementChild.style.transform = 'scale(1)'
    })

    const popup = new mapboxgl.Popup({ offset: 20, closeButton: false })
      .setHTML(`
        <div style="font-family: system-ui; padding: 4px 0;">
          <strong style="color: #1e293b;">${hall.name}</strong>
          <p style="margin: 4px 0 0; color: #64748b; font-size: 12px;">${hall.campus_area || ''} Campus</p>
        </div>
      `)

    const marker = new mapboxgl.Marker({ element: el })
      .setLngLat([hall.location_lng, hall.location_lat])
      .setPopup(popup)
      .addTo(map)

    el.addEventListener('click', () => {
      emit('hallClick', hall)
      getWalkingRoute(hall)
    })

    markers.push(marker)
  })
}

async function getWalkingRoute(hall) {
  if (!userMarker) {
    // No user location — just fly to the hall
    map.flyTo({ center: [hall.location_lng, hall.location_lat], zoom: 16 })
    return
  }

  loadingRoute.value = true
  const start = `${userMarker.lng},${userMarker.lat}`
  const end = `${hall.location_lng},${hall.location_lat}`

  try {
    const url = `https://api.mapbox.com/directions/v5/mapbox/walking/${start};${end}?geometries=geojson&access_token=${props.accessToken}`
    const res = await fetch(url)
    const data = await res.json()

    if (data.routes && data.routes.length) {
      const route = data.routes[0]
      map.getSource('route').setData({
        type: 'Feature',
        geometry: route.geometry,
      })

      routeInfo.value = {
        hallName: hall.name,
        walkMinutes: Math.round(route.duration / 60),
        distanceMi: (route.distance * 0.000621371).toFixed(2),
      }

      // Fit map to route bounds
      const coords = route.geometry.coordinates
      const bounds = coords.reduce(
        (b, c) => b.extend(c),
        new mapboxgl.LngLatBounds(coords[0], coords[0])
      )
      map.fitBounds(bounds, { padding: 80 })
    }
  } catch (e) {
    console.error('Failed to fetch walking route:', e)
  } finally {
    loadingRoute.value = false
  }
}

function clearRoute() {
  routeInfo.value = null
  if (map.getSource('route')) {
    map.getSource('route').setData({
      type: 'Feature',
      geometry: { type: 'LineString', coordinates: [] },
    })
  }
  map.flyTo({ center: CORNELL_CENTER, zoom: 14.5, pitch: 30 })
}

watch(() => props.halls, () => {
  if (map && map.loaded()) {
    addHallMarkers()
  }
}, { deep: true })

onMounted(() => {
  nextTick(() => initMap())
})

onUnmounted(() => {
  if (map) map.remove()
})
</script>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
