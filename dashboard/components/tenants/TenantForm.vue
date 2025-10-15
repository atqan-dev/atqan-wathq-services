<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Name Field -->
    <div>
      <label for="tenant-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.name') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="tenant-name"
        v-model="formData.name"
        type="text"
        required
        :disabled="isSubmitting"
        :placeholder="t('tenants.form.namePlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p v-if="errors.name" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.name }}
      </p>
    </div>

    <!-- Arabic Name Field (Optional) -->
    <div>
      <label for="tenant-name-ar" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.nameAr') }}
        <span class="text-gray-500 text-xs font-normal">({{ t('common.optional') }})</span>
      </label>
      <input
        id="tenant-name-ar"
        v-model="formData.name_ar"
        type="text"
        :disabled="isSubmitting"
        :placeholder="t('tenants.form.nameArPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {{ t('tenants.form.nameArHelp') }}
      </p>
    </div>

    <!-- Slug Field -->
    <div>
      <label for="tenant-slug" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.slug') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="tenant-slug"
        v-model="formData.slug"
        type="text"
        required
        :disabled="isSubmitting || mode === 'edit'"
        :placeholder="t('tenants.form.slugPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed
               font-mono text-sm"
        @input="handleSlugInput"
      />
      <p v-if="errors.slug" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.slug }}
      </p>
      <p v-else class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {{ t('tenants.form.slugHelp') }}
      </p>
    </div>

    <!-- Description Field -->
    <div>
      <label for="tenant-description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.description') }}
      </label>
      <textarea
        id="tenant-description"
        v-model="formData.description"
        rows="3"
        :disabled="isSubmitting"
        :placeholder="t('tenants.form.descriptionPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed
               resize-none"
      />
      <p v-if="errors.description" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.description }}
      </p>
    </div>

    <!-- Max Users Field -->
    <div>
      <label for="tenant-max-users" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.maxUsers') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="tenant-max-users"
        v-model.number="formData.max_users"
        type="number"
        min="1"
        max="10000"
        required
        :disabled="isSubmitting"
        :placeholder="t('tenants.form.maxUsersPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p v-if="errors.max_users" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.max_users }}
      </p>
    </div>

    <!-- Logo Upload Field (Optional) -->
    <div>
      <label for="tenant-logo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('tenants.form.logo') }}
        <span class="text-gray-500 text-xs font-normal">({{ t('common.optional') }})</span>
      </label>
      
      <!-- File Upload Input -->
      <div class="relative">
        <input
          id="tenant-logo"
          ref="logoFileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/svg+xml,image/webp"
          :disabled="isSubmitting"
          class="hidden"
          @change="handleLogoUpload"
        />
        <div class="flex gap-2">
          <button
            type="button"
            :disabled="isSubmitting"
            @click="logoFileInput?.click()"
            class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   hover:bg-gray-50 dark:hover:bg-gray-600
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
          >
            <UIcon name="i-heroicons-photo" class="w-5 h-5" />
            <span>{{ logoFileName || t('tenants.form.logoUpload') }}</span>
          </button>
          <button
            v-if="logoPreview"
            type="button"
            :disabled="isSubmitting"
            @click="clearLogo"
            class="px-4 py-2 border border-red-300 dark:border-red-600 rounded-lg 
                   bg-white dark:bg-gray-700 text-red-600 dark:text-red-400
                   hover:bg-red-50 dark:hover:bg-red-900/20
                   focus:ring-2 focus:ring-red-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {{ t('tenants.form.logoHelp') }}
      </p>
      
      <!-- File Size Error -->
      <p v-if="logoUploadError" class="mt-1 text-xs text-red-600 dark:text-red-400">
        {{ logoUploadError }}
      </p>
      
      <!-- Logo Preview -->
      <div v-if="logoPreview" class="mt-3">
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ t('tenants.form.logoPreview') }}
        </p>
        <div class="w-20 h-20 rounded-lg overflow-hidden bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 flex items-center justify-center">
          <img 
            :src="logoPreview" 
            :alt="formData.name || 'Logo preview'" 
            class="w-full h-full object-contain p-1"
          />
        </div>
      </div>
    </div>

    <!-- Active Status Field -->
    <div class="flex items-center">
      <input
        id="tenant-is-active"
        v-model="formData.is_active"
        type="checkbox"
        :disabled="isSubmitting"
        class="w-4 h-4 text-blue-600 border-gray-300 rounded 
               focus:ring-blue-500 focus:ring-2
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <label for="tenant-is-active" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('tenants.form.isActive') }}
      </label>
    </div>

    <!-- Validation Errors -->
    <div v-if="validationErrors.length > 0" class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      <h4 class="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
        {{ t('common.validationErrors') }}
      </h4>
      <ul class="list-disc list-inside text-sm text-red-700 dark:text-red-300 space-y-1">
        <li v-for="(error, index) in validationErrors" :key="index">{{ error }}</li>
      </ul>
    </div>

    <!-- Form Actions -->
    <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
      <UButton
        type="button"
        color="gray"
        variant="ghost"
        :disabled="isSubmitting"
        @click="handleCancel"
      >
        {{ t('common.cancel') }}
      </UButton>
      <UButton
        type="submit"
        color="primary"
        :loading="isSubmitting"
        :disabled="isSubmitting || !isFormValid"
      >
        <template #leading>
          <UIcon :name="mode === 'create' ? 'i-heroicons-plus' : 'i-heroicons-check'" />
        </template>
        {{ mode === 'create' ? t('tenants.form.create') : t('tenants.form.update') }}
      </UButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useTenants } from '@/composables/useTenants'
