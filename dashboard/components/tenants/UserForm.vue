<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Email Field -->
    <div>
      <label for="user-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.email') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="user-email"
        v-model="formData.email"
        type="email"
        required
        :disabled="isSubmitting || mode === 'edit'"
        :placeholder="t('users.form.emailPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p v-if="errors.email" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.email }}
      </p>
    </div>

    <!-- First Name Field -->
    <div>
      <label for="user-first-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.firstName') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="user-first-name"
        v-model="formData.first_name"
        type="text"
        required
        :disabled="isSubmitting"
        :placeholder="t('users.form.firstNamePlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p v-if="errors.first_name" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.first_name }}
      </p>
    </div>

    <!-- Last Name Field -->
    <div>
      <label for="user-last-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.lastName') }}
        <span class="text-red-500">*</span>
      </label>
      <input
        id="user-last-name"
        v-model="formData.last_name"
        type="text"
        required
        :disabled="isSubmitting"
        :placeholder="t('users.form.lastNamePlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p v-if="errors.last_name" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.last_name }}
      </p>
    </div>

    <!-- Arabic Name Field (Optional) -->
    <div>
      <label for="user-name-ar" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.nameAr') }}
        <span class="text-gray-500 text-xs font-normal">({{ t('common.optional') }})</span>
      </label>
      <input
        id="user-name-ar"
        v-model="formData.name_ar"
        type="text"
        :disabled="isSubmitting"
        :placeholder="t('users.form.nameArPlaceholder')"
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white
               focus:ring-2 focus:ring-blue-500 focus:border-transparent
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {{ t('users.form.nameArHelp') }}
      </p>
    </div>

    <!-- Avatar Upload Field (Optional) -->
    <div>
      <label for="user-logo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.logo') }}
        <span class="text-gray-500 text-xs font-normal">({{ t('common.optional') }})</span>
      </label>
      
      <!-- File Upload Input -->
      <div class="relative">
        <input
          id="user-logo"
          ref="logoFileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/webp"
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
            <UIcon name="i-heroicons-user-circle" class="w-5 h-5" />
            <span>{{ logoFileName || t('users.form.logoUpload') }}</span>
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
        {{ t('users.form.logoHelp') }}
      </p>
      
      <!-- File Size Error -->
      <p v-if="logoUploadError" class="mt-1 text-xs text-red-600 dark:text-red-400">
        {{ logoUploadError }}
      </p>
      
      <!-- Avatar Preview -->
      <div v-if="logoPreview" class="mt-3">
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ t('users.form.logoPreview') }}
        </p>
        <div class="w-20 h-20 rounded-full overflow-hidden bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 flex items-center justify-center">
          <img 
            :src="logoPreview" 
            :alt="`${formData.first_name} ${formData.last_name}` || 'Avatar preview'" 
            class="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>

    <!-- Password Field (Create Mode Only) -->
    <div v-if="mode === 'create'">
      <label for="user-password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('users.form.password') }}
        <span class="text-red-500">*</span>
      </label>
      <div class="relative">
        <input
          id="user-password"
          v-model="formData.password"
          :type="showPassword ? 'text' : 'password'"
          required
          :disabled="isSubmitting"
          :placeholder="t('users.form.passwordPlaceholder')"
          class="w-full px-4 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg 
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                 focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="button"
          @click="showPassword = !showPassword"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
        >
          <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-5 h-5" />
        </button>
      </div>
      <p v-if="errors.password" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.password }}
      </p>
      <p v-else class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {{ t('users.form.passwordHelp') }}
      </p>
    </div>

    <!-- Active Status Field -->
    <div class="flex items-center">
      <input
        id="user-is-active"
        v-model="formData.is_active"
        type="checkbox"
        :disabled="isSubmitting"
        class="w-4 h-4 text-blue-600 border-gray-300 rounded 
               focus:ring-blue-500 focus:ring-2
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <label for="user-is-active" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('users.form.isActive') }}
      </label>
    </div>

    <!-- Super Admin Field (Optional) -->
    <div v-if="showSuperAdminOption" class="flex items-center">
      <input
        id="user-is-superuser"
        v-model="formData.is_superuser"
        type="checkbox"
        :disabled="isSubmitting"
        class="w-4 h-4 text-blue-600 border-gray-300 rounded 
               focus:ring-blue-500 focus:ring-2
               disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <label for="user-is-superuser" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('users.form.isSuperAdmin') }}
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
        {{ mode === 'create' ? t('users.form.create') : t('users.form.update') }}
      </UButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useTenantUsers } from '@/composables/useTenantUsers'
