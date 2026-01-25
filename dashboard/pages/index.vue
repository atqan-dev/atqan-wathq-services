<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
    <!-- Dashboard Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t("dashboard.title") }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          {{ t("dashboard.subtitle") }}
        </p>
      </div>
      <UButton icon="i-heroicons-arrow-path" @click="refreshAllData" :loading="isRefreshing">
        {{ t("dashboard.refresh") }}
      </UButton>
    </div>

    <!-- Stats Cards -->
    <div v-if="appsLoading" class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <SkeletonLoader v-for="i in 4" :key="i" type="stats" />
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <UCard>
        <div class="flex items-center" :class="isRTL ? 'rtl-space-x-3' : 'space-x-3'">
          <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
            <UIcon name="i-heroicons-user-group" class="w-6 h-6 text-green-600 dark:text-green-400" />
          </div>
          <div :class="isRTL ? 'rtl-text-right' : ''">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ apiStats.tenants_count }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ t("dashboard.stats.tenants_count") }}
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center" :class="isRTL ? 'rtl-space-x-3' : 'space-x-3'">
          <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
            <UIcon name="i-heroicons-user" class="w-6 h-6 text-red-600 dark:text-red-400" />
          </div>
          <div :class="isRTL ? 'rtl-text-right' : ''">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ apiStats.users_count }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ t("dashboard.stats.users_count") }}
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center" :class="isRTL ? 'rtl-space-x-3' : 'space-x-3'">
          <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <UIcon name="i-heroicons-server-stack" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div :class="isRTL ? 'rtl-text-right' : ''">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ apiStats.online_requests_count }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ t("dashboard.stats.online_requests_count") }}
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center" :class="isRTL ? 'rtl-space-x-3' : 'space-x-3'">
          <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
            <UIcon name="i-heroicons-table-cells" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div :class="isRTL ? 'rtl-text-right' : ''">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ apiStats.offline_requests_count }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ t("dashboard.stats.offline_requests_count") }}
            </p>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Online Services Chart -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t("dashboard.charts.onlineServicesTitle") }}
            </h3>
            <UBadge color="green" variant="subtle">
              {{ servicesHistory.length }} {{ t("dashboard.charts.requests") }}
            </UBadge>
          </div>
        </template>
        <div v-if="servicesHistoryLoading" class="h-[300px] flex items-center justify-center">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>
        <div v-else-if="onlineChartData.labels.length === 0" class="h-[300px] flex items-center justify-center">
          <div class="text-center">
            <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p class="text-gray-500 dark:text-gray-400">{{ t("dashboard.charts.noDataAvailable") }}</p>
          </div>
        </div>
        <div v-else class="h-[300px]">
          <LineChart
            :labels="onlineChartData.labels"
            :datasets="onlineChartData.datasets"
            :height="300"
          />
        </div>
      </UCard>

      <!-- Offline Services Chart -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t("dashboard.charts.offlineServicesTitle") }}
            </h3>
            <UBadge color="purple" variant="subtle">
              {{ wathqOfflineData.length }} {{ t("dashboard.charts.requests") }}
            </UBadge>
          </div>
        </template>
        <div v-if="wathqOfflineDataLoading" class="h-[300px] flex items-center justify-center">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
        </div>
        <div v-else-if="offlineChartData.labels.length === 0" class="h-[300px] flex items-center justify-center">
          <div class="text-center">
            <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p class="text-gray-500 dark:text-gray-400">{{ t("dashboard.charts.noDataAvailable") }}</p>
          </div>
        </div>
        <div v-else class="h-[300px]">
          <BarChart
            :labels="offlineChartData.labels"
            :datasets="offlineChartData.datasets"
            :height="300"
          />
        </div>
      </UCard>
    </div>

    <!-- Data Tables Section -->
    <div class="space-y-8">
      <!-- System Tenants Table -->
      <div>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t("dashboard.systemTenants") }}
          </h2>
          <div class="flex gap-2">
            <UButton variant="outline" size="sm" @click="refreshTenants" :loading="tenantsLoading">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
            </UButton>
            <NuxtLink to="/tenants">
              <UButton variant="outline" size="sm">{{
                t("dashboard.viewAllTenants")
                }}</UButton>
            </NuxtLink>
            <NuxtLink to="/tenants/create" class="btn btn-primary">
              <UButton icon="i-heroicons-plus" @click="router.push('/tenants/create')">
                {{ t("tenants.createTenant") }}
              </UButton>
            </NuxtLink>
          </div>
        </div>

        <UCard>
          <div v-if="tenantsLoading" class="space-y-4">
            <SkeletonLoader v-for="i in 5" :key="i" type="table-row" />
          </div>
          <div v-else-if="tenantsError" class="text-center py-8">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p class="text-gray-600 dark:text-gray-400">
              {{ t("dashboard.tenantsError") }}
            </p>
          </div>
          <div v-else>
            <UTable :rows="tenants" :columns="tenantColumns" :loading="tenantsLoading" class="w-full">
              <template #status-data="{ row }">
                <UBadge :color="row.is_active ? 'green' : 'red'" variant="subtle">
                  {{
                    row.is_active ? t("common.active") : t("common.inactive")
                  }}
                </UBadge>
              </template>
              <template #role-data="{ row }">
                <UBadge :color="row.is_super_admin ? 'purple' : 'blue'" variant="subtle">
                  {{
                    row.is_super_admin ? t("common.superuser") : t("common.regularUser")
                  }}
                </UBadge>
              </template>
              <template #actions-data="{ row }">
                <UButton variant="ghost" size="sm" @click="router.push(`/tenants/${row.id}`)" icon="i-heroicons-eye"
                  :title="t('common.view')" />
              </template>
            </UTable>
          </div>
        </UCard>
      </div>

      <!-- System servicesHistory Table -->
      <div>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t("dashboard.systemServicesHistory") }}
          </h2>
          <div class="flex gap-2">
            <UButton variant="outline" size="sm" @click="refreshServicesHistory" :loading="servicesHistoryLoading">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
            </UButton>
            <NuxtLink to="/services">
              <UButton variant="outline" size="sm">{{
                t("dashboard.viewAllServicesOnline")
                }}</UButton>
            </NuxtLink>
          </div>
        </div>

        <UCard>
          <div v-if="appsLoading" class="space-y-4">
            <SkeletonLoader v-for="i in 5" :key="i" type="table-row" />
          </div>
          <div v-else-if="servicesHistoryError" class="text-center py-8">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p class="text-gray-600 dark:text-gray-400">
              {{ t("dashboard.servicesHistoryError") }}
            </p>
          </div>
          <div v-else>
            <UTable :rows="servicesHistory" :columns="servicesHistoryColumns" :loading="servicesHistoryLoading"
              class="w-full">
              <template #port-data="{ row }">
                <span class="font-mono text-sm">{{ row.port || "N/A" }}</span>
              </template>

            </UTable>
          </div>
        </UCard>

      </div>

      <!-- System WathqOfflineData Table -->
      <div>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t("dashboard.systemWathqOfflineData") }}
          </h2>
          <div class="flex gap-2">
            <UButton variant="outline" size="sm" @click="refreshWathqOfflineData" :loading="wathqOfflineDataLoading">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
            </UButton>
            <NuxtLink to="/services">
              <UButton variant="outline" size="sm">{{
                t("dashboard.viewAllServicesOffline")
                }}</UButton>
            </NuxtLink>
          </div>
        </div>

        <UCard>
          <div v-if="appsLoading" class="space-y-4">
            <SkeletonLoader v-for="i in 5" :key="i" type="table-row" />
          </div>
          <div v-else-if="wathqOfflineDataError" class="text-center py-8">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p class="text-gray-600 dark:text-gray-400">
              {{ t("dashboard.wathqOfflineDataError") }}
            </p>
          </div>
          <div v-else>
            <UTable :rows="wathqOfflineData" :columns="wathqOfflineDataColumns" :loading="wathqOfflineDataLoading"
              class="w-full">
              <template #port-data="{ row }">
                <span class="font-mono text-sm">{{ row.port || "N/A" }}</span>
              </template>

            </UTable>
          </div>
        </UCard>

      </div>

    </div>
