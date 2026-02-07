<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Back Button -->
      <div class="mb-6">
        <UButton
          color="gray"
          variant="ghost"
          icon="i-heroicons-arrow-left"
          @click="goBack"
        >
          Back to Logs
        </UButton>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-24">
        <div class="text-center">
          <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
          <p class="text-gray-600 dark:text-gray-400">Loading log details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex flex-col items-center justify-center py-24">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-16 h-16 text-red-500 mb-4" />
        <p class="text-lg font-medium text-gray-900 dark:text-white mb-2">Failed to load log</p>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
        <UButton @click="loadLog">Try Again</UButton>
      </div>

      <!-- Log Details -->
      <div v-else-if="currentLog" class="space-y-6">
        <!-- Header Card -->
        <UCard class="overflow-hidden">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div class="flex items-start gap-4">
              <!-- Status Icon -->
              <div 
                :class="[
                  'p-4 rounded-xl',
                  currentLog.status_code < 400 
                    ? 'bg-green-100 dark:bg-green-900/30' 
                    : 'bg-red-100 dark:bg-red-900/30'
                ]"
              >
                <UIcon 
                  :name="currentLog.status_code < 400 ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                  :class="[
                    'w-10 h-10',
                    currentLog.status_code < 400 ? 'text-green-600' : 'text-red-600'
                  ]"
                />
              </div>

              <div>
                <div class="flex items-center gap-3 mb-2">
                  <UBadge :color="getMethodColor(currentLog.method)" variant="solid" size="lg">
                    {{ currentLog.method }}
                  </UBadge>
                  <UBadge :color="getStatusColor(currentLog.status_code)" variant="subtle" size="lg">
                    {{ currentLog.status_code }} {{ getStatusText(currentLog.status_code) }}
                  </UBadge>
                </div>
                <h1 class="text-xl font-bold text-gray-900 dark:text-white font-mono break-all">
                  {{ currentLog.endpoint }}
                </h1>
              </div>
            </div>

            <div class="flex flex-wrap gap-2">
              <UButton
                color="gray"
                variant="outline"
                icon="i-heroicons-clipboard-document"
                @click="copyToClipboard(currentLog.endpoint)"
              >
                Copy Endpoint
              </UButton>
              <UButton
                color="gray"
                variant="outline"
                icon="i-heroicons-arrow-down-tray"
                @click="downloadLog"
              >
                Download
              </UButton>
            </div>
          </div>
        </UCard>

        <!-- Info Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Service -->
          <UCard>
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <UIcon name="i-heroicons-cube" class="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Service</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ getServiceDisplayName(currentLog.service_slug) }}
                </p>
              </div>
            </div>
          </UCard>

          <!-- Duration -->
          <UCard>
            <div class="flex items-center gap-3">
              <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <UIcon name="i-heroicons-clock" class="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Duration</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatDuration(currentLog.duration_ms) }}
                </p>
              </div>
            </div>
          </UCard>

          <!-- Timestamp -->
          <UCard>
            <div class="flex items-center gap-3">
              <div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
                <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Timestamp</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatDateTime(currentLog.fetched_at) }}
                </p>
              </div>
            </div>
          </UCard>

          <!-- User -->
          <UCard>
            <div class="flex items-center gap-3">
              <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <UIcon 
                  :name="currentLog.management_user_id ? 'i-heroicons-shield-check' : 'i-heroicons-user'" 
                  class="w-5 h-5 text-green-600" 
                />
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">User</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">
                  <span v-if="currentLog.management_user_id">Admin #{{ currentLog.management_user_id }}</span>
                  <span v-else-if="currentLog.user_id">User #{{ currentLog.user_id }}</span>
                  <span v-else class="text-gray-400">System</span>
                </p>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Request Data -->
        <UCard v-if="currentLog.request_data">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-arrow-up-tray" class="w-5 h-5 text-blue-500" />
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Request Data</h2>
              </div>
              <UButton
                color="gray"
                variant="ghost"
                icon="i-heroicons-clipboard-document"
                size="sm"
                @click="copyToClipboard(JSON.stringify(currentLog.request_data, null, 2))"
              >
                Copy
              </UButton>
            </div>
          </template>

          <div class="relative">
            <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono max-h-96"><code>{{ formatJson(currentLog.request_data) }}</code></pre>
          </div>
        </UCard>

        <!-- Response Data -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5 text-green-500" />
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Response Data</h2>
                <UBadge :color="currentLog.status_code < 400 ? 'green' : 'red'" variant="subtle" size="sm">
                  {{ currentLog.status_code }}
                </UBadge>
              </div>
              <div class="flex items-center gap-2">
                <UButton
                  color="gray"
                  variant="ghost"
                  :icon="isResponseExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                  size="sm"
                  @click="isResponseExpanded = !isResponseExpanded"
                >
                  {{ isResponseExpanded ? 'Collapse' : 'Expand' }}
                </UButton>
                <UButton
                  color="gray"
                  variant="ghost"
                  icon="i-heroicons-clipboard-document"
                  size="sm"
                  @click="copyToClipboard(JSON.stringify(currentLog.response_body, null, 2))"
                >
                  Copy
                </UButton>
              </div>
            </div>
          </template>

          <div class="relative">
            <pre 
              :class="[
                'bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono transition-all duration-300',
                isResponseExpanded ? 'max-h-[600px]' : 'max-h-64'
              ]"
            ><code>{{ formatJson(currentLog.response_body) }}</code></pre>
            
            <!-- Gradient overlay when collapsed -->
            <div 
              v-if="!isResponseExpanded && responseIsLarge"
              class="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-gray-900 to-transparent rounded-b-lg pointer-events-none"
            />
          </div>
        </UCard>

        <!-- Additional Info -->
        <UCard>
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-gray-500" />
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Additional Information</h2>
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Log ID</h3>
              <p class="text-sm font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded">
                {{ currentLog.id }}
              </p>
            </div>

            <div v-if="currentLog.tenant_id">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Tenant ID</h3>
              <p class="text-sm font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded">
                {{ currentLog.tenant_id }}
              </p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Service Slug</h3>
              <p class="text-sm font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded">
                {{ currentLog.service_slug }}
              </p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">HTTP Method</h3>
              <p class="text-sm font-mono text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded">
                {{ currentLog.method }}
              </p>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useWathqCallLogs } from '~/composables/useWathqCallLogs'
