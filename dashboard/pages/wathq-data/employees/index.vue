<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.stats.total') }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
          </div>
          <UIcon name="i-heroicons-user-group" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.stats.active') }}</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
          </div>
          <UIcon name="i-heroicons-check-circle" class="w-10 h-10 text-green-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.stats.nationalities') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.nationalities }}</p>
          </div>
          <UIcon name="i-heroicons-globe-alt" class="w-10 h-10 text-blue-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('employees.stats.thisMonth') }}</p>
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
      :title="t('sidebar.employees')"
      :description="t('employees.subtitle')"
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
  active: 0,
  nationalities: 0,
  thisMonth: 0
})

const getMockData = () => {
  const now = new Date().toISOString()
  
  return [
    {
      employee_id: 1,
      name: 'أحمد محمد علي',
      nationality: 'Saudi',
      working_months: 36,
      employment_details: [
        {
          employment_id: 1,
          employer: 'شركة الرياض للتقنية',
          status: 'Active',
          basic_wage: 8000.00,
          housing_allowance: 2000.00,
          other_allowance: 500.00,
          full_wage: 10500.00
        }
      ],
      created_at: now,
      updated_at: now
    },
    {
      employee_id: 2,
      name: 'Mohammed Ali Hassan',
      nationality: 'Egyptian',
      working_months: 24,
      employment_details: [
        {
          employment_id: 2,
          employer: 'Jeddah Tech Solutions',
          status: 'Active',
          basic_wage: 6000.00,
          housing_allowance: 1500.00,
          other_allowance: 300.00,
          full_wage: 7800.00
        }
      ],
      created_at: now,
      updated_at: now
    },
    {
      employee_id: 3,
      name: 'فاطمة حسن',
      nationality: 'Saudi',
      working_months: 12,
      employment_details: [
        {
          employment_id: 3,
          employer: 'مؤسسة الدمام التجارية',
          status: 'Inactive',
          basic_wage: 5000.00,
          housing_allowance: 1000.00,
          other_allowance: 200.00,
          full_wage: 6200.00
        }
      ],
      created_at: now,
      updated_at: now
    }
  ]
}

function formatCurrency(amount: number | null | undefined) {
  if (!amount) return '-'
  return new Intl.NumberFormat('ar-SA', { 
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 2
  }).format(amount)
}

const tableConfig: DataTableConfig<any> = {
  fetchFunction: async (params) => {
    try {
      const skip = (params.page - 1) * params.pageSize
      
      const response = await $fetch('/api/v1/wathq/employees/', {
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
            item.name?.toLowerCase().includes(searchLower) ||
            item.nationality?.toLowerCase().includes(searchLower) ||
            item.employee_id?.toString().includes(searchLower)
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
      
      const activeCount = data.filter((item: any) => 
        item.employment_details?.some((ed: any) => ed.status === 'Active')
      ).length
      stats.value.active = activeCount
      
      const uniqueNationalities = new Set(data.map((item: any) => item.nationality).filter(Boolean))
      stats.value.nationalities = uniqueNationalities.size
      
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
      console.error('Failed to fetch employees:', error)
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.active = mockData.filter((item: any) => 
        item.employment_details?.some((ed: any) => ed.status === 'Active')
      ).length
      stats.value.nationalities = new Set(mockData.map((item: any) => item.nationality)).size
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
      key: 'employee_id',
      label: t('employees.table.employeeId'),
      sortable: true,
      width: '120px',
      render: (value) => `<span class="font-mono text-sm text-gray-600">#${value}</span>`
    },
    {
      key: 'name',
      label: t('employees.table.name'),
      sortable: true,
      searchable: true,
      width: '200px',
      render: (value) => `<span class="font-medium">${value || '-'}</span>`
    },
    {
      key: 'nationality',
      label: t('employees.table.nationality'),
      sortable: true,
      searchable: true,
      width: '150px'
    },
    {
      key: 'working_months',
      label: t('employees.table.workingMonths'),
      sortable: true,
      width: '150px',
      render: (value) => {
        if (!value) return '-'
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">${value} ${t('employees.view.fields.months')}</span>`
      }
    },
    {
      key: 'employment_details',
      label: t('employees.table.employmentCount'),
      sortable: false,
      width: '150px',
      render: (value) => {
        const count = Array.isArray(value) ? value.length : 0
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">${count}</span>`
      }
    },
    {
      key: 'employment_details',
      label: t('employees.table.status'),
      sortable: false,
      width: '120px',
      render: (value) => {
        const hasActive = Array.isArray(value) && value.some((ed: any) => ed.status === 'Active')
        if (hasActive) {
          return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</span>`
        }
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">Inactive</span>`
      }
    }
  ],

  filters: [
    {
      key: 'nationality',
      label: t('employees.table.nationality'),
      type: 'select',
      placeholder: 'All Nationalities',
      options: [
        { label: 'All Nationalities', value: null },
        { label: 'Saudi', value: 'Saudi' },
        { label: 'Egyptian', value: 'Egyptian' },
        { label: 'Indian', value: 'Indian' },
        { label: 'Pakistani', value: 'Pakistani' },
        { label: 'Bangladeshi', value: 'Bangladeshi' }
      ],
      searchable: true
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
        router.push(`/wathq-data/employees/${row.employee_id}`)
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
        title: 'Delete Employee',
        message: 'Are you sure you want to delete this employee? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/employees/${row.employee_id}`, {
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

  keyField: 'employee_id',
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
  searchPlaceholder: t('employees.search'),
  searchDebounce: 300,
  
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  initialSortColumn: 'employee_id',
  initialSortDirection: 'desc',
  
  emptyStateIcon: 'i-heroicons-user-group',
  emptyStateTitle: t('employees.noData'),
  emptyStateDescription: 'No employees found. Try adjusting your filters.',
  
  persistState: true,
  stateKey: 'employees-table-v1'
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
    }>('/api/v1/wathq/sync/employee/sync', {
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
