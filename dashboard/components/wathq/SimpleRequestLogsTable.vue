<template>
  <div>
    <!-- Search and Filters -->
    <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-4">
      <div class="flex-1 max-w-md">
        <UInput
          v-model="searchQuery"
          placeholder="Search requests..."
          icon="i-heroicons-magnifying-glass"
          :loading="isLoading"
          clearable
        />
      </div>
      <div class="flex items-center gap-2">
        <UButton
          variant="outline"
          color="gray"
          icon="i-heroicons-arrow-path"
          :loading="isLoading"
          @click="refreshData"
        >
          Refresh
        </UButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredData.length === 0" class="text-center py-12">
      <UIcon name="i-heroicons-document-text" class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
        No requests found
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Try making some API calls or adjusting your search
      </p>
    </div>

    <!-- Data Table -->
    <div v-else class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Header -->
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Method
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Endpoint
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Status
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Duration
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Timestamp
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              Actions
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="request in paginatedData"
            :key="request.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <!-- Method -->
            <td class="px-6 py-4">
              <UBadge :color="getMethodColor(request.method)" variant="subtle" size="sm">
                {{ request.method }}
              </UBadge>
            </td>

            <!-- Endpoint -->
            <td class="px-6 py-4">
              <code class="text-xs font-mono text-gray-900 dark:text-white">
                {{ request.endpoint }}
              </code>
            </td>

            <!-- Status -->
            <td class="px-6 py-4">
              <UBadge
                :color="request.is_success ? 'green' : 'red'"
                variant="subtle"
              >
                <UIcon
                  :name="request.is_success ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                  class="w-3 h-3"
                />
                {{ request.status_code }}
              </UBadge>
            </td>

            <!-- Duration -->
            <td class="px-6 py-4">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ request.duration_ms || 0 }}ms
              </span>
            </td>

            <!-- Timestamp -->
            <td class="px-6 py-4">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ formatTimestamp(request.created_at) }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-6 py-4 text-right">
              <UButton
                size="xs"
                color="gray"
                variant="ghost"
                icon="i-heroicons-eye"
                @click="viewDetails(request)"
              >
                View
              </UButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="filteredData.length > pageSize" class="flex justify-center mt-4">
      <UPagination
        v-model="currentPage"
        :page-count="totalPages"
        :total="filteredData.length"
        :max="5"
      />
    </div>

    <!-- Request Details Modal -->
    <UModal v-model="isDetailsModalOpen" :ui="{ width: 'w-full max-w-4xl', height: 'h-full max-h-[90vh]' }">
      <UCard :ui="{ body: { padding: 'p-0' }, header: { padding: 'px-6 py-4' }, footer: { padding: 'px-6 py-4' } }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Request Details
            </h3>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="isDetailsModalOpen = false"
            />
          </div>
        </template>

        <div v-if="selectedRequest" class="px-6 py-4 space-y-6 overflow-y-auto max-h-[70vh]">
          <!-- Basic Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Endpoint
              </label>
              <code class="block mt-1 text-sm bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded break-all">
                {{ selectedRequest.method }} {{ selectedRequest.endpoint }}
              </code>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Status
              </label>
              <p class="mt-1">
                <UBadge
                  :color="getStatusColor(selectedRequest.status_code)"
                  variant="subtle"
                >
                  <UIcon
                    :name="selectedRequest.status_code >= 200 && selectedRequest.status_code < 300 ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                    class="w-3 h-3"
                  />
                  {{ selectedRequest.status_code }}
                </UBadge>
              </p>
            </div>
            <div v-if="selectedRequest.duration_ms">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Duration
              </label>
              <p class="mt-1 text-sm">{{ selectedRequest.duration_ms }}ms</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Timestamp
              </label>
              <p class="mt-1 text-sm">{{ formatTimestamp(selectedRequest.created_at) }}</p>
            </div>
          </div>

          <!-- Request Data -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Request Data
            </label>
            <div class="bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
              <pre class="text-xs p-4 overflow-auto max-h-64 whitespace-pre-wrap">{{ formatJsonData(selectedRequest.request_data) }}</pre>
            </div>
          </div>

          <!-- Response Data -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Response Data
            </label>
            <div class="bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
              <pre class="text-xs p-4 overflow-auto max-h-64 whitespace-pre-wrap">{{ formatJsonData(getResponseData(selectedRequest)) }}</pre>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="selectedRequest.error_message">
            <label class="text-sm font-medium text-red-700 dark:text-red-300 mb-2 block">
              Error
            </label>
            <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p class="text-sm text-red-600 dark:text-red-400">
                {{ selectedRequest.error_message }}
              </p>
            </div>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end">
            <UButton
              color="gray"
              variant="ghost"
              @click="isDetailsModalOpen = false"
            >
              Close
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useWathqServices } from '~/composables/useWathqServices'
import type { WathqApiRequest } from '~/types/wathq'

interface Props {
  type: 'live' | 'logs' | 'offline'
  serviceType?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'logs'
})

// Use the existing WATHQ services composable
const { requests, isLoading, fetchRequests, fetchOfflineRequests } = useWathqServices()

// Local state
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(25)
const isDetailsModalOpen = ref(false)
const selectedRequest = ref<WathqApiRequest | null>(null)

// Computed properties
const filteredData = computed(() => {
  if (!searchQuery.value) return requests.value
  
  const query = searchQuery.value.toLowerCase()
  return requests.value.filter(request => 
    request.endpoint?.toLowerCase().includes(query) ||
    request.method?.toLowerCase().includes(query) ||
    request.service_type?.toLowerCase().includes(query)
  )
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// Watch for search changes
watch(searchQuery, () => {
  currentPage.value = 1
})

// Methods
function getMethodColor(method: string): 'blue' | 'green' | 'yellow' | 'red' | 'purple' {
  switch (method) {
    case 'GET':
      return 'blue'
    case 'POST':
      return 'green'
    case 'PUT':
      return 'yellow'
    case 'DELETE':
      return 'red'
    default:
      return 'purple'
  }
}

function getStatusColor(statusCode: number): 'green' | 'yellow' | 'red' | 'gray' {
  if (statusCode >= 200 && statusCode < 300) return 'green'
  if (statusCode >= 300 && statusCode < 400) return 'yellow'
  if (statusCode >= 400) return 'red'
  return 'gray'
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}

function formatJsonData(data: any): string {
  if (!data) return 'No data available'
  if (typeof data === 'string') return data
  try {
    return JSON.stringify(data, null, 2)
  } catch (error) {
    return 'Invalid JSON data'
  }
}

function getResponseData(request: WathqApiRequest): any {
  // Try different possible response data field names
  return request.response_data || 
         (request as any).response_body || 
         'No response data available'
}

function viewDetails(request: WathqApiRequest) {
  selectedRequest.value = request
  isDetailsModalOpen.value = true
}

async function refreshData() {
  try {
    if (props.type === 'offline') {
      await fetchOfflineRequests((props.serviceType || 'commercial-registration') as any)
    } else {
      await fetchRequests({ 
        service_type: (props.serviceType || 'commercial-registration') as any
      })
    }
  } catch (error) {
    console.error('Failed to refresh data:', error)
  }
}

// Load data on mount
onMounted(() => {
  refreshData()
})

// Expose refresh method
defineExpose({
  refresh: refreshData
})
</script>
