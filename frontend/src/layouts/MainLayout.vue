<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-uos-blue text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-avatar size="40px" class="q-mr-sm">
          <img src="/images/uos-logo.png" alt="UoS Logo" @error="handleLogoError" />
        </q-avatar>
        <q-toolbar-title>
          <router-link to="/" class="text-white text-decoration-none">{{ appName }}</router-link>
        </q-toolbar-title>
        <q-space />
        <q-btn flat round icon="shopping_cart" to="/cart">
          <q-badge color="red" floating>{{ cartStore.totalItems }}</q-badge>
        </q-btn>
        <q-btn v-if="!authStore.isAuthenticated" flat label="Login" to="/auth/login" />
        <q-btn v-else flat round>
          <q-avatar size="26px">{{ authStore.user?.username?.[0]?.toUpperCase() }}</q-avatar>
          <q-menu>
            <q-list style="min-width: 150px">
              <q-item clickable v-close-popup to="/profile">
                <q-item-section>Profile</q-item-section>
              </q-item>
              <q-item clickable v-close-popup to="/orders">
                <q-item-section>Orders</q-item-section>
              </q-item>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/admin">
                <q-item-section>Admin Dashboard</q-item-section>
              </q-item>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/forecasting">
                <q-item-section>Stock Forecasting</q-item-section>
              </q-item>
              <q-item v-if="authStore.user?.is_staff" clickable v-close-popup to="/inventory-ml">
                <q-item-section>Inventory ML</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup @click="logout">
                <q-item-section>Logout</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Navigation</q-item-label>
        <q-item clickable to="/" v-close-popup>
          <q-item-section avatar><q-icon name="home" /></q-item-section>
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-item clickable to="/products" v-close-popup>
          <q-item-section avatar><q-icon name="shopping_bag" /></q-item-section>
          <q-item-section>Products</q-item-section>
        </q-item>
        <q-item clickable to="/cart" v-close-popup>
          <q-item-section avatar><q-icon name="shopping_cart" /></q-item-section>
          <q-item-section>Cart</q-item-section>
        </q-item>
        <q-item v-if="authStore.user?.is_staff" clickable to="/admin" v-close-popup>
          <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
          <q-item-section>Admin</q-item-section>
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

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const appName = import.meta.env.VITE_APP_NAME || 'Mugnificent'
const leftDrawerOpen = ref(false)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
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