const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/IndexPage.vue') },
      { path: 'products', name: 'products', component: () => import('pages/ProductsPage.vue') },
      { path: 'products/:slug', name: 'product-detail', component: () => import('pages/ProductDetailPage.vue') },
      { path: 'cart', name: 'cart', component: () => import('pages/CartPage.vue') },
      { path: 'checkout', name: 'checkout', component: () => import('pages/CheckoutPage.vue') },
      { path: 'orders', name: 'orders', component: () => import('pages/OrdersPage.vue') },
      { path: 'orders/:orderNumber', name: 'order-detail', component: () => import('pages/OrderDetailPage.vue') },
      { path: 'profile', name: 'profile', component: () => import('pages/ProfilePage.vue') },
      { path: 'admin', name: 'admin', component: () => import('pages/AdminDashboard.vue') },
    ]
  },
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('pages/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('pages/RegisterPage.vue') },
    ]
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes