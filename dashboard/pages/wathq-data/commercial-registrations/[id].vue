<template>
  <div class="commercial-registration-view">
    <!-- Header with Back Button -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/commercial-registrations')"
        >
          {{ t('wathqData.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ crData?.name || 'Commercial Registration' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            CR #{{ crData?.cr_number }}
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <UButton
          icon="i-heroicons-pencil"
          color="primary"
          variant="outline"
          @click="handleEdit"
        >
          {{ t('wathqData.view.edit') }}
        </UButton>
        
        <!-- Export Dropdown -->
        <UDropdown :items="exportMenuItems" :popper="{ placement: 'bottom-end' }">
          <UButton
            icon="i-heroicons-arrow-down-tray"
            color="gray"
            variant="outline"
            trailing-icon="i-heroicons-chevron-down"
          >
            {{ t('wathqData.view.export') }}
          </UButton>
        </UDropdown>
        
        <!-- Print Button -->
        <UButton
          icon="i-heroicons-printer"
          color="green"
          variant="soft"
          @click="printCR"
        >
          {{ t('wathqData.view.print') }}
        </UButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <div class="flex items-center gap-3">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-600" />
        <div>
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('wathqData.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="crData" class="space-y-6">
      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-building-office" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('wathqData.view.fields.id')" :value="crData.id" />
          <InfoField :label="t('wathqData.view.fields.crNumber')" :value="crData.cr_number" />
          <InfoField :label="t('wathqData.view.fields.crNationalNumber')" :value="crData.cr_national_number" />
          <InfoField :label="t('wathqData.view.fields.nameEnglish')" :value="crData.name" />
          <InfoField :label="t('wathqData.view.fields.nameArabic')" :value="crData.name_lang_desc" />
          <InfoField :label="t('wathqData.view.fields.status')" :value="crData.status_name">
            <template #value>
              <UBadge
                :color="getStatusColor(crData.status_name)"
                variant="subtle"
              >
                {{ crData.status_name }}
              </UBadge>
            </template>
          </InfoField>
          <InfoField :label="t('wathqData.view.fields.entityType')" :value="crData.entity_type_name" />
          <InfoField :label="t('wathqData.view.fields.entityForm')" :value="crData.entity_form_name" />
          <InfoField :label="t('wathqData.view.fields.capital')" :value="formatCurrency(crData.cr_capital)" />
          <InfoField :label="t('wathqData.view.fields.companyDuration')" :value="crData.company_duration ? `${crData.company_duration} ${t('wathqData.view.fields.years')}` : '-'" />
          <InfoField :label="t('wathqData.view.fields.headquarterCity')" :value="crData.headquarter_city_name" />
          <InfoField :label="t('wathqData.view.fields.issueDate')" :value="formatDate(crData.issue_date_gregorian)" />
          <InfoField :label="t('wathqData.view.fields.confirmationDate')" :value="formatDate(crData.confirmation_date_gregorian)" />
          <InfoField :label="t('wathqData.view.fields.partnersNationality')" :value="crData.partners_nationality_name" />
          <InfoField :label="t('wathqData.view.fields.hasEcommerce')" :value="crData.has_ecommerce ? t('wathqData.view.fields.yes') : t('wathqData.view.fields.no')" />
          <InfoField :label="t('wathqData.view.fields.inLiquidation')" :value="crData.in_liquidation_process ? t('wathqData.view.fields.yes') : t('wathqData.view.fields.no')" />
        </div>
      </UCard>

      <!-- Contact Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-phone" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.contactInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('wathqData.view.fields.phone')" :value="crData.contact_phone" />
          <InfoField :label="t('wathqData.view.fields.mobile')" :value="crData.contact_mobile" />
          <InfoField :label="t('wathqData.view.fields.email')" :value="crData.contact_email" />
          <InfoField :label="t('wathqData.view.fields.website')" :value="crData.contact_website" />
        </div>
      </UCard>

      <!-- Fiscal Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.fiscalInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('wathqData.view.fields.calendarType')" :value="crData.fiscal_calendar_type_name" />
          <InfoField :label="t('wathqData.view.fields.isFirstFiscalYear')" :value="crData.fiscal_is_first ? t('wathqData.view.fields.yes') : t('wathqData.view.fields.no')" />
          <InfoField :label="t('wathqData.view.fields.fiscalEndMonth')" :value="crData.fiscal_end_month" />
          <InfoField :label="t('wathqData.view.fields.fiscalEndDay')" :value="crData.fiscal_end_day" />
          <InfoField :label="t('wathqData.view.fields.fiscalEndYear')" :value="crData.fiscal_end_year" />
          <InfoField :label="t('wathqData.view.fields.managementStructure')" :value="crData.mgmt_structure_name" />
        </div>
      </UCard>

      <!-- Audit Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('wathqData.view.fields.createdAt')" :value="formatDateTime(crData.created_at)" />
          <InfoField :label="t('wathqData.view.fields.updatedAt')" :value="formatDateTime(crData.updated_at)" />
          <InfoField :label="t('wathqData.view.fields.createdBy')" :value="crData.created_by" />
          <InfoField :label="t('wathqData.view.fields.updatedBy')" :value="crData.updated_by" />
        </div>
      </UCard>

      <!-- Capital Info Section -->
      <UCard v-if="crData.capital_info">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-banknotes" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.capitalInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('wathqData.view.fields.currency')" :value="crData.capital_info.currency_name" />
          <InfoField :label="t('wathqData.view.fields.contributionType')" :value="crData.capital_info.contrib_type_name" />
          <InfoField :label="t('wathqData.view.fields.cashContribution')" :value="formatCurrency(crData.capital_info.contrib_cash)" />
          <InfoField :label="t('wathqData.view.fields.inKindContribution')" :value="formatCurrency(crData.capital_info.contrib_in_kind)" />
        </div>
      </UCard>

      <!-- Activities Section -->
      <UCard v-if="crData.activities && crData.activities.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-briefcase" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.activities') }} ({{ crData.activities.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(activity, index) in crData.activities"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.activityName')" :value="activity.activity_name" />
              <InfoField :label="t('wathqData.view.fields.isicCode')" :value="activity.isic_code" />
              <InfoField :label="t('wathqData.view.fields.isicDescription')" :value="activity.isic_desc" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Entity Characters Section -->
      <UCard v-if="crData.entity_characters && crData.entity_characters.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.entityCharacters') }} ({{ crData.entity_characters.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(character, index) in crData.entity_characters"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField :label="t('wathqData.view.fields.characterId')" :value="character.character_id" />
              <InfoField :label="t('wathqData.view.fields.characterName')" :value="character.character_name" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Parties Section -->
      <UCard v-if="crData.parties && crData.parties.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-users" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.parties') }} ({{ crData.parties.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(party, index) in crData.parties"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.partyName')" :value="party.name" />
              <InfoField :label="t('wathqData.view.fields.partyType')" :value="party.type_name" />
              <InfoField :label="t('wathqData.view.fields.identityId')" :value="party.identity_id" />
              <InfoField :label="t('wathqData.view.fields.identityType')" :value="party.identity_type_name" />
              <InfoField :label="t('wathqData.view.fields.shareCashCount')" :value="party.share_cash_count" />
              <InfoField :label="t('wathqData.view.fields.shareInKindCount')" :value="party.share_in_kind_count" />
              <InfoField :label="t('wathqData.view.fields.shareTotalCount')" :value="party.share_total_count" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Managers Section -->
      <UCard v-if="crData.managers && crData.managers.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-user-circle" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.managers') }} ({{ crData.managers.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(manager, index) in crData.managers"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.managerName')" :value="manager.name" />
              <InfoField :label="t('wathqData.view.fields.managerType')" :value="manager.type_name" />
              <InfoField :label="t('wathqData.view.fields.identityId')" :value="manager.identity_id" />
              <InfoField :label="t('wathqData.view.fields.identityType')" :value="manager.identity_type_name" />
              <InfoField :label="t('wathqData.view.fields.nationality')" :value="manager.nationality_name" />
              <InfoField :label="t('wathqData.view.fields.isLicensed')" :value="manager.is_licensed ? t('wathqData.view.fields.yes') : t('wathqData.view.fields.no')" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Stocks Section -->
      <UCard v-if="crData.stocks && crData.stocks.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.stocks') }} ({{ crData.stocks.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(stock, index) in crData.stocks"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.stockType')" :value="stock.type_name" />
              <InfoField :label="t('wathqData.view.fields.stockCount')" :value="stock.stock_count" />
              <InfoField :label="t('wathqData.view.fields.stockValue')" :value="formatCurrency(stock.stock_value)" />
              <InfoField :label="t('wathqData.view.fields.className')" :value="stock.class_name" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- E-Stores Section -->
      <UCard v-if="crData.estores && crData.estores.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-shopping-cart" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.estores') }} ({{ crData.estores.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(estore, index) in crData.estores"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.authPlatformUrl')" :value="estore.auth_platform_url" />
              <InfoField :label="t('wathqData.view.fields.storeUrl')" :value="estore.store_url" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Liquidators Section -->
      <UCard v-if="crData.liquidators && crData.liquidators.length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-scale" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('wathqData.view.sections.liquidators') }} ({{ crData.liquidators.length }})</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(liquidator, index) in crData.liquidators"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoField :label="t('wathqData.view.fields.liquidatorName')" :value="liquidator.name" />
              <InfoField :label="t('wathqData.view.fields.liquidatorType')" :value="liquidator.type_name" />
              <InfoField :label="t('wathqData.view.fields.identityId')" :value="liquidator.identity_id" />
              <InfoField :label="t('wathqData.view.fields.identityType')" :value="liquidator.identity_type_name" />
              <InfoField :label="t('wathqData.view.fields.nationality')" :value="liquidator.nationality_name" />
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useAuthStore } from '@/stores/auth'
import { useAlert } from '@/composables/useAlert'
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useAlert()

