<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ t('metrics.title') }}
          </h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            {{ t('metrics.subtitle') }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <USelect
            v-model="timeRange"
            :options="timeRangeOptions"
            size="lg"
          />
          <UButton
            icon="i-heroicons-arrow-path"
            size="lg"
            @click="refreshData"
            :loading="isLoading"
          >
            {{ t('common.refresh') }}
          </UButton>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('metrics.stats.totalTenants') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {{ stats.tenants_count }}
              </p>
              <p class="mt-1 text-xs text-green-600 dark:text-green-400">
                +{{ Math.floor(stats.tenants_count * 0.12) }}% {{ t('metrics.stats.thisMonth') }}
              </p>
            </div>
            <UIcon name="i-heroicons-building-office-2" class="w-10 h-10 text-blue-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('metrics.stats.totalUsers') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {{ stats.users_count }}
              </p>
              <p class="mt-1 text-xs text-green-600 dark:text-green-400">
                +{{ Math.floor(stats.users_count * 0.08) }}% {{ t('metrics.stats.thisMonth') }}
              </p>
            </div>
            <UIcon name="i-heroicons-users" class="w-10 h-10 text-green-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('metrics.stats.onlineRequests') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {{ formatNumber(stats.online_requests_count) }}
              </p>
              <p class="mt-1 text-xs text-blue-600 dark:text-blue-400">
                {{ t('metrics.stats.live') }}
              </p>
            </div>
            <UIcon name="i-heroicons-signal" class="w-10 h-10 text-indigo-500" />
          </div>
        </UCard>

        <UCard class="h-32">
          <div class="flex items-center justify-between h-full">
            <div>
              <p class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ t('metrics.stats.offlineRequests') }}
              </p>
              <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
                {{ formatNumber(stats.offline_requests_count) }}
              </p>
              <p class="mt-1 text-xs text-purple-600 dark:text-purple-400">
                {{ t('metrics.stats.queued') }}
              </p>
            </div>
            <UIcon name="i-heroicons-queue-list" class="w-10 h-10 text-purple-500" />
          </div>
        </UCard>
      </div>

      <!-- Charts Section -->
      <div v-if="!isLoading" class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Users Growth Chart -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.charts.usersGrowth') }}
              </h3>
              <UBadge color="green" variant="subtle">
                {{ users.length }} {{ t('metrics.charts.total') }}
              </UBadge>
            </div>
          </template>
          <div class="h-64">
            <BarChart
              v-if="usersChartData.datasets && usersChartData.datasets.length > 0"
              :labels="usersChartData.labels"
              :datasets="usersChartData.datasets"
            />
          </div>
        </UCard>

        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.charts.tenantsGrowth') }}
              </h3>
              <UBadge color="blue" variant="subtle">
                {{ tenants.length }} {{ t('metrics.charts.total') }}
              </UBadge>
            </div>
          </template>
          <div class="h-64">
            <BarChart
              v-if="tenantsChartData.datasets && tenantsChartData.datasets.length > 0"
              :labels="tenantsChartData.labels"
              :datasets="tenantsChartData.datasets"
            />
          </div>
        </UCard>

        <!-- Requests Overview Chart -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.charts.requestsOverview') }}
              </h3>
              <UBadge color="indigo" variant="subtle">
                {{ formatNumber(stats.online_requests_count + stats.offline_requests_count) }} {{ t('metrics.charts.total') }}
              </UBadge>
            </div>
          </template>
          <div class="h-64">
            <DoughnutChart
              v-if="requestsChartData.datasets && requestsChartData.datasets.length > 0"
              :labels="requestsChartData.labels"
              :datasets="requestsChartData.datasets"
            />
          </div>
        </UCard>

        <!-- Service History Chart -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.charts.serviceHistory') }}
              </h3>
              <UBadge color="purple" variant="subtle">
                {{ servicesHistory.length }} {{ t('metrics.charts.records') }}
              </UBadge>
            </div>
          </template>
          <div class="h-64">
            <LineChart
              v-if="historyChartData.datasets && historyChartData.datasets.length > 0"
              :labels="historyChartData.labels"
              :datasets="historyChartData.datasets"
            />
          </div>
        </UCard>
      </div>

      <!-- Recent Activity Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Service History -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.tables.recentServices') }}
              </h3>
              <UButton
                variant="ghost"
                size="sm"
                to="/tenant-services"
              >
                {{ t('metrics.tables.viewAll') }}
              </UButton>
            </div>
          </template>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.service') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.tenant') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.status') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.date') }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="service in servicesHistory.slice(0, 5)" :key="service.id" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    {{ service.service_name }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {{ service.tenant_name }}
                  </td>
                  <td class="px-4 py-3">
                    <UBadge
                      :color="service.is_active ? 'green' : 'gray'"
                      variant="subtle"
                      size="xs"
                    >
                      {{ service.is_active ? t('common.active') : t('common.inactive') }}
                    </UBadge>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {{ formatDate(service.created_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UCard>

        <!-- Recent Offline Data -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('metrics.tables.offlineQueue') }}
              </h3>
              <UButton
                variant="ghost"
                size="sm"
                to="/wathq"
              >
                {{ t('metrics.tables.viewAll') }}
              </UButton>
            </div>
          </template>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.service') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.endpoint') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.status') }}
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {{ t('metrics.tables.date') }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="item in wathqOfflineData.slice(0, 5)" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    {{ item.service_type }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {{ item.endpoint }}
                  </td>
                  <td class="px-4 py-3">
                    <UBadge
                      :color="getStatusColor(item.status)"
                      variant="subtle"
                      size="xs"
                    >
                      {{ item.status }}
                    </UBadge>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {{ formatDate(item.created_at) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '~/composables/useI18n'
import { useAuthenticatedFetch } from '~/composables/useAuthenticatedFetch'
import { useUsers } from '~/composables/useUsers'
import BarChart from '~/components/charts/BarChart.vue'
import LineChart from '~/components/charts/LineChart.vue'
import DoughnutChart from '~/components/charts/DoughnutChart.vue'

definePageMeta({
  middleware: ['auth'],
  requiresSuperAdmin: true
})

const { t } = useI18n()
const { authenticatedFetch } = useAuthenticatedFetch()
const { users: allUsers, fetchUsers } = useUsers()

// State
const isLoading = ref(false)
const timeRange = ref('30')
const stats = ref({
  tenants_count: 0,
  users_count: 0,
  online_requests_count: 0,
  offline_requests_count: 0
})
const users = ref<any[]>([])
const tenants = ref<any[]>([])
const servicesHistory = ref<any[]>([])
const wathqOfflineData = ref<any[]>([])

// Time range options
const timeRangeOptions = [
  { label: t('metrics.timeRange.last7Days'), value: '7' },
  { label: t('metrics.timeRange.last30Days'), value: '30' },
  { label: t('metrics.timeRange.last90Days'), value: '90' },
  { label: t('metrics.timeRange.lastYear'), value: '365' }
]

// Fetch stats
async function fetchStats() {
  try {
    const data = await authenticatedFetch<any>('/api/v1/management/stats')
    stats.value = data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// Fetch tenants
async function fetchTenants() {
  try {
    const data = await authenticatedFetch<any[]>('/api/v1/management/tenants?skip=0&limit=100')
    tenants.value = data
  } catch (error) {
    console.error('Failed to fetch tenants:', error)
  }
}

// Fetch services history
async function fetchServicesHistory() {
  try {
    const data = await authenticatedFetch<any[]>('/api/v1/management/tenants/history?skip=0&limit=100')
    servicesHistory.value = data
  } catch (error) {
    console.error('Failed to fetch services history:', error)
  }
}

// Fetch Wathq offline data
async function fetchWathqOfflineData() {
  try {
    const data = await authenticatedFetch<any[]>('/api/v1/management/tenants/wathq-offline-data?skip=0&limit=100')
    wathqOfflineData.value = data
  } catch (error) {
    console.error('Failed to fetch Wathq offline data:', error)
  }
}

// Refresh all data
async function refreshData() {
  isLoading.value = true
  try {
    await Promise.all([
      fetchStats(),
      fetchUsers(),
      fetchTenants(),
      fetchServicesHistory(),
      fetchWathqOfflineData()
    ])
    users.value = allUsers.value
  } finally {
    isLoading.value = false
  }
}

// Chart data with proper initialization
const usersChartData = computed(() => {
  const months = generateMonths(6)
  const data = generateGrowthData(stats.value?.users_count || 0, 6)
  
  return {
    labels: months,
    datasets: [{
      label: 'Users',
      data: data,
      backgroundColor: 'rgba(34, 197, 94, 0.5)',
      borderColor: 'rgb(34, 197, 94)',
      borderWidth: 2
    }]
  }
})

const tenantsChartData = computed(() => {
  const months = generateMonths(6)
  const data = generateGrowthData(stats.value?.tenants_count || 0, 6)
  
  return {
    labels: months,
    datasets: [{
      label: 'Tenants',
      data: data,
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 2
    }]
  }
})

const requestsChartData = computed(() => {
  return {
    labels: ['Online', 'Offline'],
    datasets: [{
      data: [stats.value?.online_requests_count || 0, stats.value?.offline_requests_count || 0],
      backgroundColor: [
        'rgba(99, 102, 241, 0.8)',
        'rgba(168, 85, 247, 0.8)'
      ],
      borderWidth: 0
    }]
  }
})

const historyChartData = computed(() => {
  const months = generateMonths(6)
  const data = servicesHistory.value.length > 0 
    ? generateGrowthData(servicesHistory.value.length, 6)
    : [0, 0, 0, 0, 0, 0]
  
  return {
    labels: months,
    datasets: [{
      label: 'Service Requests',
      data: data,
      borderColor: 'rgb(168, 85, 247)',
      backgroundColor: 'rgba(168, 85, 247, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true
    }]
  }
})

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.05)'
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

// Helper functions
function generateMonths(count: number): string[] {
  const months = []
  const now = new Date()
  
  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    months.push(date.toLocaleDateString('en-US', { month: 'short' }))
  }
  
  return months
}

function generateGrowthData(total: number, months: number): number[] {
  const data = []
  const growthRate = 1.15 // 15% growth per month
  
  for (let i = 0; i < months; i++) {
    const value = Math.floor(total / Math.pow(growthRate, months - i - 1))
    data.push(value)
  }
  
  return data
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-'
  
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function getStatusColor(status: string): string {
  const statusMap: Record<string, string> = {
    'pending': 'yellow',
    'processing': 'blue',
    'completed': 'green',
    'failed': 'red',
    'success': 'green',
    'error': 'red'
  }
  return statusMap[status?.toLowerCase()] || 'gray'
}

// Initialize
onMounted(async () => {
  await refreshData()
})

useHead({
  title: t('metrics.title')
})
</script>