</div>
  </div>
</template>

<script setup lang="ts">
import type { Tenant, ServiceHistory } from "~/types/tenant";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import { useSettings } from "@/composables/useSettings";
import LineChart from "~/components/charts/LineChart.vue";
import BarChart from "~/components/charts/BarChart.vue";

// Page meta
definePageMeta({
  middleware: ["auth"],
});

// Import our custom i18n composable
const { t } = useI18n();
const { isRTL } = useLanguage();

// Get current user from auth store
const authStore = useAuthStore();
const user = computed(() => authStore.user);

const router = useRouter();

// Get auto-refresh settings
const { dashboardAutoRefresh, dashboardRefreshInterval } = useSettings();

// API stats data
const apiStats = ref<{ tenants_count: number; users_count: number; online_requests_count: number; offline_requests_count: number }>({
  tenants_count: 0,
  users_count: 0,
  online_requests_count: 0,
  offline_requests_count: 0,
});
const apiStatsLoading = ref(true);
const apiStatsError = ref(null);

// Tenants data
const tenants = ref<Tenant[]>([]);
const tenantsLoading = ref(true);
const tenantsError = ref(null);

// ServicesHistory data
const servicesHistory = ref<ServiceHistory[]>([]);
const servicesHistoryLoading = ref(false);
const servicesHistoryError = ref(null);

