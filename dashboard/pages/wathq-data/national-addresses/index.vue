<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.stats.total') }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
          </div>
          <UIcon name="i-heroicons-map-pin" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.stats.primary') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.primary }}</p>
          </div>
          <UIcon name="i-heroicons-star" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.stats.cities') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.cities }}</p>
          </div>
          <UIcon name="i-heroicons-building-office-2" class="w-10 h-10 text-blue-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('nationalAddresses.stats.thisMonth') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ stats.thisMonth }}</p>
          </div>
          <UIcon name="i-heroicons-calendar" class="w-10 h-10 text-purple-500" />
        </div>
      </UCard>
    </div>

    <!-- Action Bar -->
    <div class="flex justify-between items-center mb-4">
      <div></div>
      <div class="flex gap-3">
        <UButton
          icon="i-heroicons-arrow-path"
          color="green"
          size="lg"
          :loading="isSyncing"
          @click="handleSync"
        >
          {{ t('wathqData.syncFromLogs') }}
        </UButton>
      </div>
    </div>

    <!-- Advanced DataTable -->
    <AdvancedDataTable
      ref="dataTableRef"
      :config="tableConfig"
      :title="t('sidebar.nationalAddresses')"
      :description="t('nationalAddresses.subtitle')"
      @row-click="handleRowClick"
      @action-click="handleActionClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useRouter } from 'vue-router'
import { useAuthenticatedFetch } from '@/composables/useAuthenticatedFetch'
import type { DataTableConfig } from '~/types/datatable'
import AdvancedDataTable from '~/components/ui/AdvancedDataTable.vue'

const { t } = useI18n()
const router = useRouter()
const toast = useToast()
const { authenticatedFetch } = useAuthenticatedFetch()

// Sync state
const isSyncing = ref(false)
const dataTableRef = ref<InstanceType<typeof AdvancedDataTable> | null>(null)

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const stats = ref({
  total: 0,
  primary: 0,
  cities: 0,
  thisMonth: 0
})

const getMockData = () => {
  const now = new Date().toISOString()
  
  return [
    {
      pk_address_id: 'ADDR-RYD-001',
      title: 'Main Office - Riyadh',
      address: 'King Fahd Road, Al Olaya District',
      address2: 'Tower A, Floor 15',
      latitude: 24.7136,
      longitude: 46.6753,
      building_number: '7890',
      street: 'King Fahd Road',
      district: 'Al Olaya',
      district_id: 'RYD-OLY',
      city: 'Riyadh',
      city_id: 'RYD',
      post_code: '12345',
      additional_number: '1234',
      region_name: 'Riyadh Region',
      region_id: 'RG-01',
      is_primary_address: true,
      unit_number: '1501',
      restriction: null,
      status: 'Active',
      created_at: now,
      updated_at: now
    },
    {
      pk_address_id: 'ADDR-JED-002',
      title: 'Branch Office - Jeddah',
      address: 'Tahlia Street, Al Zahra District',
      address2: 'Building B',
      latitude: 21.5433,
      longitude: 39.1728,
      building_number: '4567',
      street: 'Tahlia Street',
      district: 'Al Zahra',
      district_id: 'JED-ZAH',
      city: 'Jeddah',
      city_id: 'JED',
      post_code: '23456',
      additional_number: '5678',
      region_name: 'Makkah Region',
      region_id: 'RG-02',
      is_primary_address: false,
      unit_number: '201',
      restriction: null,
      status: 'Active',
      created_at: now,
      updated_at: now
    },
    {
      pk_address_id: 'ADDR-DAM-003',
      title: 'Warehouse - Dammam',
      address: 'King Saud Road, Al Faisaliyah',
      address2: null,
      latitude: 26.4207,
      longitude: 50.0888,
      building_number: '1234',
      street: 'King Saud Road',
      district: 'Al Faisaliyah',
      district_id: 'DAM-FAS',
      city: 'Dammam',
      city_id: 'DAM',
      post_code: '34567',
      additional_number: '9012',
      region_name: 'Eastern Region',
      region_id: 'RG-03',
      is_primary_address: false,
      unit_number: null,
      restriction: 'Commercial use only',
      status: 'Active',
      created_at: now,
      updated_at: now
    }
  ]
}