import type { Tenant, CreateTenantData, UpdateTenantData } from '~/types/tenant'

interface Props {
  mode: 'create' | 'edit'
  tenant?: Tenant | null
  isSubmitting?: boolean
}

interface Emits {
  (e: 'submit', data: CreateTenantData | UpdateTenantData): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
  tenant: null,
  isSubmitting: false
})

const emit = defineEmits<Emits>()

const { t } = useI18n()
const { validateTenantData } = useTenants()

// Form data
const formData = ref<CreateTenantData>({
  name: '',
  name_ar: '',
  slug: '',
  description: '',
  is_active: true,
  max_users: 10,
  logo: ''
})

// Validation errors
const errors = ref<Record<string, string>>({})
const validationErrors = ref<string[]>([])

// Logo upload
const logoFileInput = ref<HTMLInputElement | null>(null)
const logoPreview = ref<string>('')
const logoFileName = ref<string>('')
const logoUploadError = ref<string>('')

// Auto-generate slug from name (only in create mode)
watch(() => formData.value.name, (newName) => {
  if (props.mode === 'create' && newName) {
    // Generate slug: lowercase, remove special chars, replace spaces with hyphens
    formData.value.slug = newName
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove non-alphanumeric except spaces and hyphens
      .replace(/\s+/g, '-')          // Replace spaces with hyphens
      .replace(/-+/g, '-')           // Replace multiple hyphens with single
      .replace(/^-+|-+$/g, '')       // Remove leading/trailing hyphens
      .trim()
  }
  
  // Real-time validation for English characters only
  validateNameField()
})

// Initialize form data when editing
watch(() => props.tenant, (tenant) => {
  if (tenant && props.mode === 'edit') {
    formData.value = {
      name: tenant.name,
      name_ar: tenant.name_ar || '',
      slug: tenant.slug,
      description: tenant.description || '',
      is_active: tenant.is_active,
      max_users: tenant.max_users,
      logo: tenant.logo || ''
    }
    // Set preview for existing logo
    if (tenant.logo) {
      logoPreview.value = tenant.logo
      logoFileName.value = t('tenants.form.existingLogo')
    }
  }
}, { immediate: true })