// WathqOfflineData data
const wathqOfflineData = ref<ServiceHistory[]>([]);
const wathqOfflineDataLoading = ref(false);
const wathqOfflineDataError = ref(null);

// Global loading state
const isRefreshing = ref(false);

// Check if user can manage processes (superuser only)
const canManageProcesses = computed(() => {
  return user.value?.is_super_admin || false;
});

// Loading state for apps (tenants)
const appsLoading = computed(() => tenantsLoading.value || servicesHistoryLoading.value);


const tenantColumns = [
  {
    key: "name",
    label: t("common.name"),
    sortable: true,
  },
  {
    key: "slug",
    label: t("common.slug"),
    sortable: true,
  },
  {
    key: "description",
    label: t("common.description"),
  },
  {
    key: "is_active",
    label: t("common.is_active"),
  },
  {
    key: "max_users",
    label: t("common.max_users"),
  },
  {
    key: "actions",
    label: t("common.actions"),
  },
];


const servicesHistoryColumns = [
  {
    key: "id",
    label: t("common.id"),
    sortable: true,
  },
  {
    key: "tenant_id",
    label: t("common.tenant_id"),
    sortable: true,
  },
  {
    key: "user_id",
    label: t("common.user_id"),
    sortable: true,
  },
  {
    key: "service_slug",
    label: t("common.slug"),
  },
  {
    key: "endpoint",
    label: t("common.endpoint"),
  },
  {
    key: "method",
    label: t("common.method"),
  },
  {
    key: "status_code",
    label: t("common.status_code"),
  },
  {
    key: "duration_ms",
    label: t("common.duration_ms"),
  },
  {
    key: "fetched_at",
    label: t("common.fetched_at"),
  },
];

const wathqOfflineDataColumns = [
  {
    key: "service_id",
    label: t("common.service_id"),
    sortable: true,
  },
  {
    key: "tenant_id",
    label: t("common.tenant_id"),
    sortable: true,
  },
  {
    key: "fetched_by",
    label: t("common.user_id"),
    sortable: true,
  },
  {
    key: "full_external_url",
    label: t("common.full_external_url"),
  },
  {
    key: "response_body",
    label: t("common.response_body"),
  },
  {
    key: "id",
    label: t("common.id"),
    sortable: true,
  },
  {
    key: "fetched_at",
    label: t("common.fetched_at"),
  },
]
// Fetch functions
// http://localhost:5500/api/v1/management/tenants?skip=0&limit=100
const fetchTenants = async () => {
  try {
    tenantsLoading.value = true;
    tenantsError.value = null;

    const { authenticatedFetch } = useAuthenticatedFetch();
    const data = await authenticatedFetch<Tenant[]>("/api/v1/management/tenants?skip=0&limit=100");
    tenants.value = data.slice(0, 10); // Show only first 10 users on dashboard
  } catch (err: any) {
    tenantsError.value = err;
    console.error("Failed to fetch tenants:", err);
  } finally {
    tenantsLoading.value = false;
  }
};

