<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h4">Role & Permission Management</div>
      <q-space />
      <q-btn flat round icon="refresh" @click="refreshData" :loading="loading">
        <q-tooltip>Refresh</q-tooltip>
      </q-btn>
    </div>

    <div v-if="!isAdmin" class="text-center q-pa-xl">
      <q-icon name="lock" size="100px" color="grey-4" />
      <div class="text-h6 q-mt-md text-grey">Admin access required</div>
    </div>

    <div v-else>
      <q-tabs v-model="tab" class="q-mb-md" align="left" active-color="primary" indicator-color="primary">
        <q-tab name="roles" label="Roles" />
        <q-tab name="permissions" label="Permissions" />
        <q-tab name="users" label="User Management" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <!-- ROLES TAB -->
        <q-tab-panel name="roles">
          <div class="row q-mb-md">
            <q-btn color="primary" label="Create Role" icon="add" @click="showRoleDialog()" />
            <q-space />
            <q-btn flat color="primary" label="Seed Defaults" @click="seedDefaultsHandler" :loading="loading" />
          </div>
          
          <q-table
            :rows="roles"
            :columns="roleColumns"
            row-key="id"
            :filter="roleFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="roleFilter" dense debounce="300" placeholder="Search roles">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn-group flat>
                  <q-btn flat dense color="primary" icon="edit" @click="showRoleDialog(props.row)" />
                  <q-btn flat dense color="negative" icon="delete" @click="deleteRole(props.row.id)" />
                </q-btn-group>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- PERMISSIONS TAB -->
        <q-tab-panel name="permissions">
          <div class="row q-mb-md">
            <q-btn color="primary" label="Create Permission" icon="add" @click="showPermissionDialog()" />
          </div>
          
          <q-table
            :rows="permissions"
            :columns="permissionColumns"
            row-key="id"
            :filter="permissionFilter"
            flat
          >
            <template v-slot:top-right>
              <q-input v-model="permissionFilter" dense debounce="300" placeholder="Search permissions">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn-group flat>
                  <q-btn flat dense color="negative" icon="delete" @click="deletePermission(props.row.id)" />
                </q-btn-group>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>

        <!-- USERS TAB -->
        <q-tab-panel name="users">
          <div class="row q-mb-md">
            <q-input v-model="userFilter" dense debounce="300" placeholder="Search users" class="q-mr-md">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-space />
            <q-btn flat color="primary" label="Refresh Users" @click="loadUsers" :loading="loading" />
          </div>
          
          <q-table
            :rows="users"
            :columns="userColumns"
            row-key="id"
            flat
          >
            <template v-slot:body-cell-role="props">
              <q-td :props="props">
                <q-chip 
                  :color="props.row.role ? 'primary' : 'grey'" 
                  text-color="white" 
                  size="sm"
                >
                  {{ props.row.role?.name || 'No Role' }}
                </q-chip>
              </q-td>
            </template>
            <template v-slot:body-cell-is_staff="props">
              <q-td :props="props">
                <q-toggle 
                  v-model="props.row.is_staff" 
                  @update:model-value="toggleStaffStatus(props.row.id, props.row.is_staff)"
                  :disable="props.row.id === authStore.user.id" 
                />
              </q-td>
            </template>
            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-select
                  v-model="props.row.role"
                  :options="selectableRoles"
                  option-label="name"
                  option-value="id"
                  emit-value
                  map-options
                  dense
                  outlined
                  @update:model-value="assignUserRole(props.row.id, props.row.role)"
                  style="min-width: 150px"
                />
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Role Dialog -->
    <q-dialog v-model="roleDialog.show">
      <q-card style="min-width: 500px">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ roleDialog.editing ? 'Edit Role' : 'Create Role' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="roleDialog.form.name"
            label="Role Name"
            outlined
            dense
            :rules="[val => !!val && val.trim().length > 0 || 'Role name is required']"
            class="q-mb-md"
          />
          <q-input
            v-model="roleDialog.form.description"
            label="Description"
            outlined
            dense
            type="textarea"
            class="q-mb-md"
          />
          <q-checkbox
            v-model="roleDialog.form.is_default"
            label="Default Role"
            class="q-mb-md"
          />
          
          <div class="text-subtitle2 q-mb-md">Permissions</div>
          <q-option-group
            v-model="roleDialog.form.permissions"
            :options="permissionOptions"
            type="checkbox"
            dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" :label="roleDialog.editing ? 'Update' : 'Create'" @click="saveRole" :loading="saving" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Permission Dialog -->
    <q-dialog v-model="permissionDialog.show">
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center">
          <div class="text-h6">Create Permission</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="permissionDialog.form.name"
            label="Permission Name"
            hint="Use lowercase with underscores (e.g. view_products)"
            outlined
            dense
            :rules="[val => !!val && val.trim().length > 0 || 'Permission name is required', val => /^[a-z0-9_]+$/.test(val) || 'Use lowercase, numbers, underscores only']"
            class="q-mb-md"
          />
          <q-input
            v-model="permissionDialog.form.description"
            label="Description"
            outlined
            dense
            type="textarea"
            :rules="[val => !!val && val.trim().length > 0 || 'Description is required']"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Create" @click="savePermission" :loading="saving" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useRbac } from 'src/composables/useApi'
