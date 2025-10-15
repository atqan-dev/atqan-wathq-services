<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="flex justify-center">
        <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
      </div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
        {{ t('passwordResetConfirm.title') }}
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
        {{ tokenValid ? t('passwordResetConfirm.subtitle') : t('passwordResetConfirm.invalidToken') }}
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white dark:bg-gray-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
        
        <!-- Loading State -->
        <div v-if="validatingToken" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('passwordResetConfirm.validatingToken') }}</p>
        </div>

        <!-- Invalid Token State -->
        <div v-else-if="!tokenValid" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900 mb-4">
            <svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('passwordResetConfirm.tokenExpiredTitle') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
            {{ t('passwordResetConfirm.tokenExpiredMessage') }}
          </p>
          <NuxtLink
            to="/reset-password"
            class="w-full bg-blue-600 border border-transparent rounded-md py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-center block"
          >
            {{ t('passwordResetConfirm.requestNewLink') }}
          </NuxtLink>
        </div>

        <!-- Success State -->
        <div v-else-if="resetSuccess" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900 mb-4">
            <svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {{ t('passwordResetConfirm.successTitle') }}
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
            {{ t('passwordResetConfirm.successMessage') }}
          </p>
          <NuxtLink
            to="/login"
            class="w-full bg-blue-600 border border-transparent rounded-md py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-center block"
          >
            {{ t('passwordResetConfirm.goToLogin') }}
          </NuxtLink>
        </div>

        <!-- Reset Form -->
        <form v-else @submit.prevent="handleSubmit" class="space-y-6">
          <!-- User Info -->
          <div v-if="userEmail" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
                  {{ t('passwordResetConfirm.resettingFor') }}
                </h3>
                <p class="mt-1 text-sm text-blue-700 dark:text-blue-300">
                  {{ userEmail }}
                </p>
              </div>
            </div>
          </div>

          <!-- New Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('passwordResetConfirm.newPasswordLabel') }}
            </label>
            <div class="mt-1 relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                name="password"
                required
                :disabled="loading"
                @input="checkPasswordStrength"
                class="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                :placeholder="t('passwordResetConfirm.passwordPlaceholder')"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg v-if="showPassword" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
                <svg v-else class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('passwordResetConfirm.confirmPasswordLabel') }}
            </label>
            <div class="mt-1 relative">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                name="confirmPassword"
                required
                :disabled="loading"
                class="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                :placeholder="t('passwordResetConfirm.confirmPasswordPlaceholder')"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg v-if="showConfirmPassword" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
                <svg v-else class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Password Strength Indicator -->
          <div v-if="passwordStrength && password" class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ t('passwordResetConfirm.passwordStrength') }}
              </span>
              <span class="text-sm" :class="strengthColor">
                {{ t(`passwordResetConfirm.strength.${passwordStrength.strength}`) }}
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-300"
                :class="strengthBarColor"
                :style="{ width: `${(passwordStrength.score / 8) * 100}%` }"
              ></div>
            </div>
            <div v-if="passwordStrength.errors.length > 0" class="text-sm text-red-600 dark:text-red-400">
              <ul class="list-disc list-inside space-y-1">
                <li v-for="error in passwordStrength.errors" :key="error">{{ error }}</li>
              </ul>
            </div>
            <div v-if="passwordStrength.suggestions && passwordStrength.suggestions.length > 0" class="text-sm text-blue-600 dark:text-blue-400">
              <p class="font-medium mb-1">{{ t('passwordResetConfirm.suggestions') }}:</p>
              <ul class="list-disc list-inside space-y-1">
                <li v-for="suggestion in passwordStrength.suggestions" :key="suggestion">{{ suggestion }}</li>
              </ul>
            </div>
          </div>

          <!-- Password Match Check -->
          <div v-if="password && confirmPassword && password !== confirmPassword" class="text-sm text-red-600 dark:text-red-400">
            {{ t('passwordResetConfirm.passwordsDoNotMatch') }}
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                  {{ error }}
                </h3>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading || !isFormValid"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              </span>
              {{ loading ? t('passwordResetConfirm.resetting') : t('passwordResetConfirm.resetPassword') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useNotifications } from '~/composables/useNotifications'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const notify = useNotifications()
const api = useApi()

// Reactive state
const token = ref(route.query.token as string || '')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const validatingToken = ref(true)
const tokenValid = ref(false)
const resetSuccess = ref(false)
const error = ref<string | null>(null)
const userEmail = ref<string | null>(null)
const passwordStrength = ref<any>(null)

// Computed properties
const isFormValid = computed(() => {
  return password.value && 
         confirmPassword.value && 
         password.value === confirmPassword.value &&
         passwordStrength.value?.is_valid
})

const strengthColor = computed(() => {
  if (!passwordStrength.value) return 'text-gray-500'
  
  switch (passwordStrength.value.strength) {
    case 'very_strong': return 'text-green-600 dark:text-green-400'
    case 'strong': return 'text-blue-600 dark:text-blue-400'
    case 'medium': return 'text-yellow-600 dark:text-yellow-400'
    case 'weak': return 'text-red-600 dark:text-red-400'
    default: return 'text-gray-500'
  }
})

const strengthBarColor = computed(() => {
  if (!passwordStrength.value) return 'bg-gray-300'
  
  switch (passwordStrength.value.strength) {
    case 'very_strong': return 'bg-green-500'
    case 'strong': return 'bg-blue-500'
    case 'medium': return 'bg-yellow-500'
    case 'weak': return 'bg-red-500'
    default: return 'bg-gray-300'
  }
})

// Validate token on mount
const validateToken = async () => {
  if (!token.value) {
    tokenValid.value = false
    validatingToken.value = false
    return
  }

  try {
    const response = await api.post('/users/password-reset/validate-token', {
      token: token.value
    }) as { is_valid: boolean; user_email?: string; expires_at?: string }

    tokenValid.value = response.is_valid
    userEmail.value = response.user_email || null
  } catch (err: any) {
    console.error('Token validation failed:', err)
    tokenValid.value = false
  } finally {
    validatingToken.value = false
  }
}

// Check password strength
const checkPasswordStrength = async () => {
  if (!password.value || password.value.length < 3) {
    passwordStrength.value = null
    return
  }

  try {
    const response = await api.post('/users/password-strength-check', {
      password: password.value
    }) as { is_valid: boolean; errors: string[]; strength: string; score: number; suggestions?: string[] }
    passwordStrength.value = response
  } catch (err: any) {
    console.error('Password strength check failed:', err)
  }
}

// Handle form submission
const handleSubmit = async () => {
  if (!isFormValid.value) return

  loading.value = true
  error.value = null

  try {
    const response = await api.post('/users/password-reset/confirm', {
      token: token.value,
      new_password: password.value
    }) as { success: boolean; message: string; password_strength?: string }

    if (response.success) {
      resetSuccess.value = true
      notify.success(t('passwordResetConfirm.successTitle'))
    }
  } catch (err: any) {
    console.error('Password reset failed:', err)
    
    if (err.status === 400 && err.data?.detail?.errors) {
      error.value = err.data.detail.errors.join(', ')
    } else {
      error.value = err.message || t('passwordResetConfirm.resetError')
    }
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  validateToken()
})

// SEO and meta
useHead({
  title: t('passwordResetConfirm.pageTitle'),
  meta: [
    { name: 'description', content: t('passwordResetConfirm.pageDescription') }
  ]
})
</script>
