<template>
  <div class="container mx-auto py-8 px-4">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-4">
        <h1 class="text-2xl font-bold mb-2">{{t('notifications.title')}}</h1>
        <!-- Connection status indicator -->
        <div class="flex items-center space-x-2 text-sm">
          <span 
            class="w-2 h-2 rounded-full dark:bg-gray-400 p-1"
            :class="{
              'bg-green-500': connectionStatus === 'connected',
              'bg-yellow-500': connectionStatus === 'connecting',
              'bg-orange-500': connectionStatus === 'polling',
              'bg-gray-400': connectionStatus === 'disconnected'
            }"
          ></span>
          <span class="text-gray-600 dark:text-gray-400 capitalize">{{ connectionStatus }}</span>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <UButton 
          v-if="unreadCount > 0"
          size="sm" 
          variant="outline" 
          @click="markAllAsRead"
          class="flex-shrink-0"
        >
          {{ t('notifications.markAllAsRead') }}
        </UButton>
        <USelectMenu v-model="statusFilter" :options="statusOptions"  class="w-80" />
      </div>
    </div>
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-bell" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <span class="text-sm font-medium text-blue-900 dark:text-blue-100" >{{ t('notifications.total') }}</span>
        </div>
        <p class="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-1">{{ notifications.length }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-dot" class="w-5 h-5 text-red-600 dark:text-red-400" />
          <span class="text-sm font-medium text-red-900 dark:text-red-100">{{ t('notifications.unread') }}</span>
        </div>
        <p class="text-2xl font-bold text-red-900 dark:text-red-100 mt-1">{{ unreadCount }}</p>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-green-600 dark:text-green-400" />
          <span class="text-sm font-medium text-green-900 dark:text-green-100">{{ t('notifications.read') }}</span>
        </div>
        <p class="text-2xl font-bold text-green-900 dark:text-green-100 mt-1">{{ notifications.length - unreadCount }}</p>
      </div>
    </div>

    <!-- Notifications List -->
    <div v-if="filteredNotifications.length === 0" class="text-center text-gray-400 py-12">
      <UIcon name="i-heroicons-bell" class="w-16 h-16 mx-auto mb-4 text-gray-300" />
      <p class="text-lg font-medium">{{ t('notifications.noNotifications') }}</p>
      <p class="text-sm text-gray-500 mt-1">{{ t('notifications.allCaughtUp') }}</p>
    </div>
    <div v-else class="space-y-3">
      <div v-for="n in filteredNotifications" :key="n.id" class="flex items-start space-x-3 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
        <UIcon :name="n.status === 'unread' ? 'i-heroicons-dot' : 'i-heroicons-check-circle'" :class="n.status === 'unread' ? 'text-blue-500' : 'text-gray-400'" class="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div class="flex-1 min-w-0">
          <div class="text-base text-gray-900 dark:text-white" :class="{ 'font-semibold': n.status === 'unread' }">{{ n.message }}</div>
          <div class="text-sm text-gray-500 mt-1">{{ formatDate(n.created_at) }}</div>
          <div class="text-xs text-gray-400 mt-1">ID: {{ n.id }}</div>
        </div>
        <div class="flex items-center space-x-2">
          <UButton 
            v-if="n.status === 'unread'" 
            size="xs" 
            variant="outline" 
            @click="markAsRead(n)"
            class="flex-shrink-0"
          >
            {{ t('notifications.markAsRead') }}
          </UButton>
          <!-- <UButton 
            v-else 
            size="xs" 
            variant="ghost" 
            @click="markAsUnread(n)"
            class="flex-shrink-0"
          >
            {{ t('notifications.markAsUnread') }}
          </UButton> -->
        </div>
      </div>
    </div>
  </div>
</template>

// Page meta
definePageMeta({
  middleware: 'auth'
})

<script setup>
import { ref, computed } from 'vue'
import { useNotifications } from '~/composables/useNotifications'

const { t } = useI18n()

const { notifications, unreadCount, connectionStatus, markAsRead, formatDate } = useNotifications()

const statusFilter = ref('all')
const statusOptions = computed(() => [
  { label: t('notifications.all'), value: 'all' },
  { label: t('notifications.unread'), value: 'unread' },
  { label: t('notifications.read'), value: 'read' }
])

const filteredNotifications = computed(() => {
  let filterValue = statusFilter.value
  if (typeof filterValue === 'object' && filterValue !== null) {
    filterValue = filterValue.value
  }
  if (filterValue === 'all') return notifications.value
  return notifications.value.filter(n => {
    const status = (n.status || '').toLowerCase()
    return status === String(filterValue).toLowerCase()
  })
})

// Mark all notifications as read
const markAllAsRead = async () => {
  try {
    const unreadNotifications = notifications.value.filter(n => n.status === 'unread')
    for (const notification of unreadNotifications) {
      await markAsRead(notification)
    }
    
  } catch (error) {
    console.error('Error marking all notifications as read:', error)
  }
}
</script> 