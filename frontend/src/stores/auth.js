import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, refreshToken as apiRefresh } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshTokenVal = ref(localStorage.getItem('refresh_token') || null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const { data } = await apiLogin(username, password)
    token.value = data.access
    refreshTokenVal.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
  }

  async function refreshToken() {
    if (!refreshTokenVal.value) return false
    try {
      const { data } = await apiRefresh(refreshTokenVal.value)
      token.value = data.access
      localStorage.setItem('access_token', data.access)
      return true
    } catch {
      return false
    }
  }

  function logout() {
    token.value = null
    refreshTokenVal.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { token, isAuthenticated, login, refreshToken, logout }
})
