<template>
  <div>
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <!-- Empty State -->
    <div v-else-if="requests.length === 0" class="text-center py-12">
      <UIcon name="i-heroicons-document-text" class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
        {{ t('wathq.logs.empty.title') }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ t('wathq.logs.empty.description') }}
      </p>
    </div>

    <!-- Requests Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              {{ t('wathq.logs.table.endpoint') }}
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              {{ t('wathq.logs.table.status') }}
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              {{ t('wathq.logs.table.duration') }}
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              {{ t('wathq.logs.table.timestamp') }}
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              {{ t('common.actions') }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="request in requests"
            :key="request.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <!-- Endpoint -->
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <UBadge :color="getMethodColor(request.method)" variant="subtle" size="sm">
                  {{ request.method }}
                </UBadge>
                <code class="text-xs font-mono text-gray-900 dark:text-white">
                  {{ request.endpoint }}
                </code>
              </div>
            </td>

            <!-- Status -->
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
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
              </div>
            </td>

            <!-- Duration -->
            <td class="px-6 py-4">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ request.duration_ms }}ms
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
                {{ t('common.view') }}
              </UButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
            <pre class="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded overflow-auto max-h-48">{{ JSON.stringify(selectedRequest.response_data, null, 2) }}</pre>
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
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '~/composables/useI18n'
import type { WathqApiRequest } from '~/types/wathq'

interface Props {
  requests: WathqApiRequest[]
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false
})

const { t } = useI18n()

const isDetailsModalOpen = ref(false)
const selectedRequest = ref<WathqApiRequest | null>(null)

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

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}

function viewDetails(request: WathqApiRequest) {
  selectedRequest.value = request
  isDetailsModalOpen.value = true
}
</script>
