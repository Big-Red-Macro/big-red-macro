import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useMainStore = defineStore('main', () => {
  const isConnectedToCalendar = ref(false)
  const waitTimes = ref([])
  const itinerary = ref(null)
  const tokenDict = ref(null)
  const isLoading = ref(false)
  const currentError = ref(null)

  // Fetch Auth URL
  const getConnectUrl = async () => {
    try {
      const response = await api.get('/calendar/connect/')
      return response.data.auth_url
    } catch (e) {
      console.error("Failed to generate connect URL", e)
      currentError.value = "Failed to connect to Google Services."
      return null
    }
  }

  // Receive callback
  const submitCalendarCode = async (code, state) => {
    isLoading.value = true
    try {
      // For local demo, we might get a token dictionary back
      const res = await api.get('/calendar/callback/', { params: { code, state } })
      tokenDict.value = res.data.token_dict
      isConnectedToCalendar.value = true
    } catch (e) {
      console.error(e)
      currentError.value = "Failed to authenticate with Google."
    } finally {
      isLoading.value = false
    }
  }

  // Generate Meal Plan
  const generateMealPlan = async () => {
    isLoading.value = true
    try {
      const body = { google_auth_token: tokenDict.value || {} }
      const res = await api.post('/meal-plan/generate-ai/', body)
      if (res.data.ai_plan && !res.data.ai_plan.error) {
        itinerary.value = res.data.ai_plan
      } else {
        currentError.value = res.data.ai_plan?.error || "AI could not generate plan."
      }
    } catch (e) {
      console.error(e)
      currentError.value = "An error occurred while generating the plan."
    } finally {
      isLoading.value = false
    }
  }

  // Wait Times (Mock fetch or real hit to /wait-times/)
  const fetchWaitTimes = async () => {
    // A placeholder for hitting /api/wait-times/
    // Since wait times wasn't fully mocked yet in views, we'll provide some hardcoded data for the demo view.
    waitTimes.value = [
      { id: 1, name: 'Becker House', wait_time: 5, capacity: 'low' },
      { id: 2, name: 'North Star', wait_time: 15, capacity: 'medium' },
      { id: 3, name: 'Okenshields', wait_time: 35, capacity: 'high' }
    ]
  }

  return {
    isConnectedToCalendar,
    waitTimes,
    itinerary,
    tokenDict,
    isLoading,
    currentError,
    getConnectUrl,
    submitCalendarCode,
    generateMealPlan,
    fetchWaitTimes
  }
})
