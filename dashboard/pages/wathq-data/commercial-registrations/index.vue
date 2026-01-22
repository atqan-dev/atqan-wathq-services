<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.total') }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
          </div>
          <UIcon name="i-heroicons-building-office" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.active') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
          </div>
          <UIcon name="i-heroicons-check-circle" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.suspended') }}</p>
            <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.suspended }}</p>
          </div>
          <UIcon name="i-heroicons-pause-circle" class="w-10 h-10 text-yellow-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.cancelled') }}</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ stats.cancelled }}</p>
          </div>
          <UIcon name="i-heroicons-x-circle" class="w-10 h-10 text-red-500" />
        </div>
      </UCard>
    </div>

    <!-- Action Bar -->
    <div class="flex justify-between items-center mb-4">
      <div></div>
      <div class="flex gap-3">
        <UButton
          icon="i-heroicons-arrow-path"
          color="green"
          size="lg"
          :loading="isSyncing"
          @click="handleSync"
        >
          {{ t('wathqData.syncFromLogs') }}
        </UButton>
        <UButton
          icon="i-heroicons-bolt"
          color="primary"
          size="lg"
          @click="openLiveRequestDialog"
        >
          {{ t('liveRequest.title') }}
        </UButton>
      </div>
    </div>

    <!-- Advanced DataTable -->
    <AdvancedDataTable
      :config="tableConfig"
      :title="t('sidebar.commercialRegistrations')"
      :description="t('wathqData.commercialRegistrations.subtitle')"
      @row-click="handleRowClick"
      @action-click="handleActionClick"
    />

    <!-- Live Request Dialog -->
    <UModal v-model="isLiveRequestDialogOpen" :ui="{ width: 'w-full max-w-7xl' }" fullscreen>
      <UCard :ui="{ body: { padding: '' } }">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <UIcon name="i-heroicons-bolt" class="w-6 h-6 text-primary-500" />
              <div>
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
                  {{ t('liveRequest.title') }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('liveRequest.subtitle') }}
                </p>
              </div>
            </div>
            <UButton
              icon="i-heroicons-x-mark"
              color="gray"
              variant="ghost"
              @click="closeLiveRequestDialog"
            />
          </div>
        </template>

        <!-- Two Column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-0 min-h-[600px]">
          <!-- Left Side: Form Fields -->
          <div class="p-6 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div class="space-y-5">
              <div>
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" />
                  {{ t('liveRequest.requestConfiguration') }}
                </h4>
              </div>

              <!-- URL Input -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('liveRequest.apiUrl') }} <span class="text-red-500">{{ t('liveRequest.required') }}</span>
                </label>
                <div class="flex gap-2">
                  <UInput
                    v-model="liveRequest.url"
                    :placeholder="t('liveRequest.placeholder.url')"
                    size="lg"
                    icon="i-heroicons-link"
                    class="flex-1"
                  />
                  <UButton
                    icon="i-heroicons-sparkles"
                    color="primary"
                    variant="soft"
                    size="lg"
                    @click="generateDefaultUrl"
                    :title="t('liveRequest.generateUrl')"
                  />
                </div>
              </div>

              <!-- Commercial Registration Number Input -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('liveRequest.crNumber') }} <span class="text-red-500">{{ t('liveRequest.required') }}</span>
                </label>
                <UInput
                  v-model="liveRequest.crNumber"
                  :placeholder="t('liveRequest.placeholder.crNumber')"
                  size="lg"
                  icon="i-heroicons-identification"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ t('liveRequest.parameter') }} <code class="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">id</code>
                </p>
              </div>

              <!-- Language Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('liveRequest.language') }} <span class="text-red-500">{{ t('liveRequest.required') }}</span>
                </label>
                <USelectMenu
                  v-model="liveRequest.language"
                  :options="languageOptions"
                  size="lg"
                  value-attribute="value"
                  option-attribute="label"
                >
                  <template #label>
                    <span v-if="liveRequest.language" class="block truncate">
                      {{ languageOptions.find((l: any) => l.value === liveRequest.language)?.label }}
                    </span>
                    <span v-else class="text-gray-400">{{ t('liveRequest.selectLanguage') }}</span>
                  </template>
                </USelectMenu>
              </div>

              <!-- Make Request Button -->
              <div class="pt-2">
                <UButton
                  color="primary"
                  size="xl"
                  block
                  :loading="liveRequest.loading"
                  :disabled="!liveRequest.url || !liveRequest.crNumber || !liveRequest.language"
                  @click="handleMakeRequest"
                >
                  <UIcon name="i-heroicons-paper-airplane" class="mr-2" />
                  {{ liveRequest.loading ? t('liveRequest.sendingRequest') : t('liveRequest.makeRequest') }}
                </UButton>
              </div>

              <!-- Request Status -->
              <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('liveRequest.status') }}
                </label>
                <div class="flex items-center gap-2">
                  <UBadge
                    :color="getRequestStatusColor()"
                    variant="subtle"
                    size="lg"
                  >
                    {{ liveRequest.status }}
                  </UBadge>
                  <span v-if="liveRequest.loading" class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1">
                    <UIcon name="i-heroicons-arrow-path" class="animate-spin w-4 h-4" />
                    {{ t('liveRequest.sendingRequest') }}
                  </span>
                </div>
              </div>

              <!-- Request Info -->
              <div v-if="liveRequest.response" class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div class="flex items-start gap-2">
                  <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                  <div class="text-sm">
                    <p class="font-medium text-blue-900 dark:text-blue-100">{{ t('liveRequest.responseReceived') }}</p>
                    <p class="text-blue-700 dark:text-blue-300 mt-1">
                      {{ t('liveRequest.statusLabel') }} {{ liveRequest.response.status }} {{ liveRequest.response.statusText }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Side: JSON Response -->
          <div class="p-6 bg-gray-50 dark:bg-gray-950 flex flex-col">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <UIcon name="i-heroicons-code-bracket" class="w-4 h-4" />
                {{ t('liveRequest.responseData') }}
              </h4>
              <UButton
                v-if="liveRequest.response"
                size="xs"
                color="gray"
                variant="ghost"
                icon="i-heroicons-clipboard-document"
                @click="copyToClipboard"
              >
                {{ t('liveRequest.copy') }}
              </UButton>
            </div>
            
            <div class="flex-1 border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden">
              <textarea
                v-model="formattedJsonResponse"
                readonly
                class="w-full h-full p-4 font-mono text-xs bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 resize-none focus:outline-none"
                :placeholder="t('liveRequest.placeholder.response')"
              ></textarea>
            </div>
          </div>
        </div>

        <template #footer>
          <!-- Warning Note -->
          <div class="mb-4 p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-l-4 border-amber-500 dark:border-amber-600 rounded-lg">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-amber-600 dark:text-amber-400 animate-pulse" />
              </div>
              <div class="flex-1">
                <h5 class="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-1 flex items-center gap-2">
                  <span>{{ t('liveRequest.warning.title') }}</span>
                  <UBadge color="amber" variant="solid" size="xs">Important</UBadge>
                </h5>
                <p class="text-sm text-amber-800 dark:text-amber-200 leading-relaxed" :dir="locale === 'ar' ? 'rtl' : 'ltr'">
                  {{ t('liveRequest.warning.message') }}
                </p>
                <div class="mt-2 flex items-center gap-2">
                  <UIcon name="i-heroicons-chart-bar" class="w-4 h-4 text-amber-700 dark:text-amber-300" />
                  <span class="text-xs font-medium text-amber-700 dark:text-amber-300">
                    {{ t('liveRequest.warning.requestCount') }}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full bg-amber-200 dark:bg-amber-800 text-amber-900 dark:text-amber-100 font-bold">
                      {{ liveRequest.requestCount }}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Actions -->
          <div class="flex justify-between items-center">
            <div class="text-xs text-gray-500 dark:text-gray-400">
              <span v-if="liveRequest.response">
                {{ t('liveRequest.responseSize') }} {{ responseSize }} {{ t('liveRequest.bytes') }}
              </span>
            </div>
            <div class="flex gap-3">
              <UButton
                color="gray"
                variant="outline"
                @click="handleCloseWithConfirm"
              >
                {{ t('liveRequest.close') }}
              </UButton>
              <UButton
                color="green"
                :disabled="!liveRequest.response"
                @click="handleSaveData"
              >
                <UIcon name="i-heroicons-arrow-down-tray" class="mr-2" />
                {{ t('liveRequest.saveData') }}
              </UButton>
            </div>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useRouter } from 'vue-router'
