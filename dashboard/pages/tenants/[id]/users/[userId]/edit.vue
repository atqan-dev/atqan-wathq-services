<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-6">
        <NuxtLink to="/tenants" class="hover:text-blue-600 dark:hover:text-blue-400">
          {{ t('tenants.title') }}
        </NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        <NuxtLink :to="`/tenants/${tenantId}/users`" class="hover:text-blue-600 dark:hover:text-blue-400">
          {{ t('users.title') }}
        </NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        <span>{{ t('users.editUser') }}</span>
      </div>

      <!-- Tenant Info Card -->
      <TenantInfoCard
        :tenant="currentTenant"
        :is-loading="isTenantLoading"
        :error="tenantError"
        :show-actions="false"
      />

      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('users.editUser') }}
        </h1>
        <p v-if="currentUser" class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('users.editUserDescription', { name: `${currentUser.first_name} ${currentUser.last_name}` }) }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <UCard>
          <div class="flex flex-col items-center">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mb-4" />
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {{ t('common.error') }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
            <div class="flex items-center gap-3">
              <UButton color="gray" @click="router.back()">
                {{ t('common.goBack') }}
              </UButton>
              <UButton @click="loadUser">
                {{ t('common.retry') }}
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Form Card -->
      <UCard v-else-if="currentUser">
        <template #header>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-user" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('users.form.userDetails') }}
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('users.form.updateDetails') }}
              </p>
            </div>
          </div>
        </template>

        <UserForm
          mode="edit"
          :user="currentUser"
          :is-submitting="isSaving"
          :show-super-admin-option="true"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenantUsers } from '@/composables/useTenantUsers'
import { useTenants } from '@/composables/useTenants'
import TenantInfoCard from '@/components/tenants/TenantInfoCard.vue'
import UserForm from '@/components/tenants/UserForm.vue'
import type { UpdateUserData } from '~/types/user'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Get IDs from route
const tenantId = computed(() => parseInt(route.params.id as string))
const userId = computed(() => parseInt(route.params.userId as string))

// Tenant info
const {
  currentTenant,
  isLoading: isTenantLoading,
  error: tenantError,
  fetchTenant
} = useTenants()

// User management
const {
  currentUser,
  isLoading,
  isSaving,
  error,
  fetchUser,
  updateUser
} = useTenantUsers(tenantId.value)

// Load user data
async function loadUser() {
  await fetchUser(userId.value)
}

// Handle form submission
async function handleSubmit(data: UpdateUserData) {
  const result = await updateUser(userId.value, data)
  
  if (result) {
    // Navigate back to users list
    router.push(`/tenants/${tenantId.value}/users`)
  }
}

// Handle cancel
function handleCancel() {
  router.back()
}

// Load data on mount
onMounted(() => {
  fetchTenant(tenantId.value)
  loadUser()
})

// Set page title
useHead({
  title: computed(() => 
    currentUser.value 
      ? t('users.editUser') + ': ' + `${currentUser.value.first_name} ${currentUser.value.last_name}`
      : t('users.editUser')
  )
})
</script>
