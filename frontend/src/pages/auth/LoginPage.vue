<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px">
      <q-card-section>
        <div class="text-h5">Login</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <q-input
            v-model="username"
            label="Username"
            :rules="[val => !!val || 'Username is required']"
          />
          <q-input
            v-model="password"
            type="password"
            label="Password"
            :rules="[val => !!val || 'Password is required']"
          />
          <q-btn
            type="submit"
            color="primary"
            label="Login"
            class="full-width"
            :loading="loading"
          />
        </q-form>
      </q-card-section>
      <q-card-section class="text-center">
        <router-link to="/auth/register">Don't have an account? Register</router-link>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from 'src/stores/auth'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    $q.notify({ type: 'positive', message: 'Login successful!' })
    router.push('/')
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Login failed. Check credentials.' })
  } finally {
    loading.value = false
  }
}
</script>