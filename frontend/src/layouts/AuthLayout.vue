<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="flex flex-center bg-grey-2">
        <q-card style="width: 400px; max-width: 90vw">
          <q-card-section class="text-center">
            <div class="text-h5 text-primary">{{ appName }}</div>
            <div class="text-caption text-grey">{{ title }}</div>
          </q-card-section>
          <q-card-section>
            <router-view />
          </q-card-section>
          <q-card-section class="text-center">
            <router-link to="/auth/login" v-if="title === 'Register'">Already have an account? Login</router-link>
            <router-link to="/auth/register" v-else>Don't have an account? Register</router-link>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta?.title || (route.name === 'login' ? 'Login' : 'Register'))
const appName = import.meta.env.VITE_APP_NAME || 'Mugnificent'
</script>