const crData = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const isExportingXls = ref(false)
const isExportingPdf = ref(false)

const id = computed(() => route.params.id)

// Export menu items
const exportMenuItems = computed(() => [[
  {
    label: t('wathq.actions.exportJson'),
    icon: 'i-heroicons-arrow-down-tray',
    click: exportToJson
  },
  {
    label: t('wathq.actions.exportXls'),
    icon: 'i-heroicons-table-cells',
    click: exportToXls,
    loading: isExportingXls.value
  },
  {
    label: t('wathq.actions.exportPdf'),
    icon: 'i-heroicons-document-text',
    click: exportToPdf,
    loading: isExportingPdf.value
  }
]])

// Mock data for development
const getMockCRData = (id: number) => {
  return {
    id: id,
    cr_number: '1010711252',
    cr_national_number: '7001234567',
    version_no: 1,
    name: 'Saudi Technology Company',
    name_lang_desc: 'شركة التقنية السعودية',
    cr_capital: 5000000,
    company_duration: 99,
    is_main: true,
    issue_date_gregorian: '2020-01-15',
    issue_date_hijri: '1441-05-20',
    status_id: 1,
    status_name: 'Active',
    entity_type_id: 1,
    entity_type_name: 'Limited Liability Company',
    entity_form_id: 1,
    entity_form_name: 'LLC',
    headquarter_city_id: 1,
    headquarter_city_name: 'Riyadh',
    partners_nationality_id: 1,
    partners_nationality_name: 'Saudi',
    has_ecommerce: true,
    in_liquidation_process: false,
    contact_phone: '+966112345678',
    contact_mobile: '+966501234567',
    contact_email: 'info@sauditech.sa',
    contact_website: 'https://sauditech.sa',
    fiscal_calendar_type_id: 1,
    fiscal_calendar_type_name: 'Gregorian',
    fiscal_is_first: true,
    fiscal_end_month: 12,
    fiscal_end_day: 31,
    fiscal_end_year: 2024,
    mgmt_structure_id: 1,
    mgmt_structure_name: 'Board of Directors',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    created_by: 1,
    updated_by: 1,
    request_body: null,
    confirmation_date_gregorian: '2020-01-20',
    capital_info: {
      currency_id: 1,
      currency_name: 'SAR',
      contrib_type_id: 1,
      contrib_type_name: 'Cash',
      contrib_cash: 5000000,
      contrib_in_kind: 0
    },
    activities: [
      {
        activity_name: 'Software Development',
        isic_code: '6201',
        isic_desc: 'Computer programming activities'
      },
      {
        activity_name: 'IT Consulting',
        isic_code: '6202',
        isic_desc: 'Computer consultancy activities'
      }
    ],
    entity_characters: [
      {
        entity_character_name: 'Technology Company',
        entity_character_desc: 'Specialized in technology solutions'
      }
    ],
    parties: [
      {
        party_name: 'Ahmed Al-Saud',
        party_type_name: 'Partner',
        party_id_number: '1234567890',
        party_nationality_name: 'Saudi',
        party_birth_date_gregorian: '1985-05-15',
        party_gender_name: 'Male'
      }
    ],
    managers: [
      {
        manager_name: 'Mohammed Al-Rashid',
        manager_id_number: '9876543210',
        manager_nationality_name: 'Saudi',
        manager_birth_date_gregorian: '1980-03-20',
        manager_gender_name: 'Male'
      }
    ],
    stocks: [
      {
        stock_type_name: 'Common Stock',
        number_of_stocks: 1000,
        stock_value: 5000
      }
    ],
    estores: [
      {
        estore_name: 'Saudi Tech Store',
        estore_url: 'https://store.sauditech.sa',
        estore_platform_name: 'Custom Platform'
      }
    ],
    liquidators: []
  }
}

