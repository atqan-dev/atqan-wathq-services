<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Tenant Info Card -->
      <TenantInfoCard
        :tenant="tenant"
        :is-loading="isLoadingTenant"
        :error="tenantError"
        :show-actions="true"
        @edit="navigateToEdit"
        @back="navigateBack"
      />

      <!-- Tenant Services Section -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('tenants.services.title') }}
              </h2>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.subtitle') }}
              </p>
            </div>
            <UButton
              color="purple"
              icon="i-heroicons-plus"
              @click="openAssignServiceModal"
            >
              {{ t('tenants.assignService.button') }}
            </UButton>
          </div>
        </template>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-cube" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.stats.total') }}
              </span>
            </div>
            <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
              {{ stats.total_services }}
            </p>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-green-600 dark:text-green-400" />
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.stats.active') }}
              </span>
            </div>
            <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
              {{ stats.active_services }}
            </p>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.stats.approved') }}
              </span>
            </div>
            <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
              {{ stats.approved_services }}
            </p>
          </div>

          <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.stats.pending') }}
              </span>
            </div>
            <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
              {{ stats.pending_approval }}
            </p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoadingServices" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>

        <!-- Error State -->
        <div v-else-if="servicesError" class="flex items-center justify-center gap-3 py-12 text-red-600 dark:text-red-400">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" />
          <span>{{ servicesError }}</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="services.length === 0" class="flex flex-col items-center justify-center py-12">
          <UIcon name="i-heroicons-cube" class="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('tenants.services.empty.title') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {{ t('tenants.services.empty.description') }}
          </p>
          <UButton
            color="purple"
            icon="i-heroicons-plus"
            @click="openAssignServiceModal"
          >
            {{ t('tenants.assignService.button') }}
          </UButton>
        </div>

        <!-- Services Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.services.table.service') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.services.table.status') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.services.table.approval') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.services.table.usage') }}
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('common.actions') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="service in services"
                :key="service.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <ServiceRow
                  :service="service"
                  @approve="handleApprove"
                  @toggle-active="handleToggleActive"
                  @delete="handleDelete"
                />
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Quick Actions Section -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <UCard class="hover:shadow-lg transition-shadow cursor-pointer" @click="navigateToUsers">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <UIcon name="i-heroicons-users" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 class="font-medium text-gray-900 dark:text-white">
                {{ t('tenants.manageUsers') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.quickActions.users') }}
              </p>
            </div>
          </div>
        </UCard>

        <UCard class="hover:shadow-lg transition-shadow cursor-pointer" @click="navigateToEdit">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <UIcon name="i-heroicons-pencil" class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h3 class="font-medium text-gray-900 dark:text-white">
                {{ t('common.edit') }} {{ t('tenants.title') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.quickActions.edit') }}
              </p>
            </div>
          </div>
        </UCard>

        <UCard class="hover:shadow-lg transition-shadow cursor-pointer" @click="openAssignServiceModal">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <UIcon name="i-heroicons-cube" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 class="font-medium text-gray-900 dark:text-white">
                {{ t('tenants.assignService.button') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('tenants.services.quickActions.assign') }}
              </p>
            </div>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Assign Service Modal -->
    <AssignServiceModal
      v-if="tenant"
      v-model="isAssignServiceModalOpen"
      :tenant="{ id: tenant.id, name: tenant.name, slug: tenant.slug }"
      @assigned="handleServiceAssigned"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from '~/composables/useI18n'
import { useTenants } from '~/composables/useTenants'
import { useTenantServices } from '~/composables/useTenantServices'
import { useConfirm } from '~/composables/useConfirm'
import TenantInfoCard from '~/components/tenants/TenantInfoCard.vue'
import ServiceRow from '~/components/tenant-services/ServiceRow.vue'
import AssignServiceModal from '~/components/tenants/AssignServiceModal.vue'
import type { TenantService } from '~/types/tenant-service'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { confirmDelete } = useConfirm()

// Get tenant ID from route
const tenantId = computed(() => Number(route.params.id))

// Tenant composable
const {
  currentTenant: tenant,
  isLoading: isLoadingTenant,
  error: tenantError,
  fetchTenant
} = useTenants()

// Tenant Services composable
const {
  services,
  stats,
  isLoading: isLoadingServices,
  error: servicesError,
  fetchServices,
  approveService,
  toggleActive,
  deleteService
} = useTenantServices()

// Assign Service Modal
const isAssignServiceModalOpen = ref(false)

// Navigation functions
function navigateBack() {
  router.push('/tenants')
}

function navigateToEdit() {
  router.push(`/tenants/${tenantId.value}/edit`)
}

function navigateToUsers() {
  router.push(`/tenants/${tenantId.value}/users`)
}

// Service actions
async function handleApprove(service: TenantService) {
  const confirmed = await confirmDelete(
    t('tenants.services.confirmApprove', { name: service.service.name }),
    t('tenants.services.approveTitle')
  )

  if (confirmed) {
    const success = await approveService(service.id, service.tenant_id)
    if (success) {
      await fetchServices({ tenant_id: tenantId.value })
    }
  }
}

async function handleToggleActive(service: TenantService) {
  const confirmed = await confirmDelete(
    service.is_active
      ? t('tenants.services.confirmDeactivate', { name: service.service.name })
      : t('tenants.services.confirmActivate', { name: service.service.name }),
    t('common.confirm')
  )

  if (confirmed) {
    const success = await toggleActive(service.id)
    if (success) {
      await fetchServices({ tenant_id: tenantId.value })
    }
  }
}

async function handleDelete(service: TenantService) {
  const confirmed = await confirmDelete(
    t('tenants.services.confirmDelete', { name: service.service.name })
  )

  if (confirmed) {
    const success = await deleteService(service.id)
    if (success) {
      await fetchServices({ tenant_id: tenantId.value })
    }
  }
}

// Modal handlers
function openAssignServiceModal() {
  isAssignServiceModalOpen.value = true
}

async function handleServiceAssigned() {
  isAssignServiceModalOpen.value = false
  await fetchServices({ tenant_id: tenantId.value })
}

// Load data on mount
onMounted(async () => {
  await fetchTenant(tenantId.value)
  await fetchServices({ tenant_id: tenantId.value })
})
</script>
