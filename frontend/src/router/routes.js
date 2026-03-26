const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/home/IndexPage.vue') },
      { path: 'products', name: 'products', component: () => import('pages/products/ProductsPage.vue') },
      { path: 'products/:slug', name: 'product-detail', component: () => import('pages/products/ProductDetailPage.vue') },
      { path: 'cart', name: 'cart', component: () => import('pages/cart/CartPage.vue') },
      { path: 'checkout', name: 'checkout', component: () => import('pages/cart/CheckoutPage.vue') },
      { path: 'orders', name: 'orders', component: () => import('pages/orders/OrdersPage.vue') },
      { path: 'orders/:orderNumber', name: 'order-detail', component: () => import('pages/orders/OrderDetailPage.vue') },
      { path: 'profile', name: 'profile', component: () => import('pages/user/ProfilePage.vue') },
      { path: 'admin', name: 'admin', component: () => import('pages/admin/AdminDashboard.vue') },
      { path: 'admin/rbac', name: 'rbac', component: () => import('pages/admin/RBACManagementPage.vue') },
      { path: 'forecasting', name: 'forecasting', component: () => import('pages/forecasting/ForecastingPage.vue') },
      { path: 'forecasting/enhanced', name: 'enhanced-forecasting', component: () => import('pages/forecasting/EnhancedForecastingPage.vue') },
      { path: 'inventory-ml', name: 'inventory-ml', component: () => import('pages/inventory/InventoryMLPage.vue') },
      { path: 'inventory', name: 'inventory', component: () => import('pages/inventory/InventoryManagementPage.vue') },
      { path: 'delivery', name: 'delivery', component: () => import('pages/delivery/DeliveryTrackingPage.vue') },
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