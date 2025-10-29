<template>
  <ServicePageLayout
    :service-name="t('wathq.services.commercialRegistration.name')"
    :service-description="t('wathq.services.commercialRegistration.description')"
    service-icon="i-heroicons-building-office-2"
    service-image="/commercial_registration.svg"
    :stats="stats"
    @refresh-live="fetchLiveRequests"
    @refresh-logs="fetchRequestLogs"
    @refresh-offline="fetchOfflineRequests"
  >
    <!-- Test API Form -->
    <template #test-form>
      <EndpointTester
        :endpoints="endpoints"
        :base-url="baseUrl"
        service-type="commercial-registration"
      />
    </template>

    <!-- Live Requests -->
    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput
              v-model="liveForm.cr_number"
              :label="t('wathq.services.commercialRegistration.fields.crNumber')"
              placeholder="1010711252"
              required
            />
            <UInput
              v-model="liveForm.date_gregorian"
              :label="t('wathq.services.commercialRegistration.fields.dateGregorian')"
              type="date"
              :placeholder="t('common.optional')"
            />
          </div>

          <UButton
            type="submit"
            :loading="isLoading"
            icon="i-heroicons-signal"
            color="green"
          >
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
import { ref, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useWathqServices } from '~/composables/useWathqServices'
import ServicePageLayout from '~/components/wathq/ServicePageLayout.vue'
import RequestLogsTable from '~/components/wathq/RequestLogsTable.vue'
import EndpointTester from '~/components/wathq/EndpointTester.vue'
import type { WathqTestResponse, CommercialRegistrationParams } from '~/types/wathq'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/commercial-registration'

