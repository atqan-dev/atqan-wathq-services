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
          <span>{{ t('tenants.editTenant') }}</span>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('tenants.editTenant') }}
        </h1>
        <p v-if="currentTenant" class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('tenants.editTenantDescription', { name: currentTenant.name }) }}
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
              <UButton @click="loadTenant">
                {{ t('common.retry') }}
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Form Card -->
      <UCard v-else-if="currentTenant">
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
                {{ t('tenants.form.updateDetails') }}
              </p>
            </div>
          </div>
        </template>

        <TenantForm
          mode="edit"
          :tenant="currentTenant"
          :is-submitting="isSaving"
          @submit="handleSubmit"
          @cancel="handleCancel"
        />
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useTenants } from '@/composables/useTenants'
import TenantForm from '@/components/tenants/TenantForm.vue'
import type { UpdateTenantData } from '~/types/tenant'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const {
  currentTenant,
  isLoading,
  isSaving,
  error,
  fetchTenant,
  updateTenant
} = useTenants()

// Get tenant ID from route
const tenantId = computed(() => parseInt(route.params.id as string))

// Load tenant data
async function loadTenant() {
  await fetchTenant(tenantId.value)
}

// Handle form submission
async function handleSubmit(data: UpdateTenantData) {
  const result = await updateTenant(tenantId.value, data)
  
  if (result) {
    // Navigate back to tenants list
    router.push('/tenants')
  }
}

// Handle cancel
function handleCancel() {
  router.back()
}

// Load tenant on mount
onMounted(() => {
  loadTenant()
})

// Set page title
useHead({
  title: computed(() => 
    currentTenant.value 
      ? t('tenants.editTenant') + ': ' + currentTenant.value.name
      : t('tenants.editTenant')
  )
})
</script>