import { useConfirm } from '@/composables/useConfirm'
import { useAuthenticatedFetch } from '@/composables/useAuthenticatedFetch'
import { useAuthStore } from '@/stores/auth'
import type { DataTableConfig } from '~/types/datatable'
import AdvancedDataTable from '~/components/ui/AdvancedDataTable.vue'

const { t, locale } = useI18n()
const router = useRouter()
const { confirm, confirmWarning } = useConfirm()
const { authenticatedFetch } = useAuthenticatedFetch()
const toast = useToast()

// Define page metadata
definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// Stats state
const stats = ref({
  total: 0,
  active: 0,
  suspended: 0,
  cancelled: 0
})

// Live Request Dialog State
const isLiveRequestDialogOpen = ref(false)
const liveRequest = ref({
  url: '',
  crNumber: '',
  language: '',
  status: 'Ready',
  loading: false,
  response: null as any,
  requestCount: 1
})

const languageOptions = computed(() => [
  { label: t('liveRequest.arabic'), value: 'ar' },
  { label: t('liveRequest.english'), value: 'en' }
])

const formattedJsonResponse = computed(() => {
  if (!liveRequest.value.response) {
    return ''
  }
  try {
    return JSON.stringify(liveRequest.value.response, null, 2)
  } catch (error) {
    return String(liveRequest.value.response)
  }
})

