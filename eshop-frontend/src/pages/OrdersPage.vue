<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">My Orders</div>

    <div v-if="!authStore.isAuthenticated" class="text-center q-pa-xl">
      <q-icon name="lock" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Please login to view orders</div>
      <q-btn color="primary" label="Login" to="/auth/login" class="q-mt-md" />
    </div>

    <div v-else-if="orders.length === 0" class="text-center q-pa-xl">
      <q-icon name="receipt_long" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">No orders yet</div>
      <q-btn color="primary" label="Start Shopping" to="/products" class="q-mt-md" />
    </div>

    <q-list v-else separator>
      <q-item v-for="order in orders" :key="order.id" clickable :to="`/orders/${order.order_number}`">
        <q-item-section>
          <q-item-label class="text-subtitle1">Order #{{ order.order_number }}</q-item-label>
          <q-item-label caption>{{ formatDate(order.created_at) }}</q-item-label>
        </q-item-section>
        <q-item-section side>
          <q-badge :color="order.is_paid ? 'positive' : 'warning'">
            {{ order.is_paid ? 'Paid' : 'Pending' }}
          </q-badge>
        </q-item-section>
        <q-item-section side>
          <div class="text-subtitle1">${{ parseFloat(order.total).toFixed(2) }}</div>
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { ordersAPI } from 'src/boot/api'

const $q = useQuasar()
const authStore = useAuthStore()
const orders = ref([])

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

async function loadOrders() {
  try {
    const res = await ordersAPI.getAll(authStore.userId)
    orders.value = res.data
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load orders' })
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadOrders()
  }
})
</script>
