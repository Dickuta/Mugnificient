<template>
  <q-page class="flex flex-center bg-gradient">
    <div class="login-container">
      <div class="login-card">
        <!-- Logo Section -->
        <div class="login-header text-center">
          <q-avatar size="80px" class="q-mb-md bg-white shadow-2">
            <img src="/images/uos-logo.png" alt="University of Suffolk" @error="handleLogoError" />
          </q-avatar>
          <div class="text-h4 text-weight-bold text-primary q-mb-sm">Create Account</div>
          <div class="text-subtitle2 text-grey-7">Join University of Suffolk Mug Store</div>
        </div>

        <!-- Registration Form -->
        <q-card-section class="q-pt-md">
          <q-form @submit="onSubmit" class="q-gutter-lg">
            <q-input
              v-model="form.username"
              outlined
              dense
              label="Username"
              color="primary"
              :rules="[val => !!val || 'Username is required', val => val.length >= 3 || 'Min 3 characters']"
            >
              <template v-slot:prepend>
                <q-icon name="person" color="primary" />
              </template>
            </q-input>

            <q-input
              v-model="form.email"
              outlined
              dense
              type="email"
              label="Email Address"
              color="primary"
              :rules="[
                val => !!val || 'Email is required',
                val => /.+@.+\..+/.test(val) || 'Invalid email format'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="email" color="primary" />
              </template>
            </q-input>

            <q-input
              v-model="form.password"
              outlined
              dense
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              color="primary"
              :rules="[
                val => !!val || 'Password is required',
                val => val.length >= 8 || 'Min 8 characters',
                val => /[A-Z]/.test(val) || 'One uppercase letter',
                val => /[0-9]/.test(val) || 'One number'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="primary" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>

            <q-input
              v-model="form.confirmPassword"
              outlined
              dense
              :type="showConfirmPassword ? 'text' : 'password'"
              label="Confirm Password"
              color="primary"
              :rules="[
                val => !!val || 'Please confirm your password',
                val => val === form.password || 'Passwords do not match'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="lock" color="primary" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="showConfirmPassword = !showConfirmPassword"
                />
              </template>
            </q-input>

            <div class="q-mb-md">
              <q-checkbox
                v-model="form.acceptTerms"
                :rules="[val => val || 'You must accept the terms']"
              >
                <span class="text-body2">I accept the
                  <a href="#" class="text-primary text-weight-medium" @click.prevent="showTerms">Terms & Conditions</a>
                </span>
              </q-checkbox>
            </div>

            <q-btn
              type="submit"
              color="primary"
              label="Create Account"
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

        <!-- Login Link -->
        <q-card-section class="text-center q-pb-lg">
          <div class="text-body2 text-grey-7 q-mb-sm">Already have an account?</div>
          <q-btn
            flat
            color="primary"
            label="Sign In"
            class="text-weight-bold"
            @click="router.push('/auth/login')"
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
import { authAPI } from 'src/boot/api'

const $q = useQuasar()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)

async function onSubmit() {
  if (form.value.password !== form.value.confirmPassword) {
    $q.notify({
      type: 'negative',
      message: 'Passwords do not match',
      position: 'top'
    })
    return
  }

  if (!form.value.acceptTerms) {
    $q.notify({
      type: 'warning',
      message: 'Please accept the Terms & Conditions',
      position: 'top'
    })
    return
  }

  loading.value = true
  try {
    await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })
    $q.notify({
      type: 'positive',
      message: 'Account created successfully! Please login.',
      position: 'top',
      html: true
    })
    router.push('/auth/login')
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Registration failed. Please try again.',
      position: 'top',
      html: true
    })
  } finally {
    loading.value = false
  }
}

function showTerms() {
  $q.notify({
    type: 'info',
    message: 'Terms & Conditions page coming soon',
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
  max-width: 450px;
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
  padding: 25px 25px 12px;
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

:deep(.q-item) {
  padding: 4px 12px !important;
}
</style>
