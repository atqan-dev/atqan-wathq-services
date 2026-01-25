<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
          🔔 Browser Notifications Test
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Test and configure browser notifications for your SaaS app
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Settings Panel -->
        <div>
          <BrowserNotificationSettings />
        </div>

        <!-- Test Panel -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            🧪 Test Different Notifications
          </h3>
          
          <div class="space-y-4">
            <!-- System Notifications -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                System Notifications
              </h4>
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="testSystemNotification('info')"
                  class="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-blue-800 text-sm rounded-md transition-colors"
                >
                  📢 Info
                </button>
                <button
                  @click="testSystemNotification('success')"
                  class="px-3 py-2 bg-green-100 hover:bg-green-200 text-green-800 text-sm rounded-md transition-colors"
                >
                  ✅ Success
                </button>
                <button
                  @click="testSystemNotification('warning')"
                  class="px-3 py-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 text-sm rounded-md transition-colors"
                >
                  ⚠️ Warning
                </button>
                <button
                  @click="testSystemNotification('error')"
                  class="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-800 text-sm rounded-md transition-colors"
                >
                  ❌ Error
                </button>
              </div>
            </div>

            <!-- App Notifications -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                App-Specific Notifications
              </h4>
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="testAppNotification('deployment')"
                  class="px-3 py-2 bg-purple-100 hover:bg-purple-200 text-purple-800 text-sm rounded-md transition-colors"
                >
                  🚀 Deployment
                </button>
                <button
                  @click="testAppNotification('backup')"
                  class="px-3 py-2 bg-indigo-100 hover:bg-indigo-200 text-indigo-800 text-sm rounded-md transition-colors"
                >
                  💾 Backup
                </button>
                <button
                  @click="testAppNotification('alert')"
                  class="px-3 py-2 bg-orange-100 hover:bg-orange-200 text-orange-800 text-sm rounded-md transition-colors"
                >
                  🚨 Alert
                </button>
                <button
                  @click="testAppNotification('update')"
                  class="px-3 py-2 bg-cyan-100 hover:bg-cyan-200 text-cyan-800 text-sm rounded-md transition-colors"
                >
                  🔄 Update
                </button>
              </div>
            </div>

            <!-- Custom Notification -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Custom Notification
              </h4>
              <div class="space-y-2">
                <input
                  v-model="customTitle"
                  type="text"
                  placeholder="Notification title"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                <textarea
                  v-model="customMessage"
                  placeholder="Notification message"
                  rows="2"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                ></textarea>
                <button
                  @click="testCustomNotification"
                  :disabled="!customTitle || !customMessage"
                  class="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-md transition-colors"
                >
                  Send Custom Notification
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Integration Status -->
      <div class="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
          🔗 Integration Status
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Browser Notifications -->
          <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center mb-2">
              <div :class="[
                'w-3 h-3 rounded-full mr-2',
                shouldShowNotifications ? 'bg-green-500' : 'bg-red-500'
              ]"></div>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                Browser Notifications
              </span>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ shouldShowNotifications ? 'Active' : 'Inactive' }}
            </p>
          </div>

          <!-- In-App Notifications -->
          <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center mb-2">
              <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                In-App Notifications
              </span>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ connectionStatus === 'connected' ? 'WebSocket' : 'Polling' }}
            </p>
          </div>

          <!-- Slack Notifications -->
          <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div class="flex items-center mb-2">
              <div class="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                Slack Notifications
              </span>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              Available
            </p>
          </div>
        </div>
      </div>

      <!-- Back to Dashboard -->
      <div class="mt-8 text-center">
        <NuxtLink
          to="/"
          class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
        >
          ← Back to Dashboard
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useBrowserNotifications } from '~/composables/useBrowserNotifications'
import { useNotifications } from '~/composables/useNotifications'

// Browser notifications
const {
  shouldShowNotifications,
  notifySystemEvent,
  notifyAppEvent,
  showBrowserNotification
} = useBrowserNotifications()

// In-app notifications
const { connectionStatus } = useNotifications()

// Custom notification form
const customTitle = ref('')
const customMessage = ref('')

// Test functions
function testSystemNotification(type: 'info' | 'success' | 'warning' | 'error') {
  const messages = {
    info: 'This is an informational notification from your SaaS app.',
    success: 'Operation completed successfully! Everything is working perfectly.',
    warning: 'Please review this important warning message.',
    error: 'An error occurred that requires your attention.'
  }

  notifySystemEvent({
    message: messages[type],
    type,
    onClick: () => {
      console.log(`Clicked ${type} notification`)
    }
  })
}

function testAppNotification(appType: string) {
  const notifications = {
    deployment: {
      appName: 'My Web App',
      message: 'Deployment completed successfully to production environment.',
      type: 'success' as const
    },
    backup: {
      appName: 'Database Service',
      message: 'Daily backup completed. All data has been safely stored.',
      type: 'info' as const
    },
    alert: {
      appName: 'Monitoring System',
      message: 'High CPU usage detected. Please check your application.',
      type: 'warning' as const
    },
    update: {
      appName: 'API Service',
      message: 'New updates are available. Click to review changes.',
      type: 'info' as const
    }
  }

  const notification = notifications[appType as keyof typeof notifications]
  if (notification) {
    notifyAppEvent({
      ...notification,
      onClick: () => {
        console.log(`Clicked ${appType} app notification`)
      }
    })
  }
}

function testCustomNotification() {
  if (!customTitle.value || !customMessage.value) return

  showBrowserNotification({
    title: customTitle.value,
    message: customMessage.value,
    type: 'info',
    icon: '/favicon.ico',
    onClick: () => {
      console.log('Clicked custom notification')
    }
  })

  // Clear form
  customTitle.value = ''
  customMessage.value = ''
}

// Page meta
definePageMeta({
  title: 'Browser Notifications Test'
})
</script>
