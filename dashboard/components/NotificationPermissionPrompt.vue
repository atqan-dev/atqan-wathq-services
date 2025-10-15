<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div
      v-if="showPrompt"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click="handleDismiss"
    >
      <!-- Modal -->
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 transform transition-all"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center mb-4">
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mr-4">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM9 7H4l5-5v5zm6 10V7a1 1 0 00-1-1H5a1 1 0 00-1 1v10a1 1 0 001 1h9a1 1 0 001-1z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{  t('notificationPermissionPrompt.title') }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{  t('notificationPermissionPrompt.description') }}
            </p>
          </div>
        </div>

        <!-- Content -->
        <div class="mb-6">
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            {{  t('notificationPermissionPrompt.content') }}
          </p>
          
          <div class="space-y-3">
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{  t('notificationPermissionPrompt.deploymentStatusUpdates') }}
            </div>
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{  t('notificationPermissionPrompt.systemAlertsAndWarnings') }}
            </div>
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{  t('notificationPermissionPrompt.importantAppNotifications') }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3">
          <button
            @click="handleAllow"
            :disabled="isRequesting"
            class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            {{ isRequesting ? t('notificationPermissionPrompt.requesting') : t('notificationPermissionPrompt.allowNotifications') }}
          </button>
          <button
            @click="handleDismiss"
            class="flex-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 font-medium py-2 px-4 rounded-md transition-colors"
          >
            {{ t('notificationPermissionPrompt.maybeLater') }}
          </button>
        </div>

        <!-- Don't show again -->
        <div class="mt-4 text-center">
          <button
            @click="handleNeverShow"
            class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 underline"
          >
            {{ t('notificationPermissionPrompt.neverShow') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useNotificationPermissionPrompt } from '~/composables/useNotificationPermissionPrompt'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const {
  showPrompt,
  handleAllow: handleAllowPrompt,
  handleDismiss,
  handleNeverShow
} = useNotificationPermissionPrompt()

// Local state for UI
const isRequesting = ref(false)

// Methods
async function handleAllow() {
  isRequesting.value = true
  try {
    await handleAllowPrompt()
  } finally {
    isRequesting.value = false
  }
}
</script>
