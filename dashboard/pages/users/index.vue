<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              {{ t('users.title') }}
            </h1>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              {{ t('users.subtitle') }}
            </p>
          </div>
          <UButton
            icon="i-heroicons-arrow-path"
            size="lg"
            variant="outline"
            @click="refreshUsers"
            :loading="isLoading"
          >
            {{ t('common.refresh') }}
          </UButton>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.total') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {{ stats.total }}
              </p>
            </div>
            <UIcon name="i-heroicons-users" class="w-10 h-10 text-blue-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.active') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-green-600 dark:text-green-400">
                {{ stats.active }}
              </p>
            </div>
            <UIcon name="i-heroicons-check-circle" class="w-10 h-10 text-green-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.inactive') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-600 dark:text-gray-400">
                {{ stats.inactive }}
              </p>
            </div>
            <UIcon name="i-heroicons-x-circle" class="w-10 h-10 text-gray-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.superAdmins') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-purple-600 dark:text-purple-400">
                {{ stats.superAdmins }}
              </p>
            </div>
            <UIcon name="i-heroicons-shield-check" class="w-10 h-10 text-purple-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.regularUsers') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                {{ stats.regularUsers }}
              </p>
            </div>
            <UIcon name="i-heroicons-user" class="w-10 h-10 text-indigo-500" />
          </div>
        </UCard>
      </div>

      <!-- Users Table -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('users.allUsers') }}
              </h2>
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('users.table.rowsPerPage') }}:</span>
                <USelect
                  v-model="pageSize"
                  :options="pageSizeOptions"
                  size="sm"
                  class="w-20"
                />
              </div>
            </div>
            <UInput
              v-model="search"
              icon="i-heroicons-magnifying-glass"
              :placeholder="t('users.search')"
              class="w-64"
            />
          </div>
        </template>

        <UTable
          v-model:sort="sort"
          :rows="paginatedUsers"
          :columns="columns"
          :loading="isLoading"
          :empty-state="{ icon: 'i-heroicons-users', label: t('users.noUsers') }"
          sort-mode="manual"
          @update:sort="onSort"
        >
          <!-- Name Column -->
          <template #name-data="{ row }">
            <div class="flex items-center gap-3">
              <UAvatar
                :alt="`${row.first_name} ${row.last_name}`"
                size="sm"
              />
              <div>
                <p class="font-medium text-gray-900 dark:text-white">
                  {{ row.first_name }} {{ row.last_name }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ row.email }}
                </p>
              </div>
            </div>
          </template>

          <!-- Status Column -->
          <template #is_active-data="{ row }">
            <UBadge
              :color="row.is_active ? 'green' : 'gray'"
              variant="subtle"
            >
              {{ row.is_active ? t('users.status.active') : t('users.status.inactive') }}
            </UBadge>
          </template>

          <!-- Role Column -->
          <template #is_superuser-data="{ row }">
            <UBadge
              :color="row.is_superuser ? 'purple' : 'blue'"
              variant="subtle"
            >
              {{ row.is_superuser ? t('users.role.superAdmin') : t('users.role.user') }}
            </UBadge>
          </template>

          <!-- Tenant Column -->
          <template #tenant_id-data="{ row }">
            <span class="text-gray-900 dark:text-white">
              {{ row.tenant_id }}
            </span>
          </template>

          <!-- Created At Column -->
          <template #created_at-data="{ row }">
            <span class="text-gray-600 dark:text-gray-400">
              {{ formatDate(row.created_at) }}
            </span>
          </template>

          <!-- Actions Column -->
          <template #actions-data="{ row }">
            <UDropdown :items="getActionItems(row)">
              <UButton
                color="gray"
                variant="ghost"
                icon="i-heroicons-ellipsis-horizontal"
              />
            </UDropdown>
          </template>
        </UTable>

        <!-- Pagination -->
        <template #footer>
          <div class="flex items-center justify-between px-4 py-3">
            <div class="text-sm text-gray-700 dark:text-gray-300">
              {{ t('users.table.showing') }} 
              <span class="font-medium">{{ startIndex + 1 }}</span>
              {{ t('users.table.to') }}
              <span class="font-medium">{{ endIndex }}</span>
              {{ t('users.table.of') }}
              <span class="font-medium">{{ totalFilteredUsers }}</span>
              {{ t('users.table.results') }}
            </div>
            <UPagination
              v-model="page"
              :page-count="pageSize"
              :total="totalFilteredUsers"
              :max="5"
              show-first
              show-last
            />
          </div>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useUsers } from '~/composables/useUsers'
