<template>
  <q-page class="q-pa-md">
    <q-btn flat icon="arrow_back" label="Back to Products" to="/products" class="q-mb-md" />

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="!product" class="text-center q-pa-xl">
      <q-icon name="error" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Product not found</div>
    </div>

    <div v-else class="row q-col-gutter-lg">
      <div class="col-12 col-md-6">
        <q-img :src="product.image || 'https://via.placeholder.com/500'" style="border-radius: 8px;" />
      </div>

      <div class="col-12 col-md-6">
        <div class="text-caption text-primary">{{ product.category?.name }}</div>
        <div class="text-h4 q-mb-sm">{{ product.name }}</div>
        
        <div class="q-mb-md">
          <span class="text-h5 text-primary">${{ product.price }}</span>
          <span v-if="product.compare_price" class="text-body1 text-grey q-ml-md" style="text-decoration: line-through;">
            ${{ product.compare_price }}
          </span>
        </div>

        <div class="text-body1 q-mb-md" style="white-space: pre-line;">{{ product.description }}</div>

        <div class="q-mb-md">
          <span class="text-body2 text-grey">SKU: </span>
          <span>{{ product.sku || 'N/A' }}</span>
        </div>

        <div class="q-mb-md">
          <span class="text-body2 text-grey">Stock: </span>
          <span :class="product.stock > 0 ? 'text-positive' : 'text-negative'">
            {{ product.stock > 0 ? `${product.stock} available` : 'Out of stock' }}
          </span>
        </div>

        <div class="row items-center q-gutter-md q-mb-lg">
          <q-input v-model.number="quantity" type="number" min="1" :max="product.stock" dense outlined style="width: 80px" />
          <q-btn color="primary" label="Add to Cart" :disable="product.stock <= 0" @click="addToCart" :loading="adding" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useQuasar } from 'quasar'
import { productsAPI, cartAPI } from 'src/boot/api'
import { useCartStore } from 'src/stores/cart'

const $q = useQuasar()
const route = useRoute()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(true)
const adding = ref(false)
const quantity = ref(1)

async function loadProduct() {
  loading.value = true
  try {
    const res = await productsAPI.getBySlug(route.params.slug)
    product.value = res.data
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Product not found' })
  } finally {
    loading.value = false
  }
}

async function addToCart() {
  adding.value = true
  try {
    await cartAPI.add({ product_id: product.value.id, quantity: quantity.value })
    await cartStore.fetchCart()
    $q.notify({ type: 'positive', message: 'Added to cart!' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to add to cart' })
  } finally {
    adding.value = false
  }
}

onMounted(loadProduct)
</script>
