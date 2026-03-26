<template>
  <q-page class="q-pa-md">
    <q-btn flat icon="arrow_back" label="Back to Orders" to="/orders" class="q-mb-md" />

    <div v-if="!order" class="text-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
      <div class="q-mt-md">Loading order...</div>
    </div>

    <div v-else>
      <div class="row items-center q-mb-md">
        <div class="text-h4">Order #{{ order.order_number }}</div>
        <q-space />
        <q-badge :color="order.is_paid ? 'positive' : 'warning'" class="q-ml-md">
          {{ order.is_paid ? 'Paid' : 'Pending' }}
        </q-badge>
      </div>

      <div class="text-caption text-grey q-mb-lg">
        Placed on {{ formatDate(order.created_at) }}
      </div>

      <div class="row q-col-gutter-lg">
        <div class="col-12 col-md-7">
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="text-h6 q-mb-md">Items</div>
              <q-list separator>
                <q-item v-for="item in order.items" :key="item.id">
                  <q-item-section>
                    <q-item-label>{{ item.product_name }}</q-item-label>
                    <q-item-label caption>${{ parseFloat(item.product_price).toFixed(2) }} x {{ item.quantity }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-subtitle1">${{ parseFloat(item.subtotal).toFixed(2) }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>

          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Shipping Address</div>
              <div>{{ order.shipping_name }}</div>
              <div>{{ order.shipping_address_line1 }}</div>
              <div v-if="order.shipping_address_line2">{{ order.shipping_address_line2 }}</div>
              <div>{{ order.shipping_city }}, {{ order.shipping_state }} {{ order.shipping_zip_code }}</div>
              <div>{{ order.shipping_country }}</div>
              <div class="q-mt-sm">Phone: {{ order.shipping_phone }}</div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-5">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Order Summary</div>
              <div class="row justify-between q-mb-sm">
                <span>Subtotal</span>
                <span>${{ parseFloat(order.subtotal).toFixed(2) }}</span>
              </div>
              <div class="row justify-between q-mb-sm">
                <span>Shipping</span>
                <span>${{ parseFloat(order.shipping_cost).toFixed(2) }}</span>
              </div>
              <div class="row justify-between q-mb-sm">
                <span>Tax</span>
                <span>${{ parseFloat(order.tax).toFixed(2) }}</span>
              </div>
              <q-separator class="q-my-md" />
              <div class="row justify-between">
                <span class="text-h6">Total</span>
                <span class="text-h5 text-primary">${{ parseFloat(order.total).toFixed(2) }}</span>
              </div>
            </q-card-section>
            <q-card-actions v-if="!order.is_paid" class="q-pa-md">
              <q-btn color="positive" label="Mark as Paid" class="full-width" size="lg" :loading="loading" @click="markPaid" />
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { ordersAPI } from 'src/boot/api'

const $q = useQuasar()
const route = useRoute()
const authStore = useAuthStore()
const order = ref(null)
const loading = ref(false)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

async function loadOrder() {
  try {
    const res = await ordersAPI.getOne(route.params.orderNumber, authStore.userId)
    order.value = res.data
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Order not found' })
  }
}

async function markPaid() {
  loading.value = true
  try {
    await ordersAPI.pay(route.params.orderNumber)
    $q.notify({ type: 'positive', message: 'Order marked as paid!' })
    await loadOrder()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to process payment' })
  } finally {
    loading.value = false
  }
}

onMounted(loadOrder)
</script>
