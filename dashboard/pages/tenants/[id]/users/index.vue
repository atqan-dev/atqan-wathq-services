<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
        <NuxtLink to="/tenants" class="hover:text-blue-600 dark:hover:text-blue-400">
          {{ t('tenants.title') }}
        </NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        <span>{{ t('users.title') }}</span>
      </div>

      <!-- Tenant Info Card -->
      <TenantInfoCard
        :tenant="currentTenant"
        :is-loading="isTenantLoading"
        :error="tenantError"
        :show-actions="true"
        @edit="navigateToEditTenant"
        @back="navigateToTenants"
      />

      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              {{ t('users.title') }}
            </h1>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              {{ t('users.subtitle') }}
            </p>
          </div>
          <UButton
            size="lg"
            @click="navigateToCreate"
          >
            <template #leading>
              <UIcon name="i-heroicons-plus" />
            </template>
            {{ t('users.addUser') }}
          </UButton>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.total') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ users.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-users" class="w-12 h-12 text-blue-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.active') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
                {{ activeUsers.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.inactive') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
                {{ inactiveUsers.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-x-circle" class="w-12 h-12 text-red-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('users.stats.admins') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
                {{ superAdmins.length }}
              </p>
            </div>
            <UIcon name="i-heroicons-shield-check" class="w-12 h-12 text-purple-500" />
          </div>
        </UCard>
      </div>

      <!-- Users Table -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('users.list') }}
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
                @click="fetchUsers"
              >
                {{ t('common.refresh') }}
              </UButton>
            </div>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="isLoading && users.length === 0" class="flex items-center justify-center py-12">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
          <UButton @click="fetchUsers">
            {{ t('common.retry') }}
          </UButton>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredUsers.length === 0 && !searchQuery" class="text-center py-12">
          <UIcon name="i-heroicons-users" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('users.noUsers') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {{ t('users.noUsersMessage') }}
          </p>
          <UButton @click="navigateToCreate">
            <template #leading>
              <UIcon name="i-heroicons-plus" />
            </template>
            {{ t('users.createFirstUser') }}
          </UButton>
        </div>

        <!-- No Search Results -->
        <div v-else-if="filteredUsers.length === 0 && searchQuery" class="text-center py-12">
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
                  {{ t('users.table.name') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('users.table.email') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('users.table.status') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('users.table.role') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('users.table.createdAt') }}
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  {{ t('users.table.actions') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="user in paginatedUsers"
                :key="user.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <!-- Name -->
                <td class="px-6 py-4">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <span class="text-blue-600 dark:text-blue-300 font-medium">
                        {{ user.first_name[0] }}{{ user.last_name[0] }}
                      </span>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">
                        {{ user.first_name }} {{ user.last_name }}
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Email -->
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ user.email }}
                  </div>
                </td>

                <!-- Status -->
                <td class="px-6 py-4">
                  <UBadge
                    :color="user.is_active ? 'green' : 'red'"
                    variant="subtle"
                  >
                    {{ user.is_active ? t('common.active') : t('common.inactive') }}
                  </UBadge>
                </td>

                <!-- Role -->
                <td class="px-6 py-4">
                  <UBadge
                    v-if="user.is_super_admin"
                    color="purple"
                    variant="subtle"
                  >
                    {{ t('users.table.admin') }}
                  </UBadge>
                  <UBadge
                    v-else
                    color="gray"
                    variant="subtle"
                  >
                    {{ t('users.table.user') }}
                  </UBadge>
                </td>

                <!-- Created At -->
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(user.created_at) }}
                </td>

                <!-- Actions -->
                <td class="px-6 py-4 text-right text-sm font-medium">
                  <div class="flex items-center justify-end gap-2">
                    <UButton
                      size="xs"
                      color="gray"
                      variant="ghost"
                      icon="i-heroicons-pencil"
                      @click="navigateToEdit(user.id)"
                    />
                    <UButton
                      size="xs"
                      :color="user.is_active ? 'yellow' : 'green'"
                      variant="ghost"
                      :icon="user.is_active ? 'i-heroicons-pause' : 'i-heroicons-play'"
                      @click="handleToggleActive(user)"
                    />
                    <UButton
                      size="xs"
                      color="red"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      @click="handleDelete(user)"
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
              {{ t('common.showingResults', { from: startIndex + 1, to: endIndex, total: filteredUsers.length }) }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenantUsers } from '@/composables/useTenantUsers'
import { useTenants } from '@/composables/useTenants'
import TenantInfoCard from '@/components/tenants/TenantInfoCard.vue'
import type { User } from '~/types/user'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Get tenant ID from route
const tenantId = computed(() => parseInt(route.params.id as string))

// Tenant info
const {
  currentTenant,
  isLoading: isTenantLoading,
  error: tenantError,
  fetchTenant
} = useTenants()

// Users management
const {
  users,
  activeUsers,
  inactiveUsers,
  superAdmins,
  isLoading,
  error,
  fetchUsers,
  toggleActive,
  deleteUser,
  setTenantId
} = useTenantUsers(tenantId.value)

// Search and pagination
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Filtered users based on search
const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return users.value
  }

  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user =>
    user.first_name.toLowerCase().includes(query) ||
    user.last_name.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query)
  )
})

// Pagination
const totalPages = computed(() => 
  Math.ceil(filteredUsers.value.length / itemsPerPage)
)

const startIndex = computed(() => 
  (currentPage.value - 1) * itemsPerPage
)

const endIndex = computed(() => 
  Math.min(startIndex.value + itemsPerPage, filteredUsers.value.length)
)

const paginatedUsers = computed(() => 
  filteredUsers.value.slice(startIndex.value, endIndex.value)
)

// Format date
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

// Navigation
function navigateToCreate() {
  router.push(`/tenants/${tenantId.value}/users/create`)
}

function navigateToEdit(userId: number) {
  router.push(`/tenants/${tenantId.value}/users/${userId}/edit`)
}

function navigateToTenants() {
  router.push('/tenants')
}

function navigateToEditTenant() {
  router.push(`/tenants/${tenantId.value}/edit`)
}

// Toggle active status
async function handleToggleActive(user: User) {
  const confirmed = confirm(
    user.is_active
      ? t('users.confirmDeactivate')
      : t('users.confirmActivate')
  )

  if (confirmed) {
    await toggleActive(user.id)
  }
}

// Delete user
async function handleDelete(user: User) {
  const confirmed = confirm(t('users.confirmDelete', { name: `${user.first_name} ${user.last_name}` }))

  if (confirmed) {
    await deleteUser(user.id)
  }
}

// Reset pagination when search changes
watch(searchQuery, () => {
  currentPage.value = 1
})

// Load data on mount
onMounted(() => {
  fetchTenant(tenantId.value)
  fetchUsers()
})
</script>
