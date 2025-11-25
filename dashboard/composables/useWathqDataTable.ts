import { useDataTable, type UseDataTableReturn, type DataTableColumn, type DataTableFilter, type DataTableAction } from './useDataTable'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useI18n } from './useI18n'
import type { WathqApiRequest } from '~/types/wathq'

export interface WathqDataTableOptions {
  serviceType?: string
  endpoint?: string
  columns?: DataTableColumn[]
  filters?: DataTableFilter[]
  actions?: DataTableAction[]
  bulkActions?: DataTableAction[]
  persistState?: boolean
}

export function useWathqLiveRequestsTable(options: WathqDataTableOptions = {}): UseDataTableReturn<WathqApiRequest> {
  const { t } = useI18n()
  const { authenticatedFetch } = useAuthenticatedFetch()

  const defaultColumns: DataTableColumn[] = [
    {
      key: 'method',
      label: t('wathq.logs.table.method'),
      sortable: true,
      type: 'badge',
      width: '80px',
      format: (value) => value
    },
    {
      key: 'endpoint',
      label: t('wathq.logs.table.endpoint'),
      sortable: true,
      searchable: true,
      type: 'text',
      format: (value) => value
    },
    {
      key: 'status_code',
      label: t('wathq.logs.table.status'),
      sortable: true,
      type: 'badge',
      width: '100px',
      format: (value) => {
        const isSuccess = value >= 200 && value < 300
        return `${isSuccess ? '✓' : '✗'} ${value}`
      }
    },
    {
      key: 'duration_ms',
      label: t('wathq.logs.table.duration'),
      sortable: true,
      type: 'number',
      width: '100px',
      align: 'right',
      format: (value) => value ? `${value}ms` : '-'
    },
    {
      key: 'fetched_at',
      label: t('wathq.logs.table.timestamp'),
      sortable: true,
      type: 'date',
      width: '180px',
      format: (value) => new Date(value).toLocaleString()
    },
    {
      key: 'actions',
      label: t('common.actions'),
      type: 'actions',
      width: '120px',
      align: 'right'
    }
  ]

  const defaultFilters: DataTableFilter[] = [
    {
      key: 'method',
      label: t('wathq.logs.table.method'),
      type: 'select',
      options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' },
        { label: 'PUT', value: 'PUT' },
        { label: 'DELETE', value: 'DELETE' }
      ]
    },
    {
      key: 'is_success',
      label: t('wathq.logs.table.status'),
      type: 'select',
      options: [
        { label: t('common.success'), value: true },
        { label: t('common.failed'), value: false }
      ]
    },
    {
      key: 'service_type',
      label: t('wathq.logs.table.service'),
      type: 'select',
      options: [
        { label: 'Commercial Registration', value: 'commercial-registration' },
        { label: 'Real Estate', value: 'real-estate' },
        { label: 'Employee', value: 'employee' },
        { label: 'Attorney', value: 'attorney' },
        { label: 'Company Contract', value: 'company-contract' },
        { label: 'SPL National Address', value: 'spl-national-address' }
      ]
    },
    {
      key: 'date_range',
      label: t('common.dateRange'),
      type: 'daterange'
    }
  ]

  const defaultActions: DataTableAction[] = [
    {
      key: 'view',
      label: t('common.view'),
      icon: 'i-heroicons-eye',
      color: 'gray',
      variant: 'ghost',
      size: 'xs',
      handler: (row) => {
        // Emit event or handle view action
        console.log('View request:', row)
      }
    },
    {
      key: 'retry',
      label: t('common.retry'),
      icon: 'i-heroicons-arrow-path',
      color: 'blue',
      variant: 'ghost',
      size: 'xs',
      condition: (row) => !row.is_success,
      handler: async (row) => {
        // Handle retry logic
        console.log('Retry request:', row)
      }
    }
  ]

  const fetchFunction = async (params: {
    page: number
    pageSize: number
    search?: string
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
    filters?: Record<string, any>
  }) => {
    const queryParams = new URLSearchParams({
      skip: ((params.page - 1) * params.pageSize).toString(),
      limit: params.pageSize.toString()
    })

    // Apply filters
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, value.toString())
        }
      })
    }

    // Use the correct endpoint based on service type
    let endpoint = '/api/v1/wathq/logs/my-calls'
    if (options.serviceType) {
      endpoint = `/api/v1/wathq/logs/service-calls/${options.serviceType}`
    }

    const response = await authenticatedFetch(`${endpoint}?${queryParams}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch live requests: ${response.statusText}`)
    }

    const result = await response.json()
    
    // The API returns an array directly, not a paginated response
    const data = Array.isArray(result) ? result : []
    
    return {
      data: data,
      total: data.length // Since we don't have total count, use array length
    }
  }

  return useDataTable<WathqApiRequest>(fetchFunction, {
    columns: options.columns || defaultColumns,
    filters: options.filters || defaultFilters,
    actions: options.actions || defaultActions,
    bulkActions: options.bulkActions || [],
    initialPageSize: 25,
    initialSortColumn: 'fetched_at',
    initialSortDirection: 'desc',
    persistState: options.persistState ?? true,
    stateKey: `wathq-live-requests-${options.serviceType || 'all'}`,
    exportable: true,
    selectable: true,
    searchPlaceholder: t('wathq.logs.searchPlaceholder'),
    emptyStateTitle: t('wathq.logs.empty.title'),
    emptyStateDescription: t('wathq.logs.empty.description')
  })
}

