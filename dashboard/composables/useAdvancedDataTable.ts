/**
 * Advanced DataTable Composable
 * A comprehensive, reusable composable for data tables with all features
 */

import { ref, computed, reactive, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type {
  DataTableItem,
  DataTableColumn,
  DataTableFilter,
  DataTableAction,
  DataTableBulkAction,
  DataTableConfig,
  DataTableState,
  DataTableFetchParams,
  DataTableFetchResult,
  DataTableFetchFunction,
  DataTableSort,
  DataTablePagination,
  DataTableSelection
} from '~/types/datatable'

// Utility functions
const debounce = <T extends (...args: any[]) => any>(fn: T, delay: number): T => {
  let timeoutId: NodeJS.Timeout
  return ((...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }) as T
}

const deepClone = <T>(obj: T): T => JSON.parse(JSON.stringify(obj))

const getNestedValue = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

const setNestedValue = (obj: any, path: string, value: any): void => {
  const keys = path.split('.')
  const lastKey = keys.pop()!
  const target = keys.reduce((current, key) => {
    if (!(key in current)) current[key] = {}
    return current[key]
  }, obj)
  target[lastKey] = value
}

export function useAdvancedDataTable<T extends DataTableItem = DataTableItem>(
  config: DataTableConfig<T>
) {
  // Reactive state
  const state = reactive<DataTableState<T>>({
    data: [],
    filteredData: [],
    paginatedData: [],
    loading: false,
    refreshing: false,
    pagination: {
      page: config.initialPage || 1,
      pageSize: config.initialPageSize || 10,
      total: 0,
      totalPages: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: true,
      pageSizeOptions: config.pageSizeOptions || [10, 20, 50, 100]
    },
    sort: {
      column: config.initialSortColumn || null,
      direction: config.initialSortDirection || null
    },
    filters: {},
    globalSearch: '',
    selection: {
      enabled: config.selectable || false,
      multiple: config.multiSelect !== false,
      selectedRows: [],
      selectedIds: [],
      selectAll: false,
      indeterminate: false
    },
    visibleColumns: config.columns.filter(col => col.visible !== false).map(col => col.key),
    columnOrder: config.columns.map(col => col.key),
    expandedRows: [],
    error: null
  })

  // Refs for internal state
  const searchDebounceMs = ref(config.searchDebounce || 300)
  const keyField = ref(config.keyField || 'id')

  // Initialize filters
  if (config.filters) {
    config.filters.forEach(filter => {
      state.filters[filter.key] = filter.defaultValue || null
    })
  }

  // Computed properties
  const visibleColumnsComputed = computed(() => 
    config.columns.filter(col => state.visibleColumns.includes(col.key))
  )

  const hasSelection = computed(() => state.selection.enabled)
  const hasActions = computed(() => config.actions && config.actions.length > 0)
  const hasBulkActions = computed(() => config.bulkActions && config.bulkActions.length > 0)
  const hasFilters = computed(() => config.filters && config.filters.length > 0)

  const selectedCount = computed(() => state.selection.selectedRows.length)
  const isAllSelected = computed(() => 
    state.paginatedData.length > 0 && 
    state.selection.selectedRows.length === state.paginatedData.length
  )
  const isIndeterminate = computed(() => 
    state.selection.selectedRows.length > 0 && 
    state.selection.selectedRows.length < state.paginatedData.length
  )

  // Data processing functions
  const applyFilters = (data: T[]): T[] => {
    let filtered = [...data]

    // Apply global search
    if (state.globalSearch && config.globalSearch !== false) {
      const searchTerm = state.globalSearch.toLowerCase()
      const searchableColumns = config.columns.filter(col => col.searchable !== false)
      
      filtered = filtered.filter(row => 
        searchableColumns.some(col => {
          const value = getNestedValue(row, col.key)
          return String(value || '').toLowerCase().includes(searchTerm)
        })
      )
    }

    // Apply column filters
    Object.entries(state.filters).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') return

      const filter = config.filters?.find(f => f.key === key)
      if (!filter) return

      filtered = filtered.filter(row => {
        const rowValue = getNestedValue(row, key)
        
        switch (filter.type) {
          case 'text':
            return String(rowValue || '').toLowerCase().includes(String(value).toLowerCase())
          
          case 'select':
            return filter.multiple 
              ? Array.isArray(value) && value.includes(rowValue)
              : rowValue === value
          
          case 'multiselect':
            return Array.isArray(value) && value.includes(rowValue)
          
          case 'boolean':
            return Boolean(rowValue) === Boolean(value)
          
          case 'number':
            return Number(rowValue) === Number(value)
          
          case 'numberrange':
            if (Array.isArray(value) && value.length === 2) {
              const num = Number(rowValue)
              return num >= value[0] && num <= value[1]
            }
            return true
          
          case 'date':
            const rowDate = new Date(rowValue)
            const filterDate = new Date(value)
            return rowDate.toDateString() === filterDate.toDateString()
          
          case 'daterange':
            if (Array.isArray(value) && value.length === 2) {
              const rowDate = new Date(rowValue)
              const startDate = new Date(value[0])
              const endDate = new Date(value[1])
              return rowDate >= startDate && rowDate <= endDate
            }
            return true
          
          default:
            return true
        }
      })
    })

    return filtered
  }

  const applySorting = (data: T[]): T[] => {
    if (!state.sort.column || !state.sort.direction) return data

    const column = config.columns.find(col => col.key === state.sort.column)
    if (!column || column.sortable === false) return data

    return [...data].sort((a, b) => {
      const aValue = getNestedValue(a, state.sort.column!)
      const bValue = getNestedValue(b, state.sort.column!)

      let comparison = 0

      if (column.type === 'number') {
        comparison = Number(aValue || 0) - Number(bValue || 0)
      } else if (column.type === 'date') {
        comparison = new Date(aValue || 0).getTime() - new Date(bValue || 0).getTime()
      } else {
        const aStr = String(aValue || '').toLowerCase()
        const bStr = String(bValue || '').toLowerCase()
        comparison = aStr.localeCompare(bStr)
      }

      return state.sort.direction === 'desc' ? -comparison : comparison
    })
  }

  const applyPagination = (data: T[]): T[] => {
    if (!config.pagination) return data

    const start = (state.pagination.page - 1) * state.pagination.pageSize
    const end = start + state.pagination.pageSize
    return data.slice(start, end)
  }

  const processData = () => {
    let processed = [...state.data]
    
    // Apply filters
    processed = applyFilters(processed)
    state.filteredData = processed

    // Update pagination totals
    state.pagination.total = processed.length
    state.pagination.totalPages = Math.ceil(processed.length / state.pagination.pageSize)

    // Apply sorting
    processed = applySorting(processed)

    // Apply pagination
    state.paginatedData = applyPagination(processed)

    // Update selection state
    updateSelectionState()
  }

  // Selection functions
  const updateSelectionState = () => {
    state.selection.selectAll = isAllSelected.value
    state.selection.indeterminate = isIndeterminate.value
  }

  const toggleRowSelection = (row: T, selected?: boolean) => {
    const id = getNestedValue(row, keyField.value)
    const index = state.selection.selectedIds.indexOf(id)
    const isSelected = selected !== undefined ? selected : index === -1

    if (isSelected && index === -1) {
      if (!state.selection.multiple) {
        state.selection.selectedRows = [row]
        state.selection.selectedIds = [id]
      } else {
        state.selection.selectedRows.push(row)
        state.selection.selectedIds.push(id)
      }
    } else if (!isSelected && index !== -1) {
      state.selection.selectedRows.splice(index, 1)
      state.selection.selectedIds.splice(index, 1)
    }

    updateSelectionState()
  }

  const toggleAllSelection = (selected?: boolean) => {
    const shouldSelect = selected !== undefined ? selected : !state.selection.selectAll

    if (shouldSelect) {
      state.paginatedData.forEach(row => {
        const id = getNestedValue(row, keyField.value)
        if (!state.selection.selectedIds.includes(id)) {
          state.selection.selectedRows.push(row)
          state.selection.selectedIds.push(id)
        }
      })
    } else {
      state.paginatedData.forEach(row => {
        const id = getNestedValue(row, keyField.value)
        const index = state.selection.selectedIds.indexOf(id)
        if (index !== -1) {
          state.selection.selectedRows.splice(index, 1)
          state.selection.selectedIds.splice(index, 1)
        }
      })
    }

    updateSelectionState()
  }

  const clearSelection = () => {
    state.selection.selectedRows = []
    state.selection.selectedIds = []
    updateSelectionState()
  }

  // Data fetching
  const fetchData = async (params?: Partial<DataTableFetchParams>) => {
    if (!config.fetchFunction) return

    state.loading = true
    state.error = null

    try {
      const fetchParams: DataTableFetchParams = {
        page: state.pagination.page,
        pageSize: state.pagination.pageSize,
        search: state.globalSearch,
        sortBy: state.sort.column || undefined,
        sortOrder: state.sort.direction || undefined,
        filters: { ...state.filters },
        ...params
      }

      const result = await config.fetchFunction(fetchParams)
      
      state.data = result.data
      state.pagination.total = result.total
      state.pagination.totalPages = result.totalPages || Math.ceil(result.total / state.pagination.pageSize)
      
      if (result.page) state.pagination.page = result.page
      if (result.pageSize) state.pagination.pageSize = result.pageSize

      processData()
    } catch (error) {
      state.error = error instanceof Error ? error.message : 'Failed to fetch data'
      console.error('DataTable fetch error:', error)
    } finally {
      state.loading = false
    }
  }

  const refresh = async () => {
    state.refreshing = true
    await fetchData()
    state.refreshing = false
  }

  // Pagination functions
  const goToPage = (page: number) => {
    if (page < 1 || page > state.pagination.totalPages) return
    state.pagination.page = page
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  const changePageSize = (pageSize: number) => {
    state.pagination.pageSize = pageSize
    state.pagination.page = 1
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  const nextPage = () => goToPage(state.pagination.page + 1)
  const prevPage = () => goToPage(state.pagination.page - 1)
  const firstPage = () => goToPage(1)
  const lastPage = () => goToPage(state.pagination.totalPages)

  // Sorting functions
  const sortBy = (column: string, direction?: 'asc' | 'desc') => {
    const col = config.columns.find(c => c.key === column)
    if (!col || col.sortable === false) return

    if (state.sort.column === column) {
      // Toggle direction
      if (state.sort.direction === 'asc') {
        state.sort.direction = 'desc'
      } else if (state.sort.direction === 'desc') {
        state.sort.column = null
        state.sort.direction = null
      } else {
        state.sort.direction = 'asc'
      }
    } else {
      state.sort.column = column
      state.sort.direction = direction || 'asc'
    }

    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  const clearSort = () => {
    state.sort.column = null
    state.sort.direction = null
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  // Filter functions
  const setFilter = (key: string, value: any) => {
    state.filters[key] = value
    state.pagination.page = 1 // Reset to first page when filtering
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  const clearFilter = (key: string) => {
    delete state.filters[key]
    state.pagination.page = 1
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  const clearAllFilters = () => {
    state.filters = {}
    state.globalSearch = ''
    state.pagination.page = 1
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }

  // Search function with debouncing
  const debouncedSearch = debounce(() => {
    state.pagination.page = 1
    
    if (config.fetchFunction) {
      fetchData()
    } else {
      processData()
    }
  }, searchDebounceMs.value)

  const setGlobalSearch = (search: string) => {
    state.globalSearch = search
    debouncedSearch()
  }

  // Column visibility functions
  const toggleColumnVisibility = (columnKey: string) => {
    const index = state.visibleColumns.indexOf(columnKey)
    if (index === -1) {
      state.visibleColumns.push(columnKey)
    } else {
      state.visibleColumns.splice(index, 1)
    }
  }

  const showColumn = (columnKey: string) => {
    if (!state.visibleColumns.includes(columnKey)) {
      state.visibleColumns.push(columnKey)
    }
  }

  const hideColumn = (columnKey: string) => {
    const index = state.visibleColumns.indexOf(columnKey)
    if (index !== -1) {
      state.visibleColumns.splice(index, 1)
    }
  }

  const resetColumnVisibility = () => {
    state.visibleColumns = config.columns.filter(col => col.visible !== false).map(col => col.key)
  }

  // Export functions
  const exportData = async (format: 'csv' | 'excel' | 'pdf' | 'json', filename?: string) => {
    const dataToExport = config.exportable ? state.filteredData : state.data
    const exportFilename = filename || `datatable-export-${new Date().toISOString().split('T')[0]}`

    // This would typically integrate with a library like xlsx, jsPDF, etc.
    // For now, we'll provide the basic structure
    
    switch (format) {
      case 'csv':
        exportToCsv(dataToExport, exportFilename)
        break
      case 'json':
        exportToJson(dataToExport, exportFilename)
        break
      case 'excel':
        // Would use xlsx library
        console.log('Excel export not implemented yet')
        break
      case 'pdf':
        // Would use jsPDF library
        console.log('PDF export not implemented yet')
        break
    }
  }

  const exportToCsv = (data: T[], filename: string) => {
    const headers = visibleColumnsComputed.value.map(col => col.label).join(',')
    const rows = data.map(row => 
      visibleColumnsComputed.value.map(col => {
        const value = getNestedValue(row, col.key)
        return `"${String(value || '').replace(/"/g, '""')}"`
      }).join(',')
    ).join('\n')
    
    const csv = `${headers}\n${rows}`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const exportToJson = (data: T[], filename: string) => {
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // State persistence
  const saveState = () => {
    if (!config.persistState || !config.stateKey) return

    const stateToSave = {
      pagination: state.pagination,
      sort: state.sort,
      filters: state.filters,
      visibleColumns: state.visibleColumns,
      columnOrder: state.columnOrder
    }

    localStorage.setItem(`datatable-${config.stateKey}`, JSON.stringify(stateToSave))
  }

  const loadState = () => {
    if (!config.persistState || !config.stateKey) return

    try {
      const savedState = localStorage.getItem(`datatable-${config.stateKey}`)
      if (savedState) {
        const parsed = JSON.parse(savedState)
        Object.assign(state.pagination, parsed.pagination)
        Object.assign(state.sort, parsed.sort)
        Object.assign(state.filters, parsed.filters)
        state.visibleColumns = parsed.visibleColumns || state.visibleColumns
        state.columnOrder = parsed.columnOrder || state.columnOrder
      }
    } catch (error) {
      console.warn('Failed to load DataTable state:', error)
    }
  }

  // Watchers
  watch(
    () => [state.pagination, state.sort, state.filters, state.visibleColumns, state.columnOrder],
    () => {
      if (config.persistState) {
        saveState()
      }
    },
    { deep: true }
  )

  // Initialize
  onMounted(() => {
    loadState()
    
    if (config.data) {
      state.data = [...config.data]
      processData()
    } else if (config.fetchFunction) {
      fetchData()
    }
  })

  // Cleanup
  onUnmounted(() => {
    if (config.persistState) {
      saveState()
    }
  })

  // Return the composable API
  return {
    // State
    state: readonly(state),
    
    // Computed
    visibleColumns: visibleColumnsComputed,
    hasSelection,
    hasActions,
    hasBulkActions,
    hasFilters,
    selectedCount,
    isAllSelected,
    isIndeterminate,
    
    // Data operations
    refresh,
    fetchData,
    processData,
    
    // Pagination
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    changePageSize,
    
    // Sorting
    sortBy,
    clearSort,
    
    // Filtering
    setFilter,
    clearFilter,
    clearAllFilters,
    setGlobalSearch,
    
    // Selection
    toggleRowSelection,
    toggleAllSelection,
    clearSelection,
    
    // Column management
    toggleColumnVisibility,
    showColumn,
    hideColumn,
    resetColumnVisibility,
    
    // Export
    exportData,
    
    // Utilities
    getNestedValue,
    setNestedValue
  }
}

export type DataTableComposable<T extends DataTableItem = DataTableItem> = ReturnType<typeof useAdvancedDataTable<T>>
