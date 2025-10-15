<template>
  <div class="container mx-auto py-8 px-4">
    <h1 class="text-2xl font-bold mb-6">Notifications Test Page</h1>
    
    <!-- Connection Status -->
    <div class="mb-6 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <h2 class="text-lg font-semibold mb-2">Connection Status</h2>
      <div class="flex items-center space-x-2">
        <span 
          class="w-3 h-3 rounded-full"
          :class="{
            'bg-green-500': connectionStatus === 'connected',
            'bg-yellow-500': connectionStatus === 'connecting',
            'bg-orange-500': connectionStatus === 'polling',
            'bg-gray-400': connectionStatus === 'disconnected'
          }"
        ></span>
        <span class="capitalize">{{ connectionStatus }}</span>
      </div>
    </div>
    
    <!-- Notifications Count -->
    <div class="mb-6 p-4 bg-blue-100 dark:bg-blue-900 rounded-lg">
      <h2 class="text-lg font-semibold mb-2">Notifications Summary</h2>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Total Notifications</p>
          <p class="text-2xl font-bold">{{ notifications.length }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600 dark:text-gray-400">Unread Count</p>
          <p class="text-2xl font-bold text-red-600">{{ unreadCount }}</p>
        </div>
      </div>
    </div>
    
    <!-- Notifications List -->
    <div class="mb-6">
      <h2 class="text-lg font-semibold mb-4">All Notifications</h2>
      <div v-if="notifications.length === 0" class="text-center text-gray-400 py-8">
        <UIcon name="i-heroicons-bell" class="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No notifications found</p>
      </div>
      <div v-else class="space-y-3">
        <div v-for="n in notifications" :key="n.id" class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <UIcon 
                :name="n.status === 'unread' ? 'i-heroicons-dot' : 'i-heroicons-check-circle'" 
                :class="n.status === 'unread' ? 'text-blue-500' : 'text-gray-400'" 
                class="w-5 h-5 mt-0.5 flex-shrink-0" 
              />
              <div>
                <p class="text-sm text-gray-900 dark:text-white" :class="{ 'font-semibold': n.status === 'unread' }">
                  {{ n.message }}
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(n.created_at) }}</p>
                <p class="text-xs text-gray-400 mt-1">ID: {{ n.id }} | Status: {{ n.status }}</p>
              </div>
            </div>
            <UButton 
              v-if="n.status === 'unread'" 
              size="xs" 
              variant="outline" 
              @click="markAsRead(n)"
            >
              Mark as Read
            </UButton>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Test Actions -->
    <div class="p-4 bg-green-100 dark:bg-green-900 rounded-lg">
      <h2 class="text-lg font-semibold mb-4">Test Actions</h2>
      <div class="space-x-4">
        <UButton @click="refreshNotifications" variant="outline">
          Refresh Notifications
        </UButton>
        <UButton @click="testMarkAllAsRead" variant="outline">
          Mark All as Read
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useNotifications } from '~/composables/useNotifications'

const { notifications, unreadCount, connectionStatus, markAsRead, formatDate } = useNotifications()

// Test functions
const refreshNotifications = async () => {
  
  // The useNotifications composable handles fetching automatically
  // This is just for testing the UI
}

const testMarkAllAsRead = async () => {
  
  for (const notification of notifications.value) {
    if (notification.status === 'unread') {
      await markAsRead(notification)
    }
  }
}
</script> 