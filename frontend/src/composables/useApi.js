import { ref } from 'vue'
import axios from 'axios'
import ENDPOINTS from '../config/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: `${API_BASE_URL}`,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

export function useAuth() {
  const loading = ref(false)
  const error = ref(null)
  const user = ref(null)

  const register = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(ENDPOINTS.auth.register, data)
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Registration failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  const login = async (credentials) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(ENDPOINTS.auth.login, credentials, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      localStorage.setItem('token', response.data.access_token)
      await fetchUser()
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Login failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get(ENDPOINTS.auth.me)
      user.value = response.data
    } catch (e) {
      user.value = null
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    user.value = null
  }

  return { loading, error, user, register, login, fetchUser, logout }
}

export function useProducts() {
  const loading = ref(false)
  const products = ref([])
  const error = ref(null)

  const fetchProducts = async (params) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.products.list, { params })
      products.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchBySlug = async (slug) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.products.bySlug(slug))
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading, products, error, fetchProducts, fetchBySlug }
}

export function useCart() {
  const loading = ref(false)
  const items = ref([])
  const error = ref(null)

  const fetchCart = async (userId) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.cart.get, { params: { user_id: userId } })
      items.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const addItem = async (data) => {
    loading.value = true
    try {
      const response = await api.post(ENDPOINTS.cart.add, null, { params: data })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateQuantity = async (itemId, quantity) => {
    try {
      const response = await api.put(ENDPOINTS.cart.update(itemId), null, { params: { quantity } })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const removeItem = async (itemId) => {
    try {
      await api.delete(ENDPOINTS.cart.remove(itemId))
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return { loading, items, error, fetchCart, addItem, updateQuantity, removeItem }
}

export function useOrders() {
  const loading = ref(false)
  const orders = ref([])
  const error = ref(null)

  const fetchOrders = async (userId) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.orders.list, { params: { user_id: userId } })
      orders.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const checkout = async (data) => {
    loading.value = true
    try {
      const response = await api.post(ENDPOINTS.orders.checkout, data)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading, orders, error, fetchOrders, checkout }
}

export function useForecasting() {
  const loading = ref(false)
  const forecasts = ref([])
  const error = ref(null)

  const fetchDashboard = async () => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.forecasting.dashboard)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchForecast = async (productId, daysAhead = 30) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.forecasting.forecast(productId), {
        params: { days_ahead: daysAhead }
      })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateAutoOrder = async (productId, data) => {
    try {
      const response = await api.put(ENDPOINTS.forecasting.autoOrderSettings(productId), data)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const fetchPurchaseOrders = async () => {
    try {
      const response = await api.get(ENDPOINTS.forecasting.purchaseOrders)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return { loading, forecasts, error, fetchDashboard, fetchForecast, updateAutoOrder, fetchPurchaseOrders }
}

export function useInventoryML() {
  const loading = ref(false)
  const predictions = ref([])
  const refillRequests = ref([])
  const error = ref(null)

  const fetchPredictions = async () => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.inventoryML.predictions)
      predictions.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchRefillRequests = async (status) => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.inventoryML.refillRequests, { params: { status } })
      refillRequests.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const createRefillRequest = async (data) => {
    try {
      const response = await api.post(ENDPOINTS.inventoryML.refillRequests, data)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const approveRefill = async (requestId, approved, notes) => {
    try {
      const response = await api.post(ENDPOINTS.inventoryML.approveRefill(requestId), { approved, notes })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const receiveRefill = async (requestId, actualQuantity, actualCost) => {
    try {
      const response = await api.post(ENDPOINTS.inventoryML.receiveRefill(requestId), {
        actual_quantity: actualQuantity,
        actual_cost: actualCost
      })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    loading, predictions, refillRequests, error,
    fetchPredictions, fetchRefillRequests, createRefillRequest, approveRefill, receiveRefill
  }
}

export function useInventory() {
  const loading = ref(false)
  const dashboard = ref(null)
  const alerts = ref([])
  const error = ref(null)

  const fetchDashboard = async () => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.inventory.dashboard)
      dashboard.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchAlerts = async () => {
    try {
      const response = await api.get(ENDPOINTS.inventory.alerts)
      alerts.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return { loading, dashboard, alerts, error, fetchDashboard, fetchAlerts }
}

export function useRbac() {
  const loading = ref(false)
  const permissions = ref([])
  const roles = ref([])
  const error = ref(null)

  const fetchPermissions = async () => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.rbac.permissions)
      permissions.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchRoles = async () => {
    loading.value = true
    try {
      const response = await api.get(ENDPOINTS.rbac.roles)
      roles.value = response.data
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchUserRoles = async (userId) => {
    try {
      const response = await api.get(ENDPOINTS.rbac.userRoles(userId))
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const assignRole = async (userId, data) => {
    try {
      const response = await api.put(ENDPOINTS.rbac.assignRole(userId), data)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const setStaff = async (userId, isStaff) => {
    try {
      const response = await api.put(ENDPOINTS.rbac.setStaff(userId), null, { params: { is_staff: isStaff } })
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const getMyPermissions = async () => {
    try {
      const response = await api.get(ENDPOINTS.rbac.myPermissions)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const seedDefaults = async () => {
    try {
      const response = await api.post(ENDPOINTS.rbac.seedDefaults)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return { 
    loading, permissions, roles, error, 
    fetchPermissions, fetchRoles, fetchUserRoles, assignRole, setStaff, getMyPermissions, seedDefaults
  }
}

export function useDelivery() {
  const loading = ref(false)
  const error = ref(null)

  const createDelivery = async (data) => {
    loading.value = true
    try {
      const response = await api.post(ENDPOINTS.delivery.create, data)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const trackShipment = async (trackingNumber) => {
    try {
      const response = await api.get(ENDPOINTS.delivery.track(trackingNumber))
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const cancelShipment = async (trackingNumber) => {
    try {
      const response = await api.post(ENDPOINTS.delivery.cancel(trackingNumber))
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  const getProviders = async () => {
    try {
      const response = await api.get(ENDPOINTS.delivery.providers)
      return response.data
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return { loading, error, createDelivery, trackShipment, cancelShipment, getProviders }
}

export default {
  useAuth,
  useProducts,
  useCart,
  useOrders,
  useForecasting,
  useInventoryML,
  useInventory,
  api
}