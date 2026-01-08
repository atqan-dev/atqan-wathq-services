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
          <UIcon name="i-heroicons-document-text" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.stats.totalCapital') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ formatCurrency(stats.totalCapital) }}</p>
          </div>
          <UIcon name="i-heroicons-banknotes" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.stats.thisMonth') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.thisMonth }}</p>
          </div>
          <UIcon name="i-heroicons-calendar" class="w-10 h-10 text-blue-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('corporateContracts.stats.avgCapital') }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ formatCurrency(stats.avgCapital) }}</p>
          </div>
          <UIcon name="i-heroicons-chart-bar" class="w-10 h-10 text-purple-500" />
        </div>
      </UCard>
    </div>

    <!-- Advanced DataTable -->
    <AdvancedDataTable
      :config="tableConfig"
      :title="t('sidebar.corporateContracts')"
      :description="t('corporateContracts.subtitle')"
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
  totalCapital: 0,
  thisMonth: 0,
  avgCapital: 0
})

// Mock data for development/testing
const getMockData = () => {
  const now = new Date().toISOString()
  return [
    {
      id: 1,
      contract_id: 12345,
      contract_copy_number: 1,
      contract_date: '2024-01-15',
      cr_national_number: '7001234567',
      cr_number: '1010711252',
      entity_name: 'شركة التقنية السعودية',
      entity_name_lang_desc: 'Saudi Technology Company',
      company_duration: 99,
      headquarter_city_name: 'الرياض',
      is_license_based: false,
      entity_type_name: 'شركة',
      entity_form_name: 'ذات مسؤولية محدودة',
      fiscal_calendar_type: 'ميلادي',
      total_capital: 5000000,
      paid_capital: 5000000,
      currency_name: 'ريال سعودي',
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1
    },
    {
      id: 2,
      contract_id: 12346,
      contract_copy_number: 1,
      contract_date: '2024-02-20',
      cr_national_number: '7001234568',
      cr_number: '1010711253',
      entity_name: 'شركة التجارة الحديثة',
      entity_name_lang_desc: 'Modern Trading Company',
      company_duration: 50,
      headquarter_city_name: 'جدة',
      is_license_based: false,
      entity_type_name: 'شركة',
      entity_form_name: 'مساهمة',
      fiscal_calendar_type: 'ميلادي',
      total_capital: 10000000,
      paid_capital: 10000000,
      currency_name: 'ريال سعودي',
      created_at: now,
      updated_at: now,
      created_by: 1,
      updated_by: 1
    },
    {
      id: 3,
      contract_id: 12347,
      contract_copy_number: 1,
      contract_date: '2024-03-10',
      cr_national_number: '7001234569',
      cr_number: '1010711254',
      entity_name: 'مؤسسة الخدمات المتقدمة',
      entity_name_lang_desc: 'Advanced Services Est.',
      company_duration: 25,
      headquarter_city_name: 'الدمام',
      is_license_based: true,
      entity_type_name: 'مؤسسة',
      entity_form_name: 'فردية',
      fiscal_calendar_type: 'هجري',
      total_capital: 2000000,
      paid_capital: 2000000,
      currency_name: 'ريال سعودي',
      created_at: now,
      updated_at: now,
      created_by: 2,
      updated_by: 2
    }
  ]
}

