<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ t('tenantServices.title') }}
          </h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            {{ t('tenantServices.subtitle') }}
          </p>
        </div>
        <UButton
          size="lg"
          icon="i-heroicons-arrow-path"
          :loading="isLoading"
          @click="handleRefresh"
        >
          {{ t('common.refresh') }}
        </UButton>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-8">
        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.total') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ stats.total_services }}
              </p>
            </div>
            <UIcon name="i-heroicons-squares-2x2" class="w-12 h-12 text-blue-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.active') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
                {{ stats.active_services }}
              </p>
            </div>
            <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.inactive') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
                {{ stats.inactive_services }}
              </p>
            </div>
            <UIcon name="i-heroicons-x-circle" class="w-12 h-12 text-red-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.approved') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-blue-600 dark:text-blue-400">
                {{ stats.approved_services }}
              </p>
            </div>
            <UIcon name="i-heroicons-shield-check" class="w-12 h-12 text-blue-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.pending') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                {{ stats.pending_approval }}
              </p>
            </div>
            <UIcon name="i-heroicons-clock" class="w-12 h-12 text-yellow-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenantServices.stats.totalUsage') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
                {{ stats.total_usage }}
              </p>
            </div>
            <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-purple-500" />
          </div>
        </UCard>
      </div>

      <!-- Filters and Table -->
      <UCard>
        <template #header>
          <div class="flex flex-col gap-4">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('tenantServices.list') }}
            </h2>
            
            <!-- Filters -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Search -->
              <UInput
                v-model="filters.search"
                :placeholder="t('common.search')"
                icon="i-heroicons-magnifying-glass"
                size="sm"
                @input="handleFilterChange"
              />

              <!-- Category Filter -->
              <USelect
                v-model="filters.category"
                :options="categoryOptions"
                size="sm"
                @change="handleFilterChange"
              />

              <!-- Status Filter -->
              <USelect
                v-model="filters.is_active"
                :options="statusOptions"
                size="sm"
                @change="handleFilterChange"
              />

              <!-- Approval Filter -->
              <USelect
                v-model="filters.is_approved"
                :options="approvalOptions"
                size="sm"
                @change="handleFilterChange"
              />
            </div>

            <!-- Group By and Sort -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ t('tenants.services.table.groupBy') }}:
                </span>
                <USelect
                  v-model="groupBy"
                  :options="groupByOptions"
                  size="sm"
                  @change="handleGroupByChange"
                />
              </div>

              <div class="flex items-center gap-3">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ t('common.sort') }}:
                </span>
                <USelect
                  v-model="sortBy"
                  :options="sortOptions"
                  size="sm"
                  @change="handleSortChange"
                />
                <UButton
                  size="sm"
                  color="gray"
                  variant="ghost"
                  :icon="sortOrder === 'asc' ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-down'"
                  @click="toggleSortOrder"
                />
              </div>
            </div>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="isLoading && services.length === 0" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
          <UButton @click="handleRefresh">
            {{ t('common.retry') }}
          </UButton>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredAndSortedServices.length === 0" class="text-center py-12">
          <UIcon name="i-heroicons-squares-2x2" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('tenantServices.noServices') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ filters.search ? t('common.noSearchResults') : t('tenantServices.noServicesMessage') }}
          </p>
        </div>

        <!-- Data Table (Grouped or Ungrouped) -->
        <div v-else class="overflow-x-auto">
          <!-- Grouped View -->
          <div v-if="groupBy !== 'none'" class="space-y-6">
            <div
              v-for="(groupServices, groupKey) in groupedServices"
              :key="groupKey"
              class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
            >
              <!-- Group Header -->
              <div
                class="bg-gray-100 dark:bg-gray-800 px-4 py-3 flex items-center justify-between cursor-pointer"
                @click="toggleGroup(groupKey)"
              >
                <div class="flex items-center gap-3">
                  <UIcon
                    :name="expandedGroups.has(groupKey) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
                    class="w-5 h-5 text-gray-500"
                  />
                  <h3 class="text-sm font-semibold text-gray-900 dark:text-white">
                    {{ getGroupLabel(groupKey) }}
                  </h3>
                  <UBadge size="sm" color="gray" variant="subtle">
                    {{ groupServices.length }}
                  </UBadge>
                </div>
              </div>

              <!-- Group Content -->
              <div v-show="expandedGroups.has(groupKey)">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead class="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.service') }}
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.tenant') }}
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.status') }}
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.approval') }}
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.usage') }}
                      </th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {{ t('tenantServices.table.actions') }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    <tr
                      v-for="service in groupServices"
                      :key="service.id"
                      class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <ServiceRow
                        :service="service"
                        @approve="handleApprove"
                        @toggle-active="handleToggleActive"
                        @delete="handleDelete"
                      />
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Regular Table View -->
          <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.service') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.tenant') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.status') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.approval') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.usage') }}
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  {{ t('tenantServices.table.actions') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="service in paginatedServices"
                :key="service.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <ServiceRow
                  :service="service"
                  @approve="handleApprove"
                  @toggle-active="handleToggleActive"
                  @delete="handleDelete"
                />
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <template v-if="totalPages > 1 && groupBy === 'none'" #footer>
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ t('common.showingResults', { from: startIndex + 1, to: endIndex, total: filteredAndSortedServices.length }) }}
            </div>
            <div class="flex items-center gap-2">
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-chevron-left"
                :disabled="currentPage === 1"
                @click="currentPage--"
              />
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-chevron-right"
                :disabled="currentPage === totalPages"
                @click="currentPage++"
              />
            </div>
          </div>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useTenantServices } from '@/composables/useTenantServices'
