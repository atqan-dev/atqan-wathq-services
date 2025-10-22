<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Service Header -->
      <div class="mb-8">
        <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
          <NuxtLink to="/wathq" class="hover:text-gray-900 dark:hover:text-white">
            {{ t('wathq.services.title') }}
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          <span class="text-gray-900 dark:text-white">{{ serviceName }}</span>
        </div>
        
        <div class="flex items-start justify-between">
          <div class="flex items-start gap-4">
            <div class="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center p-2">
              <img 
                :src="serviceImage" 
                :alt="serviceName"
                class="w-full h-full object-contain"
              />
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                {{ serviceName }}
              </h1>
              <p class="mt-2 text-gray-600 dark:text-gray-400">
                {{ serviceDescription }}
              </p>
            </div>
          </div>
          <UButton
            color="gray"
            variant="ghost"
            icon="i-heroicons-arrow-left"
            @click="navigateBack"
          >
            {{ t('common.back') }}
          </UButton>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.totalRequests') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                {{ stats.total_requests }}
              </p>
            </div>
            <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-blue-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.successful') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
                {{ stats.successful_requests }}
              </p>
            </div>
            <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.failed') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
                {{ stats.failed_requests }}
              </p>
            </div>
            <UIcon name="i-heroicons-x-circle" class="w-12 h-12 text-red-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.avgDuration') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
                {{ stats.average_duration_ms }}ms
              </p>
            </div>
            <UIcon name="i-heroicons-clock" class="w-12 h-12 text-purple-500" />
          </div>
        </UCard>
      </div>

      <!-- Tabs -->
      <UTabs v-model="selectedTab" :items="tabs" class="mb-6">
        <!-- Test API Tab -->
        <template #test>
          <!-- <div class="p-4 bg-red-100 border-2 border-red-500 rounded mb-4">
            <p class="font-bold">DEBUG: Tab #test is rendering!</p>
          </div> -->
          <UCard>
            <template #header>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('wathq.tabs.testApi') }}
              </h3>
            </template>
            
            <!-- <div class="p-4 bg-green-100 border-2 border-green-500 rounded mb-4">
              <p class="font-bold">DEBUG: Inside UCard, before slot</p>
            </div> -->
            
            <slot name="test-form"></slot>
            
            <!-- <div class="p-4 bg-purple-100 border-2 border-purple-500 rounded mt-4">
              <p class="font-bold">DEBUG: After slot</p>
            </div> -->
          </UCard>
        </template>

        <!-- Live Requests Tab -->
        <template #live>
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('wathq.tabs.liveRequests') }}
                </h3>
                <UButton
                  size="sm"
                  icon="i-heroicons-arrow-path"
                  @click="$emit('refresh-live')"
                >
                  {{ t('common.refresh') }}
                </UButton>
              </div>
            </template>
            
            <slot name="live-requests"></slot>
          </UCard>
        </template>

        <!-- Request Logs Tab -->
        <template #logs>
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('wathq.tabs.requestLogs') }}
                </h3>
                <UButton
                  size="sm"
                  icon="i-heroicons-arrow-path"
                  @click="$emit('refresh-logs')"
                >
                  {{ t('common.refresh') }}
                </UButton>
              </div>
            </template>
            
            <slot name="request-logs"></slot>
          </UCard>
        </template>

        <!-- Offline Requests Tab -->
        <template #offline>
          <UCard>
            <template #header>
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ t('wathq.tabs.offlineRequests') }}
                </h3>
                <UButton
                  size="sm"
                  icon="i-heroicons-arrow-path"
                  @click="$emit('refresh-offline')"
                >
                  {{ t('common.refresh') }}
                </UButton>
              </div>
            </template>
            
            <slot name="offline-requests"></slot>
          </UCard>
        </template>
      </UTabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '~/composables/useI18n'
import type { WathqStats } from '~/types/wathq'

interface Props {
  serviceName: string
  serviceDescription: string
  serviceIcon: string
  serviceImage: string
  stats: WathqStats
}

interface Emits {
  (e: 'refresh-live'): void
  (e: 'refresh-logs'): void
  (e: 'refresh-offline'): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

const router = useRouter()
const { t } = useI18n()

const selectedTab = ref(0)

const tabs = computed(() => [
  {
    slot: 'test',
    label: t('wathq.tabs.testApi'),
    icon: 'i-heroicons-beaker'
  },
  {
    slot: 'live',
    label: t('wathq.tabs.liveRequests'),
    icon: 'i-heroicons-signal'
  },
  {
    slot: 'logs',
    label: t('wathq.tabs.requestLogs'),
    icon: 'i-heroicons-document-text'
  },
  {
    slot: 'offline',
    label: t('wathq.tabs.offlineRequests'),
    icon: 'i-heroicons-archive-box'
  }
])

function navigateBack() {
  router.push('/wathq')
}
</script>
