import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})


export default api

// -- Auth --
export const login = (username, password) =>
  api.post('/auth/login/', { username, password })

export const loginGoogle = (credential) =>
  api.post('/auth/google/', { credential })

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
