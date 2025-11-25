<template>
  <div class="space-y-4">
    <!-- Endpoint Selection -->
    <div class="grid grid-cols-1 gap-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('wathq.endpoint') }}
      </label>
      <USelect
        v-model="selectedEndpoint"
        :options="endpointOptions"
        size="lg"
        :placeholder="t('wathq.selectEndpoint')"
        @change="handleEndpointChange"
      />
    </div>

    <!-- Endpoint Details -->
    <UCard v-if="selectedEndpointData">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <UBadge :color="getMethodColor(selectedEndpointData.method)" variant="subtle">
              {{ selectedEndpointData.method }}
            </UBadge>
            <h3 class="font-semibold text-gray-900 dark:text-white">
              {{ selectedEndpointData.name }}
            </h3>
          </div>
        </div>
      </template>

      <!-- Description -->
      <div v-if="selectedEndpointData.description" class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <p class="text-sm text-blue-700 dark:text-blue-300">
          {{ selectedEndpointData.description }}
        </p>
      </div>

      <!-- Parameters Form -->
      <UForm  v-if="selectedEndpointData.params.length > 0" @submit.prevent="handleSubmit" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="param in selectedEndpointData.params" :key="param.key">
            <!-- Select Input -->
            <USelect
              v-if="param.type === 'select'"
              v-model="formData[param.key]"
              :label="param.label"
              :placeholder="param.placeholder"
              :options="param.options"
              :required="param.required"
            >
              <template v-if="param.description" #help>
                <span class="text-xs text-gray-500">{{ param.description }}</span>
              </template>
            </USelect>
            
            <!-- Number Input -->
            <UInput
              v-else-if="param.type === 'number'"
              v-model.number="formData[param.key]"
              :label="param.label"
              :placeholder="param.placeholder"
              :required="param.required"
              type="number"
            >
              <template v-if="param.description" #help>
                <span class="text-xs text-gray-500">{{ param.description }}</span>
              </template>
            </UInput>
            
            <!-- Default Text Input -->
            <UInput
              v-else
              v-model="formData[param.key]"
              :label="param.label"
              :placeholder="param.placeholder"
              :required="param.required"
            >
              <template v-if="param.description" #help>
                <span class="text-xs text-gray-500">{{ param.description }}</span>
              </template>
            </UInput>
          </div>
        </div>

        <div class="flex gap-3">
          <UButton
            type="submit"
            :loading="isLoading"
            icon="i-heroicons-paper-airplane"
            size="lg"
          >
            {{ t('wathq.actions.sendRequest') }}
          </UButton>
          <UButton
            type="button"
            color="gray"
            variant="ghost"
            @click="resetForm"
          >
            {{ t('common.reset') }}
          </UButton>
        </div>
      </UForm>

      <!-- No Parameters -->
      <div v-else>
        <UButton
          :loading="isLoading"
          icon="i-heroicons-paper-airplane"
          size="lg"
          @click="handleSubmit"
        >
          {{ t('wathq.actions.sendRequest') }}
        </UButton>
      </div>
    </UCard>

    <!-- Response Section -->
    <UCard v-if="response">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <h3 class="font-semibold text-gray-900 dark:text-white">
              {{ t('wathq.response') }}
            </h3>
            <UBadge
              :color="response.success ? 'green' : 'red'"
              variant="subtle"
            >
              {{ response.success ? t('common.success') : t('common.error') }}
            </UBadge>
            <span v-if="response.duration_ms" class="text-sm text-gray-500">
              {{ response.duration_ms }}ms
            </span>
          </div>
          <div class="flex items-center gap-2">
            <UButton
              size="sm"
              color="gray"
              variant="ghost"
              icon="i-heroicons-clipboard-document"
              @click="copyResponse"
              :title="t('wathq.actions.copyResponse')"
            >
              {{ copied ? t('wathq.actions.copied') : t('wathq.actions.copy') }}
            </UButton>
            <UButton
              size="sm"
              color="gray"
              variant="ghost"
              icon="i-heroicons-arrow-down-tray"
              @click="exportResponse"
              :title="t('wathq.actions.exportJson')"
            >
              {{ t('wathq.actions.export') }}
            </UButton>
            <UButton
              size="sm"
              color="blue"
              variant="soft"
              icon="i-heroicons-table-cells"
              @click="exportToXls"
              :title="t('wathq.actions.exportXls')"
              :loading="isExportingXls"
            >
              {{ t('wathq.actions.exportXls') }}
            </UButton>
          </div>
        </div>
      </template>

      <!-- Response Code Block -->
      <div class="relative">
        <pre class="text-xs bg-gray-900 dark:bg-gray-950 text-gray-100 p-4 rounded-lg overflow-auto max-h-[600px] font-mono leading-relaxed"><code>{{ formattedResponse }}</code></pre>
        
        <!-- Quick Copy Button on Hover -->
        <UButton
          size="xs"
          color="gray"
          variant="solid"
          icon="i-heroicons-clipboard-document"
          class="absolute top-2 right-2 opacity-0 hover:opacity-100 transition-opacity"
          @click="copyResponse"
        />
      </div>

      <!-- Response Metadata -->
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span class="text-gray-500 dark:text-gray-400">{{ t('wathq.metadata.status') }}:</span>
            <span class="ml-2 font-medium" :class="response.success ? 'text-green-600' : 'text-red-600'">
              {{ response.status_code || (response.success ? '200' : '500') }}
            </span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">{{ t('wathq.metadata.duration') }}:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">
              {{ response.duration_ms }}ms
            </span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">{{ t('wathq.metadata.timestamp') }}:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">
              {{ formatTimestamp(response.timestamp) }}
            </span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">{{ t('wathq.metadata.size') }}:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">
              {{ formatBytes(JSON.stringify(response.data).length) }}
            </span>
          </div>
        </div>
      </div>
    </UCard>

    <!-- Empty State -->
    <UCard v-if="!selectedEndpoint && !response">
      <div class="text-center py-12">
        <UIcon name="i-heroicons-cursor-arrow-rays" class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          {{ t('wathq.selectEndpointPrompt') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ t('wathq.selectEndpointDescription') }}
        </p>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useI18n } from '~/composables/useI18n'
