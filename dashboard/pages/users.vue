<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ t('users.title') }}</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">{{ t('users.subtitle') }}</p>
        </div>
        <UButton
          icon="i-heroicons-plus"
          size="lg"
          @click="openCreateModal"
        >
          {{ t('users.addNew') }}
        </UButton>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UIcon name="i-heroicons-users" class="h-8 w-8 text-blue-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('users.stats.total') }}</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ pagination.total }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UIcon name="i-heroicons-check-circle" class="h-8 w-8 text-green-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('users.stats.active') }}</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.active }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UIcon name="i-heroicons-x-circle" class="h-8 w-8 text-red-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('users.stats.inactive') }}</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.inactive }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <UIcon name="i-heroicons-shield-check" class="h-8 w-8 text-purple-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('users.stats.admins') }}</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.superAdmins }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow mb-6 p-6">
        <div class="grid grid-cols-1 gap-4" :class="availableRoles.length > 0 ? 'md:grid-cols-4' : 'md:grid-cols-3'">
          <!-- Search -->
          <div class="md:col-span-2">
            <UInput
              v-model="searchQuery"
              icon="i-heroicons-magnifying-glass"
              :placeholder="t('users.search')"
              @input="handleSearch"
            />
          </div>

          <!-- Status Filter -->
          <div>
            <USelect
              v-model="statusFilter"
              :options="statusOptions"
              @change="handleFilterChange"
            />
          </div>

          <!-- Role Filter (only show if roles are available) -->
          <div v-if="availableRoles.length > 0">
            <USelect
              v-model="roleFilter"
              :options="roleOptions"
              @change="handleFilterChange"
            />
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div v-if="isLoading" class="p-8 text-center">
          <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin mx-auto text-blue-600" />
          <p class="mt-2 text-gray-600 dark:text-gray-400">{{ t('common.loading') }}</p>
        </div>

        <div v-else-if="users.length === 0" class="p-8 text-center">
          <UIcon name="i-heroicons-user-group" class="h-12 w-12 mx-auto text-gray-400" />
          <p class="mt-2 text-gray-600 dark:text-gray-400">{{ t('users.noUsers') }}</p>
        </div>

        <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.user') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.email') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.roles') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.status') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.created') }}
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('users.table.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <span class="text-blue-600 dark:text-blue-300 font-medium">
                        {{ user.first_name.charAt(0) }}{{ user.last_name.charAt(0) }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ user.first_name }} {{ user.last_name }}
                    </div>
                    <div v-if="user.name_ar" class="text-sm text-gray-500 dark:text-gray-400">
                      {{ user.name_ar }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-wrap gap-1">
                  <UBadge
                    v-for="role in user.roles"
                    :key="role.id"
                    color="blue"
                    variant="subtle"
                  >
                    {{ role.name }}
                  </UBadge>
                  <UBadge v-if="user.is_superuser" color="purple" variant="subtle">
                    {{ t('users.superuser') }}
                  </UBadge>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <UBadge :color="user.is_active ? 'green' : 'red'" variant="subtle">
                  {{ user.is_active ? t('users.status.active') : t('users.status.inactive') }}
                </UBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <UButton
                    icon="i-heroicons-pencil"
                    size="sm"
                    color="gray"
                    variant="ghost"
                    @click="openEditModal(user)"
                  />
                  <UButton
                    icon="i-heroicons-trash"
                    size="sm"
                    color="red"
                    variant="ghost"
                    @click="confirmDelete(user)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="users.length > 0" class="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <UButton
                :disabled="pagination.skip === 0"
                @click="previousPage"
              >
                {{ t('common.previous') }}
              </UButton>
              <UButton
                :disabled="pagination.skip + pagination.limit >= pagination.total"
                @click="nextPage"
              >
                {{ t('common.next') }}
              </UButton>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  {{ t('common.showing') }}
                  <span class="font-medium">{{ pagination.skip + 1 }}</span>
                  {{ t('common.to') }}
                  <span class="font-medium">{{ Math.min(pagination.skip + pagination.limit, pagination.total) }}</span>
                  {{ t('common.of') }}
                  <span class="font-medium">{{ pagination.total }}</span>
                  {{ t('common.results') }}
                </p>
              </div>
              <div class="flex gap-2">
                <UButton
                  icon="i-heroicons-chevron-left"
                  :disabled="pagination.skip === 0"
                  @click="previousPage"
                >
                  {{ t('common.previous') }}
                </UButton>
                <UButton
                  icon="i-heroicons-chevron-right"
                  :disabled="pagination.skip + pagination.limit >= pagination.total"
                  @click="nextPage"
                >
                  {{ t('common.next') }}
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <UserFormModal
      v-model="showFormModal"
      :user="selectedUser"
      :roles="availableRoles"
      @saved="handleUserSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useUsers } from '@/composables/useUsers'
import { useRoles } from '@/composables/useRoles'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import type { User } from '~/types/user'

definePageMeta({
  middleware: ['auth']
})

const { t } = useI18n()
const { 
  users, 
  isLoading, 
  pagination, 
  filters,
  stats,
  fetchUsers, 
  deleteUser,
  setFilters,
  setPagination
} = useUsers()

const { roles: availableRoles, fetchRoles } = useRoles()
const { confirm } = useConfirmDialog()

// Local state
const searchQuery = ref('')
const statusFilter = ref('all')
const roleFilter = ref('all')
const showFormModal = ref(false)
const selectedUser = ref<User | null>(null)

// Options for filters
const statusOptions = computed(() => [
  { label: t('users.filters.allStatus'), value: 'all' },
  { label: t('users.filters.active'), value: 'active' },
  { label: t('users.filters.inactive'), value: 'inactive' }
])

const roleOptions = computed(() => [
  { label: t('users.filters.allRoles'), value: 'all' },
  ...availableRoles.value.map(role => ({
    label: role.name,
    value: role.id.toString()
  }))
])

// Methods
function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString()
}

