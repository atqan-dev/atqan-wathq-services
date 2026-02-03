<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/real-estate-deeds')"
        >
          {{ t('realEstateDeeds.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ deedData?.deed_number || 'Loading...' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ t('realEstateDeeds.subtitle') }}
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
          {{ t('realEstateDeeds.view.edit') }}
        </UButton>
        
        <!-- Export Dropdown -->
        <UDropdown :items="exportMenuItems" :popper="{ placement: 'bottom-end' }">
          <UButton
            icon="i-heroicons-arrow-down-tray"
            color="primary"
            trailing-icon="i-heroicons-chevron-down"
          >
            {{ t('realEstateDeeds.view.export') }}
          </UButton>
        </UDropdown>

        <!-- Print Button -->
        <UButton
          icon="i-heroicons-printer"
          color="gray"
          variant="outline"
          @click="handlePrint"
        >
          Print
        </UButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-600" />
        <div>
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('realEstateDeeds.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="deedData" class="space-y-6">
      <!-- Overview Cards Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.view.fields.deedNumber') }}</p>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ deedData.deed_number || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.view.fields.deedArea') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{{ formatArea(deedData.deed_area) }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.view.sections.owners') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ deedData.owners?.length || 0 }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.view.sections.realEstates') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ deedData.real_estates?.length || 0 }}</p>
          </div>
        </UCard>
      </div>

      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('realEstateDeeds.view.fields.id')" :value="deedData.id" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedNumber')" :value="deedData.deed_number" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedSerial')" :value="deedData.deed_serial" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedDate')" :value="deedData.deed_date" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedCity')" :value="deedData.deed_city" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedStatus')" :value="deedData.deed_status" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedSource')" :value="deedData.deed_source" />
        </div>
      </UCard>

      <!-- Area Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-square-3-stack-3d" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.areaInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoField :label="t('realEstateDeeds.view.fields.deedArea')" :value="formatArea(deedData.deed_area)" />
          <InfoField :label="t('realEstateDeeds.view.fields.deedAreaText')" :value="deedData.deed_area_text" />
        </div>
      </UCard>

      <!-- Status Flags Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-flag" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.statusFlags') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('realEstateDeeds.view.fields.isRealEstateConstrained')">
            <UBadge :color="deedData.is_real_estate_constrained ? 'red' : 'green'" variant="subtle">
              {{ deedData.is_real_estate_constrained ? t('realEstateDeeds.view.fields.yes') : t('realEstateDeeds.view.fields.no') }}
            </UBadge>
          </InfoField>
          <InfoField :label="t('realEstateDeeds.view.fields.isRealEstateHalted')">
            <UBadge :color="deedData.is_real_estate_halted ? 'red' : 'green'" variant="subtle">
              {{ deedData.is_real_estate_halted ? t('realEstateDeeds.view.fields.yes') : t('realEstateDeeds.view.fields.no') }}
            </UBadge>
          </InfoField>
          <InfoField :label="t('realEstateDeeds.view.fields.isRealEstateMortgaged')">
            <UBadge :color="deedData.is_real_estate_mortgaged ? 'red' : 'green'" variant="subtle">
              {{ deedData.is_real_estate_mortgaged ? t('realEstateDeeds.view.fields.yes') : t('realEstateDeeds.view.fields.no') }}
            </UBadge>
          </InfoField>
          <InfoField :label="t('realEstateDeeds.view.fields.isRealEstateTestamented')">
            <UBadge :color="deedData.is_real_estate_testamented ? 'orange' : 'green'" variant="subtle">
              {{ deedData.is_real_estate_testamented ? t('realEstateDeeds.view.fields.yes') : t('realEstateDeeds.view.fields.no') }}
            </UBadge>
          </InfoField>
        </div>
      </UCard>

      <!-- Boundaries Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-map" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.limits') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- North Limit -->
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ t('realEstateDeeds.view.sections.northLimit') }}</h3>
            <div class="space-y-2">
              <InfoField :label="t('realEstateDeeds.view.fields.limitName')" :value="deedData.limit_north_name" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitDescription')" :value="deedData.limit_north_description" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLength')" :value="deedData.limit_north_length" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLengthChar')" :value="deedData.limit_north_length_char" />
            </div>
          </div>

          <!-- South Limit -->
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ t('realEstateDeeds.view.sections.southLimit') }}</h3>
            <div class="space-y-2">
              <InfoField :label="t('realEstateDeeds.view.fields.limitName')" :value="deedData.limit_south_name" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitDescription')" :value="deedData.limit_south_description" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLength')" :value="deedData.limit_south_length" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLengthChar')" :value="deedData.limit_south_length_char" />
            </div>
          </div>

          <!-- East Limit -->
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ t('realEstateDeeds.view.sections.eastLimit') }}</h3>
            <div class="space-y-2">
              <InfoField :label="t('realEstateDeeds.view.fields.limitName')" :value="deedData.limit_east_name" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitDescription')" :value="deedData.limit_east_description" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLength')" :value="deedData.limit_east_length" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLengthChar')" :value="deedData.limit_east_length_char" />
            </div>
          </div>

          <!-- West Limit -->
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ t('realEstateDeeds.view.sections.westLimit') }}</h3>
            <div class="space-y-2">
              <InfoField :label="t('realEstateDeeds.view.fields.limitName')" :value="deedData.limit_west_name" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitDescription')" :value="deedData.limit_west_description" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLength')" :value="deedData.limit_west_length" />
              <InfoField :label="t('realEstateDeeds.view.fields.limitLengthChar')" :value="deedData.limit_west_length_char" />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Deed Text Card -->
      <UCard v-if="deedData.deed_text">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.fields.deedText') }}</h2>
          </div>
        </template>

        <div class="prose dark:prose-invert max-w-none">
          <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ deedData.deed_text }}</p>
        </div>
      </UCard>

      <!-- Audit Info Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('realEstateDeeds.view.fields.createdAt')" :value="formatDateTime(deedData.created_at)" />
          <InfoField :label="t('realEstateDeeds.view.fields.updatedAt')" :value="formatDateTime(deedData.updated_at)" />
          <InfoField :label="t('realEstateDeeds.view.fields.createdBy')" :value="deedData.created_by" />
          <InfoField :label="t('realEstateDeeds.view.fields.updatedBy')" :value="deedData.updated_by" />
        </div>
      </UCard>

      <!-- Owners Section -->
      <UCard v-if="deedData.owners && deedData.owners.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-users" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.owners') }}</h2>
            </div>
            <UBadge color="purple" variant="subtle">{{ deedData.owners.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.ownerName') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.idNumber') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.nationality') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.owningArea') }}</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(owner, index) in deedData.owners" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ owner.owner_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ owner.id_number || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ owner.nationality || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ formatArea(owner.owning_area) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Real Estates Section -->
      <UCard v-if="deedData.real_estates && deedData.real_estates.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-building-office-2" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('realEstateDeeds.view.sections.realEstates') }}</h2>
            </div>
            <UBadge color="blue" variant="subtle">{{ deedData.real_estates.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.cityName') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.districtName') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.realEstateTypeName') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.area') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ t('realEstateDeeds.view.fields.landNumber') }}</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(estate, index) in deedData.real_estates" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ estate.city_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ estate.district_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ estate.real_estate_type_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ formatArea(estate.area) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ estate.land_number || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useRealEstateDeedExport } from '@/composables/useRealEstateDeedExport'
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { 
  exportToPDF, 
  exportToJSON, 
  exportToCSV, 
  exportToExcel, 
  previewDeed,
  printDeed 
} = useRealEstateDeedExport()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const loading = ref(true)
const error = ref<string | null>(null)
const deedData = ref<any>(null)

