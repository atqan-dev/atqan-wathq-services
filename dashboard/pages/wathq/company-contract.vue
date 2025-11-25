<template>
  <ServicePageLayout
    :service-name="t('wathq.services.companyContract.name')"
    :service-description="t('wathq.services.companyContract.description')"
    service-icon="i-heroicons-document-text"
    service-image="/commercial_registration.svg"
    :stats="stats"
    @refresh-live="fetchLiveRequests"
    @refresh-logs="fetchRequestLogs"
    @refresh-offline="fetchOfflineRequests"
  >
    <!-- Test API Form -->
    <template #test-form>
      <ClientOnly>
        <EndpointTester
          :endpoints="endpoints"
          :base-url="baseUrl"
          service-type="company-contract"
        />
      </ClientOnly>
    </template>

    <!-- Live Requests -->
    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput
              v-model="liveForm.contract_number"
              :label="t('wathq.services.companyContract.fields.contractNumber')"
              required
            />
            <UInput
              v-model="liveForm.company_cr"
              :label="t('wathq.services.companyContract.fields.companyCR')"
            />
          </div>
          <UButton type="submit" :loading="isLoading" icon="i-heroicons-signal" color="green">
            {{ t('wathq.actions.makeLiveRequest') }}
          </UButton>
        </form>
        <RequestLogsTable :requests="liveRequests" :is-loading="isLoading" />
      </div>
    </template>

    <!-- Request Logs -->
    <template #request-logs>
      <RequestLogsTable :requests="requests" :is-loading="isLoading" />
    </template>

    <!-- Offline Requests -->
    <template #offline-requests>
      <RequestLogsTable :requests="offlineRequests" :is-loading="isLoading" />
    </template>
  </ServicePageLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useWathqServices } from '~/composables/useWathqServices'
import ServicePageLayout from '~/components/wathq/ServicePageLayout.vue'
import RequestLogsTable from '~/components/wathq/RequestLogsTable.vue'
import EndpointTester from '~/components/wathq/EndpointTester.vue'
import type { WathqTestResponse, CompanyContractParams } from '~/types/wathq'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/company-contract'

// Endpoint definitions
const endpoints = [
  {
    id: 'info',
    name: 'Get Contract Info',
    description: 'Retrieve company contract information',
    path: '/info/{cr_national_number}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_national_number',
        label: 'CR National Number',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration National Number'
      }
    ],
    category: 'Information'
  },
  {
    id: 'management',
    name: 'Get Management Info',
    description: 'Retrieve company management information',
    path: '/management/{cr_national_number}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_national_number',
        label: 'CR National Number',
        placeholder: '1010711252',
        required: true
      }
    ],
    category: 'Information'
  },
  {
    id: 'manager',
    name: 'Get Manager Info',
    description: 'Retrieve specific manager information',
    path: '/manager/{cr_national_number}/{manager_id}/{id_type}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_national_number',
        label: 'CR National Number',
        placeholder: '1010711252',
        required: true
      },
      {
        key: 'manager_id',
        label: 'Manager ID',
        placeholder: '1234567890',
        required: true,
        description: 'Manager National ID or Iqama'
      },
      {
        key: 'id_type',
        label: 'ID Type',
        placeholder: '1',
        required: true,
        description: '1=National ID, 2=Iqama'
      }
    ],
    category: 'People'
  },
  {
    id: 'lookup-articleParts',
    name: 'Get Article Parts Lookup',
    description: 'Get article parts lookup table',
    path: '/lookup/articleParts',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-partnerDecision',
    name: 'Get Partner Decision Lookup',
    description: 'Get partner decision types lookup table',
    path: '/lookup/partnerDecision',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-exerciseMethod',
    name: 'Get Exercise Method Lookup',
    description: 'Get exercise method lookup table',
    path: '/lookup/exerciseMethod',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  }
]

const { requests, stats, isLoading, isTesting, fetchRequests, testApiCall, makeLiveRequest, fetchOfflineRequests: fetchOffline } = useWathqServices()

const testForm = ref<CompanyContractParams>({ contract_number: '', company_cr: '' })
const liveForm = ref<CompanyContractParams>({ contract_number: '', company_cr: '' })
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

async function handleTestApi() {
  testResult.value = await testApiCall({
    service_type: 'company-contract',
    endpoint: '/query',
    parameters: testForm.value
  })
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest('company-contract', 'query', liveForm.value)
    liveRequests.value.unshift(result)
    liveForm.value = { contract_number: '', company_cr: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { contract_number: '', company_cr: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'company-contract', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'company-contract' })
  } catch (error) {
    console.log('Not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('company-contract')
    offlineRequests.value = requests.value
  } catch (error) {
    offlineRequests.value = []
  }
}

useHead({ title: t('wathq.services.companyContract.name') })
</script>
