<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.stats.total') }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
          </div>
          <UIcon name="i-heroicons-home-modern" class="w-10 h-10 text-primary-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.stats.constrained') }}</p>
            <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ stats.constrained }}</p>
          </div>
          <UIcon name="i-heroicons-lock-closed" class="w-10 h-10 text-orange-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.stats.mortgaged') }}</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ stats.mortgaged }}</p>
          </div>
          <UIcon name="i-heroicons-banknotes" class="w-10 h-10 text-red-500" />
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('realEstateDeeds.stats.thisMonth') }}</p>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.thisMonth }}</p>
          </div>
          <UIcon name="i-heroicons-calendar" class="w-10 h-10 text-blue-500" />
        </div>
      </UCard>
    </div>

    <!-- Advanced DataTable -->
    <AdvancedDataTable
      :config="tableConfig"
      :title="t('sidebar.realEstateDeeds')"
      :description="t('realEstateDeeds.subtitle')"
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

definePageMeta({
  layout: 'default',
  middleware: 'auth'
})

const stats = ref({
  total: 0,
  constrained: 0,
  mortgaged: 0,
  thisMonth: 0
})

const getMockData = () => {
  const now = new Date().toISOString()
  
  return [
    {
      id: 1,
      deed_number: '123456789',
      deed_serial: 'RYD-2024-001',
      deed_date: '1445/06/15',
      deed_city: 'Riyadh',
      deed_status: 'Active',
      deed_area: 500.50,
      deed_area_text: 'خمسمائة وخمسون سنتيمتر مربع',
      is_real_estate_constrained: false,
      is_real_estate_halted: false,
      is_real_estate_mortgaged: false,
      is_real_estate_testamented: false,
      owners: [{ owner_name: 'أحمد محمد' }, { owner_name: 'سارة علي' }],
      real_estates: [{ city_name: 'Riyadh', area: 500.50 }],
      created_at: now,
      updated_at: now
    },
    {
      id: 2,
      deed_number: '987654321',
      deed_serial: 'JED-2024-002',
      deed_date: '1445/05/10',
      deed_city: 'Jeddah',
      deed_status: 'Active',
      deed_area: 750.25,
      deed_area_text: 'سبعمائة وخمسون سنتيمتر مربع',
      is_real_estate_constrained: true,
      is_real_estate_halted: false,
      is_real_estate_mortgaged: true,
      is_real_estate_testamented: false,
      owners: [{ owner_name: 'خالد سعيد' }],
      real_estates: [{ city_name: 'Jeddah', area: 750.25 }],
      created_at: now,
      updated_at: now
    },
    {
      id: 3,
      deed_number: '456789123',
      deed_serial: 'DAM-2024-003',
      deed_date: '1445/07/20',
      deed_city: 'Dammam',
      deed_status: 'Pending',
      deed_area: 1000.00,
      deed_area_text: 'ألف متر مربع',
      is_real_estate_constrained: false,
      is_real_estate_halted: true,
      is_real_estate_mortgaged: false,
      is_real_estate_testamented: true,
      owners: [{ owner_name: 'فاطمة حسن' }, { owner_name: 'محمد عبدالله' }],
      real_estates: [{ city_name: 'Dammam', area: 1000.00 }],
      created_at: now,
      updated_at: now
    }
  ]
}

function formatArea(area: number) {
  if (!area) return '-'
  return new Intl.NumberFormat('ar-SA', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  }).format(area) + ' م²'
}

