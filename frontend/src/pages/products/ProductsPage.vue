<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Products</div>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-sm-4">
        <q-input v-model="search" placeholder="Search products..." dense outlined @update:model-value="loadProducts">
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
      <div class="col-12 col-sm-4">
        <q-select v-model="selectedCategory" :options="categoryOptions" label="Category" dense outlined emit-value map-options @update:model-value="loadProducts" />
      </div>
    </div>

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="products.length === 0" class="text-center q-pa-xl">
      <q-icon name="inventory_2" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">No products found</div>
    </div>

    <div v-else class="row q-col-gutter-md">
      <div class="col-12 col-sm-6 col-md-4 col-lg-3" v-for="product in products" :key="product.id">
        <q-card class="product-card">
          <q-img :src="product.image || 'https://via.placeholder.com/300'" :ratio="1" />
          <q-card-section>
            <div class="text-subtitle1">{{ product.name }}</div>
            <div class="text-body2 text-grey">{{ product.category?.name }}</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <div class="text-h6">${{ product.price }}</div>
          </q-card-section>
          <q-card-actions>
            <q-btn color="primary" label="Add to Cart" @click="addToCart(product.id)" />
            <q-space />
            <q-btn flat color="primary" label="View" :to="`/products/${product.slug}`" />
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { productsAPI, categoriesAPI, cartAPI } from 'src/boot/api'
import { useCartStore } from 'src/stores/cart'

const $q = useQuasar()
const cartStore = useCartStore()

const products = ref([])
const categories = ref([])
const search = ref('')
const selectedCategory = ref(null)
const loading = ref(false)

const categoryOptions = ref([{ label: 'All Categories', value: null }])

async function loadCategories() {
  try {
    const res = await categoriesAPI.getAll()
    categories.value = res.data
    categories.value.forEach(cat => {
      categoryOptions.value.push({ label: cat.name, value: cat.slug })
    })
  } catch (err) {
    console.error('Failed to load categories:', err)
  }
}

async function loadProducts() {
  loading.value = true
  try {
    const params = {}
    if (search.value) params.search = search.value
    if (selectedCategory.value) params.category = selectedCategory.value
    
    const res = await productsAPI.getAll(params)
    products.value = res.data
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load products' })
  } finally {
    loading.value = false
  }
}

async function addToCart(productId) {
  try {
    await cartAPI.add({ product_id: productId, quantity: 1 })
    await cartStore.fetchCart()
    $q.notify({ type: 'positive', message: 'Added to cart!' })
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to add to cart' })
  }
}

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>