const id = computed(() => route.params.id)

onMounted(() => {
  fetchDeedData()
})

function getMockDeedData(id: number) {
  const now = new Date().toISOString()
  
  return {
    id: id,
    deed_number: `${String(id).padStart(9, '0')}`,
    deed_serial: `RYD-2024-${String(id).padStart(3, '0')}`,
    deed_date: '1445/06/15',
    deed_text: 'هذا نص الصك العقاري الكامل الذي يحتوي على جميع التفاصيل القانونية والشروط والأحكام المتعلقة بالعقار.',
    deed_source: 'وزارة العدل',
    deed_city: 'Riyadh',
    deed_status: 'Active',
    deed_area: 500.50,
    deed_area_text: 'خمسمائة وخمسون سنتيمتر مربع',
    is_real_estate_constrained: false,
    is_real_estate_halted: false,
    is_real_estate_mortgaged: false,
    is_real_estate_testamented: false,
    limit_north_name: 'شارع الملك فهد',
    limit_north_description: 'شارع عام بعرض 30 متر',
    limit_north_length: 25.50,
    limit_north_length_char: 'خمسة وعشرون متر ونصف',
    limit_south_name: 'أرض فضاء',
    limit_south_description: 'أرض فضاء ملك خاص',
    limit_south_length: 25.50,
    limit_south_length_char: 'خمسة وعشرون متر ونصف',
    limit_east_name: 'منزل سكني',
    limit_east_description: 'منزل سكني ملك أحمد محمد',
    limit_east_length: 20.00,
    limit_east_length_char: 'عشرون متر',
    limit_west_name: 'شارع فرعي',
    limit_west_description: 'شارع فرعي بعرض 15 متر',
    limit_west_length: 20.00,
    limit_west_length_char: 'عشرون متر',
    created_at: now,
    updated_at: now,
    created_by: 1,
    updated_by: 1,
    owners: [
      {
        id: 1,
        owner_name: 'أحمد محمد علي',
        birth_date: '1980-05-15',
        id_number: '1234567890',
        id_type: '1',
        id_type_text: 'هوية وطنية',
        owner_type: 'فرد',
        nationality: 'سعودي',
        owning_area: 250.25,
        owning_amount: 500000.00,
        constrained: 0,
        halt: 0,
        pawned: 0,
        testament: 0
      },
      {
        id: 2,
        owner_name: 'سارة علي حسن',
        birth_date: '1985-08-20',
        id_number: '0987654321',
        id_type: '1',
        id_type_text: 'هوية وطنية',
        owner_type: 'فرد',
        nationality: 'سعودي',
        owning_area: 250.25,
        owning_amount: 500000.00,
        constrained: 0,
        halt: 0,
        pawned: 0,
        testament: 0
      }
    ],
    real_estates: [
      {
        id: 1,
        deed_serial: 'RYD-2024-001',
        region_code: '01',
        region_name: 'منطقة الرياض',
        city_code: 1,
        city_name: 'الرياض',
        real_estate_type_name: 'أرض سكنية',
        land_number: '12345',
        plan_number: 'A-123',
        area: 500.50,
        area_text: 'خمسمائة وخمسون سنتيمتر مربع',
        district_code: 101,
        district_name: 'حي النخيل',
        location_description: 'تقع الأرض في حي النخيل شمال الرياض',
        constrained: 0,
        halt: 0,
        pawned: 0,
        testament: 0,
        is_north_riyadh_exceptioned: 0
      }
    ]
  }
}

