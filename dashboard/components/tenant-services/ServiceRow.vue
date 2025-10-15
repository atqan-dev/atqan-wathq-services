<template>
  <!-- Service Name & Description -->
  <td class="px-6 py-4">
    <div class="flex items-center gap-3">
      <div class="flex-shrink-0">
        <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
          <UIcon name="i-heroicons-cube" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
      <div>
        <div class="text-sm font-medium text-gray-900 dark:text-white">
          {{ service.service.name }}
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          {{ service.service.slug }}
        </div>
        <div v-if="service.service.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate max-w-xs">
          {{ service.service.description }}
        </div>
      </div>
    </div>
  </td>

  <!-- Tenant ID -->
  <td class="px-6 py-4">
    <div class="text-sm text-gray-900 dark:text-white">
      Tenant #{{ service.tenant_id }}
    </div>
    <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
      {{ t('tenantServices.table.maxUsers') }}: {{ service.max_users }}
    </div>
  </td>

  <!-- Status -->
  <td class="px-6 py-4">
    <div class="flex flex-col gap-2">
      <UBadge
        :color="service.is_active ? 'green' : 'red'"
        variant="subtle"
        size="sm"
      >
        {{ service.is_active ? t('common.active') : t('common.inactive') }}
      </UBadge>
      <UBadge
        :color="getCategoryColor(service.service.category)"
        variant="subtle"
        size="sm"
      >
        {{ service.service.category }}
      </UBadge>
    </div>
  </td>

  <!-- Approval Status -->
  <td class="px-6 py-4">
    <div class="flex flex-col gap-1">
      <UBadge
        :color="service.is_approved ? 'blue' : 'yellow'"
        variant="subtle"
        size="sm"
      >
        <UIcon
          :name="service.is_approved ? 'i-heroicons-check-circle' : 'i-heroicons-clock'"
          class="w-3 h-3"
        />
        {{ service.is_approved ? t('tenantServices.approved') : t('tenantServices.pending') }}
      </UBadge>
      <div v-if="service.approved_at" class="text-xs text-gray-500 dark:text-gray-400">
        {{ formatDate(service.approved_at) }}
      </div>
      <div v-if="service.service.requires_approval" class="text-xs text-yellow-600 dark:text-yellow-400">
        {{ t('tenantServices.requiresApproval') }}
      </div>
    </div>
  </td>

  <!-- Usage -->
  <td class="px-6 py-4">
    <div class="text-sm text-gray-900 dark:text-white font-semibold">
      {{ service.usage_count }}
    </div>
    <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
      {{ t('tenantServices.table.registered') }}:
    </div>
    <div class="text-xs text-gray-500 dark:text-gray-400">
      {{ formatDate(service.registered_at) }}
    </div>
  </td>

  <!-- Actions -->
  <td class="px-6 py-4 text-right">
    <div class="flex items-center justify-end gap-2">
      <!-- Approve Button -->
      <UButton
        v-if="!service.is_approved && service.service.requires_approval"
        size="xs"
        color="blue"
        variant="ghost"
        icon="i-heroicons-check-circle"
        :title="t('tenantServices.actions.approve')"
        @click="emit('approve', service)"
      />

      <!-- Toggle Active -->
      <UButton
        size="xs"
        :color="service.is_active ? 'yellow' : 'green'"
        variant="ghost"
        :icon="service.is_active ? 'i-heroicons-pause' : 'i-heroicons-play'"
        :title="service.is_active ? t('common.deactivate') : t('common.activate')"
        @click="emit('toggle-active', service)"
      />

      <!-- View Details -->
      <UButton
        size="xs"
        color="gray"
        variant="ghost"
        icon="i-heroicons-eye"
        :title="t('common.view')"
        @click="showDetails = !showDetails"
      />

      <!-- Delete -->
      <UButton
        size="xs"
        color="red"
        variant="ghost"
        icon="i-heroicons-trash"
        :title="t('common.delete')"
        @click="emit('delete', service)"
      />
    </div>

    <!-- Expandable Details -->
    <Transition
      enter-active-class="transition-all duration-200"
      leave-active-class="transition-all duration-200"
      enter-from-class="opacity-0 max-h-0"
      leave-to-class="opacity-0 max-h-0"
    >
      <div
        v-if="showDetails"
        class="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg text-left"
      >
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ t('tenantServices.details.serviceId') }}:</span>
            <span class="text-gray-600 dark:text-gray-400 ml-2">{{ service.service_id }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ t('tenantServices.details.price') }}:</span>
            <span class="text-gray-600 dark:text-gray-400 ml-2">{{ service.service.price }}</span>
          </div>
          <div v-if="service.wathq_api_key" class="col-span-2">
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ t('tenantServices.details.apiKey') }}:</span>
            <code class="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded ml-2">
              {{ maskApiKey(service.wathq_api_key) }}
            </code>
          </div>
          <div v-if="service.approved_by" class="col-span-2">
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ t('tenantServices.details.approvedBy') }}:</span>
            <span class="text-gray-600 dark:text-gray-400 ml-2">User #{{ service.approved_by }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </td>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/composables/useI18n'
import type { TenantService } from '~/types/tenant-service'

interface Props {
  service: TenantService
}

interface Emits {
  (e: 'approve', service: TenantService): void
  (e: 'toggle-active', service: TenantService): void
  (e: 'delete', service: TenantService): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const showDetails = ref(false)

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

function getCategoryColor(category: string): 'purple' | 'gray' | 'blue' | 'green' | 'red' | 'yellow' {
  switch (category) {
    case 'wathq':
      return 'purple'
    default:
      return 'gray'
  }
}

function maskApiKey(key: string): string {
  if (key.length <= 8) return key
  return `${key.substring(0, 4)}${'*'.repeat(key.length - 8)}${key.substring(key.length - 4)}`
}
</script>
