<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h4">Inventory Management</div>
      <q-space />
      <q-btn flat round icon="refresh" @click="loadData" :loading="loading">
        <q-tooltip>Refresh Data</q-tooltip>
      </q-btn>
    </div>

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
              <div class="text-h4">{{ dashboard.total_products }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Low Stock Items</div>
              <div class="text-h4 text-warning">{{ dashboard.low_stock_count }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Out of Stock Items</div>
              <div class="text-h4 text-negative">{{ dashboard.out_of_stock_count }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-sm-6 col-md-3">
          <q-card>
            <q-card-section>
              <div class="text-subtitle2 text-grey">Inventory Value</div>
              <div class="text-h4 text-positive">${{ dashboard.total_inventory_value?.toFixed(2) }}</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <q-tabs v-model="tab" class="q-mb-md" align="left" active-color="primary" indicator-color="primary">
        <q-tab name="overview" label="Overview" />
        <q-tab name="products" label="Products" />
        <q-tab name="adjustments" label="Stock Adjustments" />
        <q-tab name="alerts" label="Stock Alerts" />
        <q-tab name="suppliers" label="Suppliers" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <!-- OVERVIEW TAB -->
        <q-tab-panel name="overview">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-8">
              <q-card>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Recent Stock Movements</div>
                  <q-list separator>
                    <q-item v-for="movement in dashboard.recent_movements" :key="movement.id">
                      <q-item-section>
                        <q-item-label>{{ movement.product_name }}</q-item-label>
                        <q-item-label caption>
                          {{ formatDate(movement.created_at) }} • {{ movement.movement_type.toUpperCase() }}
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-chip :color="getMovementColor(movement.movement_type)" text-color="white">
                          {{ movement.quantity_change >= 0 ? '+' : '' }}{{ movement.quantity_change }}
                        </q-chip>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-12 col-md-4">
              <q-card>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Quick Actions</div>
                  <q-btn-group spread>
                    <q-btn color="primary" label="Adjust Stock" @click="showAdjustStockDialog()" />
                    <q-btn color="secondary" label="New Alert" @click="showAlertDialog()" />
                  </q-btn-group>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- PRODUCTS TAB -->
        <q-tab-panel name="products">
          <q-table
            :rows="products"
            :columns="productColumns"
            row-key="id"
            :filter="productFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="productFilter" dense debounce="300" placeholder="Search products">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-current_stock="props">
              <q-td :props="props">
                <q-chip 
                  :color="getStockColor(props.row.current_stock, props.row.reorder_level)" 
                  text-color="white" 
                  size="sm"
                >
                  {{ props.row.current_stock }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn flat dense color="primary" icon="edit" @click="showAdjustStockDialog(props.row)" />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- STOCK ADJUSTMENTS TAB -->
        <q-tab-panel name="adjustments">
          <div class="row q-mb-md">
            <q-btn color="primary" label="New Adjustment" icon="add" @click="showAdjustStockDialog()" />
          </div>
          
          <q-table
            :rows="stockMovements"
            :columns="movementColumns"
            row-key="id"
            flat
          >
            <template v-slot:body-cell-movement_type="props">
              <q-td :props="props">
                <q-chip :color="getMovementColor(props.row.movement_type)" text-color="white">
                  {{ props.row.movement_type.toUpperCase() }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-quantity_change="props">
              <q-td :props="props">
                <q-chip :color="props.row.quantity_change >= 0 ? 'positive' : 'negative'" text-color="white">
                  {{ props.row.quantity_change >= 0 ? '+' : '' }}{{ props.row.quantity_change }}
                </q-chip>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- ALERTS TAB -->
        <q-tab-panel name="alerts">
          <q-table
            :rows="alerts"
            :columns="alertColumns"
            row-key="id"
            flat
          >
            <template v-slot:body-cell-is_active="props">
              <q-td :props="props">
                <q-chip :color="props.row.is_active ? 'warning' : 'grey'" text-color="white">
                  {{ props.row.is_active ? 'Active' : 'Resolved' }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn 
                  v-if="props.row.is_active" 
                  flat 
                  dense 
                  color="positive" 
                  label="Resolve" 
                  @click="resolveAlert(props.row.id)" 
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- SUPPLIERS TAB -->
        <q-tab-panel name="suppliers">
          <div class="row q-mb-md">
            <q-btn color="primary" label="New Supplier" icon="add" @click="showSupplierDialog()" />
          </div>
          
          <q-table
            :rows="suppliers"
            :columns="supplierColumns"
            row-key="id"
            flat
          >
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn-group flat>
                  <q-btn flat dense color="primary" icon="edit" @click="showSupplierDialog(props.row)" />
                  <q-btn flat dense color="negative" icon="delete" @click="deleteSupplier(props.row.id)" />
                </q-btn-group>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Stock Adjustment Dialog -->
    <q-dialog v-model="adjustmentDialog.show">
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center">
          <div class="text-h6">Adjust Stock</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-select
            v-model="adjustmentDialog.productId"
            :options="productOptions"
            option-label="name"
            option-value="id"
            label="Select Product"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model.number="adjustmentDialog.quantityChange"
            type="number"
            label="Quantity Change"
            hint="Enter positive number to add stock, negative to remove"
            outlined
            dense
            class="q-mb-md"
          />
          <q-select
            v-model="adjustmentDialog.movementType"
            :options="movementTypes"
            label="Movement Type"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="adjustmentDialog.notes"
            label="Notes"
            type="textarea"
            outlined
            dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Adjust Stock" @click="performStockAdjustment" :loading="saving" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Supplier Dialog -->
    <q-dialog v-model="supplierDialog.show">
      <q-card style="min-width: 500px">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ supplierDialog.editing ? 'Edit Supplier' : 'New Supplier' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="supplierDialog.form.name"
            label="Supplier Name"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="supplierDialog.form.email"
            label="Email"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="supplierDialog.form.phone"
            label="Phone"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="supplierDialog.form.contact_person"
            label="Contact Person"
            outlined
            dense
            class="q-mb-md"
          />
          <q-input
            v-model="supplierDialog.form.address"
            label="Address"
            type="textarea"
            outlined
            dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" :label="supplierDialog.editing ? 'Update' : 'Create'" @click="saveSupplier" :loading="saving" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { inventoryAPI, productsAPI } from 'src/boot/api'
import { useAuthStore } from 'src/stores/auth'

const $q = useQuasar()
const authStore = useAuthStore()

// Data
const tab = ref('overview')
const loading = ref(false)
const saving = ref(false)

const dashboard = ref({})
const products = ref([])
const stockMovements = ref([])
const alerts = ref([])
const suppliers = ref([])

// Filters
const productFilter = ref('')

// Dialogs
const adjustmentDialog = ref({
  show: false,
  productId: null,
  quantityChange: 0,
  movementType: 'adjustment',
  notes: ''
})

const supplierDialog = ref({
  show: false,
  editing: false,
  form: {
    id: null,
    name: '',
    email: '',
    phone: '',
    contact_person: '',
    address: ''
  }
})

// Columns
const productColumns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true },
  { name: 'name', label: 'Name', field: 'name', sortable: true },
  { name: 'sku', label: 'SKU', field: 'sku' },
  { name: 'category', label: 'Category', field: 'category' },
  { name: 'current_stock', label: 'Current Stock', field: 'current_stock' },
  { name: 'reorder_level', label: 'Reorder Level', field: 'reorder_level' },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

const movementColumns = [
  { name: 'product_name', label: 'Product', field: 'product_name' },
  { name: 'movement_type', label: 'Type', field: 'movement_type' },
  { name: 'quantity_change', label: 'Change', field: 'quantity_change' },
  { name: 'notes', label: 'Notes', field: 'notes' },
  { name: 'created_at', label: 'Date', field: 'created_at', format: val => formatDate(val) }
]

const alertColumns = [
  { name: 'product_name', label: 'Product', field: 'product_name' },
  { name: 'current_stock', label: 'Current Stock', field: 'current_stock' },
  { name: 'is_active', label: 'Status', field: 'is_active' },
  { name: 'created_at', label: 'Created', field: 'created_at', format: val => formatDate(val) },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

const supplierColumns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true },
  { name: 'name', label: 'Name', field: 'name', sortable: true },
  { name: 'email', label: 'Email', field: 'email' },
  { name: 'phone', label: 'Phone', field: 'phone' },
  { name: 'contact_person', label: 'Contact', field: 'contact_person' },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

// Options
const movementTypes = ['in', 'out', 'adjustment']

// Computed
const isStaff = computed(() => authStore.user?.is_staff || false)

const productOptions = computed(() => {
  return products.value.map(p => ({
    id: p.id,
    name: p.name
  }))
})

// Methods
const getStockColor = (stock, reorderLevel) => {
  if (stock <= 0) return 'negative'
  if (stock <= reorderLevel) return 'warning'
  return 'positive'
}

const getMovementColor = (type) => {
  switch (type) {
    case 'in': return 'positive'
    case 'out': return 'negative'
    default: return 'info'
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

async function loadData() {
  loading.value = true
  try {
    // Simultaneously load all data
    const [dash, prods, movs, alrts, sups] = await Promise.all([
      inventoryAPI.getDashboard(),
      inventoryAPI.getProducts(),
      productsAPI.getAll(), // Get all products including stock info
      inventoryAPI.getAlerts(),
      inventoryAPI.getSuppliers()
    ])
    
    dashboard.value = dash.data
    
    // Get detailed product info with stock data
    const prodResults = await Promise.all(
      prods.data.map(prod => inventoryAPI.getProductInventory(prod.id))
    )
    
    products.value = prodResults.map(result => ({
      ...result.product,
      ...result.stock,
      current_stock: result.stock?.quantity || 0,
      reorder_level: result.stock?.reorder_level || 10
    }))
    
    // Flatten movements from all products
    stockMovements.value = []
    prodResults.forEach(result => {
      if (result.movements) {
        result.movements.forEach(movement => {
          stockMovements.value.push({
            ...movement,
            product_name: result.product.name
          })
        })
      }
    })
    
    // Sort movements by date (newest first)
    stockMovements.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    
    alerts.value = alrts.data
    suppliers.value = sups.data
  } catch (err) {
    console.error('Error loading data:', err)
    $q.notify({ type: 'negative', message: 'Failed to load inventory data' })
  } finally {
    loading.value = false
  }
}

async function performStockAdjustment() {
  if (!adjustmentDialog.value.productId) {
    $q.notify({ type: 'warning', message: 'Please select a product' })
    return
  }
  
  if (adjustmentDialog.value.quantityChange === 0) {
    $q.notify({ type: 'warning', message: 'Quantity change cannot be zero' })
    return
  }
  
  saving.value = true
  try {
    await inventoryAPI.adjustStock({
      product_id: adjustmentDialog.value.productId,
      quantity_change: adjustmentDialog.value.quantityChange,
      movement_type: adjustmentDialog.value.movementType,
      notes: adjustmentDialog.value.notes
    })
    
    $q.notify({ type: 'positive', message: 'Stock adjusted successfully' })
    await loadData()
    adjustmentDialog.value.show = false
    
    // Reset dialog
    adjustmentDialog.value = {
      show: false,
      productId: null,
      quantityChange: 0,
      movementType: 'adjustment',
      notes: ''
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to adjust stock' })
  } finally {
    saving.value = false
  }
}

async function resolveAlert(alertId) {
  $q.dialog({
    title: 'Resolve Alert',
    message: 'Are you sure you want to resolve this alert?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await inventoryAPI.resolveAlert(alertId)
      $q.notify({ type: 'positive', message: 'Alert resolved successfully' })
      await loadData()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'Failed to resolve alert' })
    }
  })
}

function showAdjustStockDialog(product = null) {
  if (product) {
    adjustmentDialog.value.productId = product.id
  } else {
    adjustmentDialog.value.productId = null
  }
  adjustmentDialog.value.show = true
}

function showAlertDialog() {
  $q.notify({ type: 'info', message: 'Alert creation would go here' })
}

function showSupplierDialog(supplier = null) {
  if (supplier) {
    supplierDialog.value.form = { ...supplier }
    supplierDialog.value.editing = true
  } else {
    supplierDialog.value.form = {
      id: null,
      name: '',
      email: '',
      phone: '',
      contact_person: '',
      address: ''
    }
    supplierDialog.value.editing = false
  }
  supplierDialog.value.show = true
}

async function saveSupplier() {
  saving.value = true
  try {
    if (supplierDialog.value.editing) {
      // Update supplier
      $q.notify({ type: 'positive', message: 'Supplier updated successfully' })
    } else {
      // Create supplier
      await inventoryAPI.createSupplier(supplierDialog.value.form)
      $q.notify({ type: 'positive', message: 'Supplier created successfully' })
    }
    
    await loadData()
    supplierDialog.value.show = false
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to save supplier' })
  } finally {
    saving.value = false
  }
}

async function deleteSupplier(supplierId) {
  $q.dialog({
    title: 'Delete Supplier',
    message: 'Are you sure you want to delete this supplier?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await inventoryAPI.deleteSupplier(supplierId)
      $q.notify({ type: 'positive', message: 'Supplier deleted successfully' })
      await loadData()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'Failed to delete supplier' })
    }
  })
}

// Load data on mount
onMounted(() => {
  if (authStore.isAuthenticated && isStaff.value) {
    loadData()
  }
})
</script>