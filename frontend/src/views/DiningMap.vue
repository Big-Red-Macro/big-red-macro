<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Dining Halls</h1>
      <select v-model="period" @change="dining.fetchWaitTimes(period)" class="input w-auto text-sm">
        <option value="breakfast">Breakfast</option>
        <option value="lunch">Lunch</option>
        <option value="dinner">Dinner</option>
      </select>
    </div>

    <p class="text-sm text-cornell-gray">
      Wait times are predicted based on historical foot traffic and time of day.
    </p>

    <div v-if="dining.loading" class="text-center py-10 text-cornell-gray">Loading…</div>

    <div v-else class="space-y-2">
      <DiningHallCard
        v-for="hall in sortedHalls"
        :key="hall.id"
        :hall="hall"
        :waitMinutes="dining.waitForHall(hall.id)"
      />
    </div>

    <!-- Checkin -->
    <div class="card" v-if="nearestHall">
      <h2 class="font-semibold mb-2">You're near {{ nearestHall.name }}</h2>
      <p class="text-sm text-cornell-gray mb-3">
        Checked in? Help others by reporting the current wait.
      </p>
      <div class="flex gap-2">
        <input
          v-model.number="reportedWait"
          type="number"
          min="0"
          max="60"
          placeholder="Wait (min)"
          class="input w-32"
        />
        <button @click="submitCheckin" class="btn-primary" :disabled="submitting">
          {{ submitting ? 'Submitting…' : 'Report Wait' }}
        </button>
      </div>
      <p v-if="checkinMsg" class="text-sm text-green-600 mt-2">{{ checkinMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGeolocation } from '@vueuse/core'
import { useDiningStore } from '@/stores/dining'
import { recordCheckin } from '@/api'
import DiningHallCard from '@/components/DiningHallCard.vue'

const dining = useDiningStore()
const { coords } = useGeolocation()
const period = ref('lunch')
const reportedWait = ref(null)
const submitting = ref(false)
const checkinMsg = ref('')

function distance(hall) {
  if (!coords.value?.latitude) return Infinity
  const dlat = hall.location_lat - coords.value.latitude
  const dlng = hall.location_lng - coords.value.longitude
  return Math.sqrt(dlat ** 2 + dlng ** 2)
}

const sortedHalls = computed(() =>
  [...dining.halls].sort((a, b) => {
    const wa = dining.waitForHall(a.id) ?? 999
    const wb = dining.waitForHall(b.id) ?? 999
    return wa - wb
  })
)

const nearestHall = computed(() => {
  if (!coords.value?.latitude || !dining.halls.length) return null
  return [...dining.halls].sort((a, b) => distance(a) - distance(b))[0]
})

async function submitCheckin() {
  if (!nearestHall.value || reportedWait.value === null) return
  submitting.value = true
  try {
    await recordCheckin(nearestHall.value.id, reportedWait.value)
    checkinMsg.value = 'Thanks for reporting!'
    reportedWait.value = null
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await dining.fetchHalls()
  await dining.fetchWaitTimes(period.value)
})
</script>