const tableConfig: DataTableConfig<any> = {
  fetchFunction: async (params) => {
    try {
      const skip = (params.page - 1) * params.pageSize
      
      const response = await $fetch('/api/v1/wathq/real-estate-deeds/', {
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
            item.deed_number?.toLowerCase().includes(searchLower) ||
            item.deed_serial?.toLowerCase().includes(searchLower) ||
            item.deed_city?.toLowerCase().includes(searchLower) ||
            item.deed_status?.toLowerCase().includes(searchLower)
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
      stats.value.constrained = data.filter((item: any) => item.is_real_estate_constrained).length
      stats.value.mortgaged = data.filter((item: any) => item.is_real_estate_mortgaged).length
      
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
      console.error('Failed to fetch deeds:', error)
      const mockData = getMockData()
      
      stats.value.total = mockData.length
      stats.value.constrained = mockData.filter((item: any) => item.is_real_estate_constrained).length
      stats.value.mortgaged = mockData.filter((item: any) => item.is_real_estate_mortgaged).length
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
      key: 'id',
      label: 'ID',
      sortable: true,
      visible: true,
      width: '80px',
      render: (value) => `<span class="font-mono text-sm text-gray-600">#${value}</span>`
    },
    {
      key: 'deed_number',
      label: t('realEstateDeeds.table.deedNumber'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm font-medium">${value || '-'}</span>`
    },
    {
      key: 'deed_serial',
      label: t('realEstateDeeds.table.deedSerial'),
      sortable: true,
      searchable: true,
      width: '150px',
      render: (value) => `<span class="font-mono text-sm">${value || '-'}</span>`
    },
    {
      key: 'deed_date',
      label: t('realEstateDeeds.table.deedDate'),
      sortable: true,
      width: '130px'
    },
    {
      key: 'deed_city',
      label: t('realEstateDeeds.table.deedCity'),
      sortable: true,
      searchable: true,
      width: '120px'
    },
    {
      key: 'deed_status',
      label: t('realEstateDeeds.table.deedStatus'),
      sortable: true,
      type: 'badge',
      width: '120px',
      cellClass: (value) => {
        const status = value?.toLowerCase()
        if (status === 'active') return 'text-green-600'
        if (status === 'pending') return 'text-yellow-600'
        return 'text-gray-600'
      }
    },
    {
      key: 'deed_area',
      label: t('realEstateDeeds.table.deedArea'),
      sortable: true,
      width: '130px',
      format: (value) => formatArea(value)
    },
    {
      key: 'owners',
      label: t('realEstateDeeds.table.ownersCount'),
      sortable: false,
      width: '120px',
      render: (value) => {
        const count = Array.isArray(value) ? value.length : 0
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">${count}</span>`
      }
    },
    {
      key: 'real_estates',
      label: t('realEstateDeeds.table.realEstatesCount'),
      sortable: false,
      width: '120px',
      render: (value) => {
        const count = Array.isArray(value) ? value.length : 0
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">${count}</span>`
      }
    }
  ],

  filters: [
    {
      key: 'deed_status',
      label: t('realEstateDeeds.table.deedStatus'),
      type: 'select',
      placeholder: 'All Statuses',
      options: [
        { label: 'All Statuses', value: null },
        { label: 'Active', value: 'Active' },
        { label: 'Pending', value: 'Pending' },
        { label: 'Inactive', value: 'Inactive' }
      ]
    },
    {
      key: 'deed_city',
      label: t('realEstateDeeds.table.deedCity'),
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
        router.push(`/wathq-data/real-estate-deeds/${row.id}`)
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
        title: 'Delete Deed',
        message: 'Are you sure you want to delete this deed? This action cannot be undone.'
      },
      handler: async (row) => {
        try {
          await $fetch(`/api/v1/wathq/real-estate-deeds/${row.id}`, {
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

  keyField: 'deed_number',
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
  searchPlaceholder: t('realEstateDeeds.search'),
  searchDebounce: 300,
  
  exportable: true,
  exportFormats: ['csv', 'json'],
  
  initialSortColumn: 'deed_number',
  initialSortDirection: 'desc',
  
  emptyStateIcon: 'i-heroicons-home-modern',
  emptyStateTitle: t('realEstateDeeds.noData'),
  emptyStateDescription: 'No real estate deeds found. Try adjusting your filters.',
  
  persistState: true,
  stateKey: 'real-estate-deeds-table-v1'
}

function handleRowClick(row: any, index: number, event: Event) {
  console.log('Row clicked:', row)
}

function handleActionClick(action: any, row: any, index: number) {
  console.log('Action clicked:', action.key, row)
}
</script>
