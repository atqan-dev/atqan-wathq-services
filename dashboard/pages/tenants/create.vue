<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
          <NuxtLink to="/tenants" class="hover:text-blue-600 dark:hover:text-blue-400">
            {{ t('tenants.title') }}
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          <span>{{ t('tenants.createTenant') }}</span>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('tenants.createTenant') }}
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('tenants.createTenantDescription') }}
        </p>
      </div>

      <!-- Form Card -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-building-office-2" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('tenants.form.tenantDetails') }}
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('tenants.form.fillRequiredFields') }}
              </p>
            </div>
          </div>
        </template>

        <TenantForm
          mode="create"
          :is-submitting="isSaving"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenants } from '@/composables/useTenants'
import TenantForm from '@/components/tenants/TenantForm.vue'
import type { CreateTenantData } from '~/types/tenant'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const router = useRouter()
const { t } = useI18n()
const { createTenant, isSaving } = useTenants()

// Handle form submission
async function handleSubmit(data: CreateTenantData) {
  const result = await createTenant(data)
  
  if (result) {
    // Navigate back to tenants list
    router.push('/tenants')
  }
}

// Handle cancel
function handleCancel() {
  router.back()
}

// Set page title
useHead({
  title: t('tenants.createTenant')
})
</script>