// http://localhost:5500/api/v1/management/tenants/history?skip=0&limit=100
const fetchServicesHistory = async () => {
  try {
    servicesHistoryLoading.value = true;
    servicesHistoryError.value = null;

    const { authenticatedFetch } = useAuthenticatedFetch();
    console.log('Fetching services history...');
    const data = await authenticatedFetch<ServiceHistory[]>("/api/v1/management/tenants/history?skip=0&limit=100");
    console.log('Services history response:', data);
    servicesHistory.value = Array.isArray(data) ? data.slice(0, 10) : []; // Show only first 10 items on dashboard
  } catch (err: any) {
    servicesHistoryError.value = err;
    console.error("Failed to fetch services history:", err);
    servicesHistory.value = []; // Set empty array on error
  } finally {
    servicesHistoryLoading.value = false;
  }
};
// http://localhost:5500/api/v1/management/tenants/wathq-offline-data?skip=0&limit=100
const fetchWathqOfflineData = async () => {
  try {
    wathqOfflineDataLoading.value = true;
    wathqOfflineDataError.value = null;

    const { authenticatedFetch } = useAuthenticatedFetch();
    console.log('Fetching WATHQ offline data...');
    const data = await authenticatedFetch<ServiceHistory[]>("/api/v1/management/tenants/wathq-offline-data?skip=0&limit=100");
    console.log('WATHQ offline data response:', data);
    wathqOfflineData.value = Array.isArray(data) ? data.slice(0, 10) : []; // Show only first 10 items on dashboard
  } catch (err: any) {
    wathqOfflineDataError.value = err;
    console.error("Failed to fetch wathq offline data:", err);
    wathqOfflineData.value = []; // Set empty array on error
  } finally {
    wathqOfflineDataLoading.value = false;
  }
};


// http://localhost:5500/api/v1/management/stats
// {
//   "tenants_count": 10,
//   "users_count": 150,
//   "online_requests_count": 5000,
//   "offline_requests_count": 1200
// }
const fetchApiStats = async () => {
  try {
    apiStatsLoading.value = true;
    apiStatsError.value = null;

    const { authenticatedFetch } = useAuthenticatedFetch();
    const data = await authenticatedFetch<{ tenants_count: number; users_count: number; online_requests_count: number; offline_requests_count: number }>("/api/v1/management/stats");
    apiStats.value = data;
  } catch (err: any) {
    apiStatsError.value = err;
    console.error("Failed to fetch stats:", err);
  } finally {
    apiStatsLoading.value = false;
  }
};
// Refresh functions
const refreshTenants = () => fetchTenants();
const refreshServicesHistory = () => fetchServicesHistory();
const refreshWathqOfflineData = () => fetchWathqOfflineData();
const refreshApiStats = () => fetchApiStats();
const refreshAllData = async () => {
  isRefreshing.value = true;
  try {
    await Promise.all([refreshTenants(), refreshServicesHistory(), refreshWathqOfflineData(), refreshApiStats()]);
  } finally {
    isRefreshing.value = false;
  }
};

// Helper functions
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return "N/A";
  try {
    return new Date(dateTime).toLocaleString();
  } catch {
    return "Invalid Date";
  }
};

// Computed stats
const dashboardStats = computed(() => {
  // return tenants count - active tenants count - inactive tenants count - all tenants users count
  // also return services history count - active services history count - inactive services history count
  if (!tenants.value || !Array.isArray(tenants.value))
    return { count: 0, active: 0, inactive: 0, usersCount: 0, servicesHistoryCount: 0, activeServicesHistoryCount: 0, inactiveServicesHistoryCount: 0 };

  return {
    count: tenants.value.length,
    active: tenants.value.filter((tenant) => tenant.is_active).length,
    inactive: tenants.value.filter((tenant) => !tenant.is_active).length,
    usersCount: tenants.value.reduce((acc, tenant) => acc + tenant.users_count, 0),
    servicesHistoryCount: servicesHistory.value.length,
    activeServicesHistoryCount: servicesHistory.value.filter((serviceHistory) => serviceHistory.is_active).length,
    inactiveServicesHistoryCount: servicesHistory.value.filter((serviceHistory) => !serviceHistory.is_active).length,
  };
});

