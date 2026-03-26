import axios from 'axios'
import ENDPOINTS from '../config/api'

const api = axios.create({
  baseURL: ENDPOINTS._base,
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

export const authAPI = {
  register: (data) => api.post(ENDPOINTS.auth.register, data),
  login: (data) => api.post(ENDPOINTS.auth.login, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
  me: () => api.get(ENDPOINTS.auth.me)
}

export const productsAPI = {
  getAll: (params) => api.get(ENDPOINTS.products.list, { params }),
  getFeatured: () => api.get(ENDPOINTS.products.featured),
  getBySlug: (slug) => api.get(ENDPOINTS.products.bySlug(slug)),
  getReviews: (productId) => api.get(ENDPOINTS.products.reviews(productId)),
  getPopular: () => api.get(ENDPOINTS.recommendations.popular),
  getNewArrivals: () => api.get(ENDPOINTS.recommendations.newArrivals),
  getSimilar: (productId) => api.get(ENDPOINTS.recommendations.similar(productId)),
  getBoughtTogether: (productId) => api.get(ENDPOINTS.recommendations.boughtTogether(productId)),
  getForYou: () => api.get(ENDPOINTS.recommendations.forYou)
}

export const categoriesAPI = {
  getAll: () => api.get(ENDPOINTS.categories.list),
  getBySlug: (slug) => api.get(ENDPOINTS.categories.bySlug(slug))
}

export const cartAPI = {
  get: (params) => api.get(ENDPOINTS.cart.get, { params }),
  add: (data) => api.post(ENDPOINTS.cart.add, null, { params: data }),
  update: (itemId, quantity) => api.put(ENDPOINTS.cart.update(itemId), null, { params: { quantity } }),
  remove: (itemId) => api.delete(ENDPOINTS.cart.remove(itemId)),
  clear: (params) => api.delete(ENDPOINTS.cart.clear, { params })
}

export const ordersAPI = {
  getAll: (userId) => api.get(ENDPOINTS.orders.list, { params: { user_id: userId } }),
  getOne: (orderNumber, userId) => api.get(ENDPOINTS.orders.byNumber(orderNumber), { params: { user_id: userId } }),
  checkout: (data) => api.post(ENDPOINTS.orders.checkout, data),
  pay: (orderNumber) => api.post(ENDPOINTS.orders.pay(orderNumber))
}

export const usersAPI = {
  get: (userId) => api.get(ENDPOINTS.users.get(userId)),
  update: (userId, data) => api.put(ENDPOINTS.users.update(userId), data),
  getAddresses: (userId) => api.get(ENDPOINTS.users.addresses(userId)),
  addAddress: (userId, data) => api.post(ENDPOINTS.users.addAddress(userId), data)
}

export const adminAPI = {
  getDashboard: () => api.get(ENDPOINTS.admin.dashboard),
  getSalesByCategory: () => api.get(ENDPOINTS.admin.salesByCategory),
  getSalesOverTime: (days = 30) => api.get(ENDPOINTS.admin.salesOverTime, { params: { days } }),
  getTopProducts: (limit = 10) => api.get(ENDPOINTS.admin.topProducts, { params: { limit } }),
  getRecentOrders: (limit = 10) => api.get(ENDPOINTS.admin.recentOrders, { params: { limit } })
}

export const forecastingAPI = {
  getDashboard: () => api.get(ENDPOINTS.forecasting.dashboard),
  getForecast: (productId, daysAhead = 30, includeSeasonal = true) => 
    api.get(ENDPOINTS.forecasting.forecast(productId), { params: { days_ahead: daysAhead, include_seasonal: includeSeasonal } }),
  getSeasonalPatterns: (productId) => api.get(ENDPOINTS.forecasting.seasonalPatterns(productId)),
  setSeasonalPattern: (productId, data) => api.post(ENDPOINTS.forecasting.seasonalPatterns(productId), data),
  getAutoOrderSettings: (productId) => api.get(ENDPOINTS.forecasting.autoOrderSettings(productId)),
  updateAutoOrderSettings: (productId, data) => api.put(ENDPOINTS.forecasting.autoOrderSettings(productId), data),
  processAutoOrders: () => api.post(ENDPOINTS.forecasting.autoOrderProcess),
  getPurchaseOrders: (status) => api.get(ENDPOINTS.forecasting.purchaseOrders, { params: { status } }),
  getPurchaseOrder: (orderId) => api.get(ENDPOINTS.forecasting.purchaseOrderById(orderId)),
  createPurchaseOrder: (data) => api.post(ENDPOINTS.forecasting.purchaseOrders, data),
  recordSales: (productId, quantity, revenue = 0, date = null) => 
    api.post(ENDPOINTS.forecasting.recordSales(productId), null, { params: { quantity, revenue, date } })
}

export const seedAPI = {
  seedForecasting: (days = 90) => api.post(ENDPOINTS.seed.forecasting, null, { params: { days } }),
  seedStock: (minStock = 20, maxStock = 100) => api.post(ENDPOINTS.seed.stock, null, { params: { min_stock: minStock, max_stock: maxStock } })
}

export const inventoryAPI = {
  getDashboard: () => api.get(ENDPOINTS.inventory.dashboard),
  getProducts: (params) => api.get(ENDPOINTS.inventory.products, { params }),
  getAlerts: () => api.get(ENDPOINTS.inventory.alerts),
  adjustStock: (data) => api.post(ENDPOINTS.inventory.adjustStock, null, { params: data }),
  resolveAlert: (alertId) => api.post(ENDPOINTS.inventory.resolveAlert(alertId)),
  getSuppliers: () => api.get(ENDPOINTS.inventory.suppliers),
  createSupplier: (data) => api.post(ENDPOINTS.inventory.suppliers, data),
  updateSupplier: (supplierId, data) => api.put(`${ENDPOINTS.inventory.suppliers}/${supplierId}`, data),
  deleteSupplier: (supplierId) => api.delete(`${ENDPOINTS.inventory.suppliers}/${supplierId}`)
}

export const inventoryMLAPI = {
  getAllPredictions: () => api.get(ENDPOINTS.inventoryML.predictions),
  getProductPrediction: (productId, days = 30) => api.get(ENDPOINTS.inventoryML.predictionByProduct(productId), { params: { days } }),
  createRefillRequest: (data) => api.post(ENDPOINTS.inventoryML.refillRequests, data),
  getRefillRequests: (status) => api.get(ENDPOINTS.inventoryML.refillRequests, { params: { status } }),
  getRefillRequest: (requestId) => api.get(ENDPOINTS.inventoryML.refillRequestById(requestId)),
  approveRefill: (requestId, approved, notes = '') => api.post(ENDPOINTS.inventoryML.approveRefill(requestId), { approved, notes }),
  markOrdered: (requestId) => api.post(ENDPOINTS.inventoryML.markOrdered(requestId)),
  receiveRefill: (requestId, actualQuantity, actualCost = null) => api.post(ENDPOINTS.inventoryML.receiveRefill(requestId), { actual_quantity: actualQuantity, actual_cost: actualCost }),
  cancelRefill: (requestId) => api.post(ENDPOINTS.inventoryML.cancelRefill(requestId))
}

export const rbacAPI = {
  getPermissions: () => api.get(ENDPOINTS.rbac.permissions),
  getRoles: () => api.get(ENDPOINTS.rbac.roles),
  getUserRoles: (userId) => api.get(ENDPOINTS.rbac.userRoles(userId)),
  assignRole: (userId, data) => api.put(ENDPOINTS.rbac.assignRole(userId), data),
  setStaff: (userId, isStaff) => api.put(ENDPOINTS.rbac.setStaff(userId), null, { params: { is_staff: isStaff } }),
  getMyPermissions: () => api.get(ENDPOINTS.rbac.myPermissions),
  seedDefaults: () => api.post(ENDPOINTS.rbac.seedDefaults)
}

export const deliveryAPI = {
  createDelivery: (data) => api.post(ENDPOINTS.delivery.create, data),
  trackShipment: (trackingNumber) => api.get(ENDPOINTS.delivery.track(trackingNumber)),
  cancelShipment: (trackingNumber) => api.post(ENDPOINTS.delivery.cancel(trackingNumber)),
  getProviders: () => api.get(ENDPOINTS.delivery.providers)
}

export default api