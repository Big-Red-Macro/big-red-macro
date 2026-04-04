import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const auth = useAuthStore()
    if (err.response?.status === 401 && !err.config._retry) {
      err.config._retry = true
      const refreshed = await auth.refreshToken()
      if (refreshed) {
        err.config.headers.Authorization = `Bearer ${auth.token}`
        return api(err.config)
      }
      auth.logout()
    }
    return Promise.reject(err)
  }
)

export default api

// -- Auth --
export const login = (username, password) =>
  api.post('/auth/login/', { username, password })

export const refreshToken = (refresh) =>
  api.post('/auth/refresh/', { refresh })

// -- Profile --
export const getProfile = () => api.get('/profile/')
export const updateProfile = (data) => api.put('/profile/', data)
export const toggleFavoriteMeal = (meal_name) => api.post('/profile/favorite-meal/', { meal_name })

// -- Meal Plans --
export const generateMealPlan = (date, location) =>
  api.post('/meal-plan/generate/', { date, location })
export const getMealPlanHistory = () => api.get('/meal-plan/history/')

// -- Dining Halls --
export const getDiningHalls = () => api.get('/dining-halls/')
export const getDiningHallMenu = (hallId, date, period) =>
  api.get(`/dining-halls/${hallId}/menu/`, { params: { date, period } })

// -- Wait Times --
export const getWaitTimes = (period) =>
  api.get('/wait-times/', { params: { period } })
export const recordCheckin = (diningHallId, waitMinutes) =>
  api.post('/checkin/', {
    dining_hall_id: diningHallId,
    estimated_wait_minutes: waitMinutes,
  })
