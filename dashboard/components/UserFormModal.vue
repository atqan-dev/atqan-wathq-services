<template>
  <UModal v-model="isOpen" :prevent-close="isSubmitting">
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ isEditMode ? t('users.edit.title') : t('users.create.title') }}
        </h3>
      </template>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.email') }} <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model="formData.email"
            type="email"
            :placeholder="t('users.form.emailPlaceholder')"
            :disabled="isEditMode"
            required
          />
        </div>

        <!-- First Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.firstName') }} <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model="formData.first_name"
            :placeholder="t('users.form.firstNamePlaceholder')"
            required
          />
        </div>

        <!-- Last Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.lastName') }} <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model="formData.last_name"
            :placeholder="t('users.form.lastNamePlaceholder')"
            required
          />
        </div>

        <!-- Arabic Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.nameAr') }}
          </label>
          <UInput
            v-model="formData.name_ar"
            :placeholder="t('users.form.nameArPlaceholder')"
          />
        </div>

        <!-- Password -->
        <div v-if="!isEditMode">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.password') }} <span class="text-red-500">*</span>
          </label>
          <UInput
            v-model="formData.password"
            type="password"
            :placeholder="t('users.form.passwordPlaceholder')"
            :required="!isEditMode"
          />
        </div>

        <!-- Change Password (Edit Mode) -->
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.newPassword') }}
          </label>
          <UInput
            v-model="formData.password"
            type="password"
            :placeholder="t('users.form.newPasswordPlaceholder')"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ t('users.form.passwordHint') }}
          </p>
        </div>

        <!-- Roles -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('users.form.roles') }}
          </label>
          <div class="space-y-2 max-h-40 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-3">
            <label
              v-for="role in roles"
              :key="role.id"
              class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-2 rounded"
            >
              <input
                type="checkbox"
                :value="role.id"
                v-model="formData.role_ids"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex-1">
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ role.name }}</div>
                <div v-if="role.description" class="text-xs text-gray-500 dark:text-gray-400">
                  {{ role.description }}
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Status -->
        <div class="flex items-center space-x-2">
          <input
            type="checkbox"
            v-model="formData.is_active"
            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ t('users.form.isActive') }}
          </label>
        </div>

        <!-- Superuser -->
        <div class="flex items-center space-x-2">
          <input
            type="checkbox"
            v-model="formData.is_superuser"
            class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ t('users.form.isSuperuser') }}
          </label>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-sm text-red-600 dark:text-red-400">{{ errorMessage }}</p>
        </div>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <UButton
            color="gray"
            variant="ghost"
            @click="handleCancel"
            :disabled="isSubmitting"
          >
            {{ t('common.cancel') }}
          </UButton>
          <UButton
            @click="handleSubmit"
            :loading="isSubmitting"
            :disabled="!isFormValid"
          >
            {{ isEditMode ? t('common.update') : t('common.create') }}
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useUsers } from '@/composables/useUsers'
import { useAuthStore } from '~/stores/auth'
import type { User, UserCreate, UserUpdate } from '~/types/user'
import type { Role } from '~/types/user'

const props = defineProps<{
  modelValue: boolean
  user: User | null
  roles: Role[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'saved': []
}>()

const { t } = useI18n()
const { createUser, updateUser } = useUsers()
const authStore = useAuthStore()

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEditMode = computed(() => !!props.user)
const isSubmitting = ref(false)
const errorMessage = ref('')

const formData = ref<UserCreate | UserUpdate>({
  email: '',
  first_name: '',
  last_name: '',
  name_ar: '',
  password: '',
  is_active: true,
  is_superuser: false,
  role_ids: []
})

const isFormValid = computed(() => {
  if (isEditMode.value) {
    return formData.value.first_name && formData.value.last_name
  }
  return formData.value.email && 
         formData.value.first_name && 
         formData.value.last_name && 
         formData.value.password
})

// Watch for user changes to populate form
watch(() => props.user, (user) => {
  if (user) {
    formData.value = {
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      name_ar: user.name_ar || '',
      password: '',
      is_active: user.is_active,
      is_superuser: user.is_superuser,
      role_ids: user.roles?.map(r => r.id) || []
    }
  } else {
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  formData.value = {
    email: '',
    first_name: '',
    last_name: '',
    name_ar: '',
    password: '',
    is_active: true,
    is_superuser: false,
    role_ids: []
  }
  errorMessage.value = ''
}

async function handleSubmit() {
  if (!isFormValid.value) return

  try {
    isSubmitting.value = true
    errorMessage.value = ''

    // Remove password if empty in edit mode
    const submitData: any = { ...formData.value }
    if (isEditMode.value && !submitData.password) {
      delete submitData.password
    }

    // Add tenant_id for management users
    // For edit mode, get from the user being edited
    // For create mode, we'll need to add a tenant selector in the future
    // For now, management users should edit existing users only
    if (authStore.user?.is_super_admin) {
      if (isEditMode.value && props.user?.tenant_id) {
        // Editing - tenant_id comes from the user being edited
        submitData.tenant_id = props.user.tenant_id
      } else if (!isEditMode.value) {
        // Creating - for now, show error that tenant selection is needed
        errorMessage.value = 'Creating users as management user requires tenant selection (feature coming soon)'
        return
      }
    }

    let result
    if (isEditMode.value && props.user) {
      result = await updateUser(props.user.id, submitData as UserUpdate)
    } else {
      result = await createUser(submitData as UserCreate)
    }

    if (result) {
      emit('saved')
      isOpen.value = false
      resetForm()
    }
  } catch (error: any) {
    errorMessage.value = error.message || t('users.form.error')
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  isOpen.value = false
  resetForm()
}
</script>
