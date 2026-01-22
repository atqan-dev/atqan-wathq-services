<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          color="gray"
          variant="ghost"
          @click="router.push('/wathq-data/power-of-attorney')"
        >
          {{ t('powerOfAttorney.view.back') }}
        </UButton>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ poaData?.code || 'Loading...' }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ t('powerOfAttorney.subtitle') }}
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
          {{ t('powerOfAttorney.view.edit') }}
        </UButton>
        <UButton
          icon="i-heroicons-arrow-down-tray"
          color="primary"
          @click="handleExport"
        >
          {{ t('powerOfAttorney.view.export') }}
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
          <h3 class="font-semibold text-red-900 dark:text-red-200">{{ t('powerOfAttorney.view.errorLoading') }}</h3>
          <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="poaData" class="space-y-6">
      <!-- Overview Cards Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.view.fields.code') }}</p>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ poaData.code || '-' }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.view.fields.status') }}</p>
            <p class="text-2xl font-bold mt-1" :class="poaData.status?.toLowerCase() === 'active' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ poaData.status || '-' }}
            </p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.view.sections.principals') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ poaData.principals?.length || 0 }}</p>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.view.sections.agents') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ poaData.agents?.length || 0 }}</p>
          </div>
        </UCard>
      </div>

      <!-- Main Information Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-check" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.mainInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InfoField :label="t('powerOfAttorney.view.fields.id')" :value="poaData.id" />
          <InfoField :label="t('powerOfAttorney.view.fields.code')" :value="poaData.code" />
          <InfoField :label="t('powerOfAttorney.view.fields.status')" :value="poaData.status" />
          <InfoField :label="t('powerOfAttorney.view.fields.attorneyType')" :value="poaData.attorney_type" />
          <InfoField :label="t('powerOfAttorney.view.fields.locationName')" :value="poaData.location_name" />
          <InfoField :label="t('powerOfAttorney.view.fields.locationId')" :value="poaData.location_id" />
        </div>
      </UCard>

      <!-- Dates Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.dates') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('powerOfAttorney.view.fields.issueHijriDate')" :value="poaData.issue_hijri_date" />
          <InfoField :label="t('powerOfAttorney.view.fields.issueGregDate')" :value="formatDate(poaData.issue_greg_date)" />
          <InfoField :label="t('powerOfAttorney.view.fields.expiryHijriDate')" :value="poaData.expiry_hijri_date" />
          <InfoField :label="t('powerOfAttorney.view.fields.expiryGregDate')" :value="formatDate(poaData.expiry_greg_date)" />
        </div>
      </UCard>

      <!-- Behavior Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-users" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.behavior') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InfoField :label="t('powerOfAttorney.view.fields.agentsBehaviorAr')" :value="poaData.agents_behavior_ar" />
          <InfoField :label="t('powerOfAttorney.view.fields.agentsBehaviorEn')" :value="poaData.agents_behavior_en" />
        </div>
      </UCard>

      <!-- Document Text Card -->
      <UCard v-if="poaData.document_text">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.documentText') }}</h2>
          </div>
        </template>

        <div class="prose dark:prose-invert max-w-none">
          <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ poaData.document_text }}</p>
        </div>
      </UCard>

      <!-- Audit Info Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary-500" />
            <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.auditInfo') }}</h2>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <InfoField :label="t('powerOfAttorney.view.fields.createdAt')" :value="formatDateTime(poaData.created_at)" />
          <InfoField :label="t('powerOfAttorney.view.fields.updatedAt')" :value="formatDateTime(poaData.updated_at)" />
          <InfoField :label="t('powerOfAttorney.view.fields.createdBy')" :value="poaData.created_by" />
          <InfoField :label="t('powerOfAttorney.view.fields.updatedBy')" :value="poaData.updated_by" />
        </div>
      </UCard>

      <!-- Allowed Actors Section -->
      <UCard v-if="poaData.allowed_actors && poaData.allowed_actors.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-user-group" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.allowedActors') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ poaData.allowed_actors.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.name') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.identityNo') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.typeName') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.crNumber') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(actor, index) in poaData.allowed_actors" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ actor.name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ actor.identity_no || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ actor.type_name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ actor.cr_number || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Principals Section -->
      <UCard v-if="poaData.principals && poaData.principals.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-user" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.principals') }}</h2>
            </div>
            <UBadge color="purple" variant="subtle">{{ poaData.principals.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.name') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.principalIdentityId') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.birthday') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.sefaName') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(principal, index) in poaData.principals" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ principal.name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ principal.principal_identity_id || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ formatDate(principal.birthday) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ principal.sefa_name || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Agents Section -->
      <UCard v-if="poaData.agents && poaData.agents.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-user-circle" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.agents') }}</h2>
            </div>
            <UBadge color="blue" variant="subtle">{{ poaData.agents.length }}</UBadge>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.name') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.agentIdentityId') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.birthday') }}
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('powerOfAttorney.view.fields.sefaName') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(agent, index) in poaData.agents" :key="index" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">{{ agent.name || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-mono">{{ agent.agent_identity_id || '-' }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ formatDate(agent.birthday) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ agent.sefa_name || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Text List Items Section -->
      <UCard v-if="poaData.text_list_items && poaData.text_list_items.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-list-bullet" class="w-5 h-5 text-primary-500" />
              <h2 class="text-lg font-semibold">{{ t('powerOfAttorney.view.sections.textListItems') }}</h2>
            </div>
            <UBadge color="primary" variant="subtle">{{ poaData.text_list_items.length }}</UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="(item, index) in poaData.text_list_items"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="flex items-start gap-3">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 text-xs font-medium">
                {{ index + 1 }}
              </span>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <UBadge v-if="item.item_type" color="gray" variant="soft">{{ item.item_type }}</UBadge>
                  <span v-if="item.list_item_id" class="text-xs text-gray-500">ID: {{ item.list_item_id }}</span>
                </div>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ item.text_content || '-' }}</p>
              </div>
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
import InfoField from '~/components/ui/InfoField.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

