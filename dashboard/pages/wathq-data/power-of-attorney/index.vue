<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.total') }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
          </div>
          <UIcon name="i-heroicons-document-check" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.stats.active') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
          </div>
          <UIcon name="i-heroicons-check-circle" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.stats.expired') }}</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ stats.expired }}</p>
          </div>
          <UIcon name="i-heroicons-x-circle" class="w-10 h-10 text-red-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('powerOfAttorney.stats.thisMonth') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.thisMonth }}</p>
          </div>
          <UIcon name="i-heroicons-calendar" class="w-10 h-10 text-blue-500" />
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
      :title="t('sidebar.powerOfAttorney')"
      :description="t('powerOfAttorney.subtitle')"
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

// Define page metadata
definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// Stats state
const stats = ref({
  total: 0,
  active: 0,
  expired: 0,
  thisMonth: 0
})

// Mock data for development/testing
const getMockData = () => {
  const now = new Date().toISOString()
  const today = new Date()
  const futureDate = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate())
  const pastDate = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
  
  return [
    {
      id: 1,
      code: 'POA-2024-001',
      status: 'Active',
      issue_hijri_date: '1445/06/15',
      issue_greg_date: '2024-01-15',
      expiry_hijri_date: '1446/06/15',
      expiry_greg_date: futureDate.toISOString().split('T')[0],
      attorney_type: 'General',
      location_id: 1,
      location_name: 'Riyadh',
      agents_behavior_ar: 'منفردين',
      agents_behavior_en: 'Individual',
      principals: [{ name: 'أحمد محمد' }, { name: 'سارة علي' }],
      agents: [{ name: 'خالد سعيد' }],
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1
    },
    {
      id: 2,
      code: 'POA-2023-045',
      status: 'Expired',
      issue_hijri_date: '1444/03/10',
      issue_greg_date: '2023-02-20',
      expiry_hijri_date: '1445/03/10',
      expiry_greg_date: pastDate.toISOString().split('T')[0],
      attorney_type: 'Special',
      location_id: 2,
      location_name: 'Jeddah',
      agents_behavior_ar: 'مجتمعين',
      agents_behavior_en: 'Joint',
      principals: [{ name: 'فاطمة حسن' }],
      agents: [{ name: 'عمر يوسف' }, { name: 'ليلى أحمد' }],
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1
    },
    {
      id: 3,
      code: 'POA-2024-012',
      status: 'Active',
      issue_hijri_date: '1445/07/20',
      issue_greg_date: '2024-03-10',
      expiry_hijri_date: '1446/07/20',
      expiry_greg_date: futureDate.toISOString().split('T')[0],
      attorney_type: 'Limited',
      location_id: 3,
      location_name: 'Dammam',
      agents_behavior_ar: 'منفردين أو مجتمعين',
      agents_behavior_en: 'Individual or Joint',
      principals: [{ name: 'محمد عبدالله' }],
      agents: [{ name: 'نورة سعد' }],
      created_at: now,
      updated_at: now,
      created_by: 2,
      updated_by: 2
    }
  ]
}

