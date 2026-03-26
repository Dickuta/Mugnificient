const API_VERSION = '/v1'
const API_BASE_URL = `/api${API_VERSION}`

export const ENDPOINTS = {
  _base: API_BASE_URL,
  auth: {
    register: '/auth/register',
    login: '/auth/login',
    me: '/auth/me'
  },
  products: {
    list: '/products/',
    featured: '/products/featured',
    bySlug: (slug) => `/products/${slug}`,
    reviews: (id) => `/products/${id}/reviews`
  },
  categories: {
    list: '/categories/',
    bySlug: (slug) => `/categories/${slug}`
  },
  cart: {
    get: '/cart/',
    add: '/cart/add',
    update: (id) => `/cart/item/${id}`,
    remove: (id) => `/cart/item/${id}`,
    clear: '/cart/clear'
  },
  orders: {
    list: '/orders/',
    byNumber: (num) => `/orders/${num}`,
    checkout: '/orders/checkout',
    pay: (num) => `/orders/${num}/pay`
  },
  users: {
    get: (id) => `/users/${id}`,
    update: (id) => `/users/${id}`,
    addresses: (id) => `/users/${id}/addresses`,
    addAddress: (id) => `/users/${id}/addresses`
  },
  admin: {
    dashboard: '/admin/dashboard',
    salesByCategory: '/admin/sales-by-category',
    salesOverTime: '/admin/sales-over-time',
    topProducts: '/admin/top-products',
    recentOrders: '/admin/recent-orders'
  },
  forecasting: {
    dashboard: '/forecasting/dashboard',
    forecast: (id) => `/forecasting/products/${id}/forecast`,
    seasonalPatterns: (id) => `/forecasting/products/${id}/seasonal-patterns`,
    recordSales: (id) => `/forecasting/products/${id}/record-sales`,
    autoOrderSettings: (id) => `/forecasting/auto-order/settings/${id}`,
    autoOrderProcess: '/forecasting/auto-order/process',
    purchaseOrders: '/forecasting/purchase-orders',
    purchaseOrderById: (id) => `/forecasting/purchase-orders/${id}`
  },
  inventory: {
    dashboard: '/inventory/dashboard',
    products: '/inventory/products',
    alerts: '/inventory/alerts',
    adjustStock: '/inventory/stock/adjust',
    resolveAlert: (id) => `/inventory/alerts/${id}/resolve`,
    suppliers: '/inventory/suppliers'
  },
  inventoryML: {
    predictions: '/inventory-ml/predictions',
    predictionByProduct: (id) => `/inventory-ml/predictions/${id}`,
    refillRequests: '/inventory-ml/refill-requests',
    refillRequestById: (id) => `/inventory-ml/refill-requests/${id}`,
    approveRefill: (id) => `/inventory-ml/refill-requests/${id}/approve`,
    markOrdered: (id) => `/inventory-ml/refill-requests/${id}/mark-ordered`,
    receiveRefill: (id) => `/inventory-ml/refill-requests/${id}/receive`,
    cancelRefill: (id) => `/inventory-ml/refill-requests/${id}/cancel`
  },
  recommendations: {
    popular: '/recommendations/popular',
    newArrivals: '/recommendations/new-arrivals',
    similar: (id) => `/recommendations/similar/${id}`,
    boughtTogether: (id) => `/recommendations/bought-together/${id}`,
    forYou: '/recommendations/for-you'
  },
  seed: {
    forecasting: '/seed/forecasting',
    stock: '/seed/stock'
  },
  rbac: {
    permissions: '/rbac/permissions',
    roles: '/rbac/roles',
    userRoles: (userId) => `/rbac/users/${userId}/roles`,
    assignRole: (userId) => `/rbac/users/${userId}/roles`,
    setStaff: (userId) => `/rbac/users/${userId}/staff`,
    myPermissions: '/rbac/my-permissions',
    seedDefaults: '/rbac/seed-defaults'
  },
  delivery: {
    create: '/delivery/create',
    track: (trackingNumber) => `/delivery/track/${trackingNumber}`,
    cancel: (trackingNumber) => `/delivery/cancel/${trackingNumber}`,
    providers: '/delivery/providers'
  }
}

export default ENDPOINTS