const responseSize = computed(() => {
  if (!formattedJsonResponse.value) {
    return 0
  }
  return new globalThis.Blob([formattedJsonResponse.value]).size
})

function openLiveRequestDialog() {
  isLiveRequestDialogOpen.value = true
  // Reset form
  liveRequest.value = {
    url: '',
    crNumber: '',
    language: '',
    status: 'Ready',
    loading: false,
    response: null,
    requestCount: 1
  }
}

function closeLiveRequestDialog() {
  isLiveRequestDialogOpen.value = false
}

function generateDefaultUrl() {
  liveRequest.value.url = 'https://api.wathq.sa/commercial-registration/fullinfo'
}

function getRequestStatusColor() {
  const status = liveRequest.value.status.toLowerCase()
  if (status === 'ready') return 'gray'
  if (status === 'loading' || status === 'processing') return 'blue'
  if (status === 'success') return 'green'
  if (status === 'error' || status === 'failed') return 'red'
  return 'gray'
}

async function handleMakeRequest() {
  // Show confirmation dialog before making request
  const message = t('liveRequest.confirm.makeRequest')
    .replace('{url}', liveRequest.value.url)
    .replace('{crNumber}', liveRequest.value.crNumber)
    .replace('{language}', liveRequest.value.language)
  
  const confirmed = await confirmWarning(message, t('liveRequest.title'))

  if (!confirmed) return

  liveRequest.value.loading = true
  liveRequest.value.status = 'Processing'
  liveRequest.value.response = null

  try {
    // Determine endpoint based on user type
    // Management users use /management endpoint, tenant users use regular endpoint
    const authStore = useAuthStore()
    const isManagementUser = authStore.user?.is_super_admin || false
    const endpoint = isManagementUser 
      ? '/api/v1/wathq/live/management/commercial-registration/query'
      : '/api/v1/wathq/live/commercial-registration/query'
    
    // Use authenticated fetch to include auth token
    const response = await authenticatedFetch(endpoint, {
      method: 'POST',
      body: JSON.stringify({
        cr_number: liveRequest.value.crNumber
      })
    })

    liveRequest.value.response = {
      status: 200,
      statusText: 'OK',
      data: response
    }

    liveRequest.value.status = 'Success'

    // Save the request to database
    await saveCrRequest(200, 'Success')
  } catch (error: any) {
    console.error('Request failed:', error)
    
    liveRequest.value.status = 'Failed'
    
    const errorMessage = error?.data?.detail || error?.message || 'Request failed'
    const statusCode = error?.statusCode || error?.status || 0
    
    liveRequest.value.response = {
      status: statusCode,
      statusText: 'Error',
      error: errorMessage,
      details: error?.data || error
    }

    // Save the failed request to database
    await saveCrRequest(statusCode, errorMessage)
  } finally {
    liveRequest.value.loading = false
  }
}

