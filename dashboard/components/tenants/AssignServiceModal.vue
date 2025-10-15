<template>
  <UModal v-model="isOpen" :ui="{ width: 'sm:max-w-2xl' }">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ t('tenants.assignService.title') }}
          </h3>
          <UButton
            color="gray"
            variant="ghost"
            icon="i-heroicons-x-mark"
            @click="closeModal"
          />
        </div>
      </template>

      <!-- Tenant Info -->
      <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-building-office-2" class="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <div>
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              {{ tenant?.name }}
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ t('tenants.assignService.assigningTo') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Service Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('tenants.assignService.selectService') }}
            <span class="text-red-500">*</span>
          </label>
          
          <!-- Loading Services -->
          <div v-if="isLoadingServices" class="flex items-center justify-center py-8">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin text-gray-400" />
          </div>

          <!-- Services Error -->
          <div v-else-if="servicesError" class="text-center py-8">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">{{ servicesError }}</p>
            <UButton size="sm" @click="loadServices">
              {{ t('common.retry') }}
            </UButton>
          </div>

          <!-- No Services -->
          <div v-else-if="activeServices.length === 0" class="text-center py-8">
            <UIcon name="i-heroicons-cube" class="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ t('tenants.assignService.noServices') }}
            </p>
          </div>

          <!-- Services Grid -->
          <div v-else class="grid grid-cols-1 gap-3 max-h-64 overflow-y-auto">
            <div
              v-for="service in activeServices"
              :key="service.id"
              :class="[
                'p-4 border-2 rounded-lg cursor-pointer transition-all',
                formData.service_id === service.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              ]"
              @click="selectService(service)"
            >
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 mt-1">
                  <div
                    :class="[
                      'w-5 h-5 rounded-full border-2 flex items-center justify-center',
                      formData.service_id === service.id
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300 dark:border-gray-600'
                    ]"
                  >
                    <UIcon
                      v-if="formData.service_id === service.id"
                      name="i-heroicons-check"
                      class="w-3 h-3 text-white"
                    />
                  </div>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ service.name }}
                    </h4>
                    <UBadge
                      v-if="service.category === 'wathq'"
                      size="xs"
                      color="purple"
                      variant="subtle"
                    >
                      {{ service.category }}
                    </UBadge>
                    <UBadge
                      v-if="service.requires_approval"
                      size="xs"
                      color="yellow"
                      variant="subtle"
                    >
                      {{ t('tenants.assignService.requiresApproval') }}
                    </UBadge>
                  </div>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {{ service.description }}
                  </p>
                  <div class="flex items-center gap-4 mt-2">
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      {{ t('tenants.assignService.price') }}: {{ service.price }} SAR
                    </span>
                    <span class="text-xs text-gray-400">•</span>
                    <code class="text-xs text-gray-500 dark:text-gray-400">
                      {{ service.slug }}
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <p v-if="errors.service_id" class="mt-1 text-sm text-red-600 dark:text-red-400">
            {{ errors.service_id }}
          </p>
        </div>

        <!-- Max Users -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('tenants.assignService.maxUsers') }}
            <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model.number="formData.max_users"
            type="number"
            :placeholder="t('tenants.assignService.maxUsersPlaceholder')"
            :min="1"
            :max="1000"
            size="lg"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ t('tenants.assignService.maxUsersHelp') }}
          </p>
          <p v-if="errors.max_users" class="mt-1 text-sm text-red-600 dark:text-red-400">
            {{ errors.max_users }}
          </p>
        </div>

        <!-- Wathq API Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('tenants.assignService.apiKey') }}
            <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model="formData.wathq_api_key"
            type="text"
            :placeholder="t('tenants.assignService.apiKeyPlaceholder')"
            size="lg"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ t('tenants.assignService.apiKeyHelp') }}
          </p>
          <p v-if="errors.wathq_api_key" class="mt-1 text-sm text-red-600 dark:text-red-400">
            {{ errors.wathq_api_key }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <UButton
            color="gray"
            variant="ghost"
            @click="closeModal"
            :disabled="isAssigning"
          >
            {{ t('common.cancel') }}
          </UButton>
          <UButton
            type="submit"
            :loading="isAssigning"
            :disabled="!isFormValid"
          >
            {{ t('tenants.assignService.assign') }}
          </UButton>
        </div>
      </form>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useServices } from '@/composables/useServices'
import type { AssignServiceRequest } from '~/types/service'

interface Props {
  modelValue: boolean
  tenant: {
    id: number
    name: string
    slug: string
  } | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const {
  activeServices,
  isLoading: isLoadingServices,
  isAssigning,
  error: servicesError,
  fetchServices,
  assignServiceToTenant
} = useServices()

// Local state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formData = ref<AssignServiceRequest>({
  service_id: '',
  max_users: 10,
  wathq_api_key: ''
})

const errors = ref({
  service_id: '',
  max_users: '',
  wathq_api_key: ''
})

// Form validation
const isFormValid = computed(() => {
  return (
    formData.value.service_id &&
    formData.value.max_users > 0 &&
    formData.value.wathq_api_key.length > 0
  )
})

// Load services when modal opens
watch(isOpen, async (newValue) => {
  if (newValue && activeServices.value.length === 0) {
    await loadServices()
  }
  
  // Reset form when modal closes
  if (!newValue) {
    resetForm()
  }
})

async function loadServices() {
  await fetchServices()
}

function selectService(service: any) {
  formData.value.service_id = service.id
  errors.value.service_id = ''
}

function validateForm(): boolean {
  errors.value = {
    service_id: '',
    max_users: '',
    wathq_api_key: ''
  }
  
  let isValid = true
  
  if (!formData.value.service_id) {
    errors.value.service_id = t('tenants.assignService.errors.serviceRequired')
    isValid = false
  }
  
  if (!formData.value.max_users || formData.value.max_users < 1) {
    errors.value.max_users = t('tenants.assignService.errors.maxUsersRequired')
    isValid = false
  }
  
  if (!formData.value.wathq_api_key || formData.value.wathq_api_key.trim() === '') {
    errors.value.wathq_api_key = t('tenants.assignService.errors.apiKeyRequired')
    isValid = false
  }
  
  return isValid
}

async function handleSubmit() {
  if (!validateForm() || !props.tenant) return
  
  const success = await assignServiceToTenant(props.tenant.id, formData.value)
  
  if (success) {
    emit('success')
    closeModal()
  }
}

function resetForm() {
  formData.value = {
    service_id: '',
    max_users: 10,
    wathq_api_key: ''
  }
  
  errors.value = {
    service_id: '',
    max_users: '',
    wathq_api_key: ''
  }
}

function closeModal() {
  isOpen.value = false
}
</script>
