<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ t('tenants.title') }}
          </h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            {{ t('tenants.subtitle') }}
          </p>
        </div>
        <UButton
          size="lg"
          @click="navigateToCreate"
        >
          <template #leading>
            <UIcon name="i-heroicons-plus" />
          </template>
          {{ t('tenants.addTenant') }}
        </UButton>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.stats.total') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ tenants.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-building-office-2" class="w-12 h-12 text-blue-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.stats.active') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
                {{ activeTenants.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.stats.inactive') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
                {{ inactiveTenants.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-x-circle" class="w-12 h-12 text-red-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('tenants.stats.totalUsers') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
                {{ totalUsers }}
              </p>
            </div>
            <UIcon name="i-heroicons-users" class="w-12 h-12 text-purple-500" />
          </div>
        </UCard>
      </div>

      <!-- Tenants Table -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('tenants.list') }}
            </h2>
            <div class="flex items-center gap-3">
              <UInput
                v-model="searchQuery"
                :placeholder="t('common.search')"
                icon="i-heroicons-magnifying-glass"
                size="sm"
              />
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-arrow-path"
                :loading="isLoading"
                @click="fetchTenants"
              >
                {{ t('common.refresh') }}
              </UButton>
            </div>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="isLoading && tenants.length === 0" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
          <UButton @click="fetchTenants">
            {{ t('common.retry') }}
          </UButton>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredTenants.length === 0 && !searchQuery" class="text-center py-12">
          <UIcon name="i-heroicons-building-office-2" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('tenants.noTenants') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {{ t('tenants.noTenantsMessage') }}
          </p>
          <UButton @click="navigateToCreate">
            <template #leading>
              <UIcon name="i-heroicons-plus" />
            </template>
            {{ t('tenants.createFirstTenant') }}
          </UButton>
        </div>

        <!-- No Search Results -->
        <div v-else-if="filteredTenants.length === 0 && searchQuery" class="text-center py-12">
          <UIcon name="i-heroicons-magnifying-glass" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('common.noResults') }}
          </p>
        </div>

        <!-- Data Table -->
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.name') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.slug') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.status') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.users') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.createdAt') }}
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('tenants.table.actions') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="tenant in paginatedTenants"
                :key="tenant.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <!-- Name & Description -->
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ tenant.name }}
                  </div>
                  <div v-if="tenant.description" class="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                    {{ tenant.description }}
                  </div>
                </td>

                <!-- Slug -->
                <td class="px-6 py-4">
                  <code class="px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-gray-800 rounded">
                    {{ tenant.slug }}
                  </code>
                </td>

                <!-- Status -->
                <td class="px-6 py-4">
                  <UBadge
                    :color="tenant.is_active ? 'green' : 'red'"
                    variant="subtle"
                  >
                    {{ tenant.is_active ? t('common.active') : t('common.inactive') }}
                  </UBadge>
                </td>

                <!-- Users -->
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ tenant.users_count ?? 0 }} / {{ tenant.max_users }}
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                    <div
                      class="bg-blue-600 h-1.5 rounded-full"
                      :style="{ width: `${Math.min(((tenant.users_count ?? 0) / tenant.max_users) * 100, 100)}%` }"
                    />
                  </div>
                </td>

                <!-- Created At -->
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(tenant.created_at) }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right text-sm font-medium">
                  <div class="flex items-center justify-end gap-2">
                    <UButton
                      size="xs"
                      color="green"
                      variant="ghost"
                      icon="i-heroicons-eye"
                      :title="t('common.view')"
                      @click="navigateToView(tenant.id)"
                    />
                    <UButton
                      size="xs"
                      color="purple"
                      variant="ghost"
                      icon="i-heroicons-cube"
                      :title="t('tenants.assignService.button')"
                      @click="openAssignServiceModal(tenant)"
                    />
                    <UButton
                      size="xs"
                      color="blue"
                      variant="ghost"
                      icon="i-heroicons-users"
                      :title="t('tenants.manageUsers')"
                      @click="navigateToUsers(tenant.id)"
                    />
                    <UButton
                      size="xs"
                      color="gray"
                      variant="ghost"
                      icon="i-heroicons-pencil"
                      :title="t('common.edit')"
                      @click="navigateToEdit(tenant.id)"
                    />
                    <UButton
                      size="xs"
                      :color="tenant.is_active ? 'yellow' : 'green'"
                      variant="ghost"
                      :icon="tenant.is_active ? 'i-heroicons-pause' : 'i-heroicons-play'"
                      :title="tenant.is_active ? t('common.deactivate') : t('common.activate')"
                      @click="handleToggleActive(tenant)"
                    />
                    <UButton
                      size="xs"
                      color="red"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      :title="t('common.delete')"
                      @click="handleDelete(tenant)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <template v-if="totalPages > 1" #footer>
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ t('common.showingResults', { from: startIndex + 1, to: endIndex, total: filteredTenants.length }) }}
            </div>
            <div class="flex items-center gap-2">
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-chevron-left"
                :disabled="currentPage === 1"
                @click="currentPage--"
              />
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-chevron-right"
                :disabled="currentPage === totalPages"
                @click="currentPage++"
              />
            </div>
          </div>
        </template>
      </UCard>
    </div>

    <!-- Assign Service Modal -->
    <AssignServiceModal
      v-model="isAssignServiceModalOpen"
      :tenant="selectedTenant"
      @success="handleServiceAssigned"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenants } from '@/composables/useTenants'