import type { User } from '~/types/user'

definePageMeta({
  middleware: ['auth'],
  requiresSuperAdmin: true
})

const { t } = useI18n()
const { users, isLoading, stats, fetchUsers } = useUsers()

const search = ref('')
const page = ref(1)
const pageSize = ref(10)
const sort = ref({ column: 'created_at', direction: 'desc' as 'asc' | 'desc' })

// Page size options
const pageSizeOptions = [
  { label: '5', value: 5 },
  { label: '10', value: 10 },
  { label: '25', value: 25 },
  { label: '50', value: 50 },
  { label: '100', value: 100 }
]

// Table columns with sortable property
const columns = [
  {
    key: 'name',
    label: t('users.table.name'),
    sortable: true
  },
  {
    key: 'is_active',
    label: t('users.table.status'),
    sortable: true
  },
  {
    key: 'is_superuser',
    label: t('users.table.role'),
    sortable: true
  },
  {
    key: 'tenant_id',
    label: t('users.table.tenant'),
    sortable: true
  },
  {
    key: 'created_at',
    label: t('users.table.createdAt'),
    sortable: true
  },
  {
    key: 'actions',
    label: ''
  }
]

// Filtered users based on search
const filteredUsers = computed(() => {
  let filtered = users.value
  
  // Apply search filter
  if (search.value) {
    const searchLower = search.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.first_name?.toLowerCase().includes(searchLower) ||
      user.last_name?.toLowerCase().includes(searchLower) ||
      user.email?.toLowerCase().includes(searchLower) ||
      user.tenant_id?.toString().includes(searchLower)
    )
  }
  
  // Apply sorting
  if (sort.value.column) {
    filtered = [...filtered].sort((a, b) => {
      let aVal: any
      let bVal: any
      
      // Handle special cases for sorting
      if (sort.value.column === 'name') {
        aVal = `${a.first_name} ${a.last_name}`.toLowerCase()
        bVal = `${b.first_name} ${b.last_name}`.toLowerCase()
      } else {
        aVal = a[sort.value.column as keyof User]
        bVal = b[sort.value.column as keyof User]
      }
      
      // Handle null/undefined values
      if (aVal == null) return 1
      if (bVal == null) return -1
      
      // Compare values
      if (aVal < bVal) return sort.value.direction === 'asc' ? -1 : 1
      if (aVal > bVal) return sort.value.direction === 'asc' ? 1 : -1
      return 0
    })
  }
  
  return filtered
})

// Total filtered users count
const totalFilteredUsers = computed(() => filteredUsers.value.length)

// Paginated users
const paginatedUsers = computed(() => {
  const start = (page.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
})

// Pagination info
const startIndex = computed(() => (page.value - 1) * pageSize.value)
const endIndex = computed(() => Math.min(page.value * pageSize.value, totalFilteredUsers.value))

// Handle sort change
function onSort(newSort: { column: string; direction: 'asc' | 'desc' }) {
  sort.value = newSort
  page.value = 1 // Reset to first page when sorting
}

// Watch for page size changes
watch(pageSize, () => {
  page.value = 1 // Reset to first page when changing page size
})

// Watch for search changes
watch(search, () => {
  page.value = 1 // Reset to first page when searching
})

// Format date
function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-'
  
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Get action items for dropdown
function getActionItems(user: User) {
  return [
    [{
      label: t('users.actions.viewDetails'),
      icon: 'i-heroicons-eye',
      click: () => viewUserDetails(user)
    }],
    [{
      label: t('users.actions.viewTenant'),
      icon: 'i-heroicons-building-office',
      click: () => viewTenant(user.tenant_id)
    }]
  ]
}

// View user details
function viewUserDetails(user: User) {
  console.log('View user details:', user)
  // TODO: Navigate to user details page or show modal
}

// View tenant
function viewTenant(tenantId: number) {
  navigateTo(`/tenants/${tenantId}`)
}

// Refresh users
async function refreshUsers() {
  await fetchUsers()
}

// Initialize
onMounted(async () => {
  await fetchUsers()
})

useHead({
  title: t('users.title')
})
</script>
