<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/national-addresses')"
        >
          {{ t('nationalAddresses.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ addressData?.title || addressData?.pk_address_id || 'Loading...' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ t('nationalAddresses.subtitle') }}
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
          {{ t('nationalAddresses.view.edit') }}
        </UButton>
        
        <!-- Export Dropdown -->
        <UDropdown :items="exportMenuItems" :popper="{ placement: 'bottom-end' }">
          <UButton
            icon="i-heroicons-arrow-down-tray"
            color="primary"
            trailing-icon="i-heroicons-chevron-down"
          >
            {{ t('nationalAddresses.view.export') }}
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
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('nationalAddresses.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="addressData" class="space-y-6">
      <!-- Overview Cards Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.view.fields.pkAddressId') }}</p>
            <p class="text-lg font-bold text-primary-600 dark:text-primary-400 mt-1 font-mono">{{ addressData.pk_address_id || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.view.fields.city') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ addressData.city || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.view.fields.postCode') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1 font-mono">{{ addressData.post_code || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.view.fields.status') }}</p>
            <UBadge 
              :color="addressData.status?.toLowerCase() === 'active' ? 'green' : 'red'" 
              variant="subtle"
              size="lg"
              class="mt-1"
            >
              {{ addressData.status || '-' }}
            </UBadge>
          </div>
        </UCard>
      </div>

      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('nationalAddresses.view.fields.pkAddressId')" :value="addressData.pk_address_id" />
          <InfoField :label="t('nationalAddresses.view.fields.title')" :value="addressData.title" />
          <InfoField :label="t('nationalAddresses.view.fields.status')" :value="addressData.status" />
          <InfoField :label="t('nationalAddresses.view.fields.isPrimaryAddress')">
            <UBadge :color="addressData.is_primary_address ? 'green' : 'gray'" variant="subtle">
              {{ addressData.is_primary_address ? t('nationalAddresses.view.fields.yes') : t('nationalAddresses.view.fields.no') }}
            </UBadge>
          </InfoField>
        </div>
      </UCard>

      <!-- Address Details Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-map" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.addressDetails') }}</h2>
          </div>
        </template>

        <div class="space-y-4">
          <InfoField :label="t('nationalAddresses.view.fields.address')" :value="addressData.address" />
          <InfoField :label="t('nationalAddresses.view.fields.address2')" :value="addressData.address2" />
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
            <InfoField :label="t('nationalAddresses.view.fields.buildingNumber')" :value="addressData.building_number" />
            <InfoField :label="t('nationalAddresses.view.fields.street')" :value="addressData.street" />
            <InfoField :label="t('nationalAddresses.view.fields.unitNumber')" :value="addressData.unit_number" />
            <InfoField :label="t('nationalAddresses.view.fields.additionalNumber')" :value="addressData.additional_number" />
          </div>
        </div>
      </UCard>

      <!-- Location Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-map-pin" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.locationInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('nationalAddresses.view.fields.district')" :value="addressData.district" />
          <InfoField :label="t('nationalAddresses.view.fields.districtId')" :value="addressData.district_id" />
          <InfoField :label="t('nationalAddresses.view.fields.city')" :value="addressData.city" />
          <InfoField :label="t('nationalAddresses.view.fields.cityId')" :value="addressData.city_id" />
          <InfoField :label="t('nationalAddresses.view.fields.postCode')" :value="addressData.post_code" />
        </div>
      </UCard>

      <!-- Coordinates Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-globe-alt" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.coordinates') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoField :label="t('nationalAddresses.view.fields.latitude')">
            <span class="font-mono">{{ formatCoordinate(addressData.latitude) }}</span>
          </InfoField>
          <InfoField :label="t('nationalAddresses.view.fields.longitude')">
            <span class="font-mono">{{ formatCoordinate(addressData.longitude) }}</span>
          </InfoField>
        </div>

        <!-- Interactive Map (if coordinates available) -->
        <div v-if="addressData.latitude && addressData.longitude" class="mt-4">
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <div id="map" class="w-full h-96"></div>
          </div>
          <div class="mt-2 flex items-center justify-between text-sm">
            <p class="text-gray-600 dark:text-gray-400">
              Coordinates: {{ formatCoordinate(addressData.latitude) }}, {{ formatCoordinate(addressData.longitude) }}
            </p>
            <a 
              :href="`https://www.google.com/maps?q=${addressData.latitude},${addressData.longitude}`"
              target="_blank"
              class="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
            >
              <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4" />
              Open in Google Maps
            </a>
          </div>
        </div>
      </UCard>

      <!-- Administrative Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-building-library" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.administrativeInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoField :label="t('nationalAddresses.view.fields.regionName')" :value="addressData.region_name" />
          <InfoField :label="t('nationalAddresses.view.fields.regionId')" :value="addressData.region_id" />
        </div>

        <div v-if="addressData.restriction" class="mt-4">
          <InfoField :label="t('nationalAddresses.view.fields.restriction')">
            <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
              <p class="text-sm text-yellow-800 dark:text-yellow-200">{{ addressData.restriction }}</p>
            </div>
          </InfoField>
        </div>
      </UCard>

      <!-- Audit Info Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('nationalAddresses.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('nationalAddresses.view.fields.createdAt')" :value="formatDateTime(addressData.created_at)" />
          <InfoField :label="t('nationalAddresses.view.fields.updatedAt')" :value="formatDateTime(addressData.updated_at)" />
          <InfoField :label="t('nationalAddresses.view.fields.createdBy')" :value="addressData.created_by" />
          <InfoField :label="t('nationalAddresses.view.fields.updatedBy')" :value="addressData.updated_by" />
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useNationalAddressExport } from '@/composables/useNationalAddressExport'
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { 
  exportToPDF, 
  exportToJSON, 
  exportToCSV, 
  exportToExcel, 
  previewAddress,
  printAddress 
} = useNationalAddressExport()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const loading = ref(true)
const error = ref<string | null>(null)
const addressData = ref<any>(null)
let map: any = null

const id = computed(() => route.params.id)

onMounted(() => {
  fetchAddressData()
  loadLeafletCSS()
})

function getMockAddressData(id: string) {
  const now = new Date().toISOString()
  
  return {
    pk_address_id: id,
    title: `National Address - ${id}`,
    address: 'King Fahd Road, Al Olaya District',
    address2: 'Tower A, Floor 15, Office 1501',
    latitude: 24.7136,
    longitude: 46.6753,
    building_number: '7890',
    street: 'King Fahd Road',
    district: 'Al Olaya',
    district_id: 'RYD-OLY-001',
    city: 'Riyadh',
    city_id: 'RYD',
    post_code: '12345',
    additional_number: '1234',
    region_name: 'Riyadh Region',
    region_id: 'RG-01',
    is_primary_address: true,
    unit_number: '1501',
    restriction: 'Commercial use only - No residential activities permitted',
    status: 'Active',
    created_at: now,
    updated_at: now,
    created_by: 1,
    updated_by: 1
  }
}

function loadLeafletCSS() {
  if (process.client && !document.getElementById('leaflet-css')) {
    const link = document.createElement('link')
    link.id = 'leaflet-css'
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY='
    link.crossOrigin = ''
    document.head.appendChild(link)
  }
}

async function initializeMap() {
  if (!process.client || !addressData.value?.latitude || !addressData.value?.longitude) {
    return
  }

  await nextTick()

  const mapElement = document.getElementById('map')
  if (!mapElement) return

  try {
    // Dynamically import Leaflet
    const L = await import('leaflet')
    
    // Clear existing map if any
    if (map) {
      map.remove()
    }

    const lat = typeof addressData.value.latitude === 'string' 
      ? parseFloat(addressData.value.latitude) 
      : addressData.value.latitude
    const lng = typeof addressData.value.longitude === 'string' 
      ? parseFloat(addressData.value.longitude) 
      : addressData.value.longitude

    // Initialize map
    map = L.map('map').setView([lat, lng], 15)

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map)

    // Add marker
    const marker = L.marker([lat, lng]).addTo(map)
    
    // Add popup with address info
    const popupContent = `
      <div class="p-2">
        <h3 class="font-semibold text-sm mb-1">${addressData.value.title || 'Address'}</h3>
        <p class="text-xs text-gray-600">${addressData.value.address || ''}</p>
        <p class="text-xs text-gray-500 mt-1">${addressData.value.city || ''}, ${addressData.value.post_code || ''}</p>
      </div>
    `
    marker.bindPopup(popupContent).openPopup()

  } catch (error) {
    console.error('Failed to initialize map:', error)
  }
}

async function fetchAddressData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching address data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/national-addresses/${id.value}`)
    console.log('API Response:', response)
    
    if (response) {
      addressData.value = response
      console.log('Address data loaded from API:', addressData.value)
    } else {
      throw new Error('No data returned from API')
    }
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    error.value = err.message || 'Failed to load address data'
    addressData.value = getMockAddressData(String(id.value))
    console.log('Using mock address data:', addressData.value)
  } finally {
    loading.value = false
    // Initialize map after data is loaded
    await nextTick()
    initializeMap()
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
  console.log('Edit address:', addressData.value)
}

async function handleExportPDF() {
  if (!addressData.value) return
  await exportToPDF(addressData.value.pk_address_id)
}

async function handleExportJSON() {
  if (!addressData.value) return
  await exportToJSON(addressData.value.pk_address_id)
}

async function handleExportCSV() {
  if (!addressData.value) return
  await exportToCSV(addressData.value.pk_address_id)
}

async function handleExportExcel() {
  if (!addressData.value) return
  await exportToExcel(addressData.value.pk_address_id)
}

function handlePreview() {
  if (!addressData.value) return
  previewAddress(addressData.value.pk_address_id)
}

function handlePrint() {
  if (!addressData.value) return
  printAddress(addressData.value.pk_address_id)
}

function formatCoordinate(coord: number | string | null | undefined) {
  if (!coord) return '-'
  const numCoord = typeof coord === 'string' ? parseFloat(coord) : coord
  if (isNaN(numCoord)) return '-'
  return numCoord.toFixed(6)
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
