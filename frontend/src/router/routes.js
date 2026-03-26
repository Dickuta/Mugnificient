const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/home/IndexPage.vue') },
      { path: 'products', name: 'products', component: () => import('pages/products/ProductsPage.vue') },
      { path: 'products/:slug', name: 'product-detail', component: () => import('pages/products/ProductDetailPage.vue') },
      { path: 'cart', name: 'cart', component: () => import('pages/cart/CartPage.vue'), meta: { requiresAuth: true } },
      { path: 'checkout', name: 'checkout', component: () => import('pages/cart/CheckoutPage.vue'), meta: { requiresAuth: true } },
      { path: 'orders', name: 'orders', component: () => import('pages/orders/OrdersPage.vue'), meta: { requiresAuth: true } },
      { path: 'orders/:orderNumber', name: 'order-detail', component: () => import('pages/orders/OrderDetailPage.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'profile', component: () => import('pages/user/ProfilePage.vue'), meta: { requiresAuth: true } },
      { path: 'admin', name: 'admin', component: () => import('pages/admin/AdminDashboard.vue'), meta: { requiresAuth: true, requiresStaff: true } },
      { path: 'admin/rbac', name: 'rbac', component: () => import('pages/admin/RBACManagementPage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      { path: 'forecasting', name: 'forecasting', component: () => import('pages/forecasting/ForecastingPage.vue'), meta: { requiresAuth: true, requiresStaff: true } },
      { path: 'forecasting/enhanced', name: 'enhanced-forecasting', component: () => import('pages/forecasting/EnhancedForecastingPage.vue'), meta: { requiresAuth: true, requiresStaff: true } },
      { path: 'inventory-ml', name: 'inventory-ml', component: () => import('pages/inventory/InventoryMLPage.vue'), meta: { requiresAuth: true, requiresStaff: true } },
      { path: 'inventory', name: 'inventory', component: () => import('pages/inventory/InventoryManagementPage.vue'), meta: { requiresAuth: true, requiresStaff: true } },
      { path: 'delivery', name: 'delivery', component: () => import('pages/delivery/DeliveryTrackingPage.vue'), meta: { requiresAuth: true, requiresStaff: true } },
    ]
  },
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('pages/auth/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('pages/auth/RegisterPage.vue') },
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/shared/ErrorNotFound.vue')
  }
]

export default routes