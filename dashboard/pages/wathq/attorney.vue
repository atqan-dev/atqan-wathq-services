<template>
  <ServicePageLayout
    :service-name="t('wathq.services.attorney.name')"
    :service-description="t('wathq.services.attorney.description')"
    service-icon="i-heroicons-scale"
    service-image="/attorney.svg"
    :stats="stats"
    @refresh-live="fetchLiveRequests"
    @refresh-logs="fetchRequestLogs"
    @refresh-offline="fetchOfflineRequests"
  >
    <template #test-form>
      <ClientOnly>
        <EndpointTester
          :endpoints="endpoints"
          :base-url="baseUrl"
          service-type="attorney"
        />
      </ClientOnly>
    </template>

    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput v-model="liveForm.authorization_number" :label="t('wathq.services.attorney.fields.authorizationNumber')" required />
            <UInput v-model="liveForm.identity_number" :label="t('wathq.services.attorney.fields.identityNumber')" />
          </div>
          <UButton type="submit" :loading="isLoading" icon="i-heroicons-signal" color="green">
            {{ t('wathq.actions.makeLiveRequest') }}
          </UButton>
        </form>
        <RequestLogsTable :requests="liveRequests" :is-loading="isLoading" />
      </div>
    </template>

    <template #request-logs>
      <RequestLogsTable :requests="requests" :is-loading="isLoading" />
    </template>

    <template #offline-requests>
      <RequestLogsTable :requests="offlineRequests" :is-loading="isLoading" />
    </template>
  </ServicePageLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useWathqServices } from '~/composables/useWathqServices'
import ServicePageLayout from '~/components/wathq/ServicePageLayout.vue'
import RequestLogsTable from '~/components/wathq/RequestLogsTable.vue'
import EndpointTester from '~/components/wathq/EndpointTester.vue'
import type { WathqTestResponse, AttorneyParams } from '~/types/wathq'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/attorney'

// Endpoint definitions
const endpoints = [
  {
    id: 'lookup',
    name: 'Get Attorney Lookup',
    description: 'Get attorney lookup data',
    path: '/lookup',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'info',
    name: 'Get Attorney Info',
    description: 'Retrieve attorney information by code',
    path: '/info/{code}',
    method: 'GET' as const,
    params: [
      {
        key: 'code',
        label: 'Attorney Code',
        placeholder: 'ATT123456',
        required: true,
        description: 'Attorney registration code'
      }
    ],
    category: 'Information'
  }
]

const { requests, stats, isLoading, isTesting, fetchRequests, testApiCall, makeLiveRequest, fetchOfflineRequests: fetchOffline } = useWathqServices()

const testForm = ref<AttorneyParams>({ authorization_number: '', identity_number: '' })
const liveForm = ref<AttorneyParams>({ authorization_number: '', identity_number: '' })
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

async function handleTestApi() {
  testResult.value = await testApiCall({ service_type: 'attorney', endpoint: '/verify', parameters: testForm.value })
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest('attorney', 'verify', liveForm.value)
    liveRequests.value.unshift(result)
    liveForm.value = { authorization_number: '', identity_number: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { authorization_number: '', identity_number: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'attorney', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'attorney' })
  } catch (error) {
    console.log('Not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('attorney')
    offlineRequests.value = requests.value
  } catch (error) {
    offlineRequests.value = []
  }
}

useHead({ title: t('wathq.services.attorney.name') })
</script>