// Helper function to format date
function formatDate(dateString: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

// DataTable Configuration
const tableConfig: DataTableConfig<any> = {
  // Data fetching
  fetchFunction: async (params) => {
    try {
      // Calculate skip for pagination
      const skip = (params.page - 1) * params.pageSize
      
      const response = await $fetch('/api/v1/wathq/power-of-attorney/', {
        params: {
          skip: skip,
          limit: params.pageSize
        }
      })

      console.log('API Response:', response)
      
      // API returns array directly
      let data = Array.isArray(response) ? response : []
      
      // If API returns empty or no data, use mock data for development
      if (data.length === 0) {
        console.warn('No data from API, using mock data')
        data = getMockData()
      }

      // Apply client-side filtering if filters are present
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

      // Apply client-side search if search term is present
      if (params.search) {
        const searchLower = params.search.toLowerCase()
        data = data.filter((item: any) => {
          return (
            item.code?.toLowerCase().includes(searchLower) ||
            item.attorney_type?.toLowerCase().includes(searchLower) ||
            item.location_name?.toLowerCase().includes(searchLower) ||
            item.status?.toLowerCase().includes(searchLower)
          )
        })
      }

      // Apply client-side sorting
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

      // Update stats based on all data (before pagination)
      stats.value.total = data.length
      stats.value.active = data.filter((item: any) => item.status?.toLowerCase() === 'active').length
      stats.value.expired = data.filter((item: any) => item.status?.toLowerCase() === 'expired').length
      
      // Count POAs from this month
      const thisMonth = new Date().getMonth()
      const thisYear = new Date().getFullYear()
      stats.value.thisMonth = data.filter((item: any) => {
        if (!item.issue_greg_date) return false
        const date = new Date(item.issue_greg_date)
        return date.getMonth() === thisMonth && date.getFullYear() === thisYear
      }).length

      // Apply pagination
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
      console.error('Failed to fetch power of attorney records:', error)
      // On error, return mock data instead of throwing
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.active = mockData.filter((item: any) => item.status?.toLowerCase() === 'active').length
      stats.value.expired = mockData.filter((item: any) => item.status?.toLowerCase() === 'expired').length
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

  // Columns configuration
  columns: [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      visible: true,
      width: '80px',
      render: (value) => `<span class="font-mono text-sm text-gray-600">#${value}</span>`
    },
    {
      key: 'code',
      label: t('powerOfAttorney.table.code'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm font-medium">${value}</span>`
    },
    {
      key: 'status',
      label: t('powerOfAttorney.table.status'),
      sortable: true,
      type: 'badge',
      width: '120px',
      cellClass: (value) => {
        const status = value?.toLowerCase()
        if (status === 'active') return 'text-green-600'
        if (status === 'expired') return 'text-red-600'
        return 'text-gray-600'
      }
    },
    {
      key: 'attorney_type',
      label: t('powerOfAttorney.table.attorneyType'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'issue_greg_date',
      label: t('powerOfAttorney.table.issueDate'),
      sortable: true,
      type: 'date',
      width: '130px',
      format: (value) => formatDate(value)
    },
    {
      key: 'expiry_greg_date',
      label: t('powerOfAttorney.table.expiryDate'),
      sortable: true,
      type: 'date',
      width: '130px',
      format: (value) => formatDate(value)
    },
    {
      key: 'location_name',
      label: t('powerOfAttorney.table.location'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'principals',
      label: t('powerOfAttorney.table.principalsCount'),
      sortable: false,
      width: '120px',
      render: (value) => {
        const count = Array.isArray(value) ? value.length : 0
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">${count}</span>`
      }
    },
    {
      key: 'agents',
      label: t('powerOfAttorney.table.agentsCount'),
      sortable: false,
      width: '120px',
      render: (value) => {
        const count = Array.isArray(value) ? value.length : 0
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">${count}</span>`
      }
    },
    {
      key: 'created_at',
      label: 'Created At',
      sortable: true,
      type: 'date',
      width: '160px',
      format: (value) => value ? new Date(value).toLocaleString() : '-'
    }
  ],

  // Filters configuration
  filters: [
    {
      key: 'status',
      label: t('powerOfAttorney.table.status'),
      type: 'select',
      placeholder: 'All Statuses',
      options: [
        { label: 'All Statuses', value: null },
        { label: 'Active', value: 'Active' },
        { label: 'Expired', value: 'Expired' }
      ]
    },
    {
      key: 'attorney_type',
      label: t('powerOfAttorney.table.attorneyType'),
      type: 'select',
      placeholder: 'All Types',
      options: [
        { label: 'All Types', value: null },
        { label: 'General', value: 'General' },
        { label: 'Special', value: 'Special' },
        { label: 'Limited', value: 'Limited' }
      ]
    },
    {
      key: 'location_name',
      label: t('powerOfAttorney.table.location'),
      type: 'select',
      placeholder: 'All Locations',
      options: [
        { label: 'All Locations', value: null },
        { label: 'Riyadh', value: 'Riyadh' },
        { label: 'Jeddah', value: 'Jeddah' },
        { label: 'Dammam', value: 'Dammam' },
        { label: 'Makkah', value: 'Makkah' },
        { label: 'Madinah', value: 'Madinah' }
      ],
      searchable: true
    }
  ],

  // Actions configuration
  actions: [
    {
      key: 'view',
      label: '',
      icon: 'i-heroicons-eye',
      color: 'primary' as const,
      variant: 'ghost',
      size: 'sm',
      handler: (row) => {
        router.push(`/wathq-data/power-of-attorney/${row.id}`)
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
        // TODO: Implement edit modal
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
        title: 'Delete Power of Attorney',
        message: 'Are you sure you want to delete this power of attorney? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/power-of-attorney/${row.id}`, {
            method: 'DELETE'
          })
          // TODO: Show success notification and refresh table
        } catch (error) {
          console.error('Failed to delete:', error)
          // TODO: Show error notification
        }
      }
    }
  ],

  // Bulk actions
  bulkActions: [
    {
      key: 'export',
      label: 'Export Selected',
      icon: 'i-heroicons-arrow-down-tray',
      color: 'primary' as const,
      variant: 'outline',
      handler: async (selectedRows) => {
        console.log('Export selected:', selectedRows)
        // TODO: Implement export functionality
      }
    },
    {
      key: 'delete',
      label: 'Delete Selected',
      icon: 'i-heroicons-trash',
      color: 'error' as const,
      variant: 'outline',
      confirm: {
        title: 'Delete Multiple Records',
        message: 'Are you sure you want to delete the selected power of attorney records?'
      },
      handler: async (selectedRows, selectedIds) => {
        try {
          await $fetch('/api/v1/wathq/power-of-attorney/bulk-delete', {
            method: 'POST',
            body: { ids: selectedIds }
          })
          // TODO: Show success notification and refresh table
        } catch (error) {
          console.error('Failed to delete:', error)
          // TODO: Show error notification
        }
      }
    }
  ],

  // Table settings
  keyField: 'code',
  selectable: true,
  multiSelect: true,
  hoverable: true,
  striped: false,
  bordered: false,
  dense: false,
  
  // Pagination settings
  pagination: true,
  initialPage: 1,
  initialPageSize: 10,
  pageSizeOptions: [10, 20, 50, 100],
  
  // Search settings
  globalSearch: true,
  searchPlaceholder: t('powerOfAttorney.search'),
  searchDebounce: 300,
  
  // Export settings
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  // Sorting
  initialSortColumn: 'code',
  initialSortDirection: 'desc',
  
  // Empty state
  emptyStateIcon: 'i-heroicons-document-check',
  emptyStateTitle: t('powerOfAttorney.noData'),
  emptyStateDescription: 'No power of attorney records found. Try adjusting your filters.',
  
  // State persistence
  persistState: true,
  stateKey: 'power-of-attorney-table-v1'
}

// Event handlers
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
    }>('/api/v1/wathq/sync/power-of-attorney/sync', {
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