export function useWathqRequestLogsTable(options: WathqDataTableOptions = {}): UseDataTableReturn<WathqApiRequest> {
  const { t } = useI18n()
  const { authenticatedFetch } = useAuthenticatedFetch()

  const defaultColumns: DataTableColumn[] = [
    {
      key: 'method',
      label: t('wathq.logs.table.method'),
      sortable: true,
      type: 'badge',
      width: '80px'
    },
    {
      key: 'endpoint',
      label: t('wathq.logs.table.endpoint'),
      sortable: true,
      searchable: true,
      type: 'text'
    },
    {
      key: 'status_code',
      label: t('wathq.logs.table.status'),
      sortable: true,
      type: 'badge',
      width: '100px',
      format: (value) => {
        const isSuccess = value >= 200 && value < 300
        return `${isSuccess ? '✓' : '✗'} ${value}`
      }
    },
    {
      key: 'duration_ms',
      label: t('wathq.logs.table.duration'),
      sortable: true,
      type: 'number',
      width: '100px',
      align: 'right',
      format: (value) => value ? `${value}ms` : '-'
    },
    {
      key: 'service_slug',
      label: t('wathq.logs.table.service'),
      sortable: true,
      searchable: true,
      type: 'text',
      width: '150px'
    },
    {
      key: 'fetched_at',
      label: t('wathq.logs.table.timestamp'),
      sortable: true,
      type: 'date',
      width: '180px',
      format: (value) => new Date(value).toLocaleString()
    },
    {
      key: 'actions',
      label: t('common.actions'),
      type: 'actions',
      width: '120px',
      align: 'right'
    }
  ]

  const defaultFilters: DataTableFilter[] = [
    {
      key: 'method',
      label: t('wathq.logs.table.method'),
      type: 'select',
      options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' },
        { label: 'PUT', value: 'PUT' },
        { label: 'DELETE', value: 'DELETE' }
      ]
    },
    {
      key: 'status_code',
      label: t('wathq.logs.table.status'),
      type: 'select',
      options: [
        { label: 'Success (2xx)', value: '2xx' },
        { label: 'Client Error (4xx)', value: '4xx' },
        { label: 'Server Error (5xx)', value: '5xx' }
      ]
    },
    {
      key: 'service_slug',
      label: t('wathq.logs.table.service'),
      type: 'select',
      options: [
        { label: 'Commercial Registration', value: 'commercial-registration' },
        { label: 'Real Estate', value: 'real-estate' },
        { label: 'Employee', value: 'employee' },
        { label: 'Attorney', value: 'attorney' },
        { label: 'Company Contract', value: 'company-contract' },
        { label: 'SPL National Address', value: 'spl-national-address' }
      ]
    }
  ]

  const defaultActions: DataTableAction[] = [
    {
      key: 'view',
      label: t('common.view'),
      icon: 'i-heroicons-eye',
      color: 'gray',
      variant: 'ghost',
      size: 'xs',
      handler: (row) => {
        console.log('View request log:', row)
      }
    }
  ]

  const fetchFunction = async (params: {
    page: number
    pageSize: number
    search?: string
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
    filters?: Record<string, any>
  }) => {
    const queryParams = new URLSearchParams({
      skip: ((params.page - 1) * params.pageSize).toString(),
      limit: params.pageSize.toString()
    })

    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, value.toString())
        }
      })
    }

    // Use tenant calls for logs (more comprehensive)
    let endpoint = '/api/v1/wathq/logs/tenant-calls'
    if (options.serviceType) {
      endpoint = `/api/v1/wathq/logs/service-calls/${options.serviceType}`
    }

    const response = await authenticatedFetch(`${endpoint}?${queryParams}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch request logs: ${response.statusText}`)
    }

    const result = await response.json()
    
    // The API returns an array directly
    const data = Array.isArray(result) ? result : []
    
    return {
      data: data,
      total: data.length
    }
  }

  return useDataTable<WathqApiRequest>(fetchFunction, {
    columns: options.columns || defaultColumns,
    filters: options.filters || defaultFilters,
    actions: options.actions || defaultActions,
    bulkActions: options.bulkActions || [],
    initialPageSize: 25,
    initialSortColumn: 'fetched_at',
    initialSortDirection: 'desc',
    persistState: options.persistState ?? true,
    stateKey: `wathq-request-logs-${options.serviceType || 'all'}`,
    exportable: true,
    selectable: true,
    searchPlaceholder: t('wathq.logs.searchPlaceholder'),
    emptyStateTitle: t('wathq.logs.empty.title'),
    emptyStateDescription: t('wathq.logs.empty.description')
  })
}

