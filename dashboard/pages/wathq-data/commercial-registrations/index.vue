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
          <UIcon name="i-heroicons-building-office" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.active') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
          </div>
          <UIcon name="i-heroicons-check-circle" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.suspended') }}</p>
            <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.suspended }}</p>
          </div>
          <UIcon name="i-heroicons-pause-circle" class="w-10 h-10 text-yellow-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('wathqData.stats.cancelled') }}</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ stats.cancelled }}</p>
          </div>
          <UIcon name="i-heroicons-x-circle" class="w-10 h-10 text-red-500" />
        </div>
      </UCard>
    </div>

    <!-- Advanced DataTable -->
    <AdvancedDataTable
      :config="tableConfig"
      :title="t('sidebar.commercialRegistrations')"
      :description="t('wathqData.commercialRegistrations.subtitle')"
      @row-click="handleRowClick"
      @action-click="handleActionClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useRouter } from 'vue-router'
import type { DataTableConfig } from '~/types/datatable'
import AdvancedDataTable from '~/components/ui/AdvancedDataTable.vue'

const { t } = useI18n()
const router = useRouter()

// Define page metadata
definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

// Stats state
const stats = ref({
  total: 0,
  active: 0,
  suspended: 0,
  cancelled: 0
})

// Mock data for development/testing
const getMockData = () => {
  const now = new Date().toISOString()
  return [
    {
      id: 1,
      cr_number: '1010711252',
      name: 'Saudi Technology Company',
      name_lang_desc: 'شركة التقنية السعودية',
      status_name: 'Active',
      headquarter_city_name: 'Riyadh',
      issue_date_gregorian: '2020-01-15',
      cr_capital: 5000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1,
      request_body: null
    },
    {
      id: 2,
      cr_number: '1010711253',
      name: 'Gulf Trading Est.',
      name_lang_desc: 'مؤسسة الخليج التجارية',
      status_name: 'Active',
      headquarter_city_name: 'Jeddah',
      issue_date_gregorian: '2019-06-20',
      cr_capital: 2000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: null,
      request_body: null
    },
    {
      id: 3,
      cr_number: '1010711254',
      name: 'Modern Services Co.',
      name_lang_desc: 'شركة الخدمات الحديثة',
      status_name: 'Suspended',
      headquarter_city_name: 'Dammam',
      issue_date_gregorian: '2021-03-10',
      cr_capital: 1500000,
      created_at: now,
      updated_at: now,
      created_by: 2,
      updated_by: 2,
      request_body: null
    },
    {
      id: 4,
      cr_number: '1010711255',
      name: 'National Industries Ltd.',
      name_lang_desc: 'الصناعات الوطنية المحدودة',
      status_name: 'Active',
      headquarter_city_name: 'Riyadh',
      issue_date_gregorian: '2018-11-05',
      cr_capital: 10000000,
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1,
      request_body: null
    },
    {
      id: 5,
      cr_number: '1010711256',
      name: 'Digital Solutions Group',
      name_lang_desc: 'مجموعة الحلول الرقمية',
      status_name: 'Cancelled',
      headquarter_city_name: 'Jeddah',
      issue_date_gregorian: '2022-02-28',
      cr_capital: 500000,
      created_at: now,
      updated_at: now,
      created_by: 3,
      updated_by: 3,
      request_body: null
    }
  ]
}

