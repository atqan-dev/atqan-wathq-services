<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              WATHQ API Call Logs
            </h1>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              Monitor and analyze all WATHQ API requests across tenants
            </p>
          </div>
          <div class="flex items-center gap-3">
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-arrow-path"
              :loading="isLoading"
              @click="refreshData"
            >
              Refresh
            </UButton>
            <UButton
              color="gray"
              variant="outline"
              icon="i-heroicons-arrow-down-tray"
              @click="exportLogs"
            >
              Export
            </UButton>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <UCard class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600 dark:text-blue-400">Total Calls</p>
              <p class="mt-1 text-3xl font-bold text-blue-700 dark:text-blue-300">
                {{ stats?.total_calls || 0 }}
              </p>
            </div>
            <div class="p-3 bg-blue-500/10 rounded-full">
              <UIcon name="i-heroicons-server-stack" class="w-8 h-8 text-blue-500" />
            </div>
          </div>
        </UCard>

        <UCard class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600 dark:text-green-400">Successful</p>
              <p class="mt-1 text-3xl font-bold text-green-700 dark:text-green-300">
                {{ stats?.success_calls || 0 }}
              </p>
            </div>
            <div class="p-3 bg-green-500/10 rounded-full">
              <UIcon name="i-heroicons-check-circle" class="w-8 h-8 text-green-500" />
            </div>
          </div>
        </UCard>

        <UCard class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-800">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400">Errors</p>
              <p class="mt-1 text-3xl font-bold text-red-700 dark:text-red-300">
                {{ stats?.error_calls || 0 }}
              </p>
            </div>
            <div class="p-3 bg-red-500/10 rounded-full">
              <UIcon name="i-heroicons-x-circle" class="w-8 h-8 text-red-500" />
            </div>
          </div>
        </UCard>

        <UCard class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600 dark:text-purple-400">Avg Duration</p>
              <p class="mt-1 text-3xl font-bold text-purple-700 dark:text-purple-300">
                {{ formatDuration(stats?.avg_duration_ms || 0) }}
              </p>
            </div>
            <div class="p-3 bg-purple-500/10 rounded-full">
              <UIcon name="i-heroicons-clock" class="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </UCard>

        <UCard class="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 border-amber-200 dark:border-amber-800">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-amber-600 dark:text-amber-400">Success Rate</p>
              <p class="mt-1 text-3xl font-bold text-amber-700 dark:text-amber-300">
                {{ successRate }}%
              </p>
            </div>
            <div class="p-3 bg-amber-500/10 rounded-full">
              <UIcon name="i-heroicons-chart-pie" class="w-8 h-8 text-amber-500" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Section -->
      <UCard class="mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <!-- Search -->
          <div class="flex-1 min-w-[200px]">
            <UInput
              v-model="searchQuery"
              placeholder="Search by endpoint, service..."
              icon="i-heroicons-magnifying-glass"
              size="lg"
              @input="debouncedSearch"
            />
          </div>

          <!-- Service Filter -->
          <USelectMenu
            v-model="selectedService"
            :options="serviceOptions"
            placeholder="All Services"
            class="w-48"
            @change="applyFilters"
          />

          <!-- Method Filter -->
          <USelectMenu
            v-model="selectedMethod"
            :options="methodOptions"
            placeholder="All Methods"
            class="w-36"
            @change="applyFilters"
          />

          <!-- Status Filter -->
          <USelectMenu
            v-model="selectedStatus"
            :options="statusOptions"
            placeholder="All Status"
            class="w-36"
            @change="applyFilters"
          />

          <!-- Clear Filters -->
          <UButton
            v-if="hasActiveFilters"
            color="gray"
            variant="ghost"
            icon="i-heroicons-x-mark"
            @click="clearFilters"
          >
            Clear
          </UButton>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              API Call History
            </h2>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              Showing {{ filteredLogs.length }} of {{ logs.length }} logs
            </div>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="isLoading && logs.length === 0" class="flex items-center justify-center py-16">
          <div class="text-center">
            <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
            <p class="text-gray-600 dark:text-gray-400">Loading call logs...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-16 h-16 text-red-500 mb-4" />
          <p class="text-lg font-medium text-gray-900 dark:text-white mb-2">Failed to load logs</p>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
          <UButton @click="refreshData">Try Again</UButton>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredLogs.length === 0" class="flex flex-col items-center justify-center py-16">
          <UIcon name="i-heroicons-document-magnifying-glass" class="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
          <p class="text-lg font-medium text-gray-900 dark:text-white mb-2">No logs found</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ hasActiveFilters ? 'Try adjusting your filters' : 'No API calls have been recorded yet' }}
          </p>
        </div>

        <!-- Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th 
                  class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="sortBy('fetched_at')"
                >
                  <div class="flex items-center gap-1">
                    Timestamp
                    <UIcon v-if="sortColumn === 'fetched_at'" :name="sortDirection === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4" />
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Service
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Method
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Endpoint
                </th>
                <th 
                  class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="sortBy('status_code')"
                >
                  <div class="flex items-center gap-1">
                    Status
                    <UIcon v-if="sortColumn === 'status_code'" :name="sortDirection === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4" />
                  </div>
                </th>
                <th 
                  class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="sortBy('duration_ms')"
                >
                  <div class="flex items-center gap-1">
                    Duration
                    <UIcon v-if="sortColumn === 'duration_ms'" :name="sortDirection === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="w-4 h-4" />
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  User
                </th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="log in paginatedLogs"
                :key="log.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                @click="viewLog(log)"
              >
                <!-- Timestamp -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ formatDate(log.fetched_at) }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatTime(log.fetched_at) }}
                  </div>
                </td>

                <!-- Service -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <UBadge :color="getServiceColor(log.service_slug)" variant="subtle" size="sm">
                    {{ getServiceDisplayName(log.service_slug) }}
                  </UBadge>
                </td>

                <!-- Method -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <UBadge :color="getMethodColor(log.method)" variant="solid" size="sm">
                    {{ log.method }}
                  </UBadge>
                </td>

                <!-- Endpoint -->
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 dark:text-white font-mono truncate max-w-xs" :title="log.endpoint">
                    {{ truncateEndpoint(log.endpoint) }}
                  </div>
                </td>

                <!-- Status -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <UBadge :color="getStatusColor(log.status_code)" variant="subtle" size="sm">
                    <UIcon 
                      :name="log.status_code < 400 ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" 
                      class="w-3 h-3 mr-1" 
                    />
                    {{ log.status_code }}
                  </UBadge>
                </td>

                <!-- Duration -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ formatDuration(log.duration_ms) }}
                  </div>
                </td>

                <!-- User -->
                <td class="px-4 py-4 whitespace-nowrap">
                  <div v-if="log.management_user_id" class="flex items-center gap-2">
                    <UIcon name="i-heroicons-shield-check" class="w-4 h-4 text-purple-500" />
                    <span class="text-sm text-gray-600 dark:text-gray-400">Admin</span>
                  </div>
                  <div v-else-if="log.user_id" class="flex items-center gap-2">
                    <UIcon name="i-heroicons-user" class="w-4 h-4 text-blue-500" />
                    <span class="text-sm text-gray-600 dark:text-gray-400">User #{{ log.user_id }}</span>
                  </div>
                  <span v-else class="text-sm text-gray-400">-</span>
                </td>

                <!-- Actions -->
                <td class="px-4 py-4 whitespace-nowrap text-right">
                  <UButton
                    color="gray"
                    variant="ghost"
                    icon="i-heroicons-eye"
                    size="sm"
                    @click.stop="viewLog(log)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <template #footer v-if="filteredLogs.length > 0">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">Rows per page:</span>
              <USelectMenu
                v-model="pageSize"
                :options="pageSizeOptions"
                class="w-20"
                @change="currentPage = 1"
              />
            </div>

            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ paginationInfo }}
              </span>
              <div class="flex gap-1">
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-chevron-double-left"
                  size="sm"
                  :disabled="currentPage === 1"
                  @click="currentPage = 1"
                />
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-chevron-left"
                  size="sm"
                  :disabled="currentPage === 1"
                  @click="currentPage--"
                />
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-chevron-right"
                  size="sm"
                  :disabled="currentPage === totalPages"
                  @click="currentPage++"
                />
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-chevron-double-right"
                  size="sm"
                  :disabled="currentPage === totalPages"
                  @click="currentPage = totalPages"
                />
              </div>
            </div>
          </div>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useWathqCallLogs, type WathqCallLog } from '~/composables/useWathqCallLogs'