// Handle logo file upload
function handleLogoUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Reset errors
  logoUploadError.value = ''
  
  // Validate file type
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml', 'image/webp']
  if (!validTypes.includes(file.type)) {
    logoUploadError.value = t('tenants.form.logoInvalidType')
    return
  }
  
  // Validate file size (max 2MB)
  const maxSize = 2 * 1024 * 1024 // 2MB in bytes
  if (file.size > maxSize) {
    logoUploadError.value = t('tenants.form.logoTooLarge')
    return
  }
  
  // Set filename
  logoFileName.value = file.name
  
  // Read file and convert to base64
  const reader = new FileReader()
  reader.onload = (e) => {
    const base64 = e.target?.result as string
    logoPreview.value = base64
    formData.value.logo = base64 // Store base64 in form data
  }
  reader.onerror = () => {
    logoUploadError.value = t('tenants.form.logoUploadFailed')
  }
  reader.readAsDataURL(file)
}

// Clear logo
function clearLogo() {
  logoPreview.value = ''
  logoFileName.value = ''
  formData.value.logo = ''
  logoUploadError.value = ''
  if (logoFileInput.value) {
    logoFileInput.value.value = ''
  }
}

// Form validation
const isFormValid = computed(() => {
  return formData.value.name.trim().length > 0 &&
         formData.value.slug.trim().length > 0 &&
         (formData.value.max_users || 0) > 0 &&
         validationErrors.value.length === 0 &&
         Object.keys(errors.value).length === 0
})

// Validate name field for English characters only
function validateNameField() {
  if (formData.value.name.trim().length === 0) {
    delete errors.value.name
    return
  }
  
  // Check for English characters only (letters, numbers, spaces, and basic symbols)
  const englishOnlyRegex = /^[a-zA-Z0-9\s\-_&]+$/
  
  if (!englishOnlyRegex.test(formData.value.name)) {
    errors.value.name = t('tenants.form.nameEnglishOnly')
  } else {
    delete errors.value.name
  }
}

// Handle slug input (enforce lowercase and valid characters)
function handleSlugInput(event: Event) {
  const input = event.target as HTMLInputElement
  const cleaned = input.value
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, '')
  
  if (input.value !== cleaned) {
    formData.value.slug = cleaned
  }
}

// Validate form
function validateForm(): boolean {
  errors.value = {}
  validationErrors.value = validateTenantData(formData.value)
  return validationErrors.value.length === 0
}

// Handle form submission
function handleSubmit() {
  if (!validateForm()) {
    return
  }

  if (props.mode === 'create') {
    // Remove empty optional fields before submitting
    const submitData = { ...formData.value } as CreateTenantData
    
    // Only include name_ar if it has a value
    if (!submitData.name_ar || submitData.name_ar.trim() === '') {
      delete submitData.name_ar
    }
    
    // Only include logo if it has a value
    if (!submitData.logo || submitData.logo.trim() === '') {
      delete submitData.logo
    }
    
    // Only include description if it has a value
    if (!submitData.description || submitData.description.trim() === '') {
      delete submitData.description
    }
    
    emit('submit', submitData)
  } else {
    // For edit mode, include all fields but remove empty optional ones
    const submitData: UpdateTenantData = {
      name: formData.value.name,
      is_active: formData.value.is_active,
      max_users: formData.value.max_users
    }
    
    // Include name_ar only if it has a value
    if (formData.value.name_ar && formData.value.name_ar.trim() !== '') {
      submitData.name_ar = formData.value.name_ar
    }
    
    // Include logo only if it has a value
    if (formData.value.logo && formData.value.logo.trim() !== '') {
      submitData.logo = formData.value.logo
    }
    
    // Include description only if it has a value
    if (formData.value.description && formData.value.description.trim() !== '') {
      submitData.description = formData.value.description
    }
    
    emit('submit', submitData)
  }
}

// Handle cancel
function handleCancel() {
  emit('cancel')
}

// Reset form
function resetForm() {
  formData.value = {
    name: '',
    name_ar: '',
    slug: '',
    description: '',
    is_active: true,
    max_users: 10,
    logo: ''
  }
  errors.value = {}
  validationErrors.value = []
  clearLogo()
}

// Expose methods for parent components
defineExpose({
  resetForm
})
</script>