// Endpoint definitions
const endpoints = [
  {
    id: 'fullinfo',
    name: t('wathq.services.commercialRegistration.endpoints.fullinfo.name'),
    description: t('wathq.services.commercialRegistration.endpoints.fullinfo.description'),
    path: '/fullinfo/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      },
      {
        key: 'language',
        label: 'Language',
        placeholder: 'Choose Language',
        required: false,
        type: 'select' as const,
        options: [
          { value: 'ar' as const, label: 'Arabic' },
          { value: 'en' as const, label: 'English' }
        ] as const,
        description: 'Response language'
      }
    ],
    category: 'Information'
  },
  {
    id: 'info',
    name: t('wathq.services.commercialRegistration.endpoints.info.name'),
    description: t('wathq.services.commercialRegistration.endpoints.info.description'),
    path: '/info/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      },
      {
        key: 'language',
        label: 'Language',
        placeholder: 'ar',
        required: false,
        type: 'select' as const,
        options: [
          { value: 'ar' as const, label: 'Arabic' },
          { value: 'en' as const, label: 'English' }
        ] as const,
        description: 'Response language'
      }
    ],
    category: 'Information'
  },
  {
    id: 'branches',
    name: t('wathq.services.commercialRegistration.endpoints.branches.name'),
    description: t('wathq.services.commercialRegistration.endpoints.branches.description'),
    path: '/branches/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      }
      ],
      category: 'Structure'
  },
  {
    id: 'status',
    name: t('wathq.services.commercialRegistration.endpoints.status.name'),
    description: t('wathq.services.commercialRegistration.endpoints.status.description'),
    path: '/status/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      }
    ],
    category: 'Information'
  },
  {
    id: 'capital',
    name: t('wathq.services.commercialRegistration.endpoints.capital.name'),
    description: t('wathq.services.commercialRegistration.endpoints.capital.description'),
    path: '/capital/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID' 
      }
    ],
    category: 'Financial'
  },
  {
    id: 'managers',
    name: t('wathq.services.commercialRegistration.endpoints.managers.name'),
    description: t('wathq.services.commercialRegistration.endpoints.managers.description'),
    path: '/managers/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      }
    ],
    category: 'People'
  },
  {
    id: 'owners',
    name: t('wathq.services.commercialRegistration.endpoints.owners.name'),
    description: t('wathq.services.commercialRegistration.endpoints.owners.description'),
    path: '/owners/{cr_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_id',
        label: 'CR ID',
        placeholder: '1010711252',
        required: true,
        description: 'Commercial Registration ID'
      }
    ],
    category: 'People'
  },
  {
    id: 'related',
    name: t('wathq.services.commercialRegistration.endpoints.related.name'),
    description: t('wathq.services.commercialRegistration.endpoints.related.description'),
    path: '/related/{identity_id}/{id_type}',
    method: 'GET' as const,
    params: [
      {
        key: 'identity_id',
        label: 'Identity ID',
        placeholder: '1234567890',
        required: true,
        description: 'Identification number (رقم هوية)'
      },
      {
        key: 'id_type',
        label: 'ID Type',
        placeholder: 'National_ID',
        required: true,
        type: 'select' as const,
        options: [
          { value: 'National_ID', label: 'National ID' },
          { value: 'Resident_ID', label: 'Resident ID' },
          { value: 'Passport', label: 'Passport' },
          { value: 'GCC_ID', label: 'GCC ID' },
          { value: 'Endowment_Deed_No', label: 'Endowment Deed No' },
          { value: 'License_No', label: 'License No' },
          { value: 'CR_National_ID', label: 'CR National ID' },
          { value: 'Foreign_CR_No', label: 'Foreign CR No' },
          { value: 'National_Number', label: 'National Number' },
          { value: 'Boarder_Number', label: 'Boarder Number' }
        ] as const,
        description: 'Identification type (نوع الهوية)'
      },
      {
        key: 'nationality',
        label: 'Nationality NIC Code',
        placeholder: '682',
        required: false,
        type: 'number' as const,
        description: 'Required for Passport, Foreign_CR_No. See lookup/nationalities for valid codes'
      },
      {
        key: 'language',
        label: 'Language',
        placeholder: 'ar',
        required: false,
        type: 'select' as const,
        options: [
          { value: 'ar' as const, label: 'Arabic' },
          { value: 'en' as const, label: 'English' }
        ] as const,
        description: 'Response language'
      }
    ],
    category: 'Relationships'
  },
  {
    id: 'owns',
    name: t('wathq.services.commercialRegistration.endpoints.owns.name'),
    description: t('wathq.services.commercialRegistration.endpoints.owns.description'),
    path: '/owns/{identity_id}/{id_type}',
    method: 'GET' as const,
    params: [
      {
        key: 'identity_id',
        label: 'Identity ID',
        placeholder: '1234567890',
        required: true
      },
      {
        key: 'id_type',
        label: 'ID Type',
        placeholder: '1',
        required: true
      }
    ],
    category: 'Relationships'
  },
  {
    id: 'crNationalNumber',
    name: t('wathq.services.commercialRegistration.endpoints.crNationalNumber.name'),
    description: t('wathq.services.commercialRegistration.endpoints.crNationalNumber.description'),
    path: '/crNationalNumber/{cr_number}',
    method: 'GET' as const,
    params: [
      {
        key: 'cr_number',
        label: 'CR Number',
        placeholder: '1010711252',
        required: true
      }
    ],
    category: 'Information'
  },
  {
    id: 'lookup-status',
    name: t('wathq.services.commercialRegistration.endpoints.lookupStatus.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupStatus.description'),
    path: '/lookup/status',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-entityType',
    name: t('wathq.services.commercialRegistration.endpoints.lookupEntityType.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupEntityType.description'),
    path: '/lookup/entityType',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-companyForm',
    name: t('wathq.services.commercialRegistration.endpoints.lookupCompanyForm.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupCompanyForm.description'),
    path: '/lookup/companyForm',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-companyCharacter',
    name: t('wathq.services.commercialRegistration.endpoints.lookupCompanyCharacter.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupCompanyCharacter.description'),
    path: '/lookup/companyCharacter',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-relation',
    name: t('wathq.services.commercialRegistration.endpoints.lookupRelation.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupRelation.description'),
    path: '/lookup/relation',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-managerPositions',
    name: t('wathq.services.commercialRegistration.endpoints.lookupManagerPositions.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupManagerPositions.description'),
    path: '/lookup/managerPositions',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-identifierType',
    name: t('wathq.services.commercialRegistration.endpoints.lookupIdentifierType.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupIdentifierType.description'),
    path: '/lookup/identifierType',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-managementStructure',
    name: t('wathq.services.commercialRegistration.endpoints.lookupManagementStructure.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupManagementStructure.description'),
    path: '/lookup/managementStructure',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-partnerType',
    name: t('wathq.services.commercialRegistration.endpoints.lookupPartnerType.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupPartnerType.description'),
    path: '/lookup/partnerType',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-partnershipType',
    name: t('wathq.services.commercialRegistration.endpoints.lookupPartnershipType.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupPartnershipType.description'),
    path: '/lookup/partnershipType',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-nationalities',
    name: t('wathq.services.commercialRegistration.endpoints.lookupNationalities.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupNationalities.description'),
    path: '/lookup/nationalities',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-activities',
    name: t('wathq.services.commercialRegistration.endpoints.lookupActivities.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupActivities.description'),
    path: '/lookup/activities',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-cities',
    name: t('wathq.services.commercialRegistration.endpoints.lookupCities.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupCities.description'),
    path: '/lookup/cities',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  },
  {
    id: 'lookup-currencies',
    name: t('wathq.services.commercialRegistration.endpoints.lookupCurrencies.name'),
    description: t('wathq.services.commercialRegistration.endpoints.lookupCurrencies.description'),
    path: '/lookup/currencies',
    method: 'GET' as const,
    params: [],
    category: 'Lookups'
  }
]

const {
  requests,
  stats,
  isLoading,
  isTesting,
  fetchRequests,
  testApiCall,
  makeLiveRequest,
  fetchOfflineRequests: fetchOffline
} = useWathqServices()

// Forms
const testForm = ref<CommercialRegistrationParams>({
  cr_number: '',
  date_gregorian: ''
})

const liveForm = ref<CommercialRegistrationParams>({
  cr_number: '',
  date_gregorian: ''
})

// State
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

// Handlers
async function handleTestApi() {
  const result = await testApiCall({
    service_type: 'commercial-registration',
    endpoint: '/query',
    parameters: testForm.value
  })
  testResult.value = result
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest(
      'commercial-registration',
      'query',
      liveForm.value
    )
    liveRequests.value.unshift(result)
    liveForm.value = { cr_number: '', date_gregorian: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { cr_number: '', date_gregorian: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'commercial-registration', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    console.log('Live requests not available yet')
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'commercial-registration' })
  } catch (error) {
    console.log('Request logs not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('commercial-registration')
    offlineRequests.value = requests.value
  } catch (error) {
    console.log('Offline requests not available yet')
    offlineRequests.value = []
  }
}

// Don't fetch on mount - let users manually test endpoints
// onMounted(async () => {
//   await fetchRequestLogs()
//   await fetchLiveRequests()
// })

useHead({
  title: t('wathq.services.commercialRegistration.name')
})
</script>