export function useWathqOfflineRequestsTable(options: WathqDataTableOptions = {}): UseDataTableReturn<any> {
  const { t } = useI18n()
  const { authenticatedFetch } = useAuthenticatedFetch()

  const defaultColumns: DataTableColumn[] = [
    {
      key: 'service_name',
      label: t('wathq.offline.table.service'),
      sortable: true,
      searchable: true,
      type: 'text',
      width: '200px'
    },
    {
      key: 'endpoint',
      label: t('wathq.offline.table.endpoint'),
      sortable: true,
      searchable: true,
      type: 'text'
    },
    {
      key: 'method',
      label: t('wathq.offline.table.method'),
      sortable: true,
      type: 'badge',
      width: '80px'
    },
    {
      key: 'cached_at',
      label: t('wathq.offline.table.cachedAt'),
      sortable: true,
      type: 'date',
      width: '180px',
      format: (value) => new Date(value).toLocaleString()
    },
    {
      key: 'data_size',
      label: t('wathq.offline.table.size'),
      sortable: true,
      type: 'text',
      width: '100px',
      align: 'right',
      format: (value) => formatBytes(value)
    },
    {
      key: 'actions',
      label: t('common.actions'),
      type: 'actions',
      width: '120px',
      align: 'right'
    }
  ]

  const defaultFilters: DataTableFilter[] = [
    {
      key: 'service_name',
      label: t('wathq.offline.table.service'),
      type: 'select',
      options: [
        { label: 'Commercial Registration', value: 'commercial-registration' },
        { label: 'Real Estate', value: 'real-estate' },
        { label: 'Employee', value: 'employee' },
        { label: 'Attorney', value: 'attorney' },
        { label: 'Company Contract', value: 'company-contract' },
        { label: 'SPL National Address', value: 'spl-national-address' }
      ]
    },
    {
      key: 'method',
      label: t('wathq.offline.table.method'),
      type: 'select',
      options: [
        { label: 'GET', value: 'GET' },
        { label: 'POST', value: 'POST' }
      ]
    }
  ]

  const defaultActions: DataTableAction[] = [
    {
      key: 'view',
      label: t('common.view'),
      icon: 'i-heroicons-eye',
      color: 'gray',
      variant: 'ghost',
      size: 'xs',
      handler: (row) => {
        console.log('View offline data:', row)
      }
    },
    {
      key: 'refresh',
      label: t('common.refresh'),
      icon: 'i-heroicons-arrow-path',
      color: 'blue',
      variant: 'ghost',
      size: 'xs',
      handler: async (row) => {
        console.log('Refresh offline data:', row)
      }
    }
  ]

  const fetchFunction = async (params: {
    page: number
    pageSize: number
    search?: string
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
    filters?: Record<string, any>
  }) => {
    const queryParams = new URLSearchParams({
      skip: ((params.page - 1) * params.pageSize).toString(),
      limit: params.pageSize.toString()
    })

    if (params.search) {
      queryParams.append('url_pattern', params.search)
    }

    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, value.toString())
        }
      })
    }

    let endpoint = '/api/v1/wathq/offline'
    
    if (options.serviceType) {
      endpoint = `/api/v1/wathq/offline/service-slug/${options.serviceType}`
    } else {
      endpoint = '/api/v1/wathq/offline/my-data'
    }

    const response = await authenticatedFetch(`${endpoint}?${queryParams}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch offline data: ${response.statusText}`)
    }

    const result = await response.json()
    
    // Handle both array response and paginated response
    const data = Array.isArray(result) ? result : (result.data || result.items || [])
    const total = Array.isArray(result) ? result.length : (result.total || result.count || data.length)
    
    return { data, total }
  }

  return useDataTable(fetchFunction, {
    columns: options.columns || defaultColumns,
    filters: options.filters || defaultFilters,
    actions: options.actions || defaultActions,
    bulkActions: options.bulkActions || [],
    initialPageSize: 25,
    initialSortColumn: 'cached_at',
    initialSortDirection: 'desc',
    persistState: options.persistState ?? true,
    stateKey: `wathq-offline-requests-${options.serviceType || 'all'}`,
    exportable: true,
    selectable: true,
    searchPlaceholder: t('wathq.offline.searchPlaceholder'),
    emptyStateTitle: t('wathq.offline.empty.title'),
    emptyStateDescription: t('wathq.offline.empty.description')
  })
}

// Helper function to format bytes
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
