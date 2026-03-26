<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Shopping Cart</div>
    
    <div v-if="cartStore.cart.items.length === 0" class="text-center q-pa-xl">
      <q-icon name="shopping_cart" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Your cart is empty</div>
      <q-btn color="primary" label="Continue Shopping" to="/products" class="q-mt-md" />
    </div>

    <div v-else>
      <q-list separator>
        <q-item v-for="item in cartStore.cart.items" :key="item.id">
          <q-item-section avatar>
            <q-img :src="item.product_image || 'https://via.placeholder.com/100'" style="width: 80px; height: 80px; border-radius: 8px;" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-subtitle1">{{ item.product_name }}</q-item-label>
            <q-item-label caption>${{ item.product_price.toFixed(2) }} each</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="row items-center q-gutter-sm">
              <q-btn flat round dense icon="remove" @click="updateQuantity(item.id, item.quantity - 1)" :disable="item.quantity <= 1" />
              <span class="text-subtitle1">{{ item.quantity }}</span>
              <q-btn flat round dense icon="add" @click="updateQuantity(item.id, item.quantity + 1)" />
            </div>
          </q-item-section>
          <q-item-section side>
            <div class="text-subtitle1">${{ item.item_total.toFixed(2) }}</div>
            <q-btn flat dense color="negative" icon="delete" label="Remove" @click="removeItem(item.id)" />
          </q-item-section>
        </q-item>
      </q-list>

      <q-card class="q-mt-lg">
        <q-card-section>
          <div class="row justify-between">
            <div class="text-h6">Total ({{ cartStore.totalItems }} items)</div>
            <div class="text-h5 text-primary">${{ cartStore.totalPrice.toFixed(2) }}</div>
          </div>
        </q-card-section>
        <q-card-actions>
          <q-btn color="primary" label="Proceed to Checkout" to="/checkout" class="full-width" size="lg" />
          <q-btn flat label="Continue Shopping" to="/products" class="full-width q-mt-sm" />
        </q-card-actions>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { useQuasar } from 'quasar'
import { useCartStore } from 'src/stores/cart'

const $q = useQuasar()
const cartStore = useCartStore()

async function updateQuantity(itemId, quantity) {
  try {
    if (quantity < 1) {
      await cartStore.removeItem(itemId)
    } else {
      await cartStore.updateItem(itemId, quantity)
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to update quantity' })
  }
}

async function removeItem(itemId) {
  try {
    await cartStore.removeItem(itemId)
    $q.notify({ type: 'positive', message: 'Item removed from cart' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to remove item' })
  }
}
</script>
