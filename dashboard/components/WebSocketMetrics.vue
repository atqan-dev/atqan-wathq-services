<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ t('websocket.metrics.title') }}
        </h3>
        <div class="flex items-center gap-2">
          <div
            :class="[
              'w-2 h-2 rounded-full',
              metrics ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
            ]"
          />
          <span class="text-sm text-gray-600 dark:text-gray-400">
            {{ metrics ? t('websocket.metrics.connected') : t('websocket.metrics.disconnected') }}
          </span>
        </div>
      </div>
    </template>

    <div v-if="isLoading && !metrics" class="flex items-center justify-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <div v-else-if="error" class="text-center py-8">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500 mx-auto mb-2" />
      <p class="text-sm text-gray-600 dark:text-gray-400">{{ error }}</p>
      <UButton size="sm" class="mt-4" @click="fetchMetrics">
        {{ t('common.retry') }}
      </UButton>
    </div>

    <div v-else-if="metrics" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- Active Connections -->
      <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-signal" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {{ metrics.active_connections }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.activeConnections') }}
        </p>
      </div>

      <!-- Connected Users -->
      <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-users" class="w-5 h-5 text-green-600 dark:text-green-400" />
          <span class="text-2xl font-bold text-green-600 dark:text-green-400">
            {{ metrics.connected_users }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.connectedUsers') }}
        </p>
      </div>

      <!-- Management Users -->
      <div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <span class="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {{ metrics.connected_management_users }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.managementUsers') }}
        </p>
      </div>

      <!-- Connected Tenants -->
      <div class="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-building-office" class="w-5 h-5 text-orange-600 dark:text-orange-400" />
          <span class="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {{ metrics.connected_tenants }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.connectedTenants') }}
        </p>
      </div>

      <!-- Total Messages -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ metrics.total_messages_sent.toLocaleString() }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.messagesSent') }}
        </p>
      </div>

      <!-- Total Connections -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-arrow-up-tray" class="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ metrics.total_connections.toLocaleString() }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.totalConnections') }}
        </p>
      </div>

      <!-- Error Rate -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon
            :name="getErrorRate() > 5 ? 'i-heroicons-exclamation-circle' : 'i-heroicons-check-circle'"
            :class="[
              'w-5 h-5',
              getErrorRate() > 5 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'
            ]"
          />
          <span
            :class="[
              'text-2xl font-bold',
              getErrorRate() > 5 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'
            ]"
          >
            {{ getErrorRate().toFixed(2) }}%
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.errorRate') }}
        </p>
      </div>

      <!-- Uptime -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <UIcon name="i-heroicons-clock" class="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <span class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatUptime(metrics.uptime_seconds) }}
          </span>
        </div>
        <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
          {{ t('websocket.metrics.uptime') }}
        </p>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useWebSocketMetrics } from '@/composables/useWebSocketMetrics'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

const {
  metrics,
  isLoading,
  error,
  fetchMetrics,
  startPolling,
  formatUptime,
  getErrorRate
} = useWebSocketMetrics()

// Start polling on mount (every 10 seconds)
onMounted(() => {
  startPolling(10000)
})
</script>
