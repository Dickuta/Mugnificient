import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartAPI } from 'src/boot/api'
import { useAuthStore } from './auth'

export const useCartStore = defineStore('cart', () => {
  const cart = ref({ items: [], total_items: 0, total_price: 0 })
  const authStore = useAuthStore()

  const totalItems = computed(() => cart.value.total_items)
  const totalPrice = computed(() => cart.value.total_price)

  async function fetchCart() {
    try {
      const params = authStore.userId ? { user_id: authStore.userId } : {}
      const res = await cartAPI.get(params)
      cart.value = res.data
    } catch (err) {
      console.error('Failed to fetch cart:', err)
    }
  }

  async function addItem(productId, quantity = 1) {
    const params = {
      product_id: productId,
      quantity,
      ...(authStore.userId ? { user_id: authStore.userId } : {})
    }
    await cartAPI.add(params)
    await fetchCart()
  }

  async function updateItem(itemId, quantity) {
    await cartAPI.update(itemId, quantity)
    await fetchCart()
  }

  async function removeItem(itemId) {
    await cartAPI.remove(itemId)
    await fetchCart()
  }

  async function clearCart() {
    const params = authStore.userId ? { user_id: authStore.userId } : {}
    await cartAPI.clear(params)
    await fetchCart()
  }

  function init() {
    fetchCart()
  }

  return { cart, totalItems, totalPrice, fetchCart, addItem, updateItem, removeItem, clearCart, init }
})