// Chart data for online services
const onlineChartData = computed(() => {
  console.log('Online chart data - servicesHistory:', servicesHistory.value);
  
  if (!servicesHistory.value || servicesHistory.value.length === 0) {
    console.log('No services history data available, using sample data');
    // Return sample data for demonstration
    const today = new Date();
    const sampleLabels = [];
    const sampleData = [];
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      sampleLabels.push(date.toLocaleDateString());
      sampleData.push(Math.floor(Math.random() * 50) + 10);
    }
    
    return {
      labels: sampleLabels,
      datasets: [
        {
          label: t("dashboard.charts.onlineRequests") || 'Online Requests',
          data: sampleData,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };
  }

  // Group by date and count requests per day
  const dailyCounts = servicesHistory.value.reduce((acc: Record<string, number>, item: ServiceHistory) => {
    const date = item.fetched_at ? new Date(item.fetched_at).toLocaleDateString() : 'Unknown';
    acc[date] = (acc[date] || 0) + 1;
    return acc;
  }, {});

  const labels = Object.keys(dailyCounts).sort();
  const data = labels.map(label => dailyCounts[label]);

  console.log('Online chart - labels:', labels, 'data:', data);

  return {
    labels,
    datasets: [
      {
        label: t("dashboard.charts.onlineRequests") || 'Online Requests',
        data,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };
});

// Chart data for offline services
const offlineChartData = computed(() => {
  console.log('Offline chart data - wathqOfflineData:', wathqOfflineData.value);
  
  if (!wathqOfflineData.value || wathqOfflineData.value.length === 0) {
    console.log('No offline data available, using sample data');
    // Return sample data for demonstration
    const today = new Date();
    const sampleLabels = [];
    const sampleData = [];
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      sampleLabels.push(date.toLocaleDateString());
      sampleData.push(Math.floor(Math.random() * 30) + 5);
    }
    
    // Color palette for bars
    const colors = [
      'rgba(139, 92, 246, 0.8)',   // purple
      'rgba(59, 130, 246, 0.8)',   // blue
      'rgba(16, 185, 129, 0.8)',   // green
      'rgba(245, 158, 11, 0.8)',   // yellow
      'rgba(239, 68, 68, 0.8)',    // red
      'rgba(168, 85, 247, 0.8)',   // violet
      'rgba(14, 165, 233, 0.8)',   // cyan
    ];
    
    return {
      labels: sampleLabels,
      datasets: [
        {
          label: t("dashboard.charts.offlineRequests") || 'Offline Requests',
          data: sampleData,
          backgroundColor: colors.slice(0, sampleData.length)
        }
      ]
    };
  }

  // Group by date and count requests per day
  const dailyCounts = wathqOfflineData.value.reduce((acc: Record<string, number>, item: any) => {
    const date = item.fetched_at ? new Date(item.fetched_at).toLocaleDateString() : 'Unknown';
    acc[date] = (acc[date] || 0) + 1;
    return acc;
  }, {});

  const labels = Object.keys(dailyCounts).sort();
  const data = labels.map(label => dailyCounts[label]);

  console.log('Offline chart - labels:', labels, 'data:', data);

  // Color palette for bars
  const colors = [
    'rgba(139, 92, 246, 0.8)',   // purple
    'rgba(59, 130, 246, 0.8)',   // blue
    'rgba(16, 185, 129, 0.8)',   // green
    'rgba(245, 158, 11, 0.8)',   // yellow
    'rgba(239, 68, 68, 0.8)',    // red
    'rgba(168, 85, 247, 0.8)',   // violet
    'rgba(14, 165, 233, 0.8)',   // cyan
    'rgba(34, 197, 94, 0.8)',    // emerald
    'rgba(251, 146, 60, 0.8)',   // orange
    'rgba(236, 72, 153, 0.8)',   // pink
  ];

  return {
    labels,
    datasets: [
      {
        label: t("dashboard.charts.offlineRequests") || 'Offline Requests',
        data,
        backgroundColor: colors.slice(0, data.length)
      }
    ]
  };
});

// Auto-refresh timer
let refreshTimer: ReturnType<typeof setInterval> | null = null;

// Setup auto-refresh based on settings
function setupAutoRefresh() {
  // Clear existing timer
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }

  // Setup new timer if auto-refresh is enabled
  if (dashboardAutoRefresh.value) {
    const intervalMs = dashboardRefreshInterval.value * 1000; // Convert seconds to milliseconds
    console.log(`[Dashboard] Auto-refresh enabled: refreshing every ${dashboardRefreshInterval.value} seconds`);
    refreshTimer = setInterval(() => {
      console.log('[Dashboard] Auto-refreshing data...');
      refreshAllData();
    }, intervalMs);
  } else {
    console.log('[Dashboard] Auto-refresh disabled');
  }
}

// Watch for changes in auto-refresh settings
watch([dashboardAutoRefresh, dashboardRefreshInterval], ([autoRefresh, interval]) => {
  console.log(`[Dashboard] Settings changed - Auto-refresh: ${autoRefresh}, Interval: ${interval}s`);
  setupAutoRefresh();
}, { deep: true });

// Load data when component mounts
onMounted(() => {
  refreshAllData();
  setupAutoRefresh();
});

// Cleanup on unmount
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
});

// Set page meta
useHead({
  title: "توثيق العدل  - لوحة التحكم",
});
</script>
