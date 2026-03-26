<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h4">Enhanced Demand Forecasting</div>
      <q-space />
      <div class="flex items-center">
        <q-select
          v-model="forecastDays"
          :options="dayOptions"
          label="Forecast Days"
          outlined
          dense
          style="min-width: 150px;"
          class="q-mr-md"
        />
        <q-btn flat round icon="refresh" @click="loadDashboard" :loading="loading">
          <q-tooltip>Refresh Data</q-tooltip>
        </q-btn>
      </div>
    </div>

    <div v-if="!isStaff" class="text-center q-pa-xl">
      <q-icon name="analytics" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Staff access required</div>
    </div>

    <div v-else>
      <div class="row q-mb-md">
        <q-btn color="secondary" label="Generate Sample Data" icon="science" @click="showSeedDialog = true" :loading="seeding" />
        <q-space />
        <q-btn color="primary" label="Process Auto-Orders" @click="processAutoOrders" :loading="processing" />
      </div>

      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Products Monitored</div>
              <div class="text-h4">{{ dashboard.total_products }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Need Attention</div>
              <div class="text-h4 text-warning">{{ dashboard.products_needing_attention }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Auto-Orders Enabled</div>
              <div class="text-h4 text-positive">{{ autoOrderCount }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Pending Orders</div>
              <div class="text-h4">{{ pendingOrders }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <q-tabs v-model="tab" class="q-mb-md" align="left" active-color="primary" indicator-color="primary">
        <q-tab name="products" label="Product Forecasts" />
        <q-tab name="seasonal" label="Seasonal Patterns" />
        <q-tab name="autoorder" label="Auto-Order Settings" />
        <q-tab name="orders" label="Purchase Orders" />
        <q-tab name="analytics" label="Analytics" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="products">
          <q-table
            :rows="dashboard.products || []"
            :columns="productColumns"
            row-key="product_id"
            :filter="productFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="productFilter" dense debounce="300" placeholder="Search">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-name="props">
              <q-td :props="props">
                <q-btn flat dense color="primary" :label="props.row.product_name" @click="showForecast(props.row)" />
              </q-td>
            </template>
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-badge v-if="props.row.needs_attention" color="warning">
                  Reorder Recommended
                </q-badge>
                <q-badge v-else color="positive">OK</q-badge>
              </q-td>
            </template>
            <template v-slot:body-cell-stock="props">
              <q-td :props="props">
                <q-chip :color="getStockColor(props.row.current_stock, props.row)" text-color="white" size="sm">
                  {{ props.row.current_stock }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-trend="props">
              <q-td :props="props">
                <q-chip 
                  :color="props.row.trend >= 0 ? 'positive' : 'negative'" 
                  text-color="white" 
                  size="sm"
                >
                  {{ props.row.trend >= 0 ? '+' : '' }}{{ props.row.trend }}%
                </q-chip>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="seasonal">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-4">
              <q-select
                v-model="selectedProduct"
                :options="productOptions"
                label="Select Product"
                emit-value
                map-options
                @update:model-value="loadSeasonalPatterns"
              />
            </div>
          </div>
          
          <div v-if="selectedProduct" class="q-mt-md">
            <q-card>
              <q-card-section>
                <div class="text-h6 q-mb-md">Monthly Demand Multipliers</div>
                <div class="row q-col-gutter-sm">
                  <div v-for="month in months" :key="month.num" class="col-6 col-sm-4 col-md-2">
                    <q-input
                      v-model.number="seasonalData[month.num]"
                      type="number"
                      :label="month.name"
                      step="0.1"
                      min="0"
                      max="5"
                      dense
                      outlined
                    >
                      <template v-slot:append>
                        <q-icon name="close" class="cursor-pointer" @click="seasonalData[month.num] = 1" />
                      </template>
                    </q-input>
                  </div>
                </div>
                <div class="q-mt-md">
                  <q-btn color="primary" label="Save Seasonal Patterns" @click="saveSeasonalPatterns" :loading="saving" />
                </div>
              </q-card-section>
            </q-card>
          </div>
        </q-tab-panel>

        <q-tab-panel name="autoorder">
          <q-table
            :rows="autoOrderProducts"
            :columns="autoOrderColumns"
            row-key="product_id"
            flat
          >
            <template v-slot:body-cell-enabled="props">
              <q-td :props="props">
                <q-toggle v-model="props.row.enabled" color="primary" @update:model-value="toggleAutoOrder(props.row)" />
              </q-td>
            </template>
            <template v-slot:body-cell-threshold="props">
              <q-td :props="props">
                <q-input
                  v-model.number="props.row.min_stock_threshold"
                  type="number"
                  dense
                  outlined
                  style="width: 80px"
                  @blur="updateAutoOrderSettings(props.row)"
                />
              </q-td>
            </template>
            <template v-slot:body-cell-orderQty="props">
              <q-td :props="props">
                <q-input
                  v-model.number="props.row.order_quantity"
                  type="number"
                  dense
                  outlined
                  style="width: 80px"
                  @blur="updateAutoOrderSettings(props.row)"
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="orders">
          <q-table
            :rows="purchaseOrders"
            :columns="poColumns"
            row-key="id"
            flat
          >
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-badge :color="statusColor(props.row.status)">
                  {{ props.row.status }}
                </q-badge>
              </q-td>
            </template>
            <template v-slot:body-cell-auto="props">
              <q-td :props="props">
                <q-badge v-if="props.row.is_auto_generated" color="info">Auto</q-badge>
              </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn-dropdown flat dense color="primary" label="Update Status">
                  <q-list>
                    <q-item clickable v-close-popup @click="updatePOStatus(props.row.id, 'ordered')">
                      <q-item-section>Mark Ordered</q-item-section>
                    </q-item>
                    <q-item clickable v-close-popup @click="updatePOStatus(props.row.id, 'received')">
                      <q-item-section>Mark Received</q-item-section>
                    </q-item>
                    <q-item clickable v-close-popup @click="updatePOStatus(props.row.id, 'cancelled')">
                      <q-item-section>Cancel</q-item-section>
                    </q-item>
                  </q-list>
                </q-btn-dropdown>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="analytics">
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Demand Trends</div>
                  <div style="height: 400px">
                    <Bar 
                      v-if="demandChart.data" 
                      :data="demandChart.data" 
                      :options="demandChart.options" 
                    />
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Forecast Detail Dialog -->
    <q-dialog v-model="showForecastDialog" persistent>
      <q-card style="min-width: 600px; max-width: 90vw;">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ selectedForecastProduct?.product_name }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="currentForecast">
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-6 col-md-3">
              <div class="text-caption text-grey">Current Stock</div>
              <div class="text-h5">{{ currentForecast.current_stock }}</div>
            </div>
            <div class="col-6 col-md-3">
              <div class="text-caption text-grey">Avg Daily Sales</div>
              <div class="text-h5">{{ currentForecast.avg_daily_sales }}</div>
            </div>
            <div class="col-6 col-md-3">
              <div class="text-caption text-grey">Trend</div>
              <div class="text-h5" :class="currentForecast.trend >= 0 ? 'text-positive' : 'text-negative'">
                {{ currentForecast.trend >= 0 ? '+' : '' }}{{ currentForecast.trend }}%
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="text-caption text-grey">30-Day Demand</div>
              <div class="text-h5">{{ currentForecast.total_predicted_demand }}</div>
            </div>
          </div>

          <div v-if="currentForecast.stock_depletion_date" class="q-mb-md">
            <q-banner class="bg-warning text-white">
              <template v-slot:avatar>
                <q-icon name="warning" />
              </template>
              Stock depletion date: {{ formatDate(currentForecast.stock_depletion_date) }}
            </q-banner>
          </div>

          <div v-if="currentForecast.recommended_order_date" class="q-mb-md">
            <q-banner class="bg-info text-white">
              <template v-slot:avatar>
                <q-icon name="shopping_cart" />
              </template>
              Recommended order date: {{ formatDate(currentForecast.recommended_order_date) }}
            </q-banner>
          </div>

          <div class="text-subtitle2 q-mb-sm">Demand Forecast</div>
          <div style="height: 300px" class="q-mb-md">
            <Line v-if="forecastChartData" :data="forecastChartData" :options="extendedChartOptions" />
          </div>
          
          <q-table
            :rows="currentForecast.forecasts || []"
            :columns="forecastColumns"
            flat
            dense
            :pagination="{ rowsPerPage: 10 }"
            class="q-mb-md"
          >
            <template v-slot:body-cell-date="props">
              <q-td :props="props">{{ formatDate(props.row.date) }}</q-td>
            </template>
          </q-table>
          
          <div class="text-subtitle2 q-mb-sm">Seasonal Patterns</div>
          <div class="row">
            <div v-for="(multiplier, month) in currentForecast.seasonal_patterns" :key="month" class="col-2">
              <div class="text-caption text-grey">{{ months[parseInt(month)-1]?.name }}</div>
              <div class="text-h6">{{ multiplier }}x</div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Seed Data Dialog -->
    <q-dialog v-model="showSeedDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Generate Sample Data</div>
        </q-card-section>
        <q-card-section>
          <p>This will generate 90 days of historical sales data and seasonal patterns for all products to help test the forecasting system.</p>
          <q-toggle v-model="seedOptions.includeStock" label="Also reset stock levels" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Generate" @click="runSeed" :loading="seeding" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { Line, Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  Filler 
} from 'chart.js'
import { forecastingAPI, inventoryAPI, seedAPI } from 'src/boot/api'
import { useAuthStore } from 'src/stores/auth'

// Register chart components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  Filler
)

const $q = useQuasar()
const authStore = useAuthStore()

// Reactive data
const isStaff = computed(() => authStore.user?.is_staff || false)
const tab = ref('products')
const productFilter = ref('')
const showHelp = ref(false)
const showSeedDialog = ref(false)
const seeding = ref(false)
const seedOptions = ref({ includeStock: true })
const loading = ref(false)
const saving = ref(false)
const processing = ref(false)
const forecastDays = ref(30)

const dashboard = ref({})
const purchaseOrders = ref([])
const autoOrderProducts = ref([])
const selectedProduct = ref(null)
const selectedForecastProduct = ref(null)
const currentForecast = ref(null)
const showForecastDialog = ref(false)

const seasonalData = ref({})
const productOptions = ref([])
const dayOptions = ref([
  { label: '7 Days', value: 7 },
  { label: '30 Days', value: 30 },
  { label: '60 Days', value: 60 },
  { label: '90 Days', value: 90 }
])

// Chart configuration
const extendedChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    y: { 
      beginAtZero: true, 
      title: { display: true, text: 'Quantity' },
      ticks: { precision: 0 }
    },
    x: { title: { display: true, text: 'Date' } }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

// Computed properties
const autoOrderCount = computed(() => autoOrderProducts.value.filter(p => p.enabled).length)
const pendingOrders = computed(() => purchaseOrders.value.filter(o => o.status === 'pending').length)

const demandChart = computed(() => {
  if (!dashboard.value.products) return { data: null, options: {} }
  
  const labels = dashboard.value.products.map(p => p.product_name.substring(0, 15))
  const stockData = dashboard.value.products.map(p => p.current_stock)
  const predictedData = dashboard.value.products.map(p => p.total_predicted_demand)
  const avgSalesData = dashboard.value.products.map(p => Math.round(p.avg_daily_sales))
  
  return {
    data: {
      labels,
      datasets: [
        {
          label: 'Current Stock',
          data: stockData,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgb(75, 192, 192)',
          borderWidth: 1
        },
        {
          label: '30-Day Demand',
          data: predictedData,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgb(255, 99, 132)',
          borderWidth: 1
        },
        {
          label: 'Avg Daily Sales',
          data: avgSalesData,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgb(54, 162, 235)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { 
          beginAtZero: true,
          title: { display: true, text: 'Quantity' },
          ticks: { precision: 0 }
        },
        x: { 
          title: { display: true, text: 'Products' },
          ticks: { maxRotation: 45, minRotation: 45 }
        }
      }
    }
  }
})

const months = [
  { num: 1, name: 'Jan' }, { num: 2, name: 'Feb' }, { num: 3, name: 'Mar' },
  { num: 4, name: 'Apr' }, { num: 5, name: 'May' }, { num: 6, name: 'Jun' },
  { num: 7, name: 'Jul' }, { num: 8, name: 'Aug' }, { num: 9, name: 'Sep' },
  { num: 10, name: 'Oct' }, { num: 11, name: 'Nov' }, { num: 12, name: 'Dec' }
]

// Table columns
const productColumns = [
  { name: 'name', label: 'Product', field: 'product_name', align: 'left', sortable: true },
  { name: 'stock', label: 'Stock', field: 'current_stock', align: 'center' },
  { name: 'avg_sales', label: 'Avg Daily', field: 'avg_daily_sales', align: 'center' },
  { name: 'predicted', label: '30-Day Demand', field: 'total_predicted_demand', align: 'center' },
  { name: 'depletion', label: 'Depletion Date', field: 'stock_depletion_date', align: 'center' },
  { name: 'trend', label: 'Trend', field: 'trend', align: 'center' },
  { name: 'status', label: 'Status', field: 'needs_attention', align: 'center' }
]

const autoOrderColumns = [
  { name: 'name', label: 'Product', field: 'product_name', align: 'left' },
  { name: 'enabled', label: 'Auto-Order', field: 'enabled', align: 'center' },
  { name: 'threshold', label: 'Min Stock', field: 'min_stock_threshold', align: 'center' },
  { name: 'orderQty', label: 'Order Qty', field: 'order_quantity', align: 'center' },
  { name: 'stock', label: 'Current', field: 'current_stock', align: 'center' }
]

const poColumns = [
  { name: 'number', label: 'Order #', field: 'order_number', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'amount', label: 'Amount', field: 'total_amount', align: 'right', format: val => `$${val?.toFixed(2)}` },
  { name: 'auto', label: 'Type', field: 'is_auto_generated', align: 'center' },
  { name: 'date', label: 'Created', field: 'created_at', align: 'center', format: val => formatDate(val) },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
]

const forecastColumns = [
  { name: 'date', label: 'Date', field: 'date', align: 'left' },
  { name: 'predicted', label: 'Predicted', field: 'predicted_quantity', align: 'center' },
  { name: 'low', label: 'Low', field: 'confidence_low', align: 'center' },
  { name: 'high', label: 'High', field: 'confidence_high', align: 'center' }
]

// Computed forecast chart data
const forecastChartData = computed(() => {
  if (!currentForecast.value?.forecasts) return null
  
  const labels = currentForecast.value.forecasts.map(f => formatDateShort(f.date))
  return {
    labels,
    datasets: [
      {
        label: 'Predicted Demand',
        data: currentForecast.value.forecasts.map(f => f.predicted_quantity),
        borderColor: '#1976D2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: false,
        tension: 0.4,
        yAxisID: 'y'
      },
      {
        label: 'Confidence Low',
        data: currentForecast.value.forecasts.map(f => f.confidence_low),
        borderColor: '#4CAF50',
        borderDash: [5, 5],
        pointRadius: 0,
        yAxisID: 'y'
      },
      {
        label: 'Confidence High',
        data: currentForecast.value.forecasts.map(f => f.confidence_high),
        borderColor: '#4CAF50',
        borderDash: [5, 5],
        pointRadius: 0,
        yAxisID: 'y'
      }
    ]
  }
})

// Helper methods
function formatDateShort(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function statusColor(status) {
  const colors = { pending: 'warning', ordered: 'info', received: 'positive', cancelled: 'negative' }
  return colors[status] || 'grey'
}

function getStockColor(stock, product) {
  const threshold = product.min_stock_threshold || 10
  if (stock <= 0) return 'negative'
  if (stock <= threshold) return 'warning'
  return 'positive'
}

// API methods
async function loadDashboard() {
  loading.value = true
  try {
    const [dash, orders, products] = await Promise.all([
      forecastingAPI.getDashboard(),
      forecastingAPI.getPurchaseOrders(),
      inventoryAPI.getProducts()
    ])
    
    dashboard.value = dash.data
    purchaseOrders.value = orders.data
    
    const productMap = {}
    products.data.forEach(p => { productMap[p.id] = p })
    
    autoOrderProducts.value = (dash.data.products || []).map(p => ({
      product_id: p.product_id,
      product_name: p.product_name,
      current_stock: p.current_stock,
      enabled: false,
      min_stock_threshold: 10,
      order_quantity: 50
    }))
    
    productOptions.value = products.data.map(p => ({ label: p.name, value: p.id }))
    
    for (const p of autoOrderProducts.value) {
      try {
        const settings = await forecastingAPI.getAutoOrderSettings(p.product_id)
        p.enabled = settings.data.enabled
        p.min_stock_threshold = settings.data.min_stock_threshold
        p.order_quantity = settings.data.order_quantity
      } catch {}
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load forecasting data' })
  } finally {
    loading.value = false
  }
}

async function showForecast(row) {
  selectedForecastProduct.value = row
  try {
    const res = await forecastingAPI.getForecast(row.product_id, forecastDays.value)
    currentForecast.value = res.data
    showForecastDialog.value = true
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load forecast' })
  }
}

async function loadSeasonalPatterns() {
  if (!selectedProduct.value) return
  try {
    const res = await forecastingAPI.getSeasonalPatterns(selectedProduct.value)
    seasonalData.value = {}
    months.forEach(m => { seasonalData.value[m.num] = 1 })
    res.data.forEach(p => { seasonalData.value[p.month] = p.demand_multiplier })
  } catch (err) {
    months.forEach(m => { seasonalData.value[m.num] = 1 })
  }
}

async function saveSeasonalPatterns() {
  if (!selectedProduct.value) return
  saving.value = true
  try {
    for (const month of months) {
      await forecastingAPI.setSeasonalPattern(selectedProduct.value, {
        month: month.num,
        demand_multiplier: seasonalData.value[month.num] || 1,
        notes: ''
      })
    }
    $q.notify({ type: 'positive', message: 'Seasonal patterns saved' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to save patterns' })
  } finally {
    saving.value = false
  }
}

async function toggleAutoOrder(row) {
  await updateAutoOrderSettings(row)
}

async function updateAutoOrderSettings(row) {
  try {
    await forecastingAPI.updateAutoOrderSettings(row.product_id, {
      enabled: row.enabled,
      min_stock_threshold: row.min_stock_threshold,
      order_quantity: row.order_quantity
    })
    $q.notify({ type: 'positive', message: 'Settings updated' })
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update settings' })
  }
}

async function processAutoOrders() {
  processing.value = true
  try {
    const res = await forecastingAPI.processAutoOrders()
    $q.notify({ type: 'positive', message: `Created ${res.data.orders_created} orders` })
    await loadDashboard()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to process auto-orders' })
  } finally {
    processing.value = false
  }
}

async function updatePOStatus(orderId, status) {
  try {
    await forecastingAPI.updatePurchaseOrder(orderId, status)
    $q.notify({ type: 'positive', message: 'Order updated' })
    await loadDashboard()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update order' })
  }
}

async function runSeed() {
  showSeedDialog.value = false
  seeding.value = true
  try {
    if (seedOptions.value.includeStock) {
      await seedAPI.seedStock()
    }
    const res = await seedAPI.seedForecasting()
    $q.notify({ 
      type: 'positive', 
      message: `Generated ${res.data.sales_records} sales records and ${res.data.seasonal_patterns} seasonal patterns` 
    })
    await loadDashboard()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to seed data' })
  } finally {
    seeding.value = false
  }
}

// Watch for forecast days change
watch(forecastDays, () => {
  if (showForecastDialog.value && selectedForecastProduct.value) {
    showForecast(selectedForecastProduct.value)
  }
})

// Initialize on mount
onMounted(() => {
  if (authStore.isAuthenticated && isStaff.value) {
    loadDashboard()
  }
})
</script>