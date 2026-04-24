import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { getWaitTimes } from '../api'

export const useMainStore = defineStore('main', () => {
  const waitTimes = ref([])
  const itinerary = ref(null)
  const isLoading = ref(false)
  const currentError = ref(null)
  const chatbotMessages = ref([])


  // Generate Meal Plan
  const generateMealPlan = async () => {
    isLoading.value = true
    try {
      const body = {}
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
  const askChatbot = async (question) => {
    isLoading.value = true
    try {
      const res = await api.post('/chatbot/ask/', { question })
      if (res.data && res.data.answer) {
        chatbotMessages.value.push({ role: 'bot', text: res.data.answer })
      } else {
        chatbotMessages.value.push({ role: 'bot', text: res.data.error || "Sorry, I couldn't understand that." })
      }
    } catch (e) {
      console.error(e)
      chatbotMessages.value.push({ role: 'bot', text: "An error occurred while talking to the chatbot." })
    } finally {
      isLoading.value = false
    }
  }

  return {
    waitTimes,
    itinerary,
    isLoading,
    currentError,
    chatbotMessages,
    generateMealPlan,
    fetchWaitTimes,
    askChatbot
  }
})
