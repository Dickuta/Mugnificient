<template>
  <q-card class="product-card">
    <q-img 
      :src="imageUrl" 
      :ratio="1" 
      @click="goToProduct"
      class="cursor-pointer"
    >
      <div v-if="product.compare_price && product.compare_price > product.price" class="absolute-top-right q-pa-xs">
        <q-badge color="negative" :label="discountLabel" />
      </div>
    </q-img>
    <q-card-section @click="goToProduct" class="cursor-pointer">
      <div class="text-subtitle1">{{ product.name }}</div>
      <div class="text-body2 text-grey">{{ categoryName }}</div>
    </q-card-section>
    <q-card-section class="q-pt-none">
      <div class="row items-center">
        <div class="text-h6 text-primary">${{ product.price }}</div>
        <div v-if="product.compare_price && product.compare_price > product.price" class="text-body2 text-grey q-ml-sm" style="text-decoration: line-through;">
          ${{ product.compare_price }}
        </div>
      </div>
      <div v-if="product.stock !== undefined" class="text-caption q-mt-xs">
        <span :class="product.stock > 0 ? 'text-positive' : 'text-negative'">
          {{ product.stock > 0 ? `${product.stock} in stock` : 'Out of stock' }}
        </span>
      </div>
    </q-card-section>
    <q-card-actions>
      <q-btn 
        color="primary" 
        label="Add to Cart" 
        @click="$emit('add-to-cart', product.id)"
        :disable="product.stock <= 0"
        class="full-width"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['add-to-cart'])

const router = useRouter()

const imageUrl = computed(() => {
  const img = props.product.image
  if (!img) return 'https://via.placeholder.com/400?text=No+Image'
  
  // Check if it's a full URL
  if (img.startsWith('http://') || img.startsWith('https://')) {
    return img
  }
  
  // Use environment-based storage configuration
  const storageType = import.meta.env.VITE_IMAGE_STORAGE_TYPE || 'local'
  const storageUrl = import.meta.env.VITE_IMAGE_STORAGE_URL || ''
  
  if (storageType === 'minio') {
    // Use MinIO storage
    return `${storageUrl}${img}`
  } else {
    // Use local storage (images served from backend)
    return `http://localhost:8000${img}`
  }
})

const categoryName = computed(() => {
  if (props.product.category) {
    return typeof props.product.category === 'object' 
      ? props.product.category.name 
      : props.product.category
  }
  return ''
})

const discountLabel = computed(() => {
  if (!props.product.compare_price || !props.product.price) return ''
  const discount = Math.round((1 - props.product.price / props.product.compare_price) * 100)
  return `-${discount}%`
})

function goToProduct() {
  router.push(`/products/${props.product.slug}`)
}
</script>

<style scoped>
.product-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.product-card .q-card__section--vert {
  flex-grow: 1;
}
</style>
