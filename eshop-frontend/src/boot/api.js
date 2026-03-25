import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
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
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
  me: () => api.get('/auth/me')
}

export const productsAPI = {
  getAll: (params) => api.get('/products/', { params }),
  getFeatured: () => api.get('/products/featured'),
  getBySlug: (slug) => api.get(`/products/${slug}`),
  getReviews: (productId) => api.get(`/products/${productId}/reviews`),
  getPopular: () => api.get('/recommendations/popular'),
  getNewArrivals: () => api.get('/recommendations/new-arrivals'),
  getSimilar: (productId) => api.get(`/recommendations/similar/${productId}`),
  getBoughtTogether: (productId) => api.get(`/recommendations/bought-together/${productId}`),
  getForYou: () => api.get('/recommendations/for-you')
}

export const categoriesAPI = {
  getAll: () => api.get('/categories/'),
  getBySlug: (slug) => api.get(`/categories/${slug}`)
}

export const cartAPI = {
  get: (params) => api.get('/cart/', { params }),
  add: (data) => api.post('/cart/add', null, { params: data }),
  update: (itemId, quantity) => api.put(`/cart/item/${itemId}`, null, { params: { quantity } }),
  remove: (itemId) => api.delete(`/cart/item/${itemId}`),
  clear: (params) => api.delete('/cart/clear', { params })
}

export const ordersAPI = {
  getAll: (userId) => api.get('/orders/', { params: { user_id: userId } }),
  getOne: (orderNumber, userId) => api.get(`/orders/${orderNumber}`, { params: { user_id: userId } }),
  checkout: (data) => api.post('/orders/checkout', data),
  pay: (orderNumber) => api.post(`/orders/${orderNumber}/pay`)
}

export const usersAPI = {
  get: (userId) => api.get(`/users/${userId}`),
  update: (userId, data) => api.put(`/users/${userId}`, data),
  getAddresses: (userId) => api.get(`/users/${userId}/addresses`),
  addAddress: (userId, data) => api.post(`/users/${userId}/addresses`, data)
}

export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getSalesByCategory: () => api.get('/admin/sales-by-category'),
  getSalesOverTime: (days = 30) => api.get('/admin/sales-over-time', { params: { days } }),
  getTopProducts: (limit = 10) => api.get('/admin/top-products', { params: { limit } }),
  getRecentOrders: (limit = 10) => api.get('/admin/recent-orders', { params: { limit } })
}

export default api