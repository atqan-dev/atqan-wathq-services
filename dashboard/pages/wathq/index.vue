<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('wathq.title') }}
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('wathq.subtitle') }}
        </p>
      </div>

      <!-- Global Stats -->
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
                {{ t('wathq.stats.today') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
                {{ stats.requests_today }}
              </p>
            </div>
            <UIcon name="i-heroicons-calendar" class="w-12 h-12 text-green-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.thisWeek') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
                {{ stats.requests_this_week }}
              </p>
            </div>
            <UIcon name="i-heroicons-clock" class="w-12 h-12 text-purple-500" />
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('wathq.stats.avgDuration') }}
              </p>
              <p class="mt-2 text-3xl font-bold text-orange-600 dark:text-orange-400">
                {{ stats.average_duration_ms }}ms
              </p>
            </div>
            <UIcon name="i-heroicons-lightning-bolt" class="w-12 h-12 text-orange-500" />
          </div>
        </UCard>
      </div>

      <!-- Services Grid -->
      <div class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {{ t('wathq.services.available') }}
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <UCard
            v-for="service in services"
            :key="service.id"
            class="hover:shadow-lg transition-all cursor-pointer group"
            @click="navigateToService(service.slug)"
          >
            <div class="flex items-start gap-4">
              <div class="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform p-2">
                <img 
                  :src="getServiceImage(service.slug)" 
                  :alt="currentLocale === 'ar' ? service.name_ar : service.name"
                  class="w-full h-full object-contain"
                />
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 dark:text-white mb-1">
                  {{ currentLocale === 'ar' ? service.name_ar : service.name }}
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                  {{ currentLocale === 'ar' ? service.description_ar : service.description }}
                </p>
                <div class="mt-3 flex items-center gap-2">
                  <UBadge
                    :color="service.is_active ? 'green' : 'red'"
                    variant="subtle"
                    size="sm"
                  >
                    {{ service.is_active ? t('common.active') : t('common.inactive') }}
                  </UBadge>
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    <UIcon name="i-heroicons-arrow-right" class="w-3 h-3" />
                  </span>
                </div>
              </div>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Recent Activity -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ t('wathq.recentActivity') }}
            </h2>
            <UButton
              size="sm"
              icon="i-heroicons-arrow-path"
              :loading="isLoading"
              @click="handleRefresh"
            >
              {{ t('common.refresh') }}
            </UButton>
          </div>
        </template>

        <RequestLogsTable :requests="requests.slice(0, 10)" :is-loading="isLoading" />
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '~/composables/useI18n'
import { useWathqServices } from '~/composables/useWathqServices'
import RequestLogsTable from '~/components/wathq/RequestLogsTable.vue'
import type { WathqServiceType } from '~/types/wathq'

// Page meta
definePageMeta({
  middleware: ['auth']
})

const router = useRouter()
const { t, locale } = useI18n()

const currentLocale = computed(() => locale.value)

const {
  services,
  requests,
  stats,
  isLoading,
  fetchServices,
  fetchRequests
} = useWathqServices()

function getServiceImage(slug: WathqServiceType): string {
  const imageMap: Record<WathqServiceType, string> = {
    'commercial-registration': '/commercial_registration.svg',
    'company-contract': '/commercial_registration.svg', // fallback to commercial registration
    'attorney': '/attorney.svg',
    'real-estate': '/real_estates_deeds.svg',
    'spl-national-address': '/national_address.svg',
    'employee': '/employee_information.svg'
  }
  return imageMap[slug] || '/favicon.svg'
}

function navigateToService(slug: WathqServiceType) {
  router.push(`/wathq/${slug}`)
}

async function handleRefresh() {
  try {
    await fetchRequests()
  } catch (error) {
    console.log('Requests not available yet')
  }
}

onMounted(async () => {
  await fetchServices()
  // Don't fetch requests on mount to avoid 404 errors
  // await fetchRequests()
})

useHead({
  title: t('wathq.title')
})
</script>