import { useAlert } from '~/composables/useAlert'

definePageMeta({
  layout: 'default',
  middleware: ['auth']
})

const route = useRoute()
const router = useRouter()
const { success } = useAlert()

const {
  currentLog,
  isLoading,
  error,
  fetchLog,
  getServiceDisplayName,
  getStatusColor,
  getMethodColor,
  formatDuration
} = useWathqCallLogs()

const isResponseExpanded = ref(false)

const responseIsLarge = computed(() => {
  if (!currentLog.value?.response_body) return false
  return JSON.stringify(currentLog.value.response_body, null, 2).split('\n').length > 15
})

function goBack() {
  router.push('/wathq-logs')
}

async function loadLog() {
  const logId = route.params.id as string
  await fetchLog(logId)
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function formatJson(data: any): string {
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

function getStatusText(code: number): string {
  const statusTexts: Record<number, string> = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    422: 'Unprocessable Entity',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable'
  }
  return statusTexts[code] || ''
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    success('Copied to clipboard')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

function downloadLog() {
  if (!currentLog.value) return

  const logData = {
    id: currentLog.value.id,
    service: currentLog.value.service_slug,
    method: currentLog.value.method,
    endpoint: currentLog.value.endpoint,
    status_code: currentLog.value.status_code,
    duration_ms: currentLog.value.duration_ms,
    fetched_at: currentLog.value.fetched_at,
    tenant_id: currentLog.value.tenant_id,
    user_id: currentLog.value.user_id,
    management_user_id: currentLog.value.management_user_id,
    request_data: currentLog.value.request_data,
    response_body: currentLog.value.response_body
  }

  const json = JSON.stringify(logData, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `wathq-log-${currentLog.value.id}.json`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadLog()
})
</script>

<style scoped>
pre {
  scrollbar-width: thin;
  scrollbar-color: #4b5563 #1f2937;
}

pre::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

pre::-webkit-scrollbar-track {
  background: #1f2937;
  border-radius: 4px;
}

pre::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}

pre::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
