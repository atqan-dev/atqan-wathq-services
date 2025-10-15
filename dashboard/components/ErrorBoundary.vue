<template>
  <div class="error-boundary">
    <!-- Critical Error State -->
    <div v-if="error && error.type === 'critical'" class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div class="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
        <div class="w-16 h-16 mx-auto mb-6 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-600 dark:text-red-400" />
        </div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Something went wrong
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ error.message || 'An unexpected error occurred. Please try refreshing the page.' }}
        </p>
        <div class="space-y-3">
          <UButton @click="retry" :loading="retrying" class="w-full">
            Try Again
          </UButton>
          <UButton @click="reload" variant="outline" class="w-full">
            Reload Page
          </UButton>
        </div>
        <details v-if="error.details && showDetails" class="mt-6 text-left">
          <summary class="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
            Technical Details
          </summary>
          <pre class="mt-2 text-xs bg-gray-100 dark:bg-gray-700 p-3 rounded overflow-auto">{{ error.details }}</pre>
        </details>
        <button 
          v-if="error.details && !showDetails"
          @click="showDetails = true"
          class="mt-4 text-xs text-gray-400 hover:text-gray-600"
        >
          Show technical details
        </button>
      </div>
    </div>

    <!-- Inline Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-start space-x-3">
        <UIcon name="i-heroicons-exclamation-circle" class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
        <div class="flex-1 min-w-0">
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
            {{ error.title || 'Error' }}
          </h3>
          <p class="mt-1 text-sm text-red-700 dark:text-red-300">
            {{ error.message || 'An error occurred while processing your request.' }}
          </p>
          <div v-if="error.action" class="mt-3">
            <UButton 
              @click="handleAction" 
              size="sm" 
              color="red" 
              variant="outline"
              :loading="actionLoading"
            >
              {{ error.action.label }}
            </UButton>
          </div>
        </div>
        <button 
          @click="dismiss"
          class="flex-shrink-0 text-red-400 hover:text-red-600"
        >
          <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Success State -->
    <slot v-else />
  </div>
</template>

<script setup>
const props = defineProps({
  error: {
    type: Object,
    default: null
  },
  onRetry: {
    type: Function,
    default: null
  },
  onDismiss: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['retry', 'dismiss', 'action'])

const retrying = ref(false)
const actionLoading = ref(false)
const showDetails = ref(false)

const retry = async () => {
  retrying.value = true
  try {
    if (props.onRetry) {
      await props.onRetry()
    }
    emit('retry')
  } finally {
    retrying.value = false
  }
}

const dismiss = () => {
  if (props.onDismiss) {
    props.onDismiss()
  }
  emit('dismiss')
}

const reload = () => {
  window.location.reload()
}

const handleAction = async () => {
  if (!props.error?.action?.handler) return
  
  actionLoading.value = true
  try {
    await props.error.action.handler()
    emit('action')
  } finally {
    actionLoading.value = false
  }
}
</script>
