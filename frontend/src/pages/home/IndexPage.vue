<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-lg">Welcome to The Mug Store</div>

    <!-- Featured Products -->
    <div class="q-mb-xl">
      <div class="text-h5 q-mb-md flex items-center">
        <q-icon name="star" color="warning" class="q-mr-sm" />
        Featured Mugs
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-sm-6 col-md-3" v-for="product in featured" :key="'f-'+product.id">
          <ProductCard :product="product" @add-to-cart="addToCart" />
        </div>
      </div>
      <div v-if="featured.length === 0" class="text-grey text-center q-pa-md">No featured products</div>
    </div>

    <!-- New Arrivals -->
    <div class="q-mb-xl">
      <div class="text-h5 q-mb-md flex items-center">
        <q-icon name="new_releases" color="positive" class="q-mr-sm" />
        New Arrivals
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-sm-6 col-md-3" v-for="product in newArrivals" :key="'n-'+product.id">
          <ProductCard :product="product" @add-to-cart="addToCart" />
        </div>
      </div>
    </div>

    <!-- Popular Products -->
    <div class="q-mb-xl">
      <div class="text-h5 q-mb-md flex items-center">
        <q-icon name="trending_up" color="primary" class="q-mr-sm" />
        Popular Mugs
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-sm-6 col-md-3" v-for="product in popular" :key="'p-'+product.id">
          <ProductCard :product="product" @add-to-cart="addToCart" />
        </div>
      </div>
      <div v-if="popular.length === 0" class="text-grey text-center q-pa-md">
        <q-icon name="shopping_cart" size="2em" />
        <div>No orders yet - be the first to buy!</div>
      </div>
    </div>

    <!-- Personalized For You (if logged in) -->
    <div v-if="isAuthenticated" class="q-mb-xl">
      <div class="text-h5 q-mb-md flex items-center">
        <q-icon name="recommend" color="accent" class="q-mr-sm" />
        Recommended For You
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-sm-6 col-md-3" v-for="product in forYou" :key="'r-'+product.id">
          <ProductCard :product="product" @add-to-cart="addToCart" />
        </div>
      </div>
    </div>

    <!-- Categories -->
    <div>
      <div class="text-h5 q-mb-md flex items-center">
        <q-icon name="category" color="secondary" class="q-mr-sm" />
        Shop by Category
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-6 col-sm-4 col-md" v-for="cat in categories" :key="cat.id">
          <q-card class="category-card text-center q-pa-md" clickable @click="goToCategory(cat.slug)">
            <q-icon :name="getCategoryIcon(cat.slug)" size="40px" color="primary" />
            <div class="text-subtitle1 q-mt-sm">{{ cat.name }}</div>
            <div class="text-caption text-grey">{{ cat.description }}</div>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productsAPI, cartAPI, categoriesAPI } from 'src/boot/api'
import { useQuasar } from 'quasar'
import { useCartStore } from 'src/stores/cart'
import { useAuthStore } from 'src/stores/auth'
import ProductCard from 'components/ProductCard.vue'

const $q = useQuasar()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const featured = ref([])
const newArrivals = ref([])
const popular = ref([])
const forYou = ref([])
const categories = ref([])

const isAuthenticated = computed(() => authStore.isAuthenticated)

const getCategoryIcon = (slug) => {
  const icons = {
    'classic-mugs': 'coffee',
    'travel-mugs': 'flight',
    'sports-mugs': 'sports_soccer',
    'kids-mugs': 'child_care',
    'premium-mugs': 'diamond'
  }
  return icons[slug] || 'shopping_bag'
}

async function loadData() {
  try {
    const [feat, newa, cat] = await Promise.all([
      productsAPI.getFeatured(),
      productsAPI.getNewArrivals(),
      categoriesAPI.getAll()
    ])
    featured.value = feat.data
    newArrivals.value = newa.data
    categories.value = cat.data
  } catch (err) {
    console.error('Failed to load:', err)
  }
}

async function loadPopular() {
  try {
    const res = await productsAPI.getPopular()
    popular.value = res.data
  } catch (err) {
    console.log('No popular products yet')
  }
}

async function loadForYou() {
  if (!isAuthenticated.value) return
  try {
    const res = await productsAPI.getForYou()
    forYou.value = res.data
  } catch (err) {
    console.log('No recommendations yet')
  }
}

async function addToCart(productId) {
  try {
    await cartAPI.add({ product_id: productId, quantity: 1 })
    await cartStore.fetchCart()
    $q.notify({ type: 'positive', message: 'Added to cart!' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to add to cart' })
  }
}

function goToCategory(slug) {
  router.push(`/products?category=${slug}`)
}

onMounted(() => {
  loadData()
  loadPopular()
  loadForYou()
})
</script>

<style scoped>
.category-card {
  transition: transform 0.2s;
}
.category-card:hover {
  transform: translateY(-5px);
}
</style>
