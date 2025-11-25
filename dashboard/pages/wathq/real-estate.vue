<template>
  <ServicePageLayout
    :service-name="t('wathq.services.realEstate.name')"
    :service-description="t('wathq.services.realEstate.description')"
    service-icon="i-heroicons-home"
    service-image="/real_estates_deeds.svg"
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
          service-type="real-estate"
        />
      </ClientOnly>
    </template>

    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput v-model="liveForm.deed_number" :label="t('wathq.services.realEstate.fields.deedNumber')" required />
            <UInput v-model="liveForm.deed_date" :label="t('wathq.services.realEstate.fields.deedDate')" type="date" />
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
import type { WathqTestResponse, RealEstateParams } from '~/types/wathq'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/real-estate'

// Endpoint definitions
const endpoints = [
  {
    id: 'deed',
    name: 'Get Deed Details',
    description: 'Retrieve detailed information about a real estate deed',
    path: '/deed/{deed_number}/{id_number}/{id_type}',
    method: 'GET' as const,
    params: [
      {
        key: 'deed_number',
        label: 'Deed Number',
        placeholder: '1234567890',
        required: true,
        description: 'Real estate deed number'
      },
      {
        key: 'id_number',
        label: 'ID Number',
        placeholder: '1234567890',
        required: true,
        description: 'National ID or Iqama number'
      },
      {
        key: 'id_type',
        label: 'ID Type',
        placeholder: '1',
        required: true,
        description: '1=National ID, 2=Iqama'
      }
    ],
    category: 'Information'
  }
]

const { requests, stats, isLoading, isTesting, fetchRequests, testApiCall, makeLiveRequest, fetchOfflineRequests: fetchOffline } = useWathqServices()

const testForm = ref<RealEstateParams>({ deed_number: '', deed_date: '' })
const liveForm = ref<RealEstateParams>({ deed_number: '', deed_date: '' })
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

async function handleTestApi() {
  testResult.value = await testApiCall({ service_type: 'real-estate', endpoint: '/query', parameters: testForm.value })
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest('real-estate', 'query', liveForm.value)
    liveRequests.value.unshift(result)
    liveForm.value = { deed_number: '', deed_date: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { deed_number: '', deed_date: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'real-estate', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'real-estate' })
  } catch (error) {
    console.log('Not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('real-estate')
    offlineRequests.value = requests.value
  } catch (error) {
    offlineRequests.value = []
  }
}

useHead({ title: t('wathq.services.realEstate.name') })
</script>