import type { Tenant } from '~/types/tenant'
import AssignServiceModal from '@/components/tenants/AssignServiceModal.vue'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const router = useRouter()
const { t } = useI18n()

const {
  tenants,
  activeTenants,
  inactiveTenants,
  totalUsers,
  isLoading,
  error,
  fetchTenants,
  toggleActive,
  deleteTenant
} = useTenants()

// Search and pagination
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Assign Service Modal
const isAssignServiceModalOpen = ref(false)
const selectedTenant = ref<{ id: number; name: string; slug: string } | null>(null)

// Filtered tenants based on search
const filteredTenants = computed(() => {
  if (!searchQuery.value) {
    return tenants.value
  }

  const query = searchQuery.value.toLowerCase()
  return tenants.value.filter(tenant =>
    tenant.name.toLowerCase().includes(query) ||
    tenant.slug.toLowerCase().includes(query) ||
    tenant.description?.toLowerCase().includes(query)
  )
})

// Pagination
const totalPages = computed(() => 
  Math.ceil(filteredTenants.value.length / itemsPerPage)
)

const startIndex = computed(() => 
  (currentPage.value - 1) * itemsPerPage
)

const endIndex = computed(() => 
  Math.min(startIndex.value + itemsPerPage, filteredTenants.value.length)
)

const paginatedTenants = computed(() => 
  filteredTenants.value.slice(startIndex.value, endIndex.value)
)

// Format date
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

// Navigation
function navigateToCreate() {
  router.push('/tenants/create')
}

function navigateToView(id: number) {
  router.push(`/tenants/${id}`)
}

function navigateToEdit(id: number) {
  router.push(`/tenants/${id}/edit`)
}

function navigateToUsers(id: number) {
  router.push(`/tenants/${id}/users`)
}

// Toggle active status
async function handleToggleActive(tenant: Tenant) {
  const confirmed = confirm(
    tenant.is_active
      ? t('tenants.confirmDeactivate')
      : t('tenants.confirmActivate')
  )

  if (confirmed) {
    await toggleActive(tenant.id)
  }
}

// Delete tenant
async function handleDelete(tenant: Tenant) {
  const confirmed = confirm(t('tenants.confirmDelete', { name: tenant.name }))

  if (confirmed) {
    await deleteTenant(tenant.id)
  }
}

// Assign Service Modal handlers
function openAssignServiceModal(tenant: Tenant) {
  selectedTenant.value = {
    id: tenant.id,
    name: tenant.name,
    slug: tenant.slug
  }
  isAssignServiceModalOpen.value = true
}

function handleServiceAssigned() {
  // Optionally refresh tenants list or show success message
  console.log('Service assigned successfully')
}

// Reset pagination when search changes
watch(searchQuery, () => {
  currentPage.value = 1
})

// Load tenants on mount
onMounted(() => {
  fetchTenants()
})
</script>