import { useAlert } from '~/composables/useAlert'

interface EndpointParam {
  key: string
  label: string
  placeholder?: string
  required?: boolean
  description?: string
  type?: 'text' | 'number' | 'select'
  options?: Array<{ value: string; label: string }>
}

interface EndpointDefinition {
  id: string
  name: string
  description?: string
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  params: EndpointParam[]
  category?: string
}

interface Props {
  endpoints: EndpointDefinition[]
  baseUrl: string
  serviceType: string
}

interface Response {
  success: boolean
  data?: any
  error?: string
  status_code?: number
  duration_ms: number
  timestamp: string
}

const props = defineProps<Props>()

const { t } = useI18n()
const { success: showSuccess, error: showError } = useAlert()
const { authenticatedFetch } = useAuthenticatedFetch()
const { fetchRequests } = useWathqServices()

const selectedEndpoint = ref<string>('')
const formData = ref<Record<string, any>>({})
const response = ref<Response | null>(null)
const isLoading = ref(false)
const copied = ref(false)
const isExportingXls = ref(false)

// Endpoint options for select
const endpointOptions = computed(() => {
  return props.endpoints.map(endpoint => ({
    value: endpoint.id,
    label: endpoint.name,
    description: endpoint.description
  }))
})

// Selected endpoint data
const selectedEndpointData = computed(() => {
  return props.endpoints.find(e => e.id === selectedEndpoint.value)
})

// Formatted response
const formattedResponse = computed(() => {
  if (!response.value) return ''
  const data = response.value.success ? response.value.data : { error: response.value.error }
  return JSON.stringify(data, null, 2)
})

// Handle endpoint change
function handleEndpointChange() {
  formData.value = {}
  response.value = null
}

// Reset form
function resetForm() {
  formData.value = {}
  if (selectedEndpointData.value) {
    selectedEndpointData.value.params.forEach(param => {
      formData.value[param.key] = ''
    })
  }
}

