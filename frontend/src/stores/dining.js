import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getDiningHalls, getWaitTimes } from '@/api'

export const useDiningStore = defineStore('dining', () => {
  const halls = ref([])
  const waitTimes = ref([])
  const loading = ref(false)

  async function fetchHalls() {
    loading.value = true
    try {
      const { data } = await getDiningHalls()
      halls.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchWaitTimes(period = 'lunch') {
    const { data } = await getWaitTimes(period)
    waitTimes.value = data
  }

  function waitForHall(hallId) {
    return waitTimes.value.find((w) => w.dining_hall_id === hallId)
      ?.estimated_wait_minutes ?? null
  }

  return { halls, waitTimes, loading, fetchHalls, fetchWaitTimes, waitForHall }
})