// DataTable Configuration
const tableConfig: DataTableConfig<any> = {
  // Data fetching
  fetchFunction: async (params) => {
    try {
      const response = await $fetch('/api/v1/wathq/cr-data/', {
        params: {
          page: params.page,
          limit: params.pageSize,
          search: params.search,
          sort_by: params.sortBy,
          sort_order: params.sortOrder,
          ...params.filters
        }
      })

      // Check if response has data, otherwise use mock data
      let data = response?.data || response || []
      
      // If API returns empty or no data, use mock data for development
      if (!Array.isArray(data) || data.length === 0) {
        console.warn('No data from API, using mock data')
        data = getMockData()
      }

      // Update stats
      stats.value.total = data.length
      stats.value.active = data.filter((item: any) => item.status_name?.toLowerCase() === 'active').length
      stats.value.suspended = data.filter((item: any) => item.status_name?.toLowerCase() === 'suspended').length
      stats.value.cancelled = data.filter((item: any) => item.status_name?.toLowerCase() === 'cancelled').length

      return {
        data: data,
        total: data.length,
        page: params.page,
        pageSize: params.pageSize,
        totalPages: Math.ceil(data.length / params.pageSize)
      }
    } catch (error) {
      console.error('Failed to fetch commercial registrations:', error)
      // On error, return mock data instead of throwing
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.active = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'active').length
      stats.value.suspended = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'suspended').length
      stats.value.cancelled = mockData.filter((item: any) => item.status_name?.toLowerCase() === 'cancelled').length

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
      key: 'cr_number',
      label: t('wathqData.table.crNumber'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm">${value}</span>`
    },
    {
      key: 'name',
      label: t('wathqData.table.name'),
      sortable: true,
      searchable: true,
      minWidth: '200px',
      render: (value, row) => {
        const langDesc = row.name_lang_desc ? `<p class="text-xs text-gray-500">${row.name_lang_desc}</p>` : ''
        return `<div><p class="font-medium text-gray-900 dark:text-white">${value}</p>${langDesc}</div>`
      }
    },
    {
      key: 'status_name',
      label: t('wathqData.table.status'),
      sortable: true,
      type: 'badge',
      width: '120px',
      cellClass: (value) => {
        const status = value?.toLowerCase()
        if (status === 'active') return 'text-green-600'
        if (status === 'suspended') return 'text-yellow-600'
        if (status === 'cancelled') return 'text-red-600'
        return 'text-gray-600'
      }
    },
    {
      key: 'headquarter_city_name',
      label: t('wathqData.table.city'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'issue_date_gregorian',
      label: t('wathqData.table.issueDate'),
      sortable: true,
      type: 'date',
      width: '130px',
      format: (value) => value ? new Date(value).toLocaleDateString() : '-'
    },
    {
      key: 'created_at',
      label: 'Created At',
      sortable: true,
      type: 'date',
      width: '160px',
      format: (value) => value ? new Date(value).toLocaleString() : '-'
    },
    {
      key: 'updated_at',
      label: 'Updated At',
      sortable: true,
      type: 'date',
      width: '160px',
      format: (value) => value ? new Date(value).toLocaleString() : '-'
    },
    {
      key: 'created_by',
      label: 'Created By',
      sortable: true,
      width: '100px',
      render: (value) => value ? `<span class="text-sm">${value}</span>` : '-'
    },
    {
      key: 'updated_by',
      label: 'Updated By',
      sortable: true,
      width: '100px',
      render: (value) => value ? `<span class="text-sm">${value}</span>` : '-'
    }
  ],

  // Filters configuration
  filters: [
    {
      key: 'status_name',
      label: t('wathqData.filters.status'),
      type: 'select',
      placeholder: t('wathqData.status.all'),
      options: [
        { label: t('wathqData.status.all'), value: null },
        { label: t('wathqData.status.active'), value: 'active' },
        { label: t('wathqData.status.suspended'), value: 'suspended' },
        { label: t('wathqData.status.cancelled'), value: 'cancelled' }
      ]
    },
    {
      key: 'headquarter_city_name',
      label: t('wathqData.filters.city'),
      type: 'select',
      placeholder: t('wathqData.filters.allCities'),
      options: [
        { label: t('wathqData.filters.allCities'), value: null },
        { label: 'Riyadh', value: 'Riyadh' },
        { label: 'Jeddah', value: 'Jeddah' },
        { label: 'Dammam', value: 'Dammam' },
        { label: 'Makkah', value: 'Makkah' },
        { label: 'Madinah', value: 'Madinah' }
      ],
      searchable: true
    },
    {
      key: 'cr_number',
      label: t('wathqData.table.crNumber'),
      type: 'text',
      placeholder: 'Search by CR number...'
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
        router.push(`/wathq-data/commercial-registrations/${row.id}`)
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
        title: 'Delete Commercial Registration',
        message: 'Are you sure you want to delete this commercial registration? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/cr-data/${row.id}`, {
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
        message: 'Are you sure you want to delete the selected commercial registrations?'
      },
      handler: async (selectedRows, selectedIds) => {
        try {
          await $fetch('/api/v1/wathq/cr-data/bulk-delete', {
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
  keyField: 'cr_number',
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
  searchPlaceholder: t('wathqData.search'),
  searchDebounce: 300,
  
  // Export settings
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  // Sorting
  initialSortColumn: 'cr_number',
  initialSortDirection: 'asc',
  
  // Empty state
  emptyStateIcon: 'i-heroicons-building-office',
  emptyStateTitle: t('wathqData.noData'),
  emptyStateDescription: 'No commercial registrations found. Try adjusting your filters.',
  
  // State persistence
  persistState: true,
  stateKey: 'commercial-registrations-table-v2'
}

// Event handlers
function handleRowClick(row: any, index: number, event: Event) {
  console.log('Row clicked:', row)
}

function handleActionClick(action: any, row: any, index: number) {
  console.log('Action clicked:', action.key, row)
}
</script>
