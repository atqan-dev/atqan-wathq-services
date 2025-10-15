<template>
  <ServicePageLayout
    :service-name="t('wathq.services.nationalAddress.name')"
    :service-description="t('wathq.services.nationalAddress.description')"
    service-icon="i-heroicons-map-pin"
    service-image="/national_address.svg"
    :stats="stats"
    @refresh-live="fetchLiveRequests"
    @refresh-logs="fetchRequestLogs"
    @refresh-offline="fetchOfflineRequests"
  >
    <template #test-form>
      <EndpointTester
        :endpoints="endpoints"
        :base-url="baseUrl"
        service-type="spl-national-address"
      />
    </template>

    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput v-model="liveForm.identity_number" :label="t('wathq.services.nationalAddress.fields.identityNumber')" required />
            <UInput v-model="liveForm.address_id" :label="t('wathq.services.nationalAddress.fields.addressId')" />
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
import type { WathqTestResponse, NationalAddressParams } from '~/types/wathq'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/spl-national-address'

// Endpoint definitions
const endpoints = [
  {
    id: 'info',
    name: 'Get National Address Info',
    description: 'Retrieve national address information by CR number',
    path: '/info/{cr_number}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_number',
        label: 'CR Number',
        placeholder: '1010000000',
        required: true,
        description: 'Commercial Registration Number'
      }
    ],
    category: 'Information'
  }
]

const { requests, stats, isLoading, isTesting, fetchRequests, testApiCall, makeLiveRequest, fetchOfflineRequests: fetchOffline } = useWathqServices()

const testForm = ref<NationalAddressParams>({ identity_number: '', address_id: '' })
const liveForm = ref<NationalAddressParams>({ identity_number: '', address_id: '' })
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

async function handleTestApi() {
  testResult.value = await testApiCall({ service_type: 'spl-national-address', endpoint: '/query', parameters: testForm.value })
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest('spl-national-address', 'query', liveForm.value)
    liveRequests.value.unshift(result)
    liveForm.value = { identity_number: '', address_id: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { identity_number: '', address_id: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'spl-national-address', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'spl-national-address' })
  } catch (error) {
    console.log('Not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('spl-national-address')
    offlineRequests.value = requests.value
  } catch (error) {
    offlineRequests.value = []
  }
}

useHead({ title: t('wathq.services.nationalAddress.name') })
</script>
