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
        <span>{{ t('users.createUser') }}</span>
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
          {{ t('users.createUser') }}
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('users.createUserDescription') }}
        </p>
      </div>

      <!-- Form Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-user-plus" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('users.form.userDetails') }}
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('users.form.fillRequiredFields') }}
              </p>
            </div>
          </div>
        </template>

        <UserForm
          mode="create"
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenantUsers } from '@/composables/useTenantUsers'
import { useTenants } from '@/composables/useTenants'
import TenantInfoCard from '@/components/tenants/TenantInfoCard.vue'
import UserForm from '@/components/tenants/UserForm.vue'
import type { CreateUserData } from '~/types/user'

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

// User management
const { createUser, isSaving } = useTenantUsers(tenantId.value)

// Handle form submission
async function handleSubmit(data: CreateUserData & { password: string }) {
  const result = await createUser(data)
  
  if (result) {
    // Navigate back to users list
    router.push(`/tenants/${tenantId.value}/users`)
  }
}

// Handle cancel
function handleCancel() {
  router.back()
}

// Load tenant on mount
onMounted(() => {
  fetchTenant(tenantId.value)
})

// Set page title
useHead({
  title: t('users.createUser')
})
</script>
