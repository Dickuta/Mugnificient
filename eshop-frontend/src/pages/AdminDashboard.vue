<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Admin Dashboard</div>

    <div v-if="!isAdmin" class="text-center q-pa-xl">
      <q-icon name="lock" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Admin access required</div>
    </div>

    <div v-else>
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Total Products</div>
              <div class="text-h4">{{ stats.total_products }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Total Orders</div>
              <div class="text-h4">{{ stats.total_orders }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Total Revenue</div>
              <div class="text-h4 text-positive">${{ stats.total_revenue?.toFixed(2) || '0.00' }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Total Users</div>
              <div class="text-h4">{{ stats.total_users }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Sales Over Time</div>
              <div style="height: 300px">
                <Line :data="salesChartData" :options="chartOptions" />
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Sales by Category</div>
              <div style="height: 300px">
                <Doughnut :data="categoryChartData" :options="chartOptions" />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Top Products</div>
              <q-list separator>
                <q-item v-for="(product, index) in topProducts" :key="index">
                  <q-item-section>
                    <q-item-label>{{ product.name }}</q-item-label>
                    <q-item-label caption>{{ product.quantity_sold }} sold</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-positive">${{ product.revenue?.toFixed(2) }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 q-mb-md">Recent Orders</div>
              <q-list separator>
                <q-item v-for="order in recentOrders" :key="order.id">
                  <q-item-section>
                    <q-item-label>#{{ order.order_number }}</q-item-label>
                    <q-item-label caption>{{ formatDate(order.created_at) }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-badge :color="order.is_paid ? 'positive' : 'warning'">
                      {{ order.is_paid ? 'Paid' : 'Pending' }}
                    </q-badge>
                    <div class="text-subtitle1 q-mt-sm">${{ order.total?.toFixed(2) }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { Line, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import { adminAPI } from 'src/boot/api'
import { useAuthStore } from 'src/stores/auth'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

const $q = useQuasar()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.is_staff || false)
const stats = ref({})
const salesData = ref([])
const categoryData = ref([])
const topProducts = ref([])
const recentOrders = ref([])

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
}

const salesChartData = computed(() => ({
  labels: salesData.value.map(d => d.date),
  datasets: [{
    label: 'Revenue',
    data: salesData.value.map(d => d.revenue),
    borderColor: '#1976D2',
    backgroundColor: 'rgba(25, 118, 210, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

const categoryChartData = computed(() => ({
  labels: categoryData.value.map(d => d.category),
  datasets: [{
    data: categoryData.value.map(d => d.revenue),
    backgroundColor: ['#1976D2', '#26A69A', '#9C27B0', '#F2C037', '#C10015']
  }]
}))

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric'
  })
}

async function loadDashboard() {
  try {
    const [dashboard, sales, category, top, recent] = await Promise.all([
      adminAPI.getDashboard(),
      adminAPI.getSalesOverTime(30),
      adminAPI.getSalesByCategory(),
      adminAPI.getTopProducts(5),
      adminAPI.getRecentOrders(5)
    ])
    stats.value = dashboard.data
    salesData.value = sales.data
    categoryData.value = category.data
    topProducts.value = top.data
    recentOrders.value = recent.data
  } catch (err) {
    if (err.response?.status === 403) {
      $q.notify({ type: 'negative', message: 'Admin access required' })
    } else {
      $q.notify({ type: 'negative', message: 'Failed to load dashboard' })
    }
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadDashboard()
  }
})
</script>
