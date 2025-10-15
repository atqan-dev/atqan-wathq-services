<template>
  <ServicePageLayout
    :service-name="t('wathq.services.employee.name')"
    :service-description="t('wathq.services.employee.description')"
    service-icon="i-heroicons-user-circle"
    service-image="/employee_information.svg"
    :stats="stats"
    @refresh-live="fetchLiveRequests"
    @refresh-logs="fetchRequestLogs"
    @refresh-offline="fetchOfflineRequests"
  >
    <template #test-form>
      <EndpointTester
        :endpoints="endpoints"
        :base-url="baseUrl"
        service-type="employee"
      />
    </template>

    <template #live-requests>
      <div class="space-y-4">
        <form @submit.prevent="handleLiveRequest" class="space-y-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <UInput v-model="liveForm.employee_id" :label="t('wathq.services.employee.fields.employeeId')" required />
            <UInput v-model="liveForm.company_id" :label="t('wathq.services.employee.fields.companyId')" />
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
import type { WathqTestResponse, EmployeeParams } from '~/types/wathq'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()

// Base URL for API
const baseUrl = '/api/v1/wathq/employee'

// Endpoint definitions
const endpoints = [
  {
    id: 'info',
    name: 'Get Employee Info',
    description: 'Retrieve employee information by employee ID',
    path: '/info/{employee_id}',
    method: 'GET' as const,
    params: [
      {
        key: 'employee_id',
        label: 'Employee ID',
        placeholder: '1234567890',
        required: true,
        description: 'Employee National ID or Iqama number'
      }
    ],
    category: 'Information'
  }
]

const { requests, stats, isLoading, isTesting, fetchRequests, testApiCall, makeLiveRequest, fetchOfflineRequests: fetchOffline } = useWathqServices()

const testForm = ref<EmployeeParams>({ employee_id: '', company_id: '' })
const liveForm = ref<EmployeeParams>({ employee_id: '', company_id: '' })
const testResult = ref<WathqTestResponse | null>(null)
const liveRequests = ref<any[]>([])
const offlineRequests = ref<any[]>([])

async function handleTestApi() {
  testResult.value = await testApiCall({ service_type: 'employee', endpoint: '/verify', parameters: testForm.value })
}

async function handleLiveRequest() {
  try {
    const result = await makeLiveRequest('employee', 'verify', liveForm.value)
    liveRequests.value.unshift(result)
    liveForm.value = { employee_id: '', company_id: '' }
  } catch (error) {
    console.error('Live request failed:', error)
  }
}

function resetTestForm() {
  testForm.value = { employee_id: '', company_id: '' }
  testResult.value = null
}

async function fetchLiveRequests() {
  try {
    await fetchRequests({ service_type: 'employee', status: 'success' })
    liveRequests.value = requests.value
  } catch (error) {
    liveRequests.value = []
  }
}

async function fetchRequestLogs() {
  try {
    await fetchRequests({ service_type: 'employee' })
  } catch (error) {
    console.log('Not available yet')
  }
}

async function fetchOfflineRequests() {
  try {
    await fetchOffline('employee')
    offlineRequests.value = requests.value
  } catch (error) {
    offlineRequests.value = []
  }
}

useHead({ title: t('wathq.services.employee.name') })
</script>
