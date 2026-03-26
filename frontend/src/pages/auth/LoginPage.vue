<template>
  <q-page class="flex flex-center bg-gradient">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo Section -->
        <div class="login-header text-center">
          <q-avatar size="80px" class="q-mb-md bg-white shadow-2">
            <img src="/images/uos-logo.png" alt="University of Suffolk" @error="handleLogoError" />
          </q-avatar>
          <div class="text-h4 text-weight-bold text-primary q-mb-sm">Welcome Back</div>
          <div class="text-subtitle2 text-grey-7">University of Suffolk Mug Store</div>
        </div>

        <!-- Login Form -->
        <q-card-section class="q-pt-md">
          <q-form @submit="onSubmit" class="q-gutter-lg">
            <q-input
              v-model="username"
              outlined
              dense
              label="Username"
              color="primary"
              :rules="[val => !!val || 'Username is required']"
            >
              <template v-slot:prepend>
                <q-icon name="person" color="primary" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              outlined
              dense
              :type="isPwd ? 'password' : 'text'"
              label="Password"
              color="primary"
              :rules="[val => !!val || 'Password is required']"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="primary" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="isPwd ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd = !isPwd"
                />
              </template>
            </q-input>

            <div class="row justify-between items-center q-mb-md">
              <q-checkbox v-model="rememberMe" label="Remember me" color="primary" />
              <a href="#" class="text-primary text-weight-medium" @click.prevent="forgotPassword">Forgot Password?</a>
            </div>

            <q-btn
              type="submit"
              color="primary"
              label="Sign In"
              class="full-width q-py-md text-weight-bold"
              size="lg"
              rounded
              unelevated
              :loading="loading"
            >
              <template v-slot:loading>
                <q-spinner-dots color="white" />
              </template>
            </q-btn>
          </q-form>
        </q-card-section>

        <!-- Divider -->
        <q-separator class="q-my-md" />

        <!-- Register Link -->
        <q-card-section class="text-center q-pb-lg">
          <div class="text-body2 text-grey-7 q-mb-sm">Don't have an account?</div>
          <q-btn
            flat
            color="primary"
            label="Create Account"
            class="text-weight-bold"
            @click="router.push('/auth/register')"
          />
        </q-card-section>

        <!-- Footer -->
        <div class="login-footer text-center q-pa-md bg-grey-2">
          <div class="text-caption text-grey-6">
            © 2026 University of Suffolk. All rights reserved.
          </div>
        </div>
      </div>
    </div>
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
const isPwd = ref(true)
const rememberMe = ref(false)
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    $q.notify({
      type: 'positive',
      message: 'Welcome back!',
      position: 'top',
      html: true
    })
    router.push('/')
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'Invalid username or password. Please try again.',
      position: 'top',
      html: true
    })
  } finally {
    loading.value = false
  }
}

function forgotPassword() {
  $q.notify({
    type: 'info',
    message: 'Password reset feature coming soon',
    position: 'top'
  })
}

function handleLogoError(event) {
  event.target.style.display = 'none'
}
</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 15px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  padding: 30px 25px 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.login-header .text-h4 {
  color: white !important;
  font-size: 1.5rem !important;
  margin-bottom: 8px !important;
}

.login-header .text-subtitle2 {
  color: rgba(255, 255, 255, 0.9) !important;
  font-size: 0.875rem !important;
}

.login-footer {
  border-top: 1px solid #e0e0e0;
  padding: 15px !important;
}

:deep(.q-field__native) {
  font-size: 14px;
}

:deep(.q-field__label) {
  font-size: 13px;
  font-weight: 500;
}

:deep(.q-btn) {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 600;
}
</style>