async function fetchDeedData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching deed data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/real-estate-deeds/${id.value}`)
    console.log('API Response:', response)
    
    if (response) {
      deedData.value = response
      console.log('Deed data loaded from API:', deedData.value)
    } else {
      throw new Error('No data returned from API')
    }
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    error.value = err.message || 'Failed to load deed data'
    deedData.value = getMockDeedData(Number(id.value))
    console.log('Using mock deed data:', deedData.value)
  } finally {
    loading.value = false
  }
}

// Export menu items
const exportMenuItems = computed(() => [
  [
    {
      label: 'Preview HTML',
      icon: 'i-heroicons-eye',
      click: () => handlePreview()
    },
    {
      label: 'Export PDF',
      icon: 'i-heroicons-document-text',
      click: () => handleExportPDF()
    }
  ],
  [
    {
      label: 'Export JSON',
      icon: 'i-heroicons-code-bracket',
      click: () => handleExportJSON()
    },
    {
      label: 'Export CSV',
      icon: 'i-heroicons-table-cells',
      click: () => handleExportCSV()
    },
    {
      label: 'Export Excel',
      icon: 'i-heroicons-document-chart-bar',
      click: () => handleExportExcel()
    }
  ]
])

function handleEdit() {
  console.log('Edit deed:', deedData.value)
}

async function handleExportPDF() {
  if (!deedData.value) return
  await exportToPDF(deedData.value.id)
}

async function handleExportJSON() {
  if (!deedData.value) return
  await exportToJSON(deedData.value.id)
}

async function handleExportCSV() {
  if (!deedData.value) return
  await exportToCSV(deedData.value.id)
}

async function handleExportExcel() {
  if (!deedData.value) return
  await exportToExcel(deedData.value.id)
}

function handlePreview() {
  if (!deedData.value) return
  previewDeed(deedData.value.id)
}

function handlePrint() {
  if (!deedData.value) return
  printDeed(deedData.value.id)
}

function formatArea(area: number | null | undefined) {
  if (!area) return '-'
  return new Intl.NumberFormat('ar-SA', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  }).format(area) + ' م²'
}

function formatDateTime(dateString: string | null | undefined) {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return dateString
  }
}
</script>