async function saveCrRequest(statusNumber: number, statusText: string) {
  try {
    await $fetch('/api/v1/cr-requests/', {
      method: 'POST',
      body: {
        url: liveRequest.value.url,
        cr_number: liveRequest.value.crNumber,
        language: liveRequest.value.language,
        response: liveRequest.value.response,
        status_number: statusNumber,
        status_text: statusText,
        created_by: 'system' // You can replace this with actual user info if available
      }
    })
  } catch (error) {
    console.error('Failed to save CR request:', error)
    // Don't show error to user, just log it
  }
}

async function handleSaveData() {
  if (!liveRequest.value.response) {
    return
  }

  const confirmed = await confirmWarning(
    t('liveRequest.confirmSave'),
    t('liveRequest.saveDataTitle')
  )

  if (!confirmed) return

  try {
    // Extract the response data from the API response
    const responseData = liveRequest.value.response?.data?.response_data || liveRequest.value.response?.data || liveRequest.value.response
    
    console.log('Full response:', liveRequest.value.response)
    console.log('Extracted responseData:', responseData)
    
    // Check if the response is successful
    if (!responseData) {
      throw new Error('No response data available to save')
    }

    // Extract commercial registration data from the Wathq API response
    // The structure should match what the Wathq API returns
    const crData = {
      cr_number: liveRequest.value.crNumber,
      cr_national_number: responseData.crNationalNumber || responseData.cr_national_number,
      version_no: responseData.versionNo || responseData.version_no,
      name: responseData.name,
      name_lang_id: responseData.nameLangId || responseData.name_lang_id,
      name_lang_desc: responseData.nameLangDesc || responseData.name_lang_desc,
      cr_capital: responseData.crCapital || responseData.cr_capital,
      company_duration: responseData.companyDuration || responseData.company_duration,
      is_main: responseData.isMain || responseData.is_main,
      issue_date_gregorian: responseData.issueDateGregorian || responseData.issue_date_gregorian,
      issue_date_hijri: responseData.issueDateHijri || responseData.issue_date_hijri,
      main_cr_national_number: responseData.mainCrNationalNumber || responseData.main_cr_national_number,
      main_cr_number: responseData.mainCrNumber || responseData.main_cr_number,
      in_liquidation_process: responseData.inLiquidationProcess || responseData.in_liquidation_process,
      has_ecommerce: responseData.hasEcommerce || responseData.has_ecommerce,
      headquarter_city_id: responseData.headquarterCityId || responseData.headquarter_city_id,
      headquarter_city_name: responseData.headquarterCityName || responseData.headquarter_city_name,
      is_license_based: responseData.isLicenseBased || responseData.is_license_based,
      license_issuer_national_number: responseData.licenseIssuerNationalNumber || responseData.license_issuer_national_number,
      license_issuer_name: responseData.licenseIssuerName || responseData.license_issuer_name,
      partners_nationality_id: responseData.partnersNationalityId || responseData.partners_nationality_id,
      partners_nationality_name: responseData.partnersNationalityName || responseData.partners_nationality_name,
      entity_type_id: responseData.entityTypeId || responseData.entity_type_id,
      entity_type_name: responseData.entityTypeName || responseData.entity_type_name,
      entity_form_id: responseData.entityFormId || responseData.entity_form_id,
      entity_form_name: responseData.entityFormName || responseData.entity_form_name,
      status_id: responseData.statusId || responseData.status_id,
      status_name: responseData.statusName || responseData.status_name,
      confirmation_date_gregorian: responseData.confirmationDateGregorian || responseData.confirmation_date_gregorian,
      confirmation_date_hijri: responseData.confirmationDateHijri || responseData.confirmation_date_hijri,
      reactivation_date_gregorian: responseData.reactivationDateGregorian || responseData.reactivation_date_gregorian,
      reactivation_date_hijri: responseData.reactivationDateHijri || responseData.reactivation_date_hijri,
      suspension_date_gregorian: responseData.suspensionDateGregorian || responseData.suspension_date_gregorian,
      suspension_date_hijri: responseData.suspensionDateHijri || responseData.suspension_date_hijri,
      deletion_date_gregorian: responseData.deletionDateGregorian || responseData.deletion_date_gregorian,
      deletion_date_hijri: responseData.deletionDateHijri || responseData.deletion_date_hijri,
      contact_phone: responseData.contactPhone || responseData.contact_phone,
      contact_mobile: responseData.contactMobile || responseData.contact_mobile,
      contact_email: responseData.contactEmail || responseData.contact_email,
      contact_website: responseData.contactWebsite || responseData.contact_website,
      fiscal_is_first: responseData.fiscalIsFirst || responseData.fiscal_is_first,
      fiscal_calendar_type_id: responseData.fiscalCalendarTypeId || responseData.fiscal_calendar_type_id,
      fiscal_calendar_type_name: responseData.fiscalCalendarTypeName || responseData.fiscal_calendar_type_name,
      fiscal_end_month: responseData.fiscalEndMonth || responseData.fiscal_end_month,
      fiscal_end_day: responseData.fiscalEndDay || responseData.fiscal_end_day,
      fiscal_end_year: responseData.fiscalEndYear || responseData.fiscal_end_year,
      mgmt_structure_id: responseData.mgmtStructureId || responseData.mgmt_structure_id,
      mgmt_structure_name: responseData.mgmtStructureName || responseData.mgmt_structure_name,
    }

    console.log('Prepared crData to send:', crData)

    // Save to commercial registrations table
    const result = await authenticatedFetch('/api/v1/wathq/cr-data/', {
      method: 'POST',
      body: JSON.stringify(crData)
    })
    
    console.log('Save result:', result)

    // Show success message
    toast.add({
      title: t('liveRequest.success.dataSaved'),
      color: 'green'
    })
    
    // Close the dialog
    isLiveRequestDialogOpen.value = false
  } catch (error: any) {
    console.error('Failed to save data:', error)
    const errorMessage = error?.data?.detail || error?.message || 'Unknown error'
    toast.add({
      title: t('liveRequest.error.saveFailed'),
      description: errorMessage,
      color: 'red'
    })
  }
}

