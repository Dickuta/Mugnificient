<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">My Profile</div>

    <div v-if="!authStore.isAuthenticated" class="text-center q-pa-xl">
      <q-icon name="lock" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Please login to view profile</div>
      <q-btn color="primary" label="Login" to="/auth/login" class="q-mt-md" />
    </div>

    <div v-else>
      <q-card class="q-mb-md">
        <q-card-section>
          <div class="text-h6 q-mb-md">Account Information</div>
          <q-form @submit.prevent="updateProfile">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input v-model="form.username" label="Username" readonly class="q-mb-md" />
              </div>
              <div class="col-12 col-sm-6">
                <q-input v-model="form.email" label="Email" readonly class="q-mb-md" />
              </div>
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input v-model="form.first_name" label="First Name" class="q-mb-md" />
              </div>
              <div class="col-12 col-sm-6">
                <q-input v-model="form.last_name" label="Last Name" class="q-mb-md" />
              </div>
            </div>
            <q-input v-model="form.phone" label="Phone" class="q-mb-md" />
            <q-input v-model="form.address" label="Address" class="q-mb-md" />
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input v-model="form.city" label="City" class="q-mb-md" />
              </div>
              <div class="col-12 col-sm-6">
                <q-input v-model="form.state" label="State" class="q-mb-md" />
              </div>
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input v-model="form.zip_code" label="ZIP Code" class="q-mb-md" />
              </div>
              <div class="col-12 col-sm-6">
                <q-input v-model="form.country" label="Country" class="q-mb-md" />
              </div>
            </div>
            <q-btn color="primary" label="Save Changes" type="submit" :loading="loading" />
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { usersAPI } from 'src/boot/api'

const $q = useQuasar()
const authStore = useAuthStore()
const loading = ref(false)

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  country: ''
})

function initForm() {
  if (authStore.user) {
    form.value = {
      username: authStore.user.username || '',
      email: authStore.user.email || '',
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      phone: authStore.user.phone || '',
      address: authStore.user.address || '',
      city: authStore.user.city || '',
      state: authStore.user.state || '',
      zip_code: authStore.user.zip_code || '',
      country: authStore.user.country || ''
    }
  }
}

async function updateProfile() {
  loading.value = true
  try {
    await usersAPI.update(authStore.userId, form.value)
    authStore.user = { ...authStore.user, ...form.value }
    localStorage.setItem('user', JSON.stringify(authStore.user))
    $q.notify({ type: 'positive', message: 'Profile updated successfully!' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update profile' })
  } finally {
    loading.value = false
  }
}

onMounted(initForm)
</script>
