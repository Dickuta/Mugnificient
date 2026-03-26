<template>
  <q-page class="q-pa-md">
    <div class="text-h4 q-mb-md">Inventory ML Predictions</div>

    <div v-if="!isStaff" class="text-center q-pa-xl">
      <q-icon name="inventory_2" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Staff access required</div>
    </div>

    <div v-else>
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Total Products</div>
              <div class="text-h4">{{ predictions.length }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Critical Risk</div>
              <div class="text-h4 text-negative">{{ criticalCount }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">High Risk</div>
              <div class="text-h4 text-warning">{{ highCount }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Pending Refills</div>
              <div class="text-h4 text-info">{{ pendingRefills }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <q-tabs v-model="tab" class="q-mb-md" align="left" active-color="primary" indicator-color="primary">
        <q-tab name="predictions" label="Predictions" />
        <q-tab name="refills" label="Refill Requests" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="predictions">
          <q-table
            :rows="predictions"
            :columns="predictionColumns"
            row-key="product_id"
            :filter="predictionFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="predictionFilter" dense debounce="300" placeholder="Search">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-risk="props">
              <q-td :props="props">
                <q-badge :color="riskColor(props.row.risk_level)">
                  {{ props.row.risk_level }}
                </q-badge>
              </q-td>
            </template>
            <template v-slot:body-cell-stockout="props">
              <q-td :props="props">
                {{ props.row.predicted_stockout_date ? formatDate(props.row.predicted_stockout_date) : '-' }}
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <q-tab-panel name="refills">
          <q-table
            :rows="refillRequests"
            :columns="refillColumns"
            row-key="id"
            :filter="refillFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="refillFilter" dense debounce="300" placeholder="Search">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-badge :color="refillStatusColor(props.row.status)">
                  {{ props.row.status }}
                </q-badge>
              </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn-group v-if="props.row.status === 'pending'" flat>
                  <q-btn flat dense color="positive" icon="check" @click="approveRefill(props.row.id, true)">
                    <q-tooltip>Approve</q-tooltip>
                  </q-btn>
                  <q-btn flat dense color="negative" icon="close" @click="approveRefill(props.row.id, false)">
                    <q-tooltip>Reject</q-tooltip>
                  </q-btn>
                </q-btn-group>
                <q-btn v-else-if="props.row.status === 'approved'" flat dense color="primary" label="Mark Ordered" @click="markOrdered(props.row.id)" />
                <q-btn v-else-if="props.row.status === 'ordered'" flat dense color="positive" label="Receive" @click="showReceiveDialog(props.row)" />
                <span v-else>-</span>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>

      <q-dialog v-model="receiveDialog">
        <q-card style="min-width: 300px">
          <q-card-section>
            <div class="text-h6">Receive Stock</div>
          </q-card-section>
          <q-card-section>
            <q-input v-model.number="receiveQuantity" type="number" label="Quantity Received" outlined />
            <q-input v-model.number="receiveCost" type="number" label="Actual Cost" outlined class="q-mt-md" />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn color="positive" label="Confirm Receipt" @click="confirmReceive" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { inventoryMLAPI } from 'src/boot/api'
import { useAuthStore } from 'src/stores/auth'

const $q = useQuasar()
const authStore = useAuthStore()

const isStaff = computed(() => authStore.user?.is_staff || false)
const tab = ref('predictions')
const predictionFilter = ref('')
const refillFilter = ref('')

const predictions = ref([])
const refillRequests = ref([])
const receiveDialog = ref(false)
const selectedRefill = ref(null)
const receiveQuantity = ref(0)
const receiveCost = ref(0)

const criticalCount = computed(() => predictions.value.filter(p => p.risk_level === 'critical').length)
const highCount = computed(() => predictions.value.filter(p => p.risk_level === 'high').length)
const pendingRefills = computed(() => refillRequests.value.filter(r => r.status === 'pending').length)

const predictionColumns = [
  { name: 'name', label: 'Product', field: 'product_name', align: 'left', sortable: true },
  { name: 'stock', label: 'Current Stock', field: 'current_stock', align: 'center' },
  { name: 'sales', label: '30-Day Sales', field: 'sales_last_30_days', align: 'center' },
  { name: 'daily', label: 'Daily Avg', field: 'daily_average_sales', align: 'center' },
  { name: 'stockout', label: 'Stockout Date', field: 'predicted_stockout_date', align: 'center' },
  { name: 'risk', label: 'Risk', field: 'risk_level', align: 'center' },
  { name: 'recommend', label: 'Order Qty', field: 'recommended_order_quantity', align: 'center' }
]

const refillColumns = [
  { name: 'product', label: 'Product', field: 'product_name', align: 'left' },
  { name: 'supplier', label: 'Supplier', field: 'supplier_name', align: 'left' },
  { name: 'quantity', label: 'Qty', field: 'quantity_requested', align: 'center' },
  { name: 'cost', label: 'Est. Cost', field: 'estimated_cost', align: 'right', format: val => `$${val?.toFixed(2)}` },
  { name: 'status', label: 'Status', field: 'status', align: 'center' },
  { name: 'date', label: 'Requested', field: 'requested_at', align: 'center', format: val => formatDate(val) },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
]

function riskColor(risk) {
  const colors = { critical: 'negative', high: 'warning', medium: 'orange', low: 'positive' }
  return colors[risk] || 'grey'
}

function refillStatusColor(status) {
  const colors = { pending: 'warning', approved: 'info', ordered: 'primary', received: 'positive', cancelled: 'negative' }
  return colors[status] || 'grey'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function loadData() {
  try {
    const [preds, refills] = await Promise.all([
      inventoryMLAPI.getAllPredictions(),
      inventoryMLAPI.getRefillRequests()
    ])
    predictions.value = preds.data
    refillRequests.value = refills.data
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load data' })
  }
}

async function approveRefill(id, approved) {
  try {
    await inventoryMLAPI.approveRefill(id, approved)
    $q.notify({ type: 'positive', message: approved ? 'Refill approved' : 'Refill rejected' })
    await loadData()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update refill' })
  }
}

async function markOrdered(id) {
  try {
    await inventoryMLAPI.markOrdered(id)
    $q.notify({ type: 'positive', message: 'Marked as ordered' })
    await loadData()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update' })
  }
}

function showReceiveDialog(refill) {
  selectedRefill.value = refill
  receiveQuantity.value = refill.quantity_requested
  receiveCost.value = refill.estimated_cost
  receiveDialog.value = true
}

async function confirmReceive() {
  try {
    await inventoryMLAPI.receiveRefill(selectedRefill.value.id, receiveQuantity.value, receiveCost.value)
    $q.notify({ type: 'positive', message: 'Stock received and added to inventory' })
    receiveDialog.value = false
    await loadData()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to receive stock' })
  }
}

onMounted(() => {
  if (authStore.isAuthenticated && isStaff.value) {
    loadData()
  }
})
</script>