import type { User, CreateUserData, UpdateUserData } from '~/types/user'

interface Props {
  mode: 'create' | 'edit'
  user?: User | null
  isSubmitting?: boolean
  showSuperAdminOption?: boolean
}

interface Emits {
  (e: 'submit', data: (CreateUserData & { password: string }) | UpdateUserData): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
  user: null,
  isSubmitting: false,
  showSuperAdminOption: false
})

const emit = defineEmits<Emits>()

const { t } = useI18n()
const { validateUserData, validatePassword } = useTenantUsers()

// Form data
const formData = ref<CreateUserData & { password?: string }>({
  email: '',
  first_name: '',
  last_name: '',
  name_ar: '',
  logo: '',
  is_active: true,
  is_superuser: false,
  password: ''
})

// UI state
const showPassword = ref(false)

// Validation errors
const errors = ref<Record<string, string>>({})
const validationErrors = ref<string[]>([])

// Logo upload
const logoFileInput = ref<HTMLInputElement | null>(null)
const logoPreview = ref<string>('')
const logoFileName = ref<string>('')
const logoUploadError = ref<string>('')

// Initialize form data when editing
watch(() => props.user, (user) => {
  if (user && props.mode === 'edit') {
    formData.value = {
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      name_ar: user.name_ar || '',
      logo: user.logo || '',
      is_active: user.is_active,
      is_superuser: user.is_super_admin,
      password: '' // Optional in edit mode
    }
    // Set preview for existing logo
    if (user.logo) {
      logoPreview.value = user.logo
      logoFileName.value = t('users.form.existingLogo')
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
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    logoUploadError.value = t('users.form.logoInvalidType')
    return
  }
  
  // Validate file size (max 2MB)
  const maxSize = 2 * 1024 * 1024 // 2MB in bytes
  if (file.size > maxSize) {
    logoUploadError.value = t('users.form.logoTooLarge')
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
    logoUploadError.value = t('users.form.logoUploadFailed')
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
  const hasRequiredFields = formData.value.email.trim().length > 0 &&
                           formData.value.first_name.trim().length > 0 &&
                           formData.value.last_name.trim().length > 0

  const hasValidPassword = props.mode === 'edit' || 
                          (formData.value.password && formData.value.password.length >= 8)

  return hasRequiredFields &&
         hasValidPassword &&
         validationErrors.value.length === 0 &&
         Object.keys(errors.value).length === 0
})

// Validate form
function validateForm(): boolean {
  errors.value = {}
  validationErrors.value = []

  // Validate user data
  const userErrors = validateUserData(formData.value)
  validationErrors.value.push(...userErrors)

  // Validate password (create mode only)
  if (props.mode === 'create' && formData.value.password) {
    const passwordErrors = validatePassword(formData.value.password)
    validationErrors.value.push(...passwordErrors)
  }

  return validationErrors.value.length === 0
}

// Handle form submission
function handleSubmit() {
  if (!validateForm()) {
    return
  }

  if (props.mode === 'create') {
    // Remove empty optional fields before submitting
    const submitData = { ...formData.value } as CreateUserData & { password: string }
    
    // Only include name_ar if it has a value
    if (!submitData.name_ar || submitData.name_ar.trim() === '') {
      delete submitData.name_ar
    }
    
    // Only include logo if it has a value
    if (!submitData.logo || submitData.logo.trim() === '') {
      delete submitData.logo
    }
    
    emit('submit', submitData)
  } else {
    const { password, ...updateData } = formData.value
    
    // Remove empty optional fields for update as well
    const submitData = { ...updateData } as UpdateUserData
    
    if (!submitData.name_ar || submitData.name_ar.trim() === '') {
      delete submitData.name_ar
    }
    
    if (!submitData.logo || submitData.logo.trim() === '') {
      delete submitData.logo
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
    email: '',
    first_name: '',
    last_name: '',
    name_ar: '',
    logo: '',
    is_active: true,
    is_superuser: false,
    password: ''
  }
  errors.value = {}
  validationErrors.value = []
  showPassword.value = false
  clearLogo()
}

// Expose methods for parent components
defineExpose({
  resetForm
})
</script>