const tableConfig: DataTableConfig<any> = {
  fetchFunction: async (params) => {
    try {
      const skip = (params.page - 1) * params.pageSize
      
      const response = await $fetch('/api/v1/wathq/national-addresses/', {
        params: {
          skip: skip,
          limit: params.pageSize
        }
      })

      let data = Array.isArray(response) ? response : []
      
      if (data.length === 0) {
        console.warn('No data from API, using mock data')
        data = getMockData()
      }

      if (params.filters && Object.keys(params.filters).length > 0) {
        data = data.filter((item: any) => {
          for (const [key, value] of Object.entries(params.filters)) {
            if (value && item[key] !== value) {
              return false
            }
          }
          return true
        })
      }

      if (params.search) {
        const searchLower = params.search.toLowerCase()
        data = data.filter((item: any) => {
          return (
            item.pk_address_id?.toLowerCase().includes(searchLower) ||
            item.title?.toLowerCase().includes(searchLower) ||
            item.address?.toLowerCase().includes(searchLower) ||
            item.city?.toLowerCase().includes(searchLower) ||
            item.post_code?.toLowerCase().includes(searchLower) ||
            item.district?.toLowerCase().includes(searchLower)
          )
        })
      }

      if (params.sortBy) {
        data.sort((a: any, b: any) => {
          const aVal = a[params.sortBy]
          const bVal = b[params.sortBy]
          
          if (aVal === null || aVal === undefined) return 1
          if (bVal === null || bVal === undefined) return -1
          
          if (params.sortOrder === 'asc') {
            return aVal > bVal ? 1 : -1
          } else {
            return aVal < bVal ? 1 : -1
          }
        })
      }

      stats.value.total = data.length
      stats.value.primary = data.filter((item: any) => item.is_primary_address).length
      
      const uniqueCities = new Set(data.map((item: any) => item.city).filter(Boolean))
      stats.value.cities = uniqueCities.size
      
      const thisMonth = new Date().getMonth()
      const thisYear = new Date().getFullYear()
      stats.value.thisMonth = data.filter((item: any) => {
        if (!item.created_at) return false
        const date = new Date(item.created_at)
        return date.getMonth() === thisMonth && date.getFullYear() === thisYear
      }).length

      const startIndex = (params.page - 1) * params.pageSize
      const paginatedData = data.slice(startIndex, startIndex + params.pageSize)

      return {
        data: paginatedData,
        total: data.length,
        page: params.page,
        pageSize: params.pageSize,
        totalPages: Math.ceil(data.length / params.pageSize)
      }
    } catch (error) {
      console.error('Failed to fetch addresses:', error)
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.primary = mockData.filter((item: any) => item.is_primary_address).length
      stats.value.cities = new Set(mockData.map((item: any) => item.city)).size
      stats.value.thisMonth = 0

      return {
        data: mockData,
        total: mockData.length,
        page: params.page,
        pageSize: params.pageSize,
        totalPages: Math.ceil(mockData.length / params.pageSize)
      }
    }
  },

  columns: [
    {
      key: 'pk_address_id',
      label: t('nationalAddresses.table.addressId'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm font-medium text-primary-600">${value || '-'}</span>`
    },
    {
      key: 'title',
      label: t('nationalAddresses.table.title'),
      sortable: true,
      searchable: true,
      width: '200px',
      render: (value) => `<span class="font-medium">${value || '-'}</span>`
    },
    {
      key: 'city',
      label: t('nationalAddresses.table.city'),
      sortable: true,
      searchable: true,
      width: '120px'
    },
    {
      key: 'district',
      label: t('nationalAddresses.table.district'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'post_code',
      label: t('nationalAddresses.table.postCode'),
      sortable: true,
      searchable: true,
      width: '120px',
      render: (value) => `<span class="font-mono text-sm">${value || '-'}</span>`
    },
    {
      key: 'building_number',
      label: t('nationalAddresses.table.buildingNumber'),
      sortable: true,
      width: '130px',
      render: (value) => `<span class="font-mono text-sm">${value || '-'}</span>`
    },
    {
      key: 'is_primary_address',
      label: t('nationalAddresses.table.isPrimary'),
      sortable: true,
      width: '120px',
      render: (value) => {
        if (value) {
          return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
            Primary
          </span>`
        }
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">Secondary</span>`
      }
    },
    {
      key: 'status',
      label: t('nationalAddresses.table.status'),
      sortable: true,
      type: 'badge',
      width: '100px',
      cellClass: (value) => {
        const status = value?.toLowerCase()
        if (status === 'active') return 'text-green-600'
        if (status === 'inactive') return 'text-red-600'
        return 'text-gray-600'
      }
    }
  ],

  filters: [
    {
      key: 'city',
      label: t('nationalAddresses.table.city'),
      type: 'select',
      placeholder: 'All Cities',
      options: [
        { label: 'All Cities', value: null },
        { label: 'Riyadh', value: 'Riyadh' },
        { label: 'Jeddah', value: 'Jeddah' },
        { label: 'Dammam', value: 'Dammam' },
        { label: 'Makkah', value: 'Makkah' },
        { label: 'Madinah', value: 'Madinah' }
      ],
      searchable: true
    },
    {
      key: 'is_primary_address',
      label: t('nationalAddresses.table.isPrimary'),
      type: 'select',
      placeholder: 'All Types',
      options: [
        { label: 'All Types', value: null },
        { label: 'Primary', value: true },
        { label: 'Secondary', value: false }
      ]
    },
    {
      key: 'status',
      label: t('nationalAddresses.table.status'),
      type: 'select',
      placeholder: 'All Statuses',
      options: [
        { label: 'All Statuses', value: null },
        { label: 'Active', value: 'Active' },
        { label: 'Inactive', value: 'Inactive' }
      ]
    }
  ],

  actions: [
    {
      key: 'view',
      label: '',
      icon: 'i-heroicons-eye',
      color: 'primary' as const,
      variant: 'ghost',
      size: 'sm',
      handler: (row) => {
        router.push(`/wathq-data/national-addresses/${row.pk_address_id}`)
      }
    },
    {
      key: 'edit',
      label: '',
      icon: 'i-heroicons-pencil',
      color: 'primary' as const,
      variant: 'ghost',
      size: 'sm',
      handler: (row) => {
        console.log('Edit:', row)
      }
    },
    {
      key: 'delete',
      label: '',
      icon: 'i-heroicons-trash',
      color: 'error' as const,
      variant: 'ghost',
      size: 'sm',
      confirm: {
        title: 'Delete Address',
        message: 'Are you sure you want to delete this address? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/national-addresses/${row.pk_address_id}`, {
            method: 'DELETE'
          })
        } catch (error) {
          console.error('Failed to delete:', error)
        }
      }
    }
  ],

  bulkActions: [
    {
      key: 'export',
      label: 'Export Selected',
      icon: 'i-heroicons-arrow-down-tray',
      color: 'primary' as const,
      variant: 'outline',
      handler: async (selectedRows) => {
        console.log('Export selected:', selectedRows)
      }
    }
  ],

  keyField: 'pk_address_id',
  selectable: true,
  multiSelect: true,
  hoverable: true,
  striped: false,
  bordered: false,
  dense: false,
  
  pagination: true,
  initialPage: 1,
  initialPageSize: 10,
  pageSizeOptions: [10, 20, 50, 100],
  
  globalSearch: true,
  searchPlaceholder: t('nationalAddresses.search'),
  searchDebounce: 300,
  
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  initialSortColumn: 'pk_address_id',
  initialSortDirection: 'asc',
  
  emptyStateIcon: 'i-heroicons-map-pin',
  emptyStateTitle: t('nationalAddresses.noData'),
  emptyStateDescription: 'No national addresses found. Try adjusting your filters.',
  
  persistState: true,
  stateKey: 'national-addresses-table-v1'
}

