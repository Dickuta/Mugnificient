import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 1. If the route requires auth and there's no token, go to login
  if (to.meta.requiresAuth && !token) {
    return next('/auth/login')
  }

  // 2. If user is logged in and tries to go to login page, go to home
  if (to.path === '/auth/login' && token) {
    return next('/')
  }

  next()
})

export default router