onMounted(async () => {
  await fetchCRData()
})

async function fetchCRData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching CR data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/cr-data/${id.value}`)
    console.log('API Response:', response)
    crData.value = response
    console.log('CR Data set:', crData.value)
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    // Fallback to mock data for development
    crData.value = getMockCRData(Number(id.value))
    console.log('Using mock CR data:', crData.value)
  } finally {
    loading.value = false
  }
}

function getStatusColor(status: string) {
  const statusLower = status?.toLowerCase()
  if (statusLower === 'active') return 'green'
  if (statusLower === 'suspended') return 'yellow'
  if (statusLower === 'cancelled') return 'red'
  return 'gray'
}

function formatCurrency(value: any) {
  if (!value) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'SAR'
  }).format(value)
}

function formatDate(value: any) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString()
}

function formatDateTime(value: any) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

function handleEdit() {
  console.log('Edit CR:', id.value)
  // TODO: Implement edit functionality
}

// Export to JSON
function exportToJson() {
  if (!crData.value) return
  
  const blob = new Blob([JSON.stringify(crData.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `commercial_registration_${crData.value.cr_number}_${Date.now()}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  showSuccess(t('wathq.exportSuccess'))
}

// Export to XLS
async function exportToXls() {
  if (!crData.value) return
  
  try {
    isExportingXls.value = true
    
    // Import XLSX library dynamically
    const XLSX = await import('xlsx')
    
    // Prepare main data
    const mainData = {
      'CR Number': crData.value.cr_number,
      'Name': crData.value.name,
      'Arabic Name': crData.value.name_lang_desc,
      'Status': crData.value.status_name,
      'Entity Type': crData.value.entity_type_name,
      'Capital': crData.value.cr_capital,
      'City': crData.value.headquarter_city_name,
      'Issue Date': crData.value.issue_date_gregorian,
      'Phone': crData.value.contact_phone,
      'Email': crData.value.contact_email
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new()
    
    // Add main info sheet
    const mainWs = XLSX.utils.json_to_sheet([mainData])
    XLSX.utils.book_append_sheet(wb, mainWs, 'Main Info')
    
    // Add activities sheet if exists
    if (crData.value.activities && crData.value.activities.length > 0) {
      const activitiesWs = XLSX.utils.json_to_sheet(crData.value.activities)
      XLSX.utils.book_append_sheet(wb, activitiesWs, 'Activities')
    }
    
    // Add parties sheet if exists
    if (crData.value.parties && crData.value.parties.length > 0) {
      const partiesWs = XLSX.utils.json_to_sheet(crData.value.parties)
      XLSX.utils.book_append_sheet(wb, partiesWs, 'Parties')
    }
    
    // Add managers sheet if exists
    if (crData.value.managers && crData.value.managers.length > 0) {
      const managersWs = XLSX.utils.json_to_sheet(crData.value.managers)
      XLSX.utils.book_append_sheet(wb, managersWs, 'Managers')
    }
    
    // Save file
    const filename = `commercial_registration_${crData.value.cr_number}_${Date.now()}.xlsx`
    XLSX.writeFile(wb, filename)
    
    showSuccess(t('wathq.exportXlsSuccess'))
  } catch (err: any) {
    console.error('XLS export error:', err)
    showError(err.message || t('wathq.exportXlsFailed'))
  } finally {
    isExportingXls.value = false
  }
}

// Export to PDF
async function exportToPdf() {
  if (!crData.value) return
  
  try {
    isExportingPdf.value = true
    
    // Use the dedicated CR PDF export endpoint
    const pdfUrl = `${config.public.apiBase}/wathq/pdf/commercial-registration/${id.value}/pdf`
    const queryParams = new URLSearchParams({
      language: 'ar',
      include_activities: 'true',
      include_parties: 'true',
      include_managers: 'true'
    })
    
    const fullUrl = `${pdfUrl}?${queryParams.toString()}`
    
    // Use fetch to download with authentication
    const token = authStore.token
    if (token) {
      const response = await fetch(fullUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `commercial_registration_${crData.value.cr_number}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        showSuccess(t('wathq.actions.exportPdfSuccess'))
      } else {
        throw new Error('Failed to generate PDF')
      }
    }
  } catch (error) {
    console.error('PDF export failed:', error)
    showError(t('wathq.actions.exportPdfError'))
  } finally {
    isExportingPdf.value = false
  }
}

// Print CR
function printCR() {
  if (!crData.value) return
  
  const printContent = `
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
      <meta charset="UTF-8">
      <title>Commercial Registration - ${crData.value.cr_number}</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          margin: 20px;
          direction: rtl;
        }
        h1 {
          color: #1e40af;
          border-bottom: 2px solid #1e40af;
          padding-bottom: 10px;
        }
        h2 {
          color: #3b82f6;
          margin-top: 20px;
          border-bottom: 1px solid #e5e7eb;
          padding-bottom: 5px;
        }
        .info-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 15px;
          margin: 15px 0;
        }
        .info-field {
          padding: 10px;
          background: #f9fafb;
          border-radius: 4px;
        }
        .info-label {
          font-weight: bold;
          color: #6b7280;
          font-size: 12px;
        }
        .info-value {
          color: #111827;
          margin-top: 5px;
        }
        .section {
          margin: 20px 0;
          page-break-inside: avoid;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 10px 0;
        }
        th, td {
          border: 1px solid #e5e7eb;
          padding: 8px;
          text-align: right;
        }
        th {
          background: #f3f4f6;
          font-weight: bold;
        }
        @media print {
          body { margin: 0; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <h1>السجل التجاري - ${crData.value.cr_number}</h1>
      
      <div class="section">
        <h2>المعلومات الأساسية</h2>
        <div class="info-grid">
          <div class="info-field">
            <div class="info-label">رقم السجل التجاري</div>
            <div class="info-value">${crData.value.cr_number || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">الاسم</div>
            <div class="info-value">${crData.value.name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">الاسم بالعربية</div>
            <div class="info-value">${crData.value.name_lang_desc || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">الحالة</div>
            <div class="info-value">${crData.value.status_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">نوع الكيان</div>
            <div class="info-value">${crData.value.entity_type_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">رأس المال</div>
            <div class="info-value">${formatCurrency(crData.value.cr_capital)}</div>
          </div>
          <div class="info-field">
            <div class="info-label">المدينة</div>
            <div class="info-value">${crData.value.headquarter_city_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">تاريخ الإصدار</div>
            <div class="info-value">${formatDate(crData.value.issue_date_gregorian)}</div>
          </div>
        </div>
      </div>
      
      ${crData.value.activities && crData.value.activities.length > 0 ? `
      <div class="section">
        <h2>الأنشطة (${crData.value.activities.length})</h2>
        <table>
          <thead>
            <tr>
              <th>اسم النشاط</th>
              <th>رمز ISIC</th>
              <th>الوصف</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.activities.map((activity: any) => `
              <tr>
                <td>${activity.activity_name || '-'}</td>
                <td>${activity.isic_code || '-'}</td>
                <td>${activity.isic_desc || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.parties && crData.value.parties.length > 0 ? `
      <div class="section">
        <h2>الشركاء (${crData.value.parties.length})</h2>
        <table>
          <thead>
            <tr>
              <th>الاسم</th>
              <th>النوع</th>
              <th>رقم الهوية</th>
              <th>الجنسية</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.parties.map((party: any) => `
              <tr>
                <td>${party.name || '-'}</td>
                <td>${party.type_name || '-'}</td>
                <td>${party.identity_id || '-'}</td>
                <td>${party.identity_type_name || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.managers && crData.value.managers.length > 0 ? `
      <div class="section">
        <h2>المديرون (${crData.value.managers.length})</h2>
        <table>
          <thead>
            <tr>
              <th>الاسم</th>
              <th>النوع</th>
              <th>رقم الهوية</th>
              <th>الجنسية</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.managers.map((manager: any) => `
              <tr>
                <td>${manager.name || '-'}</td>
                <td>${manager.type_name || '-'}</td>
                <td>${manager.identity_id || '-'}</td>
                <td>${manager.nationality_name || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.contact_phone || crData.value.contact_mobile || crData.value.contact_email || crData.value.contact_website ? `
      <div class="section">
        <h2>معلومات الاتصال</h2>
        <div class="info-grid">
          ${crData.value.contact_phone ? `
          <div class="info-field">
            <div class="info-label">الهاتف</div>
            <div class="info-value">${crData.value.contact_phone}</div>
          </div>
          ` : ''}
          ${crData.value.contact_mobile ? `
          <div class="info-field">
            <div class="info-label">الجوال</div>
            <div class="info-value">${crData.value.contact_mobile}</div>
          </div>
          ` : ''}
          ${crData.value.contact_email ? `
          <div class="info-field">
            <div class="info-label">البريد الإلكتروني</div>
            <div class="info-value">${crData.value.contact_email}</div>
          </div>
          ` : ''}
          ${crData.value.contact_website ? `
          <div class="info-field">
            <div class="info-label">الموقع الإلكتروني</div>
            <div class="info-value">${crData.value.contact_website}</div>
          </div>
          ` : ''}
        </div>
      </div>
      ` : ''}
      
      ${crData.value.capital_info ? `
      <div class="section">
        <h2>معلومات رأس المال</h2>
        <div class="info-grid">
          <div class="info-field">
            <div class="info-label">العملة</div>
            <div class="info-value">${crData.value.capital_info.currency_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">نوع المساهمة</div>
            <div class="info-value">${crData.value.capital_info.contrib_type_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">المساهمة النقدية</div>
            <div class="info-value">${formatCurrency(crData.value.capital_info.contrib_cash)}</div>
          </div>
          <div class="info-field">
            <div class="info-label">المساهمة العينية</div>
            <div class="info-value">${formatCurrency(crData.value.capital_info.contrib_in_kind)}</div>
          </div>
        </div>
      </div>
      ` : ''}
      
      ${crData.value.fiscal_calendar_type_name ? `
      <div class="section">
        <h2>المعلومات المالية</h2>
        <div class="info-grid">
          <div class="info-field">
            <div class="info-label">نوع التقويم المالي</div>
            <div class="info-value">${crData.value.fiscal_calendar_type_name || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">السنة المالية الأولى</div>
            <div class="info-value">${crData.value.fiscal_is_first ? 'نعم' : 'لا'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">شهر نهاية السنة المالية</div>
            <div class="info-value">${crData.value.fiscal_end_month || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">يوم نهاية السنة المالية</div>
            <div class="info-value">${crData.value.fiscal_end_day || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">سنة نهاية السنة المالية</div>
            <div class="info-value">${crData.value.fiscal_end_year || '-'}</div>
          </div>
          <div class="info-field">
            <div class="info-label">هيكل الإدارة</div>
            <div class="info-value">${crData.value.mgmt_structure_name || '-'}</div>
          </div>
        </div>
      </div>
      ` : ''}
      
      ${crData.value.entity_characters && crData.value.entity_characters.length > 0 ? `
      <div class="section">
        <h2>خصائص الكيان (${crData.value.entity_characters.length})</h2>
        <table>
          <thead>
            <tr>
              <th>رقم الخاصية</th>
              <th>اسم الخاصية</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.entity_characters.map((character: any) => `
              <tr>
                <td>${character.character_id || '-'}</td>
                <td>${character.character_name || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.stocks && crData.value.stocks.length > 0 ? `
      <div class="section">
        <h2>الأسهم (${crData.value.stocks.length})</h2>
        <table>
          <thead>
            <tr>
              <th>نوع السهم</th>
              <th>عدد الأسهم</th>
              <th>قيمة السهم</th>
              <th>الفئة</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.stocks.map((stock: any) => `
              <tr>
                <td>${stock.type_name || '-'}</td>
                <td>${stock.stock_count || '-'}</td>
                <td>${formatCurrency(stock.stock_value)}</td>
                <td>${stock.class_name || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.estores && crData.value.estores.length > 0 ? `
      <div class="section">
        <h2>المتاجر الإلكترونية (${crData.value.estores.length})</h2>
        <table>
          <thead>
            <tr>
              <th>رابط المنصة</th>
              <th>رابط المتجر</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.estores.map((estore: any) => `
              <tr>
                <td>${estore.auth_platform_url || '-'}</td>
                <td>${estore.store_url || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      ${crData.value.liquidators && crData.value.liquidators.length > 0 ? `
      <div class="section">
        <h2>المصفون (${crData.value.liquidators.length})</h2>
        <table>
          <thead>
            <tr>
              <th>الاسم</th>
              <th>النوع</th>
              <th>رقم الهوية</th>
              <th>الجنسية</th>
            </tr>
          </thead>
          <tbody>
            ${crData.value.liquidators.map((liquidator: any) => `
              <tr>
                <td>${liquidator.name || '-'}</td>
                <td>${liquidator.type_name || '-'}</td>
                <td>${liquidator.identity_id || '-'}</td>
                <td>${liquidator.nationality_name || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}
      
      <div class="section" style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 12px;">
        <p>تم الطباعة في: ${new Date().toLocaleString('ar-SA')}</p>
      </div>
    </body>
    </html>
  `
  
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(printContent)
    printWindow.document.close()
    printWindow.focus()
    printWindow.print()
  }
}
</script>

<style scoped>
.commercial-registration-view {
  @apply p-6;
}
</style>