import { usersAPI } from 'src/boot/api'
import { useAuthStore } from 'src/stores/auth'

const { 
  fetchPermissions, fetchRoles, fetchUserRoles, assignRole, setStaff, 
  getMyPermissions, seedDefaults, loading: rbacLoading, error: rbacError
} = useRbac()

// Keep original loading as is and use composable loading only for specific API calls

const $q = useQuasar()
const authStore = useAuthStore()

// Data
const tab = ref('roles')
const loading = ref(false)
const saving = ref(false)

const roles = ref([])
const permissions = ref([])
const users = ref([])

// Filters
const roleFilter = ref('')
const permissionFilter = ref('')
const userFilter = ref('')

// Dialogs
const roleDialog = ref({
  show: false,
  editing: false,
  form: {
    id: null,
    name: '',
    description: '',
    is_default: false,
    permissions: []
  }
})

const permissionDialog = ref({
  show: false,
  form: {
    name: '',
    description: ''
  }
})

// Columns
const roleColumns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true },
  { name: 'name', label: 'Name', field: 'name', sortable: true },
  { name: 'description', label: 'Description', field: 'description' },
  { name: 'is_default', label: 'Default', field: 'is_default', format: val => val ? 'Yes' : 'No' },
  { name: 'permission_count', label: 'Permissions', field: row => row.permissions?.length || 0 },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

const permissionColumns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true },
  { name: 'name', label: 'Name', field: 'name', sortable: true },
  { name: 'description', label: 'Description', field: 'description' },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

const userColumns = [
  { name: 'id', label: 'ID', field: 'id', sortable: true },
  { name: 'username', label: 'Username', field: 'username', sortable: true },
  { name: 'email', label: 'Email', field: 'email', sortable: true },
  { name: 'role', label: 'Role', field: 'role' },
  { name: 'is_active', label: 'Active', field: 'is_active', format: val => val ? 'Yes' : 'No' },
  { name: 'is_staff', label: 'Staff', field: 'is_staff' },
  { name: 'actions', label: 'Assign Role', field: 'actions' }
]

// Computed
const isAdmin = computed(() => authStore.user?.is_staff || false)

const selectableRoles = computed(() => {
  return roles.value.map(role => ({
    id: role.id,
    name: role.name
  }))
})

const permissionOptions = computed(() => {
  return permissions.value.map(perm => ({
    label: `${perm.name} - ${perm.description}`,
    value: perm.name
  }))
})