function handleSearch() {
  setFilters({ search: searchQuery.value })
  fetchUsers()
}

function handleFilterChange() {
  const newFilters: any = { search: searchQuery.value }
  
  if (statusFilter.value === 'active') {
    newFilters.is_active = true
  } else if (statusFilter.value === 'inactive') {
    newFilters.is_active = false
  } else {
    newFilters.is_active = null
  }
  
  if (roleFilter.value !== 'all') {
    newFilters.role_id = parseInt(roleFilter.value)
  } else {
    newFilters.role_id = null
  }
  
  setFilters(newFilters)
  fetchUsers()
}

function openCreateModal() {
  selectedUser.value = null
  showFormModal.value = true
}

function openEditModal(user: User) {
  selectedUser.value = user
  showFormModal.value = true
}

async function confirmDelete(user: User) {
  const confirmed = await confirm({
    title: t('users.delete.title'),
    message: t('users.delete.message', { name: `${user.first_name} ${user.last_name}` }),
    confirmText: t('common.delete'),
    cancelText: t('common.cancel'),
    type: 'danger'
  })
  
  if (confirmed) {
    await deleteUser(user.id)
    await fetchUsers()
  }
}

function handleUserSaved() {
  showFormModal.value = false
  fetchUsers()
}

function previousPage() {
  if (pagination.value.skip > 0) {
    setPagination(Math.max(0, pagination.value.skip - pagination.value.limit), pagination.value.limit)
    fetchUsers()
  }
}

function nextPage() {
  if (pagination.value.skip + pagination.value.limit < pagination.value.total) {
    setPagination(pagination.value.skip + pagination.value.limit, pagination.value.limit)
    fetchUsers()
  }
}

// Initialize
onMounted(async () => {
  // Fetch users
  await fetchUsers()
  
  // Try to fetch roles, but don't fail if it doesn't work
  // (Management users may not have access to roles endpoint)
  try {
    await fetchRoles()
  } catch (error) {
    console.warn('[Users] Could not fetch roles:', error)
    // Continue without roles - the page will still work
  }
})
</script>