function handleRowClick(row: any, index: number, event: Event) {
  console.log('Row clicked:', row)
}

function handleActionClick(action: any, row: any, index: number) {
  console.log('Action clicked:', action.key, row)
}

// Sync handler
async function handleSync() {
  isSyncing.value = true
  
  try {
    const response = await authenticatedFetch<{
      success: boolean
      message: string
      synced_count: number
      total_logs: number
      errors: any[]
    }>('/api/v1/wathq/sync/national-address/sync', {
      method: 'POST'
    })
    
    console.log('Sync response:', response)
    
    if (response.success) {
      const message = response.synced_count > 0
        ? `Synced ${response.synced_count} of ${response.total_logs} records from call logs`
        : `No new records to sync. Found ${response.total_logs} call logs but all records already exist.`
      
      toast.add({
        title: t('common.success'),
        description: message,
        color: 'green'
      })
      
      // Show errors if any
      if (response.errors && response.errors.length > 0) {
        console.warn('Sync errors:', response.errors)
        toast.add({
          title: 'Some records had errors',
          description: `${response.errors.length} records failed to sync. Check console for details.`,
          color: 'orange'
        })
      }
      
      // Refresh the table data
      if (response.synced_count > 0 && dataTableRef.value) {
        dataTableRef.value.refresh()
      }
    } else {
      toast.add({
        title: t('common.error'),
        description: response.message || 'Failed to sync data',
        color: 'red'
      })
    }
  } catch (error: any) {
    console.error('Sync error:', error)
    toast.add({
      title: t('common.error'),
      description: error.message || 'An error occurred during sync',
      color: 'red'
    })
  } finally {
    isSyncing.value = false
  }
}
</script>
