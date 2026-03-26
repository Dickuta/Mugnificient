<template>
  <q-layout view="hHh lpR fff">
    <!-- Enhanced E-commerce Header -->
    <q-header elevated class="bg-primary text-white">
      <!-- Top Bar -->
      <div class="bg-secondary q-py-xs">
        <div class="row justify-between items-center q-px-md" style="max-width: 1400px; margin: 0 auto;">
          <div class="text-caption">Welcome to {{ appName }} - University of Suffolk Official Store</div>
          <div class="text-caption" v-if="authStore.isAuthenticated">
            <q-icon name="person" size="xs" class="q-mr-xs" />
            {{ authStore.user?.username }}
          </div>
        </div>
      </div>

      <!-- Main Header -->
      <q-toolbar class="q-py-md">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" class="q-mr-sm" />
        
        <q-avatar size="50px" class="q-mr-md bg-white">
          <img src="/images/uos-logo.png" alt="UoS Logo" @error="handleLogoError" />
        </q-avatar>
        
        <div class="text-h5 text-weight-bold">{{ appName }}</div>
        
        <q-space />
        
        <!-- Search Bar -->
        <q-input
          v-model="searchQuery"
          dense
          outlined
          bg-color="white"
          placeholder="Search products..."
          class="q-mx-lg"
          style="width: 400px; max-width: 30vw;"
          @keyup.enter="searchProducts"
        >
          <template v-slot:append>
            <q-btn round flat icon="search" @click="searchProducts" />
          </template>
        </q-input>
        
        <!-- Cart with Badge -->
        <q-btn flat round icon="shopping_cart" to="/cart" class="q-mx-sm">
          <q-badge color="red" floating :label="cartCount" />
          <q-tooltip>Cart</q-tooltip>
        </q-btn>
        
        <!-- User Menu -->
        <q-btn v-if="!authStore.isAuthenticated" flat label="Sign In" to="/auth/login" class="q-ml-md" />
        <q-btn v-else flat round class="q-ml-md">
          <q-avatar size="32px" color="white" text-color="primary">
            {{ authStore.user?.username?.[0]?.toUpperCase() }}
          </q-avatar>
          <q-menu anchor="top right" self="top right" :offset="[0, 10]">
            <q-list style="min-width: 200px">
              <q-item clickable v-close-popup to="/profile">
                <q-item-section avatar><q-icon name="person" /></q-item-section>
                <q-item-section>My Profile</q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/orders">
                <q-item-section avatar><q-icon name="shopping_bag" /></q-item-section>
                <q-item-section>My Orders</q-item-section>
              </q-item>
              <q-separator />
              <q-item-label header>Staff Menu</q-item-label>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/admin">
                <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
                <q-item-section>Admin Dashboard</q-item-section>
              </q-item>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/forecasting">
                <q-item-section avatar><q-icon name="analytics" /></q-item-section>
                <q-item-section>Forecasting</q-item-section>
              </q-item>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/inventory-ml">
                <q-item-section avatar><q-icon name="inventory" /></q-item-section>
                <q-item-section>Inventory ML</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup @click="logout">
                <q-item-section avatar><q-icon name="logout" /></q-item-section>
                <q-item-section>Logout</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>

      <!-- Navigation Bar -->
      <q-tabs v-model="currentTab" align="left" class="bg-primary shadow-2">
        <q-tab name="home" icon="home" label="Home" to="/" />
        <q-tab name="products" icon="shopping_bag" label="All Products" to="/products" />
        <q-tab name="featured" icon="star" label="Featured" to="/products?featured=true" />
        <q-tab name="new" icon="new_releases" label="New Arrivals" to="/products?new=true" />
      </q-tabs>
    </q-header>

    <!-- Side Drawer - Hidden on home page -->
    <q-drawer v-model="leftDrawerOpen" show-if-above bordered v-if="!isHomePage">
      <q-list>
        <q-item-label header class="text-primary">Shop Categories</q-item-label>
        <q-item clickable to="/" v-close-popup>
          <q-item-section avatar><q-icon name="home" /></q-item-section>
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-item clickable to="/products" v-close-popup>
          <q-item-section avatar><q-icon name="shopping_bag" /></q-item-section>
          <q-item-section>All Products</q-item-section>
        </q-item>
        <q-item clickable to="/cart" v-close-popup>
          <q-item-section avatar><q-icon name="shopping_cart" /></q-item-section>
          <q-item-section>Shopping Cart</q-item-section>
        </q-item>
        <q-separator />
        <q-item-label header class="text-primary" v-if="authStore.user?.is_staff">Staff Area</q-item-label>
        <q-item v-if="authStore.user?.is_staff" clickable to="/admin" v-close-popup>
          <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
          <q-item-section>Admin Dashboard</q-item-section>
        </q-item>
        <q-item v-if="authStore.user?.is_staff" clickable to="/forecasting" v-close-popup>
          <q-item-section avatar><q-icon name="analytics" /></q-item-section>
          <q-item-section>Forecasting</q-item-section>
        </q-item>
        <q-item v-if="authStore.user?.is_staff" clickable to="/inventory-ml" v-close-popup>
          <q-item-section avatar><q-icon name="inventory" /></q-item-section>
          <q-item-section>Inventory ML</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useCartStore } from 'src/stores/cart'
import { computed, watch } from 'vue'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const appName = import.meta.env.VITE_APP_NAME || 'Mugnificent'
const leftDrawerOpen = ref(false)
const currentTab = ref('home')
const searchQuery = ref('')

// Reactive cart count
const cartCount = computed(() => {
  const count = cartStore.cart?.total_items || cartStore.totalItems || 0
  return count > 0 ? count : ''
})

// Watch for cart changes and show notification
watch(() => cartStore.cart, (newCart, oldCart) => {
  if (newCart && oldCart && newCart.total_items !== oldCart.total_items) {
    // Cart updated - badge will update automatically via computed property
  }
}, { deep: true })

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function searchProducts() {
  if (searchQuery.value.trim()) {
    router.push(`/products?search=${encodeURIComponent(searchQuery.value)}`)
  }
}

function logout() {
  authStore.logout()
  router.push('/auth/login')
}

function handleLogoError(event) {
  event.target.style.display = 'none'
}

onMounted(() => {
  authStore.init()
  cartStore.init()
})
</script>