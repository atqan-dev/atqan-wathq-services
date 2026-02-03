<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/employees')"
        >
          {{ t('employees.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ employeeData?.name || 'Loading...' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ t('employees.subtitle') }}
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
          {{ t('employees.view.edit') }}
        </UButton>
        
        <!-- Export Dropdown -->
        <UDropdown :items="exportMenuItems" :popper="{ placement: 'bottom-end' }">
          <UButton
            icon="i-heroicons-arrow-down-tray"
            color="primary"
            trailing-icon="i-heroicons-chevron-down"
          >
            {{ t('employees.view.export') }}
          </UButton>
        </UDropdown>

        <!-- Print Button -->
        <UButton
          icon="i-heroicons-printer"
          color="gray"
          variant="outline"
          @click="handlePrint"
        >
          {{ t('employees.view.print') }}
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
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('employees.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="employeeData" class="space-y-6">
      <!-- Overview Cards Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.view.fields.employeeId') }}</p>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">#{{ employeeData.employee_id }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.view.fields.nationality') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ employeeData.nationality || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.view.fields.workingMonths') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{{ employeeData.working_months || 0 }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.view.sections.employmentDetails') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ employeeData.employment_details?.length || 0 }}</p>
          </div>
        </UCard>
      </div>

      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-user" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('employees.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('employees.view.fields.employeeId')" :value="employeeData.employee_id" />
          <InfoField :label="t('employees.view.fields.name')" :value="employeeData.name" />
          <InfoField :label="t('employees.view.fields.nationality')" :value="employeeData.nationality" />
          <InfoField :label="t('employees.view.fields.workingMonths')">
            <span v-if="employeeData.working_months">
              {{ employeeData.working_months }} {{ t('employees.view.fields.months') }}
            </span>
            <span v-else>-</span>
          </InfoField>
        </div>
      </UCard>

      <!-- Employment Details Section -->
      <UCard v-if="employeeData.employment_details && employeeData.employment_details.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-briefcase" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('employees.view.sections.employmentDetails') }}</h2>
            </div>
            <UBadge color="purple" variant="subtle">{{ employeeData.employment_details.length }}</UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div 
            v-for="(employment, index) in employeeData.employment_details" 
            :key="employment.employment_id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-semibold text-gray-900 dark:text-white">
                {{ t('employees.view.sections.employmentDetails') }} #{{ index + 1 }}
              </h3>
              <UBadge 
                :color="employment.status === 'Active' ? 'green' : 'gray'" 
                variant="subtle"
              >
                {{ employment.status || 'Unknown' }}
              </UBadge>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField :label="t('employees.view.fields.employer')" :value="employment.employer" />
              <InfoField :label="t('employees.view.fields.status')" :value="employment.status" />
              <InfoField :label="t('employees.view.fields.basicWage')">
                <span class="font-mono">{{ formatCurrency(employment.basic_wage) }}</span>
              </InfoField>
              <InfoField :label="t('employees.view.fields.housingAllowance')">
                <span class="font-mono">{{ formatCurrency(employment.housing_allowance) }}</span>
              </InfoField>
              <InfoField :label="t('employees.view.fields.otherAllowance')">
                <span class="font-mono">{{ formatCurrency(employment.other_allowance) }}</span>
              </InfoField>
              <InfoField :label="t('employees.view.fields.fullWage')">
                <span class="font-mono font-semibold text-green-600 dark:text-green-400">
                  {{ formatCurrency(employment.full_wage) }}
                </span>
              </InfoField>
            </div>

            <!-- Wage Breakdown Chart -->
            <div v-if="employment.basic_wage || employment.housing_allowance || employment.other_allowance" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Wage Breakdown</p>
              <div class="flex gap-2">
                <div 
                  v-if="employment.basic_wage"
                  class="flex-1 bg-blue-500 h-8 rounded flex items-center justify-center text-white text-xs font-medium"
                  :style="{ width: getPercentage(employment.basic_wage, employment.full_wage) + '%' }"
                >
                  Basic: {{ formatCurrency(employment.basic_wage) }}
                </div>
                <div 
                  v-if="employment.housing_allowance"
                  class="flex-1 bg-green-500 h-8 rounded flex items-center justify-center text-white text-xs font-medium"
                  :style="{ width: getPercentage(employment.housing_allowance, employment.full_wage) + '%' }"
                >
                  Housing: {{ formatCurrency(employment.housing_allowance) }}
                </div>
                <div 
                  v-if="employment.other_allowance"
                  class="flex-1 bg-purple-500 h-8 rounded flex items-center justify-center text-white text-xs font-medium"
                  :style="{ width: getPercentage(employment.other_allowance, employment.full_wage) + '%' }"
                >
                  Other: {{ formatCurrency(employment.other_allowance) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Audit Info Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('employees.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('employees.view.fields.createdAt')" :value="formatDateTime(employeeData.created_at)" />
          <InfoField :label="t('employees.view.fields.updatedAt')" :value="formatDateTime(employeeData.updated_at)" />
          <InfoField :label="t('employees.view.fields.createdBy')" :value="employeeData.created_by" />
          <InfoField :label="t('employees.view.fields.updatedBy')" :value="employeeData.updated_by" />
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useEmployeeExport } from '@/composables/useEmployeeExport'
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { 
  exportToPDF, 
  exportToJSON, 
  exportToCSV, 
  exportToExcel, 
  previewEmployee,
  printEmployee 
} = useEmployeeExport()

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const loading = ref(true)
const error = ref<string | null>(null)
const employeeData = ref<any>(null)

const id = computed(() => route.params.id)

onMounted(() => {
  fetchEmployeeData()
})

function getMockEmployeeData(id: number) {
  const now = new Date().toISOString()
  
  return {
    employee_id: id,
    name: 'أحمد محمد علي',
    nationality: 'Saudi',
    working_months: 36,
    created_at: now,
    updated_at: now,
    created_by: 1,
    updated_by: 1,
    employment_details: [
      {
        employment_id: 1,
        employee_id: id,
        employer: 'شركة الرياض للتقنية',
        status: 'Active',
        basic_wage: 8000.00,
        housing_allowance: 2000.00,
        other_allowance: 500.00,
        full_wage: 10500.00,
        created_at: now,
        updated_at: now
      },
      {
        employment_id: 2,
        employee_id: id,
        employer: 'Jeddah Tech Solutions',
        status: 'Inactive',
        basic_wage: 6000.00,
        housing_allowance: 1500.00,
        other_allowance: 300.00,
        full_wage: 7800.00,
        created_at: now,
        updated_at: now
      }
    ]
  }
}

async function fetchEmployeeData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching employee data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/employees/${id.value}`)
    console.log('API Response:', response)
    
    if (response) {
      employeeData.value = response
      console.log('Employee data loaded from API:', employeeData.value)
    } else {
      throw new Error('No data returned from API')
    }
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    error.value = err.message || 'Failed to load employee data'
    employeeData.value = getMockEmployeeData(Number(id.value))
    console.log('Using mock employee data:', employeeData.value)
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
  console.log('Edit employee:', employeeData.value)
}

async function handleExportPDF() {
  if (!employeeData.value) return
  await exportToPDF(employeeData.value.employee_id, employeeData.value.name)
}

async function handleExportJSON() {
  if (!employeeData.value) return
  await exportToJSON(employeeData.value.employee_id, employeeData.value.name)
}

async function handleExportCSV() {
  if (!employeeData.value) return
  await exportToCSV(employeeData.value.employee_id, employeeData.value.name)
}

async function handleExportExcel() {
  if (!employeeData.value) return
  await exportToExcel(employeeData.value.employee_id, employeeData.value.name)
}

function handlePreview() {
  if (!employeeData.value) return
  previewEmployee(employeeData.value.employee_id)
}

function handlePrint() {
  if (!employeeData.value) return
  printEmployee(employeeData.value.employee_id)
}

function formatCurrency(amount: number | string | null | undefined) {
  if (!amount) return '-'
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(numAmount)) return '-'
  
  return new Intl.NumberFormat('ar-SA', { 
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 2
  }).format(numAmount)
}

function getPercentage(part: number | string | null | undefined, total: number | string | null | undefined) {
  if (!part || !total) return 0
  const numPart = typeof part === 'string' ? parseFloat(part) : part
  const numTotal = typeof total === 'string' ? parseFloat(total) : total
  if (isNaN(numPart) || isNaN(numTotal) || numTotal === 0) return 0
  return Math.round((numPart / numTotal) * 100)
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
