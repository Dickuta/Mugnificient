const API_BASE_URL = '/api/v1'

export const ENDPOINTS = {
  _base: API_BASE_URL,
  auth: {
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
    me: `${API_BASE_URL}/auth/me`
  },
  products: {
    list: `${API_BASE_URL}/products/`,
    featured: `${API_BASE_URL}/products/featured`,
    bySlug: (slug) => `${API_BASE_URL}/products/${slug}`,
    reviews: (id) => `${API_BASE_URL}/products/${id}/reviews`
  },
  categories: {
    list: `${API_BASE_URL}/categories/`,
    bySlug: (slug) => `${API_BASE_URL}/categories/${slug}`
  },
  cart: {
    get: `${API_BASE_URL}/cart/`,
    add: `${API_BASE_URL}/cart/add`,
    update: (id) => `${API_BASE_URL}/cart/item/${id}`,
    remove: (id) => `${API_BASE_URL}/cart/item/${id}`,
    clear: `${API_BASE_URL}/cart/clear`
  },
  orders: {
    list: `${API_BASE_URL}/orders/`,
    byNumber: (num) => `${API_BASE_URL}/orders/${num}`,
    checkout: `${API_BASE_URL}/orders/checkout`,
    pay: (num) => `${API_BASE_URL}/orders/${num}/pay`
  },
  users: {
    get: (id) => `${API_BASE_URL}/users/${id}`,
    update: (id) => `${API_BASE_URL}/users/${id}`,
    addresses: (id) => `${API_BASE_URL}/users/${id}/addresses`,
    addAddress: (id) => `${API_BASE_URL}/users/${id}/addresses`
  },
  admin: {
    dashboard: `${API_BASE_URL}/admin/dashboard`,
    salesByCategory: `${API_BASE_URL}/admin/sales-by-category`,
    salesOverTime: `${API_BASE_URL}/admin/sales-over-time`,
    topProducts: `${API_BASE_URL}/admin/top-products`,
    recentOrders: `${API_BASE_URL}/admin/recent-orders`
  },
  forecasting: {
    dashboard: `${API_BASE_URL}/forecasting/dashboard`,
    forecast: (id) => `${API_BASE_URL}/forecasting/products/${id}/forecast`,
    seasonalPatterns: (id) => `${API_BASE_URL}/forecasting/products/${id}/seasonal-patterns`,
    recordSales: (id) => `${API_BASE_URL}/forecasting/products/${id}/record-sales`,
    autoOrderSettings: (id) => `${API_BASE_URL}/forecasting/auto-order/settings/${id}`,
    autoOrderProcess: `${API_BASE_URL}/forecasting/auto-order/process`,
    purchaseOrders: `${API_BASE_URL}/forecasting/purchase-orders`,
    purchaseOrderById: (id) => `${API_BASE_URL}/forecasting/purchase-orders/${id}`
  },
  inventory: {
    dashboard: `${API_BASE_URL}/inventory/dashboard`,
    products: `${API_BASE_URL}/inventory/products`,
    alerts: `${API_BASE_URL}/inventory/alerts`,
    adjustStock: `${API_BASE_URL}/inventory/stock/adjust`,
    resolveAlert: (id) => `${API_BASE_URL}/inventory/alerts/${id}/resolve`,
    suppliers: `${API_BASE_URL}/inventory/suppliers`
  },
  inventoryML: {
    predictions: `${API_BASE_URL}/inventory-ml/predictions`,
    predictionByProduct: (id) => `${API_BASE_URL}/inventory-ml/predictions/${id}`,
    refillRequests: `${API_BASE_URL}/inventory-ml/refill-requests`,
    refillRequestById: (id) => `${API_BASE_URL}/inventory-ml/refill-requests/${id}`,
    approveRefill: (id) => `${API_BASE_URL}/inventory-ml/refill-requests/${id}/approve`,
    markOrdered: (id) => `${API_BASE_URL}/inventory-ml/refill-requests/${id}/mark-ordered`,
    receiveRefill: (id) => `${API_BASE_URL}/inventory-ml/refill-requests/${id}/receive`,
    cancelRefill: (id) => `${API_BASE_URL}/inventory-ml/refill-requests/${id}/cancel`
  },
  recommendations: {
    popular: `${API_BASE_URL}/recommendations/popular`,
    newArrivals: `${API_BASE_URL}/recommendations/new-arrivals`,
    similar: (id) => `${API_BASE_URL}/recommendations/similar/${id}`,
    boughtTogether: (id) => `${API_BASE_URL}/recommendations/bought-together/${id}`,
    forYou: `${API_BASE_URL}/recommendations/for-you`
  },
  seed: {
    forecasting: `${API_BASE_URL}/seed/forecasting`,
    stock: `${API_BASE_URL}/seed/stock`
  },
  rbac: {
    permissions: `${API_BASE_URL}/rbac/permissions`,
    roles: `${API_BASE_URL}/rbac/roles`,
    userRoles: (userId) => `${API_BASE_URL}/rbac/users/${userId}/roles`,
    assignRole: (userId) => `${API_BASE_URL}/rbac/users/${userId}/roles`,
    setStaff: (userId) => `${API_BASE_URL}/rbac/users/${userId}/staff`,
    myPermissions: `${API_BASE_URL}/rbac/my-permissions`,
    seedDefaults: `${API_BASE_URL}/rbac/seed-defaults`
  },
  delivery: {
    create: `${API_BASE_URL}/delivery/create`,
    track: (trackingNumber) => `${API_BASE_URL}/delivery/track/${trackingNumber}`,
    cancel: (trackingNumber) => `${API_BASE_URL}/delivery/cancel/${trackingNumber}`,
    providers: `${API_BASE_URL}/delivery/providers`
  }
}

export default ENDPOINTS