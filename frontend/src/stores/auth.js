import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, loginGoogle as apiLoginGoogle, refreshToken as apiRefresh } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshTokenVal = ref(localStorage.getItem('refresh_token') || null)

  // User info persisted across refreshes
  const userName = ref(localStorage.getItem('user_name') || '')
  const userEmail = ref(localStorage.getItem('user_email') || '')
  const userPicture = ref(localStorage.getItem('user_picture') || '')

  const isAuthenticated = computed(() => !!token.value)

  function setTokens(data) {
    token.value = data.access
    refreshTokenVal.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
  }

  function setUserInfo(user) {
    if (!user) return
    userName.value = user.first_name || user.email || ''
    userEmail.value = user.email || ''
    userPicture.value = user.picture || ''
    localStorage.setItem('user_name', userName.value)
    localStorage.setItem('user_email', userEmail.value)
    localStorage.setItem('user_picture', userPicture.value)
  }

  async function login(username, password) {
    const { data } = await apiLogin(username, password)
    setTokens(data)
  }

  async function loginGoogle(credential) {
    const { data } = await apiLoginGoogle(credential)
    setTokens(data)
    setUserInfo(data.user)
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
    userName.value = ''
    userEmail.value = ''
    userPicture.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_picture')
  }

  return {
    token, isAuthenticated,
    userName, userEmail, userPicture,
    login, loginGoogle, refreshToken, logout
  }
})