async function copyToClipboard() {
  if (!formattedJsonResponse.value) {
    return
  }

  try {
    await navigator.clipboard.writeText(formattedJsonResponse.value)
    alert(t('liveRequest.success.copied'))
  } catch (error: any) {
    console.error('Failed to copy to clipboard:', error)
    alert(t('liveRequest.error.copyFailed') + ' ' + error.message)
  }
}

async function handleCloseWithConfirm() {
  if (liveRequest.value.response) {
    // Show confirmation if there's response data
    const confirmed = await confirmWarning(
      t('liveRequest.confirm.close'),
      t('liveRequest.close')
    )

    if (confirmed) {
      closeLiveRequestDialog()
    }
  } else {
    closeLiveRequestDialog()
  }
}

// Mock data for development/testing
const getMockData = () => {
  const now = new Date().toISOString()
  return [
    {
      id: 1,
      cr_number: '1010711252',
      name: 'Saudi Technology Company',
      name_lang_desc: 'شركة التقنية السعودية',
      status_name: 'Active',
      headquarter_city_name: 'Riyadh',
      issue_date_gregorian: '2020-01-15',
      cr_capital: 5000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1,
      request_body: null
    },
    {
      id: 2,
      cr_number: '1010711253',
      name: 'Gulf Trading Est.',
      name_lang_desc: 'مؤسسة الخليج التجارية',
      status_name: 'Active',
      headquarter_city_name: 'Jeddah',
      issue_date_gregorian: '2019-06-20',
      cr_capital: 2000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: null,
      request_body: null
    },
    {
      id: 3,
      cr_number: '1010711254',
      name: 'Modern Services Co.',
      name_lang_desc: 'شركة الخدمات الحديثة',
      status_name: 'Suspended',
      headquarter_city_name: 'Dammam',
      issue_date_gregorian: '2021-03-10',
      cr_capital: 1500000,
      created_at: now,
      updated_at: now,
      created_by: 2,
      updated_by: 2,
      request_body: null
    },
    {
      id: 4,
      cr_number: '1010711255',
      name: 'National Industries Ltd.',
      name_lang_desc: 'الصناعات الوطنية المحدودة',
      status_name: 'Active',
      headquarter_city_name: 'Riyadh',
      issue_date_gregorian: '2018-11-05',
      cr_capital: 10000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1,
      request_body: null
    },
    {
      id: 5,
      cr_number: '1010711256',
      name: 'Digital Solutions Group',
      name_lang_desc: 'مجموعة الحلول الرقمية',
      status_name: 'Cancelled',
      headquarter_city_name: 'Jeddah',
      issue_date_gregorian: '2022-02-28',
      cr_capital: 500000,
      created_at: now,
      updated_at: now,
      created_by: 3,
      updated_by: 3,
      request_body: null
    }
  ]
}