definePageMeta({
  layout: 'default',
  middleware: ['auth']
})

const router = useRouter()

const {
  logs,
  isLoading,
  error,
  stats,
  fetchLogs,
  calculateStats,
  getServiceDisplayName,
  getStatusColor,
  getMethodColor,
  formatDuration
} = useWathqCallLogs()

// Filter state
const searchQuery = ref('')
const selectedService = ref<string | null>(null)
const selectedMethod = ref<string | null>(null)
const selectedStatus = ref<string | null>(null)

// Sort state
const sortColumn = ref<string>('fetched_at')
const sortDirection = ref<'asc' | 'desc'>('desc')

// Pagination state
const currentPage = ref(1)
const pageSize = ref(20)
const pageSizeOptions = [10, 20, 50, 100]

// Filter options
const serviceOptions = [
  { label: 'All Services', value: null },
  { label: 'Commercial Registration', value: 'commercial-registration' },
  { label: 'Real Estate', value: 'real-estate' },
  { label: 'Employee Verification', value: 'employee-verification' },
  { label: 'Company Contract', value: 'company-contract' },
  { label: 'Attorney Services', value: 'attorney-services' },
  { label: 'National Address', value: 'national-address' }
]

const methodOptions = [
  { label: 'All Methods', value: null },
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' }
]