// Helper function to format currency
function formatCurrency(value: number) {
  if (!value) return '-'
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

// DataTable Configuration
const tableConfig: DataTableConfig<any> = {
  // Data fetching
  fetchFunction: async (params) => {
    try {
      // Calculate skip for pagination
      const skip = (params.page - 1) * params.pageSize
      
      const response = await $fetch('/api/v1/wathq/corporate-contracts/', {
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
            item.entity_name?.toLowerCase().includes(searchLower) ||
            item.entity_name_lang_desc?.toLowerCase().includes(searchLower) ||
            item.cr_number?.toLowerCase().includes(searchLower) ||
            item.contract_id?.toString().includes(searchLower)
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
      stats.value.totalCapital = data.reduce((sum: number, item: any) => sum + (Number(item.total_capital) || 0), 0)
      stats.value.avgCapital = stats.value.total > 0 ? stats.value.totalCapital / stats.value.total : 0
      
      // Count contracts from this month
      const thisMonth = new Date().getMonth()
      const thisYear = new Date().getFullYear()
      stats.value.thisMonth = data.filter((item: any) => {
        if (!item.contract_date) return false
        const date = new Date(item.contract_date)
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
      console.error('Failed to fetch corporate contracts:', error)
      // On error, return mock data instead of throwing
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.totalCapital = mockData.reduce((sum: number, item: any) => sum + (Number(item.total_capital) || 0), 0)
      stats.value.avgCapital = stats.value.total > 0 ? stats.value.totalCapital / stats.value.total : 0
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
      key: 'contract_id',
      label: t('corporateContracts.table.contractId'),
      sortable: true,
      searchable: true,
      width: '120px',
      render: (value) => `<span class="font-mono text-sm">${value}</span>`
    },
    {
      key: 'cr_number',
      label: t('corporateContracts.table.crNumber'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm">${value}</span>`
    },
    {
      key: 'entity_name',
      label: t('corporateContracts.table.entityName'),
      sortable: true,
      searchable: true,
      minWidth: '200px',
      render: (value, row) => {
        const langDesc = row.entity_name_lang_desc ? `<p class="text-xs text-gray-500">${row.entity_name_lang_desc}</p>` : ''
        return `<div><p class="font-medium text-gray-900 dark:text-white">${value}</p>${langDesc}</div>`
      }
    },
    {
      key: 'entity_type_name',
      label: t('corporateContracts.view.fields.entityType'),
      sortable: true,
      width: '150px'
    },
    {
      key: 'contract_date',
      label: t('corporateContracts.table.contractDate'),
      sortable: true,
      type: 'date',
      width: '130px',
      format: (value) => value ? new Date(value).toLocaleDateString() : '-'
    },
    {
      key: 'total_capital',
      label: t('corporateContracts.table.totalCapital'),
      sortable: true,
      width: '150px',
      render: (value) => {
        const formatted = formatCurrency(value)
        return `<span class="font-medium text-green-600 dark:text-green-400">${formatted}</span>`
      }
    },
    {
      key: 'headquarter_city_name',
      label: t('corporateContracts.table.city'),
      sortable: true,
      searchable: true,
      width: '150px'
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
      key: 'entity_type_name',
      label: t('corporateContracts.view.fields.entityType'),
      type: 'select',
      placeholder: 'All Types',
      options: [
        { label: 'All Types', value: null },
        { label: 'شركة', value: 'شركة' },
        { label: 'مؤسسة', value: 'مؤسسة' }
      ]
    },
    {
      key: 'headquarter_city_name',
      label: t('corporateContracts.table.city'),
      type: 'select',
      placeholder: t('wathqData.filters.allCities'),
      options: [
        { label: t('wathqData.filters.allCities'), value: null },
        { label: 'الرياض', value: 'الرياض' },
        { label: 'جدة', value: 'جدة' },
        { label: 'الدمام', value: 'الدمام' },
        { label: 'مكة', value: 'مكة' },
        { label: 'المدينة', value: 'المدينة' }
      ],
      searchable: true
    },
    {
      key: 'contract_id',
      label: t('corporateContracts.table.contractId'),
      type: 'text',
      placeholder: 'Search by contract ID...'
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
        router.push(`/wathq-data/corporate-contracts/${row.id}`)
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
        title: 'Delete Corporate Contract',
        message: 'Are you sure you want to delete this corporate contract? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/corporate-contracts/${row.id}`, {
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
        message: 'Are you sure you want to delete the selected corporate contracts?'
      },
      handler: async (selectedRows, selectedIds) => {
        try {
          await $fetch('/api/v1/wathq/corporate-contracts/bulk-delete', {
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
  keyField: 'contract_id',
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
  searchPlaceholder: t('corporateContracts.search'),
  searchDebounce: 300,
  
  // Export settings
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  // Sorting
  initialSortColumn: 'contract_id',
  initialSortDirection: 'desc',
  
  // Empty state
  emptyStateIcon: 'i-heroicons-document-text',
  emptyStateTitle: t('corporateContracts.noData'),
  emptyStateDescription: 'No corporate contracts found. Try adjusting your filters.',
  
  // State persistence
  persistState: true,
  stateKey: 'corporate-contracts-table-v1'
}

// Event handlers
function handleRowClick(row: any, index: number, event: Event) {
  console.log('Row clicked:', row)
}

function handleActionClick(action: any, row: any, index: number) {
  console.log('Action clicked:', action.key, row)
}
</script>