// DataTable Configuration
const tableConfig: DataTableConfig<any> = {
  // Data fetching
  fetchFunction: async (params) => {
    try {
      const response = await $fetch('/api/v1/wathq/cr-data/', {
        params: {
          page: params.page,
          limit: params.pageSize,
          search: params.search,
          sort_by: params.sortBy,
          sort_order: params.sortOrder,
          ...params.filters
        }
      })

      // Response now has structure: { data, total, page, pageSize, totalPages }
      const data = response?.data || []
      const total = response?.total || 0
      
      // If API returns empty or no data, use mock data for development
      if (!Array.isArray(data) || data.length === 0) {
        console.warn('No data from API, using mock data')
        const mockData = getMockData()
        
        // Update stats with mock data
        stats.value.total = mockData.length
        stats.value.active = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'active').length
        stats.value.suspended = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'suspended').length
        stats.value.cancelled = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'cancelled').length
        
        return {
          data: mockData,
          total: mockData.length,
          page: params.page,
          pageSize: params.pageSize,
          totalPages: Math.ceil(mockData.length / params.pageSize)
        }
      }

      // Update stats with actual data total
      stats.value.total = total
      stats.value.active = data.filter((item: any) => item.status_name?.toLowerCase() === 'active').length
      stats.value.suspended = data.filter((item: any) => item.status_name?.toLowerCase() === 'suspended').length
      stats.value.cancelled = data.filter((item: any) => item.status_name?.toLowerCase() === 'cancelled').length

      return {
        data: data,
        total: total,
        page: response.page || params.page,
        pageSize: response.pageSize || params.pageSize,
        totalPages: response.totalPages || Math.ceil(total / params.pageSize)
      }
    } catch (error) {
      console.error('Failed to fetch commercial registrations:', error)
      // On error, return mock data instead of throwing
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.active = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'active').length
      stats.value.suspended = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'suspended').length
      stats.value.cancelled = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'cancelled').length

      return {
        data: mockData,
        total: mockData.length,
        page: params.page,
        pageSize: params.pageSize,
        totalPages: Math.ceil(mockData.length / params.pageSize)
      }
    }
  },

  // Columns configuration
  columns: [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      visible: true,
      width: '80px',
      render: (value) => `<span class="font-mono text-sm text-gray-600">#${value}</span>`
    },
    {
      key: 'cr_number',
      label: t('wathqData.table.crNumber'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm">${value}</span>`
    },
    {
      key: 'name',
      label: t('wathqData.table.name'),
      sortable: true,
      searchable: true,
      minWidth: '200px',
      render: (value, row) => {
        const langDesc = row.name_lang_desc ? `<p class="text-xs text-gray-500">${row.name_lang_desc}</p>` : ''
        return `<div><p class="font-medium text-gray-900 dark:text-white">${value}</p>${langDesc}</div>`
      }
    },
    {
      key: 'status_name',
      label: t('wathqData.table.status'),
      sortable: true,
      type: 'badge',
      width: '120px',
      cellClass: (value) => {
        const status = value?.toLowerCase()
        if (status === 'active') return 'text-green-600'
        if (status === 'suspended') return 'text-yellow-600'
        if (status === 'cancelled') return 'text-red-600'
        return 'text-gray-600'
      }
    },
    {
      key: 'headquarter_city_name',
      label: t('wathqData.table.city'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'issue_date_gregorian',
      label: t('wathqData.table.issueDate'),
      sortable: true,
      type: 'date',
      width: '130px',
      format: (value) => value ? new Date(value).toLocaleDateString() : '-'
    },
    {
      key: 'created_at',
      label: 'Created At',
      sortable: true,
      type: 'date',
      width: '160px',
      format: (value) => value ? new Date(value).toLocaleString() : '-'
    },
    {
      key: 'updated_at',
      label: 'Updated At',
      sortable: true,
      type: 'date',
      width: '160px',
      format: (value) => value ? new Date(value).toLocaleString() : '-'
    },
    {
      key: 'created_by',
      label: 'Created By',
      sortable: true,
      width: '100px',
      render: (value) => value ? `<span class="text-sm">${value}</span>` : '-'
    },
    {
      key: 'updated_by',
      label: 'Updated By',
      sortable: true,
      width: '100px',
      render: (value) => value ? `<span class="text-sm">${value}</span>` : '-'
    }
  ],

  // Filters configuration
  filters: [
    {
      key: 'status_name',
      label: t('wathqData.filters.status'),
      type: 'select',
      placeholder: t('wathqData.status.all'),
      options: [
        { label: t('wathqData.status.all'), value: null },
        { label: t('wathqData.status.active'), value: 'active' },
        { label: t('wathqData.status.suspended'), value: 'suspended' },
        { label: t('wathqData.status.cancelled'), value: 'cancelled' }
      ]
    },
    {
      key: 'headquarter_city_name',
      label: t('wathqData.filters.city'),
      type: 'select',
      placeholder: t('wathqData.filters.allCities'),
      options: [
        { label: t('wathqData.filters.allCities'), value: null },
        { label: 'Riyadh', value: 'Riyadh' },
        { label: 'Jeddah', value: 'Jeddah' },
        { label: 'Dammam', value: 'Dammam' },
        { label: 'Makkah', value: 'Makkah' },
        { label: 'Madinah', value: 'Madinah' }
      ],
      searchable: true
    },
    {
      key: 'cr_number',
      label: t('wathqData.table.crNumber'),
      type: 'text',
      placeholder: 'Search by CR number...'
    }
  ],

  // Actions configuration
  actions: [
    {
      key: 'view',
      label: '',
      icon: 'i-heroicons-eye',
      color: 'primary' as const,
      variant: 'ghost',
      size: 'sm',
      handler: (row) => {
        router.push(`/wathq-data/commercial-registrations/${row.id}`)
      }
    },
    {
      key: 'edit',
      label: '',
      icon: 'i-heroicons-pencil',
      color: 'primary' as const,
      variant: 'ghost',
      size: 'sm',
      handler: (row) => {
        console.log('Edit:', row)
        // TODO: Implement edit modal
      }
    },
    {
      key: 'delete',
      label: '',
      icon: 'i-heroicons-trash',
      color: 'red' as const,
      variant: 'ghost',
      size: 'sm',
      confirm: {
        title: 'Delete Commercial Registration',
        message: 'Are you sure you want to delete this commercial registration? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/cr-data/${row.id}`, {
            method: 'DELETE'
          })
          // TODO: Show success notification and refresh table
        } catch (error) {
          console.error('Failed to delete:', error)
          // TODO: Show error notification
        }
      }
    }
  ],

  // Bulk actions
  bulkActions: [
    {
      key: 'export',
      label: 'Export Selected',
      icon: 'i-heroicons-arrow-down-tray',
      color: 'primary' as const,
      variant: 'outline',
      handler: async (selectedRows) => {
        console.log('Export selected:', selectedRows)
        // TODO: Implement export functionality
      }
    },
    {
      key: 'delete',
      label: 'Delete Selected',
      icon: 'i-heroicons-trash',
      color: 'red' as const,
      variant: 'outline',
      confirm: {
        title: 'Delete Multiple Records',
        message: 'Are you sure you want to delete the selected commercial registrations?'
      },
      handler: async (selectedRows, selectedIds) => {
        try {
          await $fetch('/api/v1/wathq/cr-data/bulk-delete', {
            method: 'POST',
            body: { ids: selectedIds }
          })
          // TODO: Show success notification and refresh table
        } catch (error) {
          console.error('Failed to delete:', error)
          // TODO: Show error notification
        }
      }
    }
  ],

  // Table settings
  keyField: 'cr_number',
  selectable: true,
  multiSelect: true,
  hoverable: true,
  striped: false,
  bordered: false,
  dense: false,
  
  // Pagination settings
  pagination: true,
  initialPage: 1,
  initialPageSize: 10,
  pageSizeOptions: [10, 20, 50, 100],
  showSizeChanger: true,
  showTotal: true,
  
  // Search settings
  globalSearch: true,
  searchPlaceholder: t('wathqData.search'),
  searchDebounce: 300,
  
  // Export settings
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  // Sorting
  initialSortColumn: 'cr_number',
  initialSortDirection: 'asc',
  
  // Empty state
  emptyStateIcon: 'i-heroicons-building-office',
  emptyStateTitle: t('wathqData.noData'),
  emptyStateDescription: 'No commercial registrations found. Try adjusting your filters.',
  
  // State persistence
  persistState: true,
  stateKey: 'commercial-registrations-table-v2'
}

