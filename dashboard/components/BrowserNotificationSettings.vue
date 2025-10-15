<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
      🔔 Browser Notifications
    </h3>
    
    <!-- Not Supported -->
    <div v-if="!isSupported" class="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span class="text-sm text-yellow-800 dark:text-yellow-200">
          Browser notifications are not supported in this browser.
        </span>
      </div>
    </div>

    <!-- Supported -->
    <div v-else class="space-y-4">
      <!-- Permission Status -->
      <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0 mr-3">
            <div v-if="permission === 'granted'" class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div v-else-if="permission === 'denied'" class="w-3 h-3 bg-red-500 rounded-full"></div>
            <div v-else class="w-3 h-3 bg-yellow-500 rounded-full"></div>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
              Permission Status
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ permissionStatusText }}
            </p>
          </div>
        </div>
        
        <!-- Request Permission Button -->
        <button
          v-if="canRequestPermission"
          @click="handleRequestPermission"
          :disabled="isRequesting"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-md transition-colors"
        >
          {{ isRequesting ? 'Requesting...' : 'Allow Notifications' }}
        </button>
      </div>

      <!-- Enable/Disable Toggle -->
      <div v-if="hasPermission" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            Browser Notifications
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Show desktop notifications for new alerts
          </p>
        </div>
        
        <label class="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            :checked="isEnabled"
            @change="handleToggle"
            class="sr-only peer"
          >
          <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
        </label>
      </div>

      <!-- Test Notification -->
      <div v-if="shouldShowNotifications" class="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
        <div>
          <p class="text-sm font-medium text-green-800 dark:text-green-200">
            Test Notifications
          </p>
          <p class="text-xs text-green-600 dark:text-green-300">
            Send a test notification to verify everything works
          </p>
        </div>
        
        <button
          @click="handleTest"
          :disabled="isTesting"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white text-sm font-medium rounded-md transition-colors"
        >
          {{ isTesting ? 'Sending...' : 'Test' }}
        </button>
      </div>

      <!-- Permission Denied Help -->
      <div v-if="permission === 'denied'" class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-500 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="text-sm font-medium text-red-800 dark:text-red-200 mb-1">
              Notifications Blocked
            </p>
            <p class="text-xs text-red-600 dark:text-red-300 mb-2">
              To enable notifications, you need to allow them in your browser settings:
            </p>
            <ul class="text-xs text-red-600 dark:text-red-300 space-y-1 ml-4">
              <li>• Click the lock/info icon in your address bar</li>
              <li>• Select "Allow" for notifications</li>
              <li>• Refresh this page</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBrowserNotifications } from '~/composables/useBrowserNotifications'

const {
  permission,
  isSupported,
  isEnabled,
  canRequestPermission,
  hasPermission,
  shouldShowNotifications,
  requestPermission,
  setEnabled,
  testNotification
} = useBrowserNotifications()

// Local state
const isRequesting = ref(false)
const isTesting = ref(false)

// Computed properties
const permissionStatusText = computed(() => {
  switch (permission.value) {
    case 'granted':
      return 'Notifications are allowed'
    case 'denied':
      return 'Notifications are blocked'
    default:
      return 'Permission not requested'
  }
})

// Methods
async function handleRequestPermission() {
  isRequesting.value = true
  try {
    const granted = await requestPermission()
    if (granted) {
      // Auto-enable notifications when permission is granted
      setEnabled(true)
    }
  } finally {
    isRequesting.value = false
  }
}

function handleToggle(event: Event) {
  const target = event.target as HTMLInputElement
  setEnabled(target.checked)
}

async function handleTest() {
  isTesting.value = true
  try {
    testNotification()
    // Give some time for the notification to show
    await new Promise(resolve => setTimeout(resolve, 1000))
  } finally {
    isTesting.value = false
  }
}
</script>
