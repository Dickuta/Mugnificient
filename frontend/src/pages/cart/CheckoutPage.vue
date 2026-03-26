<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Checkout</div>

    <div v-if="cartStore.cart.items.length === 0" class="text-center q-pa-xl">
      <q-icon name="shopping_cart" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Your cart is empty</div>
      <q-btn color="primary" label="Go to Products" to="/products" class="q-mt-md" />
    </div>

    <div v-else-if="!authStore.isAuthenticated" class="text-center q-pa-xl">
      <q-icon name="lock" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Please login to checkout</div>
      <q-btn color="primary" label="Login" to="/auth/login" class="q-mt-md" />
    </div>

    <div v-else class="row q-col-gutter-lg">
      <div class="col-12 col-md-7">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">Shipping Information</div>
            <q-form @submit.prevent="placeOrder">
              <q-input v-model="form.shipping_name" label="Full Name" :rules="[val => !!val || 'Required']" class="q-mb-md" />
              <q-input v-model="form.shipping_address_line1" label="Address Line 1" :rules="[val => !!val || 'Required']" class="q-mb-md" />
              <q-input v-model="form.shipping_address_line2" label="Address Line 2" class="q-mb-md" />
              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                  <q-input v-model="form.shipping_city" label="City" :rules="[val => !!val || 'Required']" class="q-mb-md" />
                </div>
                <div class="col-12 col-sm-6">
                  <q-input v-model="form.shipping_state" label="State" :rules="[val => !!val || 'Required']" class="q-mb-md" />
                </div>
              </div>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-sm-6">
                  <q-input v-model="form.shipping_zip_code" label="ZIP Code" :rules="[val => !!val || 'Required']" class="q-mb-md" />
                </div>
                <div class="col-12 col-sm-6">
                  <q-input v-model="form.shipping_country" label="Country" :rules="[val => !!val || 'Required']" class="q-mb-md" />
                </div>
              </div>
              <q-input v-model="form.shipping_phone" label="Phone Number" :rules="[val => !!val || 'Required']" class="q-mb-md" />
              <q-input v-model="form.notes" label="Order Notes (optional)" type="textarea" rows="2" class="q-mb-md" />
            </q-form>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-5">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-md">Order Summary</div>
            <q-list dense>
              <q-item v-for="item in cartStore.cart.items" :key="item.id">
                <q-item-section>
                  <q-item-label>{{ item.product_name }} x{{ item.quantity }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>${{ item.item_total.toFixed(2) }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <q-separator class="q-my-md" />
            <div class="row justify-between q-mb-sm">
              <span>Subtotal</span>
              <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
            </div>
            <div class="row justify-between q-mb-sm">
              <span>Shipping</span>
              <span>$10.00</span>
            </div>
            <div class="row justify-between q-mb-sm">
              <span>Tax (8%)</span>
              <span>${{ tax.toFixed(2) }}</span>
            </div>
            <q-separator class="q-my-md" />
            <div class="row justify-between">
              <span class="text-h6">Total</span>
              <span class="text-h5 text-primary">${{ total.toFixed(2) }}</span>
            </div>
          </q-card-section>
          <q-card-actions class="q-pa-md">
            <q-btn color="primary" label="Place Order" class="full-width" size="lg" :loading="loading" @click="placeOrder" />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { useCartStore } from 'src/stores/cart'
import { ordersAPI } from 'src/boot/api'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()

const loading = ref(false)
const form = ref({
  shipping_name: '',
  shipping_address_line1: '',
  shipping_address_line2: '',
  shipping_city: '',
  shipping_state: '',
  shipping_zip_code: '',
  shipping_country: '',
  shipping_phone: '',
  notes: ''
})

const subtotal = computed(() => cartStore.totalPrice)
const shipping = 10.00
const tax = computed(() => subtotal.value * 0.08)
const total = computed(() => subtotal.value + shipping + tax.value)

async function placeOrder() {
  if (!form.value.shipping_name || !form.value.shipping_address_line1 || 
      !form.value.shipping_city || !form.value.shipping_state ||
      !form.value.shipping_zip_code || !form.value.shipping_country || 
      !form.value.shipping_phone) {
    $q.notify({ type: 'warning', message: 'Please fill in all required fields' })
    return
  }

  loading.value = true
  try {
    const data = {
      user_id: authStore.userId,
      ...form.value
    }
    const res = await ordersAPI.checkout(data)
    await cartStore.fetchCart()
    $q.notify({ type: 'positive', message: 'Order placed successfully!' })
    router.push(`/orders/${res.data.order_number}`)
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to place order' })
  } finally {
    loading.value = false
  }
}
</script>
