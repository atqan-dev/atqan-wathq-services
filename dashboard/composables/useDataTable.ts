import { ref, computed, watch, type Ref } from 'vue'
import { useTable, type UseTableOptions, type UseTableReturn } from './useTable'

export interface DataTableColumn {
  key: string
  label: string
  sortable?: boolean
  searchable?: boolean
  visible?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  type?: 'text' | 'number' | 'date' | 'badge' | 'actions' | 'custom'
  format?: (value: any, row: any) => string
  component?: string
  props?: Record<string, any>
}

export interface DataTableFilter {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'daterange' | 'number' | 'boolean'
  options?: { label: string; value: any }[]
  multiple?: boolean
  placeholder?: string
}

export interface DataTableAction {
  key: string
  label: string
  icon?: string
  color?: string
  variant?: string
  size?: string
  condition?: (row: any) => boolean
  handler: (row: any, rows?: any[]) => void | Promise<void>
}

export interface UseDataTableOptions extends UseTableOptions {
  columns: DataTableColumn[]
  filters?: DataTableFilter[]
  actions?: DataTableAction[]
  bulkActions?: DataTableAction[]
  exportable?: boolean
  selectable?: boolean
  searchPlaceholder?: string
  emptyStateTitle?: string
  emptyStateDescription?: string
  persistState?: boolean
  stateKey?: string
}

export interface UseDataTableReturn<T = any> extends UseTableReturn<T> {
  // Columns
  columns: Ref<DataTableColumn[]>
  visibleColumns: Ref<DataTableColumn[]>
  
  // Filters
  filters: Ref<DataTableFilter[]>
  activeFilters: Ref<Record<string, any>>
  hasActiveFilters: Ref<boolean>
  
  // Actions
  actions: Ref<DataTableAction[]>
  bulkActions: Ref<DataTableAction[]>
  
  // Column visibility
  toggleColumnVisibility: (columnKey: string) => void
  showAllColumns: () => void
  hideAllColumns: () => void
  resetColumnVisibility: () => void
  
  // Filtering
  setFilter: (key: string, value: any) => void
  clearFilter: (key: string) => void
  clearAllFilters: () => void
  applyFilters: () => void
  
  // Export
  exportData: (format: 'csv' | 'json' | 'xlsx') => void
  
  // State persistence
  saveState: () => void
  loadState: () => void
  clearState: () => void
}