// Define page metadata
definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// State
const loading = ref(true)
const error = ref<string | null>(null)
const poaData = ref<any>(null)

// Get ID from route
const id = computed(() => route.params.id)

// Fetch data on mount
onMounted(() => {
  fetchPoaData()
})

// Mock data generator
function getMockPoaData(id: number) {
  const now = new Date().toISOString()
  const futureDate = new Date()
  futureDate.setFullYear(futureDate.getFullYear() + 1)
  
  return {
    id: id,
    code: `POA-2024-${String(id).padStart(3, '0')}`,
    status: 'Active',
    issue_hijri_date: '1445/06/15',
    issue_greg_date: '2024-01-15',
    expiry_hijri_date: '1446/06/15',
    expiry_greg_date: futureDate.toISOString().split('T')[0],
    attorney_type: 'General',
    location_id: 1,
    location_name: 'Riyadh',
    agents_behavior_ar: 'منفردين',
    agents_behavior_en: 'Individual',
    document_text: 'This is a sample power of attorney document text. It contains the full legal text and terms of the power of attorney agreement between the principals and agents.',
    created_at: now,
    updated_at: now,
    created_by: 1,
    updated_by: 1,
    allowed_actors: [
      {
        id: 1,
        name: 'شركة التقنية المتقدمة',
        identity_no: '1234567890',
        type_name: 'شركة',
        cr_number: '1010711252',
        national_number: '7001234567'
      },
      {
        id: 2,
        name: 'مؤسسة الخدمات',
        identity_no: '0987654321',
        type_name: 'مؤسسة',
        cr_number: '1010711253',
        national_number: '7001234568'
      }
    ],
    principals: [
      {
        id: 1,
        name: 'أحمد محمد علي',
        principal_identity_id: '1234567890',
        birthday: '1980-05-15',
        sefa_id: 1,
        sefa_name: 'مالك'
      },
      {
        id: 2,
        name: 'سارة علي حسن',
        principal_identity_id: '0987654321',
        birthday: '1985-08-20',
        sefa_id: 2,
        sefa_name: 'شريك'
      }
    ],
    agents: [
      {
        id: 1,
        name: 'خالد سعيد أحمد',
        agent_identity_id: '1122334455',
        birthday: '1975-03-10',
        sefa_id: 3,
        sefa_name: 'وكيل'
      }
    ],
    text_list_items: [
      {
        id: 1,
        list_item_id: 101,
        text_content: 'التوقيع على جميع العقود والاتفاقيات نيابة عن الموكل',
        item_type: 'صلاحية'
      },
      {
        id: 2,
        list_item_id: 102,
        text_content: 'إجراء المعاملات البنكية والمالية',
        item_type: 'صلاحية'
      },
      {
        id: 3,
        list_item_id: 103,
        text_content: 'تمثيل الموكل أمام الجهات الحكومية',
        item_type: 'صلاحية'
      }
    ]
  }
}

async function fetchPoaData() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching POA data for ID:', id.value)
    const response = await $fetch(`/api/v1/wathq/power-of-attorney/${id.value}`)
    console.log('API Response:', response)
    
    // API returns the POA object directly with all relations
    if (response) {
      poaData.value = response
      console.log('POA Data loaded from API:', poaData.value)
    } else {
      throw new Error('No data returned from API')
    }
  } catch (err: any) {
    console.warn('API call failed, using mock data:', err)
    error.value = err.message || 'Failed to load power of attorney data'
    // Fallback to mock data for development
    poaData.value = getMockPoaData(Number(id.value))
    console.log('Using mock POA data:', poaData.value)
  } finally {
    loading.value = false
  }
}

function handleEdit() {
  console.log('Edit POA:', poaData.value)
  // TODO: Implement edit functionality
}

function handleExport() {
  console.log('Export POA:', poaData.value)
  // TODO: Implement export functionality
}

function formatDate(dateString: string | null | undefined) {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
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