import { useConfirm } from '@/composables/useConfirm'
import { usePageSettingsStore } from '@/stores/pageSettings'
import type { TenantService, TenantServiceFilters } from '~/types/tenant-service'
import ServiceRow from '@/components/tenant-services/ServiceRow.vue'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const { t } = useI18n()
const { confirmDelete, confirmWarning, confirm } = useConfirm()
const settingsStore = usePageSettingsStore()

const {
  services,
  isLoading,
  error,
  stats,
  fetchServices,
  approveService,
  toggleActive,
  deleteService
} = useTenantServices()

// Load settings from store
const filters = computed({
  get: () => settingsStore.tenantServices.filters,
  set: (value) => settingsStore.updateTenantServicesFilters(value)
})

const groupBy = computed({
  get: () => settingsStore.tenantServices.groupBy,
  set: (value) => settingsStore.updateTenantServicesGroupBy(value)
})

const sortBy = computed({
  get: () => settingsStore.tenantServices.sortBy,
  set: (value) => settingsStore.updateTenantServicesSorting(value, settingsStore.tenantServices.sortOrder)
})

const sortOrder = computed({
  get: () => settingsStore.tenantServices.sortOrder,
  set: (value) => settingsStore.updateTenantServicesSorting(settingsStore.tenantServices.sortBy, value)
})

const currentPage = computed({
  get: () => settingsStore.tenantServices.currentPage,
  set: (value) => settingsStore.updateTenantServicesPage(value)
})

const expandedGroups = ref<Set<string>>(new Set())
const itemsPerPage = 20

// Filter options
const categoryOptions = computed(() => [
  { value: 'all', label: t('tenantServices.filters.allCategories') },
  { value: 'wathq', label: t('tenantServices.filters.wathq') },
  { value: 'other', label: t('tenantServices.filters.other') }
])

const statusOptions = computed(() => [
  { value: 'all', label: t('tenantServices.filters.allStatuses') },
  { value: 'true', label: t('common.active') },
  { value: 'false', label: t('common.inactive') }
])

const approvalOptions = computed(() => [
  { value: 'all', label: t('tenantServices.filters.allApprovals') },
  { value: 'true', label: t('tenantServices.filters.approved') },
  { value: 'false', label: t('tenantServices.filters.pending') }
])

const groupByOptions = computed(() => [
  { value: 'none', label: t('tenantServices.groupByOptions.none') },
  { value: 'category', label: t('tenantServices.groupByOptions.category') },
  { value: 'status', label: t('tenantServices.groupByOptions.status') },
  { value: 'approval', label: t('tenantServices.groupByOptions.approval') },
  { value: 'tenant', label: t('tenantServices.groupByOptions.tenant') }
])

const sortOptions = computed(() => [
  { value: 'registered_at', label: t('tenantServices.sort.registeredAt') },
  { value: 'service_name', label: t('tenantServices.sort.serviceName') },
  { value: 'usage_count', label: t('tenantServices.sort.usage') },
  { value: 'approved_at', label: t('tenantServices.sort.approvedAt') }
])

// Filtered services
const filteredAndSortedServices = computed(() => {
  let result = [...services.value]

  // Apply search filter
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    result = result.filter(s =>
      s.service.name.toLowerCase().includes(query) ||
      s.service.slug.toLowerCase().includes(query) ||
      s.service.description.toLowerCase().includes(query)
    )
  }

  // Apply category filter
  if (filters.value.category && filters.value.category !== 'all') {
    result = result.filter(s => s.service.category === filters.value.category)
  }

  // Apply status filter
  if (filters.value.is_active !== 'all') {
    const isActive = filters.value.is_active === 'true'
    result = result.filter(s => s.is_active === isActive)
  }

  // Apply approval filter
  if (filters.value.is_approved !== 'all') {
    const isApproved = filters.value.is_approved === 'true'
    result = result.filter(s => s.is_approved === isApproved)
  }

  // Apply sorting
  result.sort((a, b) => {
    let aVal: any, bVal: any

    switch (sortBy.value) {
      case 'service_name':
        aVal = a.service.name
        bVal = b.service.name
        break
      case 'usage_count':
        aVal = a.usage_count
        bVal = b.usage_count
        break
      case 'approved_at':
        aVal = a.approved_at || ''
        bVal = b.approved_at || ''
        break
      default: // registered_at
        aVal = a.registered_at
        bVal = b.registered_at
    }

    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })

  return result
})

