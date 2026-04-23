import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { getWaitTimes, getProfile } from '../api'

export const useMainStore = defineStore('main', () => {
  const isConnectedToCalendar = ref(false)
  const waitTimes = ref([])
  const itinerary = ref(null)
  const tokenDict = ref(null)
  const isLoading = ref(false)
  const currentError = ref(null)

  // Check if calendar already connected via stored profile token
  const checkCalendarStatus = async () => {
    try {
      const res = await getProfile()
      if (res.data.has_calendar_connected) {
        isConnectedToCalendar.value = true
      }
    } catch (e) {
      // not logged in yet, ignore
    }
  }

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
  const generateMealPlan = async (date = null) => {
    isLoading.value = true
    try {
      const body = { google_auth_token: tokenDict.value || {} }
      if (date) body.date = date
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

  // Wait Times — real API call with mock fallback for demo
  const fetchWaitTimes = async () => {
    try {
      const res = await getWaitTimes()
      waitTimes.value = res.data
    } catch (e) {
      // Fallback mock data so the demo works without a backend
      waitTimes.value = [
        { id: 1, name: 'Becker House', wait_time: 5, capacity: 'low' },
        { id: 2, name: 'North Star', wait_time: 15, capacity: 'medium' },
        { id: 3, name: 'Okenshields', wait_time: 35, capacity: 'high' }
      ]
    }
  }

  return {
    isConnectedToCalendar,
    waitTimes,
    itinerary,
    tokenDict,
    isLoading,
    currentError,
    checkCalendarStatus,
    getConnectUrl,
    submitCalendarCode,
    generateMealPlan,
    fetchWaitTimes
  }
})