// Handle submit
async function handleSubmit() {
  if (!selectedEndpointData.value) return

  try {
    isLoading.value = true
    const startTime = Date.now()

    // Get auth token to check user type
    const token = authStore.token
    let isManagementUser = false
    
    // Debug: Check if token exists
    if (!token) {
      console.error('❌ No authentication token found. Please login first.')
      showError('No authentication token. Please login first.')
      isLoading.value = false
      return
    }
    
    if (token) {
      try {
        // Decode JWT to check if management user
        const parts = token.split('.')
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]))
          isManagementUser = payload.is_management_user === true
          console.log('✓ Token decoded successfully. Is management user:', isManagementUser)
        }
      } catch (e) {
        console.warn('Could not decode token:', e)
      }
    }

    // Build URL with path parameters
    let path = selectedEndpointData.value.path
    
    // Add /management prefix for management users on applicable endpoints
    if (isManagementUser && !path.startsWith('/lookup') && !path.startsWith('/management')) {
      path = `/management${path}`
    }
    
    let url = `${props.baseUrl}${path}`
    const queryParams = new URLSearchParams()
    
    // Replace path parameters and collect query parameters
    selectedEndpointData.value.params.forEach(param => {
      if (formData.value[param.key]) {
        // Check if this is a path parameter (contains {})
        if (path.includes(`{${param.key}}`)) {
          url = url.replace(`{${param.key}}`, formData.value[param.key])
        } else {
          // Otherwise treat as query parameter
          queryParams.append(param.key, formData.value[param.key])
        }
      }
    })
    
    // Append query parameters to URL
    if (queryParams.toString()) {
      url += `?${queryParams.toString()}`
    }

    // Make request using authenticated fetch
    const data = await authenticatedFetch(url, {
      method: selectedEndpointData.value.method
    })

    console.log('📥 Response status:', res.status)

    const duration = Date.now() - startTime

    console.log('✓ Response received:', { status: res.status, data })

    response.value = {
      success: true,
      data: data,
      status_code: 200,
      duration_ms: duration,
      timestamp: new Date().toISOString()
    }

    showSuccess(t('wathq.requestSuccess'))
    
    // Refresh stats to update the cards
    await fetchRequests({ service_type: props.serviceType as any })
  } catch (err: any) {
    const duration = Date.now() - startTime
    console.error('❌ Request error:', err)
    response.value = {
      success: false,
      error: err.message || 'Request failed',
      duration_ms: duration,
      timestamp: new Date().toISOString()
    }
    showError(err.message || t('wathq.requestFailed'))
  } finally {
    isLoading.value = false
  }
}

// Copy response
async function copyResponse() {
  if (!response.value) return
  
  try {
    await navigator.clipboard.writeText(formattedResponse.value)
    copied.value = true
    showSuccess(t('wathq.copiedToClipboard'))
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    showError(t('wathq.copyFailed'))
  }
}

// Export response
function exportResponse() {
  if (!response.value) return

  const blob = new Blob([formattedResponse.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.serviceType}-${selectedEndpoint.value}-${Date.now()}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  showSuccess(t('wathq.exportSuccess'))
}

// Export to XLS
async function exportToXls() {
  if (!response.value || !response.value.data) return

  try {
    isExportingXls.value = true
    
    // Import XLSX library dynamically
    const XLSX = await import('xlsx')
    
    // Prepare data
    const data = response.value.data
    const flattenedData = flattenObject(data)
    
    // Create worksheet
    const ws = XLSX.utils.json_to_sheet([flattenedData])
    
    // Adjust column widths
    const colWidths = Object.keys(flattenedData).map(key => ({
      wch: Math.min(Math.max(key.length, 15), 50)
    }))
    ws['!cols'] = colWidths
    
    // Create workbook
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Response')
    
    // Generate filename
    const filename = `${props.serviceType}-${selectedEndpoint.value}-${Date.now()}.xlsx`
    
    // Save file
    XLSX.writeFile(wb, filename)
    
    showSuccess(t('wathq.exportXlsSuccess'))
  } catch (err: any) {
    console.error('XLS export error:', err)
    showError(err.message || t('wathq.exportXlsFailed'))
  } finally {
    isExportingXls.value = false
  }
}

// Flatten nested objects for XLS export
function flattenObject(obj: any, prefix = ''): Record<string, any> {
  const flattened: Record<string, any> = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key]
      const newKey = prefix ? `${prefix}_${key}` : key
      
      if (value === null || value === undefined) {
        flattened[newKey] = ''
      } else if (typeof value === 'object') {
        if (Array.isArray(value)) {
          // For arrays, convert to JSON string
          flattened[newKey] = JSON.stringify(value)
        } else {
          // For nested objects, flatten recursively
          Object.assign(flattened, flattenObject(value, newKey))
        }
      } else if (typeof value === 'boolean') {
        flattened[newKey] = value ? 'Yes' : 'No'
      } else {
        flattened[newKey] = value
      }
    }
  }
  
  return flattened
}

// Get method color
function getMethodColor(method: string): 'blue' | 'green' | 'yellow' | 'red' {
  switch (method) {
    case 'GET':
      return 'blue'
    case 'POST':
      return 'green'
    case 'PUT':
    case 'PATCH':
      return 'yellow'
    case 'DELETE':
      return 'red'
    default:
      return 'blue'
  }
}

// Format timestamp
function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

// Format bytes
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Watch endpoint change
watch(selectedEndpoint, () => {
  if (selectedEndpointData.value) {
    // Initialize form data
    selectedEndpointData.value.params.forEach(param => {
      if (!formData.value[param.key]) {
        formData.value[param.key] = ''
      }
    })
  }
})
</script>