export function useDataTable<T = any>(
  fetchFunction: (params: {
    page: number
    pageSize: number
    search?: string
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
    filters?: Record<string, any>
  }) => Promise<{ data: T[], total: number }>,
  options: UseDataTableOptions
): UseDataTableReturn<T> {
  
  const {
    columns: initialColumns,
    filters: initialFilters = [],
    actions: initialActions = [],
    bulkActions: initialBulkActions = [],
    persistState = false,
    stateKey = 'datatable-state',
    ...tableOptions
  } = options

  // Initialize base table functionality
  const baseTable = useTable<T>(
    async (params) => {
      return await fetchFunction({
        ...params,
        filters: activeFilters.value
      })
    },
    tableOptions
  )

  // Column state
  const columns = ref<DataTableColumn[]>(
    initialColumns.map(col => ({
      ...col,
      visible: col.visible !== false // Default to visible unless explicitly false
    }))
  )

  // Filter state
  const filters = ref<DataTableFilter[]>(initialFilters)
  const activeFilters = ref<Record<string, any>>({})

  // Action state
  const actions = ref<DataTableAction[]>(initialActions)
  const bulkActions = ref<DataTableAction[]>(initialBulkActions)

  // Computed properties
  const visibleColumns = computed(() => 
    columns.value.filter(col => col.visible !== false)
  )

  const hasActiveFilters = computed(() => 
    Object.keys(activeFilters.value).some(key => {
      const value = activeFilters.value[key]
      return value !== null && value !== undefined && value !== '' && 
             (Array.isArray(value) ? value.length > 0 : true)
    })
  )

  // Watch for filter changes
  watch(activeFilters, () => {
    baseTable.currentPage.value = 1 // Reset to first page when filters change
    baseTable.refresh()
  }, { deep: true })

  // Column visibility methods
  const toggleColumnVisibility = (columnKey: string) => {
    const column = columns.value.find(col => col.key === columnKey)
    if (column) {
      column.visible = !column.visible
      saveState()
    }
  }

  const showAllColumns = () => {
    columns.value.forEach(col => {
      col.visible = true
    })
    saveState()
  }

  const hideAllColumns = () => {
    columns.value.forEach(col => {
      col.visible = false
    })
    saveState()
  }

  const resetColumnVisibility = () => {
    columns.value.forEach(col => {
      col.visible = col.visible !== false // Reset to initial state
    })
    saveState()
  }

  // Filter methods
  const setFilter = (key: string, value: any) => {
    if (value === null || value === undefined || value === '' || 
        (Array.isArray(value) && value.length === 0)) {
      delete activeFilters.value[key]
    } else {
      activeFilters.value[key] = value
    }
    saveState()
  }

  const clearFilter = (key: string) => {
    delete activeFilters.value[key]
    saveState()
  }

  const clearAllFilters = () => {
    activeFilters.value = {}
    saveState()
  }

  const applyFilters = () => {
    baseTable.refresh()
  }

  // Export methods
  const exportData = async (format: 'csv' | 'json' | 'xlsx') => {
    try {
      // Fetch all data for export (without pagination)
      const allData = await fetchFunction({
        page: 1,
        pageSize: 999999, // Large number to get all data
        search: baseTable.debouncedSearchQuery.value,
        sortBy: baseTable.sortColumn.value,
        sortOrder: baseTable.sortDirection.value,
        filters: activeFilters.value
      })

      const exportData = allData.data.map(row => {
        const exportRow: Record<string, any> = {}
        visibleColumns.value.forEach(col => {
          if (col.type !== 'actions') {
            exportRow[col.label] = col.format 
              ? col.format((row as any)[col.key], row)
              : (row as any)[col.key]
          }
        })
        return exportRow
      })

      if (format === 'csv') {
        downloadCSV(exportData)
      } else if (format === 'json') {
        downloadJSON(exportData)
      } else if (format === 'xlsx') {
        // Would need a library like xlsx for this
        console.warn('XLSX export not implemented yet')
      }
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  // Helper functions for export
  const downloadCSV = (data: any[]) => {
    if (data.length === 0) return

    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header]
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `export-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  const downloadJSON = (data: any[]) => {
    const jsonContent = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `export-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  // State persistence methods
  const saveState = () => {
    if (!persistState || !stateKey) return

    const state = {
      columns: columns.value.map(col => ({
        key: col.key,
        visible: col.visible
      })),
      filters: activeFilters.value,
      pagination: {
        pageSize: baseTable.pageSize.value
      },
      sorting: {
        column: baseTable.sortColumn.value,
        direction: baseTable.sortDirection.value
      }
    }

    try {
      localStorage.setItem(stateKey, JSON.stringify(state))
    } catch (error) {
      console.warn('Failed to save table state:', error)
    }
  }

  const loadState = () => {
    if (!persistState || !stateKey) return

    try {
      const savedState = localStorage.getItem(stateKey)
      if (!savedState) return

      const state = JSON.parse(savedState)

      // Restore column visibility
      if (state.columns) {
        state.columns.forEach((savedCol: any) => {
          const column = columns.value.find(col => col.key === savedCol.key)
          if (column) {
            column.visible = savedCol.visible
          }
        })
      }

      // Restore filters
      if (state.filters) {
        activeFilters.value = { ...state.filters }
      }

      // Restore pagination
      if (state.pagination?.pageSize) {
        baseTable.setPageSize(state.pagination.pageSize)
      }

      // Restore sorting
      if (state.sorting?.column) {
        baseTable.setSorting(state.sorting.column, state.sorting.direction)
      }
    } catch (error) {
      console.warn('Failed to load table state:', error)
    }
  }

  const clearState = () => {
    if (!persistState || !stateKey) return

    try {
      localStorage.removeItem(stateKey)
    } catch (error) {
      console.warn('Failed to clear table state:', error)
    }
  }

  // Load state on initialization
  if (persistState) {
    loadState()
  }

  return {
    // Base table functionality
    ...baseTable,
    
    // Enhanced functionality
    columns,
    visibleColumns,
    filters,
    activeFilters,
    hasActiveFilters,
    actions,
    bulkActions,
    
    // Column methods
    toggleColumnVisibility,
    showAllColumns,
    hideAllColumns,
    resetColumnVisibility,
    
    // Filter methods
    setFilter,
    clearFilter,
    clearAllFilters,
    applyFilters,
    
    // Export methods
    exportData,
    
    // State methods
    saveState,
    loadState,
    clearState
  }
}