// Sync state
const isSyncing = ref(false)

// Event handlers
function handleRowClick(row: any, index: number, event: Event) {
  console.log('Row clicked:', row)
}

function handleActionClick(action: any, row: any, index: number) {
  console.log('Action clicked:', action.key, row)
}

// Sync handler
async function handleSync() {
  try {
    isSyncing.value = true
    
    console.log('Starting sync from call logs...')
    
    const response = await authenticatedFetch<{
      success: boolean
      message: string
      synced_count: number
      total_logs: number
      errors: any[]
    }>('/api/v1/wathq/sync/commercial-registration/sync', {
      method: 'POST'
    })
    
    console.log('Sync response:', response)
    
    if (response.success) {
      const message = response.synced_count > 0
        ? `Synced ${response.synced_count} of ${response.total_logs} records from call logs`
        : `No new records to sync. Found ${response.total_logs} call logs but all records already exist.`
      
      toast.add({
        title: t('common.success'),
        description: message,
        color: 'green'
      })
      
      // Show errors if any
      if (response.errors && response.errors.length > 0) {
        console.warn('Sync errors:', response.errors)
        toast.add({
          title: 'Some records had errors',
          description: `${response.errors.length} records failed to sync. Check console for details.`,
          color: 'orange'
        })
      }
      
      // Only reload if records were synced
      if (response.synced_count > 0) {
        setTimeout(() => {
          window.location.reload()
        }, 1500)
      }
    } else {
      toast.add({
        title: t('common.error'),
        description: response.message || 'Failed to sync data from call logs',
        color: 'red'
      })
    }
  } catch (error: any) {
    console.error('Sync failed:', error)
    toast.add({
      title: t('common.error'),
      description: error.message || 'Failed to sync data from call logs',
      color: 'red'
    })
  } finally {
    isSyncing.value = false
  }
}
</script>