const statusOptions = [
  { label: 'All Status', value: null },
  { label: 'Success (2xx)', value: '2xx' },
  { label: 'Redirect (3xx)', value: '3xx' },
  { label: 'Client Error (4xx)', value: '4xx' },
  { label: 'Server Error (5xx)', value: '5xx' }
]

// Computed
const hasActiveFilters = computed(() => {
  return searchQuery.value || selectedService.value || selectedMethod.value || selectedStatus.value
})

const filteredLogs = computed(() => {
  let result = [...logs.value]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(log =>
      log.endpoint.toLowerCase().includes(query) ||
      log.service_slug.toLowerCase().includes(query) ||
      String(log.status_code).includes(query)
    )
  }

  // Service filter
  if (selectedService.value) {
    result = result.filter(log => log.service_slug === selectedService.value)
  }

  // Method filter
  if (selectedMethod.value) {
    result = result.filter(log => log.method === selectedMethod.value)
  }

  // Status filter
  if (selectedStatus.value) {
    const statusPrefix = selectedStatus.value.charAt(0)
    result = result.filter(log => String(log.status_code).startsWith(statusPrefix))
  }

  // Sort
  result.sort((a, b) => {
    let aVal: any = a[sortColumn.value as keyof WathqCallLog]
    let bVal: any = b[sortColumn.value as keyof WathqCallLog]

    if (sortColumn.value === 'fetched_at') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }

    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })

  return result
})

const totalPages = computed(() => Math.ceil(filteredLogs.value.length / pageSize.value))

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value + 1
  const end = Math.min(currentPage.value * pageSize.value, filteredLogs.value.length)
  return `${start}-${end} of ${filteredLogs.value.length}`
})

const successRate = computed(() => {
  if (!stats.value || stats.value.total_calls === 0) return 0
  return Math.round((stats.value.success_calls / stats.value.total_calls) * 100)
})

// Methods
function sortBy(column: string) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'desc'
  }
}

function applyFilters() {
  currentPage.value = 1
}

function clearFilters() {
  searchQuery.value = ''
  selectedService.value = null
  selectedMethod.value = null
  selectedStatus.value = null
  currentPage.value = 1
}

let searchTimeout: NodeJS.Timeout
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

async function refreshData() {
  await fetchLogs({ limit: 1000 })
  calculateStats()
}

function viewLog(log: WathqCallLog) {
  router.push(`/wathq-logs/${log.id}`)
}

function exportLogs() {
  const dataToExport = filteredLogs.value.map(log => ({
    timestamp: log.fetched_at,
    service: log.service_slug,
    method: log.method,
    endpoint: log.endpoint,
    status: log.status_code,
    duration_ms: log.duration_ms,
    user_id: log.user_id,
    management_user_id: log.management_user_id
  }))

  const csv = [
    Object.keys(dataToExport[0] || {}).join(','),
    ...dataToExport.map(row => Object.values(row).map(v => `"${v}"`).join(','))
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `wathq-logs-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString()
}

function truncateEndpoint(endpoint: string): string {
  if (endpoint.length > 50) {
    return endpoint.substring(0, 47) + '...'
  }
  return endpoint
}

function getServiceColor(slug: string): string {
  const colors: Record<string, string> = {
    'commercial-registration': 'blue',
    'real-estate': 'green',
    'employee-verification': 'purple',
    'company-contract': 'orange',
    'attorney-services': 'pink',
    'national-address': 'cyan'
  }
  return colors[slug] || 'gray'
}

// Watch for filter changes
watch([selectedService, selectedMethod, selectedStatus], () => {
  currentPage.value = 1
})

// Initialize
onMounted(async () => {
  await refreshData()
})
</script>
