import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from 'src/boot/api'
import router from 'src/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const userId = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  function init() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    const savedUserId = localStorage.getItem('userId')
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
      userId.value = savedUserId
    }
  }

  async function login(username, password) {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    const res = await authAPI.login(formData)
    token.value = res.data.access_token
    
    localStorage.setItem('token', token.value)
    
    const meRes = await authAPI.me()
    user.value = meRes.data
    userId.value = meRes.data.id
    
    localStorage.setItem('user', JSON.stringify(user.value))
    localStorage.setItem('userId', userId.value)
    
    router.push('/')
  }

  async function register(data) {
    const res = await authAPI.register(data)
    user.value = res.data
    userId.value = res.data.id
    localStorage.setItem('user', JSON.stringify(user.value))
    localStorage.setItem('userId', userId.value)
    router.push('/')
  }

  function logout() {
    token.value = null
    user.value = null
    userId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('userId')
  }

  return { user, token, userId, isAuthenticated, init, login, register, logout }
})