// Methods
async function loadAllData() {
  loading.value = true
  try {
    const [rolesResult, permissionsResult, usersResult] = await Promise.all([
      fetchRoles(),
      fetchPermissions(),
      usersAPI.getAll() // Assuming there's a function to get all users
    ])
    
    roles.value = rolesResult
    permissions.value = permissionsResult
    
    // Get user roles separately
    const userPromises = usersResult.data.map(async user => {
      try {
        const roleResult = await fetchUserRoles(user.id)
        return {
          ...user,
          role: roleResult.role
        }
      } catch {
        return {
          ...user,
          role: null
        }
      }
    })
    
    users.value = await Promise.all(userPromises)
  } catch (err) {
    console.error('Error loading data:', err)
    $q.notify({ type: 'negative', message: 'Failed to load data' })
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  await loadAllData()
}

async function saveRole() {
  saving.value = true
  try {
    const payload = {
      name: roleDialog.value.form.name,
      description: roleDialog.value.form.description,
      is_default: roleDialog.value.form.is_default,
      permissions: roleDialog.value.form.permissions
    }
    
    if (roleDialog.value.editing) {
      await rbacAPI.updateRole(roleDialog.value.form.id, payload)
      $q.notify({ type: 'positive', message: 'Role updated successfully' })
    } else {
      await rbacAPI.createRole(payload)
      $q.notify({ type: 'positive', message: 'Role created successfully' })
    }
    
    await loadAllData()
    roleDialog.value.show = false
  } catch (err) {
    $q.notify({ type: 'negative', message: `Failed to ${roleDialog.value.editing ? 'update' : 'create'} role` })
  } finally {
    saving.value = false
  }
}

async function savePermission() {
  saving.value = true
  try {
    await rbacAPI.createPermission({
      name: permissionDialog.value.form.name,
      description: permissionDialog.value.form.description
    })
    
    $q.notify({ type: 'positive', message: 'Permission created successfully' })
    await loadAllData()
    permissionDialog.value.show = false
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to create permission' })
  } finally {
    saving.value = false
  }
}

async function deleteRole(roleId) {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this role?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await rbacAPI.deleteRole(roleId)
      $q.notify({ type: 'positive', message: 'Role deleted successfully' })
      await loadAllData()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'Failed to delete role' })
    }
  })
}

async function deletePermission(permissionId) {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this permission?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await rbacAPI.deletePermission(permissionId)
      $q.notify({ type: 'positive', message: 'Permission deleted successfully' })
      await loadAllData()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'Failed to delete permission' })
    }
  })
}

function showRoleDialog(role = null) {
  if (role) {
    roleDialog.value.form = {
      id: role.id,
      name: role.name,
      description: role.description,
      is_default: role.is_default,
      permissions: role.permissions || []
    }
    roleDialog.value.editing = true
  } else {
    roleDialog.value.form = {
      id: null,
      name: '',
      description: '',
      is_default: false,
      permissions: []
    }
    roleDialog.value.editing = false
  }
  roleDialog.value.show = true
}

function showPermissionDialog() {
  permissionDialog.value.form = {
    name: '',
    description: ''
  }
  permissionDialog.value.show = true
}

async function assignUserRole(userId, roleId) {
  try {
    await assignRole(userId, { role_id: roleId })
    $q.notify({ type: 'positive', message: 'User role assigned successfully' })
    await loadAllData()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to assign user role' })
  }
}

async function toggleStaffStatus(userId, isStaff) {
  try {
    await setStaff(userId, isStaff)
    $q.notify({ type: 'positive', message: `Staff status ${isStaff ? 'enabled' : 'disabled'} successfully` })
    await loadAllData()
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to update staff status' })
  }
}

async function seedDefaultsHandler() {
  $q.dialog({
    title: 'Seed Default Permissions',
    message: 'Are you sure you want to seed default roles and permissions? This will create admin, manager, staff, and customer roles.',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await seedDefaults()
      $q.notify({ type: 'positive', message: 'Default roles and permissions seeded successfully' })
      await loadAllData()
    } catch (err) {
      $q.notify({ type: 'negative', message: 'Failed to seed default roles and permissions' })
    }
  })
}

// Load data on mount
onMounted(() => {
  if (authStore.isAuthenticated && isAdmin.value) {
    loadAllData()
  }
})
</script>