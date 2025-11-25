<template>
  <div>
    <!-- Enhanced Data Table -->
    <DataTable
      :table="table"
      :selectable="true"
      :exportable="true"
      :search-placeholder="t('wathq.logs.searchPlaceholder')"
      :empty-state-title="t('wathq.logs.empty.title')"
      :empty-state-description="t('wathq.logs.empty.description')"
    />

    <!-- Request Details Modal -->
    <UModal v-model="isDetailsModalOpen">
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('wathq.logs.requestDetails') }}
            </h3>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="isDetailsModalOpen = false"
            />
          </div>
        </template>

        <div v-if="selectedRequest" class="space-y-4">
          <!-- Basic Info -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('wathq.logs.table.endpoint') }}
              </label>
              <code class="block mt-1 text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {{ selectedRequest.method }} {{ selectedRequest.endpoint }}
              </code>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('wathq.logs.table.status') }}
              </label>
              <p class="mt-1">
                <UBadge
                  :color="selectedRequest.is_success ? 'green' : 'red'"
                  variant="subtle"
                >
                  {{ selectedRequest.status_code }}
                </UBadge>
              </p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('wathq.logs.table.duration') }}
              </label>
              <p class="mt-1 text-sm">{{ selectedRequest.duration_ms }}ms</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('wathq.logs.table.timestamp') }}
              </label>
              <p class="mt-1 text-sm">{{ formatTimestamp(selectedRequest.fetched_at) }}</p>
            </div>
          </div>

          <!-- Service Info -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('wathq.logs.table.service') }}
              </label>
              <p class="mt-1 text-sm">{{ selectedRequest.service_slug }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                ID
              </label>
              <p class="mt-1 text-sm font-mono text-xs">{{ selectedRequest.id }}</p>
            </div>
          </div>

          <!-- Request Data -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('wathq.logs.requestData') }}
            </label>
            <pre class="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded overflow-auto max-h-48">{{ JSON.stringify(selectedRequest.request_data, null, 2) }}</pre>
          </div>

          <!-- Response Data -->
          <div>
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('wathq.logs.responseData') }}
            </label>
            <pre class="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded overflow-auto max-h-48">{{ JSON.stringify(selectedRequest.response_body, null, 2) }}</pre>
          </div>

          <!-- Error Message -->
          <div v-if="selectedRequest.error_message">
            <label class="text-sm font-medium text-red-700 dark:text-red-300">
              {{ t('common.error') }}
            </label>
            <p class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ selectedRequest.error_message }}
            </p>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton
              color="gray"
              variant="ghost"
              @click="isDetailsModalOpen = false"
            >
              {{ t('common.close') }}
            </UButton>
            <UButton
              v-if="selectedRequest && !selectedRequest.is_success"
              color="blue"
              icon="i-heroicons-arrow-path"
              @click="retryRequest"
            >
              {{ t('common.retry') }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { 
  useWathqLiveRequestsTable, 
  useWathqRequestLogsTable, 
  useWathqOfflineRequestsTable 
} from '~/composables/useWathqDataTable'
import DataTable from '~/components/ui/DataTable.vue'
import type { WathqApiRequest } from '~/types/wathq'

interface Props {
  type: 'live' | 'logs' | 'offline'
  serviceType?: string
  endpoint?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'logs'
})

const { t } = useI18n()

// Modal state
const isDetailsModalOpen = ref(false)
const selectedRequest = ref<WathqApiRequest | null>(null)

// Initialize the appropriate table based on type
const table = computed(() => {
  const options = {
    serviceType: props.serviceType,
    endpoint: props.endpoint
  }

  switch (props.type) {
    case 'live':
      return useWathqLiveRequestsTable(options)
    case 'logs':
      return useWathqRequestLogsTable(options)
    case 'offline':
      return useWathqOfflineRequestsTable(options)
    default:
      return useWathqRequestLogsTable(options)
  }
})

// Enhance actions to include modal functionality
const enhancedActions = computed(() => {
  const baseActions = table.value.actions.value
  
  return baseActions.map(action => {
    if (action.key === 'view') {
      return {
        ...action,
        handler: (row: WathqApiRequest) => {
          selectedRequest.value = row
          isDetailsModalOpen.value = true
        }
      }
    }
    
    if (action.key === 'retry') {
      return {
        ...action,
        handler: async (row: WathqApiRequest) => {
          await retryRequestHandler(row)
        }
      }
    }
    
    return action
  })
})

// Update table actions
table.value.actions.value = enhancedActions.value

// Helper methods
function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}

async function retryRequest() {
  if (selectedRequest.value) {
    await retryRequestHandler(selectedRequest.value)
    isDetailsModalOpen.value = false
  }
}

async function retryRequestHandler(request: WathqApiRequest) {
  try {
    // Implement retry logic here
    console.log('Retrying request:', request)
    
    // You can emit an event or call a service to retry the request
    // For now, just refresh the table
    table.value.refresh()
    
    // Show success notification
    // useNotification().success(t('wathq.logs.retrySuccess'))
  } catch (error) {
    console.error('Retry failed:', error)
    // useNotification().error(t('wathq.logs.retryError'))
  }
}

// Expose table methods for parent component
defineExpose({
  refresh: () => table.value.refresh(),
  reset: () => table.value.reset(),
  exportData: (format: 'csv' | 'json' | 'xlsx') => table.value.exportData(format)
})
</script>
