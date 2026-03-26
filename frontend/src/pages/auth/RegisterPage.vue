<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px">
      <q-card-section>
        <div class="text-h5">Register</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <q-input
            v-model="form.username"
            label="Username"
            :rules="[val => !!val || 'Username is required']"
          />
          <q-input
            v-model="form.email"
            type="email"
            label="Email"
            :rules="[val => !!val || 'Email is required', val => /.+@.+/.test(val) || 'Invalid email']"
          />
          <q-input
            v-model="form.password"
            type="password"
            label="Password"
            :rules="[val => !!val || 'Password is required', val => val.length >= 6 || 'Min 6 characters']"
          />
          <q-input
            v-model="form.confirmPassword"
            type="password"
            label="Confirm Password"
            :rules="[val => val === form.password || 'Passwords do not match']"
          />
          <q-btn
            type="submit"
            color="primary"
            label="Register"
            class="full-width"
            :loading="loading"
          />
        </q-form>
      </q-card-section>
      <q-card-section class="text-center">
        <router-link to="/auth/login">Already have an account? Login</router-link>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { authAPI } from 'src/boot/api'

const $q = useQuasar()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)

async function onSubmit() {
  if (form.value.password !== form.value.confirmPassword) {
    $q.notify({ type: 'negative', message: 'Passwords do not match' })
    return
  }
  loading.value = true
  try {
    await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    $q.notify({ type: 'positive', message: 'Registration successful! Please login.' })
    router.push('/auth/login')
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Registration failed.' })
  } finally {
    loading.value = false
  }
}
</script>