// Grouped services
const groupedServices = computed(() => {
  if (groupBy.value === 'none') return {}

  const groups: Record<string, TenantService[]> = {}

  filteredAndSortedServices.value.forEach(service => {
    let key: string

    switch (groupBy.value) {
      case 'category':
        key = service.service.category
        break
      case 'status':
        key = service.is_active ? 'active' : 'inactive'
        break
      case 'approval':
        key = service.is_approved ? 'approved' : 'pending'
        break
      case 'tenant':
        key = `tenant_${service.tenant_id}`
        break
      default:
        key = 'other'
    }

    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(service)
  })

  return groups
})

// Pagination
const totalPages = computed(() => 
  Math.ceil(filteredAndSortedServices.value.length / itemsPerPage)
)

const startIndex = computed(() => 
  (currentPage.value - 1) * itemsPerPage
)

const endIndex = computed(() => 
  Math.min(startIndex.value + itemsPerPage, filteredAndSortedServices.value.length)
)

const paginatedServices = computed(() => 
  filteredAndSortedServices.value.slice(startIndex.value, endIndex.value)
)

// Handlers
function handleFilterChange() {
  settingsStore.updateTenantServicesPage(1)
}

function handleGroupByChange() {
  // Expand all groups by default
  expandedGroups.value.clear()
  Object.keys(groupedServices.value).forEach(key => {
    expandedGroups.value.add(key)
  })
}

function handleSortChange() {
  settingsStore.updateTenantServicesPage(1)
}

function toggleSortOrder() {
  const newOrder = sortOrder.value === 'asc' ? 'desc' : 'asc'
  settingsStore.updateTenantServicesSorting(sortBy.value, newOrder)
}

function toggleGroup(groupKey: string) {
  if (expandedGroups.value.has(groupKey)) {
    expandedGroups.value.delete(groupKey)
  } else {
    expandedGroups.value.add(groupKey)
  }
}

function getGroupLabel(key: string): string {
  switch (groupBy.value) {
    case 'category':
      return t(`tenantServices.filters.${key}`)
    case 'status':
      return key === 'active' ? t('common.active') : t('common.inactive')
    case 'approval':
      return key === 'approved' ? t('tenantServices.filters.approved') : t('tenantServices.filters.pending')
    case 'tenant':
      return `${t('tenantServices.table.tenant')} #${key.replace('tenant_', '')}`
    default:
      return key
  }
}

async function handleRefresh() {
  // Convert string filters to boolean for API
  const apiFilters: TenantServiceFilters = {
    category: filters.value.category as 'wathq' | 'other' | 'all',
    search: filters.value.search,
    is_active: filters.value.is_active === 'all' ? undefined : filters.value.is_active === 'true',
    is_approved: filters.value.is_approved === 'all' ? undefined : filters.value.is_approved === 'true'
  }
  await fetchServices(apiFilters)
}

async function handleApprove(service: TenantService) {
  const confirmed = await confirm({
    title: t('tenantServices.approveService'),
    message: t('tenantServices.confirmApprove', { name: service.service.name }),
    type: 'success',
    confirmText: t('common.approve'),
    confirmIcon: 'i-heroicons-check-circle',
    confirmColor: 'green'
  })
  
  if (confirmed) {
    await approveService(service.id, service.tenant_id)
  }
}

async function handleToggleActive(service: TenantService) {
  const action = service.is_active ? 'deactivate' : 'activate'
  
  const confirmed = await confirmWarning(
    t(`tenantServices.confirm${action.charAt(0).toUpperCase() + action.slice(1)}`, { 
      name: service.service.name 
    }),
    t(`common.${action}`)
  )
  
  if (confirmed) {
    await toggleActive(service.id)
  }
}

async function handleDelete(service: TenantService) {
  const confirmed = await confirmDelete(
    t('tenantServices.confirmDelete', { name: service.service.name }),
    t('tenantServices.deleteService')
  )
  
  if (confirmed) {
    await deleteService(service.id)
  }
}

// Reset pagination when filters change
watch([filters, sortBy, sortOrder], () => {
  currentPage.value = 1
}, { deep: true })

// Load services on mount
onMounted(() => {
  // Convert string filters to boolean for API
  const apiFilters: TenantServiceFilters = {
    category: filters.value.category as 'wathq' | 'other' | 'all',
    search: filters.value.search,
    is_active: filters.value.is_active === 'all' ? undefined : filters.value.is_active === 'true',
    is_approved: filters.value.is_approved === 'all' ? undefined : filters.value.is_approved === 'true'
  }
  fetchServices(apiFilters)
})

// Set page title
useHead({
  title: t('tenantServices.title')
})
</script>
