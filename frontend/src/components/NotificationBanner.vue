<template>
  <div class="notification-container">
    <q-banner
      v-for="notification in notifications"
      :key="notification.id"
      :class="`notification-${notification.type}`"
      inline-actions
      rounded
      class="q-mb-sm shadow-2"
    >
      <template v-slot:avatar>
        <q-icon 
          :name="getIconByType(notification.type)" 
          :color="getColorByType(notification.type)" 
          size="xl" 
        />
      </template>
      
      <div class="notification-content">
        <div class="text-weight-bold">{{ notification.title }}</div>
        <div>{{ notification.message }}</div>
        <div v-if="notification.timestamp" class="text-caption text-grey-7 q-mt-xs">
          {{ formatTime(notification.timestamp) }}
        </div>
      </div>
      
      <template v-slot:action>
        <q-btn 
          flat 
          icon="close" 
          @click="removeNotification(notification.id)" 
          :color="getTextColorByType(notification.type)"
        />
      </template>
    </q-banner>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'

// Props
const props = defineProps({
  autoDismiss: {
    type: Boolean,
    default: true
  },
  dismissTimeout: {
    type: Number,
    default: 5000 // 5 seconds
  }
})

// Emits
const emit = defineEmits(['notification-added', 'notification-removed'])

// Data
const notifications = ref([])
const notificationId = ref(0)
const $q = useQuasar()

// Methods
const getIconByType = (type) => {
  switch (type) {
    case 'success': return 'check_circle'
    case 'warning': return 'warning'
    case 'error': return 'error'
    case 'info': return 'info'
    default: return 'notifications'
  }
}

const getColorByType = (type) => {
  switch (type) {
    case 'success': return 'green'
    case 'warning': return 'orange'
    case 'error': return 'red'
    case 'info': return 'blue'
    default: return 'grey'
  }
}

const getTextColorByType = (type) => {
  switch (type) {
    case 'success': return 'green'
    case 'warning': return 'orange'
    case 'error': return 'red'
    case 'info': return 'blue'
    default: return 'grey'
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const addNotification = (title, message, type = 'info', autoDismiss = props.autoDismiss) => {
  const id = ++notificationId.value
  const notification = {
    id,
    title,
    message,
    type,
    timestamp: new Date()
  }
  
  notifications.value.push(notification)
  emit('notification-added', notification)
  
  if (autoDismiss && props.dismissTimeout > 0) {
    setTimeout(() => {
      removeNotification(id)
    }, props.dismissTimeout)
  }
  
  return id
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index !== -1) {
    const removed = notifications.value.splice(index, 1)[0]
    emit('notification-removed', removed)
  }
}

const clearAllNotifications = () => {
  notifications.value = []
}

// Expose methods to parent components
defineExpose({
  addNotification,
  removeNotification,
  clearAllNotifications
})

// Global notification helper registration
onMounted(() => {
  // Register global helper functions for easy access from other components
  if (typeof window !== 'undefined') {
    window.$notifications = {
      success: (title, message) => addNotification(title, message, 'success'),
      warning: (title, message) => addNotification(title, message, 'warning'),
      error: (title, message) => addNotification(title, message, 'error'),
      info: (title, message) => addNotification(title, message, 'info')
    }
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    delete window.$notifications
  }
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  max-width: 350px;
  width: 100%;
}

.notification-content {
  flex: 1;
}

.notification-success {
  background-color: rgba(76, 175, 80, 0.1);
  border-left: 4px solid #4CAF50;
}

.notification-warning {
  background-color: rgba(255, 152, 0, 0.1);
  border-left: 4px solid #FF9800;
}

.notification-error {
  background-color: rgba(244, 67, 54, 0.1);
  border-left: 4px solid #F44336;
}

.notification-info {
  background-color: rgba(33, 150, 243, 0.1);
  border-left: 4px solid #2196F3;
}
</style>