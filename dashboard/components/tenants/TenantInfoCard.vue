<template>
  <UCard class="mb-6 border-l-4" :class="tenant?.is_active ? 'border-l-green-500' : 'border-l-red-500'">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center gap-3 text-red-600 dark:text-red-400">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" />
      <span class="text-sm">{{ error }}</span>
    </div>

    <!-- Tenant Info -->
    <div v-else-if="tenant" class="flex items-start justify-between">
      <div class="flex items-start gap-4">
        <!-- Tenant Icon/Logo -->
        <div class="flex-shrink-0">
          <!-- Custom Logo -->
          <div v-if="tenant.logo" class="w-16 h-16 rounded-lg overflow-hidden bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 flex items-center justify-center">
            <img 
              :src="tenant.logo" 
              :alt="displayName(tenant)" 
              class="w-full h-full object-contain p-1"
              @error="handleImageError"
            />
          </div>
          <!-- Default Gradient Avatar -->
          <div v-else class="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span class="text-2xl font-bold text-white">
              {{ displayName(tenant).substring(0, 2).toUpperCase() }}
            </span>
          </div>
        </div>

        <!-- Tenant Details -->
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ displayName(tenant) }}
            </h2>
            <UBadge
              :color="tenant.is_active ? 'green' : 'red'"
              variant="subtle"
              size="lg"
            >
              {{ tenant.is_active ? t('common.active') : t('common.inactive') }}
            </UBadge>
          </div>

          <div class="space-y-2">
            <!-- Slug -->
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <UIcon name="i-heroicons-link" class="w-4 h-4" />
              <span class="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {{ tenant.slug }}
              </span>
            </div>

            <!-- Description -->
            <div v-if="tenant.description" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
              <UIcon name="i-heroicons-information-circle" class="w-4 h-4 mt-0.5" />
              <span>{{ tenant.description }}</span>
            </div>

            <!-- Stats Row -->
            <div class="flex items-center gap-4 text-sm">
              <!-- Max Users -->
              <div class="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                <UIcon name="i-heroicons-users" class="w-4 h-4" />
                <span>
                  <span class="font-medium">{{ t('tenants.form.maxUsers') }}:</span>
                  {{ tenant.max_users }}
                </span>
              </div>

              <!-- Created Date -->
              <div class="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
                <span>
                  <span class="font-medium">{{ t('tenants.table.createdAt') }}:</span>
                  {{ formatDate(tenant.created_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions (Optional) -->
      <div v-if="showActions" class="flex items-center gap-2">
        <UButton
          size="sm"
          color="gray"
          variant="ghost"
          icon="i-heroicons-pencil"
          @click="$emit('edit', tenant)"
        >
          {{ t('common.edit') }}
        </UButton>
        <UButton
          size="sm"
          color="gray"
          variant="ghost"
          icon="i-heroicons-arrow-left"
          @click="$emit('back')"
        >
          {{ t('tenants.backToList') }}
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Tenant } from '~/types/tenant'

interface Props {
  tenant?: Tenant | null
  isLoading?: boolean
  error?: string | null
  showActions?: boolean
}

interface Emits {
  (e: 'edit', tenant: Tenant): void
  (e: 'back'): void
}

const props = withDefaults(defineProps<Props>(), {
  tenant: null,
  isLoading: false,
  error: null,
  showActions: true
})

defineEmits<Emits>()

// Use i18n
const { t } = useI18n()

// Format date
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Get display name based on current locale
function displayName(tenant: Tenant): string {
  const locale = t('_locale') // Gets current locale from i18n
  if (locale === 'ar' && tenant.name_ar) {
    return tenant.name_ar
  }
  return tenant.name
}

// Handle image loading error - fallback handled by v-if/v-else
function handleImageError(event: Event) {
  console.warn('[TenantInfoCard] Failed to load tenant logo:', (event.target as HTMLImageElement).src)
}
</script>
