import { ref, computed, watch, type Ref } from 'vue'

export interface TablePagination {
  currentPage: number
  pageSize: number
  total: number
  totalPages: number
  from: number
  to: number
  hasPrevious: boolean
  hasNext: boolean
}

export interface TableSort {
  column: string
  direction: 'asc' | 'desc'
}

export interface UseTableOptions {
  initialPageSize?: number
  initialSortColumn?: string
  initialSortDirection?: 'asc' | 'desc'
  searchDebounceMs?: number
}

export interface UseTableReturn<T = any> {
  // Data
  data: Ref<T[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  
  // Search
  searchQuery: Ref<string>
  debouncedSearchQuery: Ref<string>
  
  // Pagination
  currentPage: Ref<number>
  pageSize: Ref<number>
  totalItems: Ref<number>
  pagination: Ref<TablePagination>
  
  // Sorting
  sortColumn: Ref<string>
  sortDirection: Ref<'asc' | 'desc'>
  sort: Ref<TableSort>
  
  // Selection
  selectedItems: Ref<(string | number)[]>
  isAllSelected: Ref<boolean>
  isPartiallySelected: Ref<boolean>
  
  // Methods
  setData: (newData: T[]) => void
  setLoading: (isLoading: boolean) => void
  setError: (errorMessage: string | null) => void
  setTotal: (total: number) => void
  
  // Pagination methods
  goToPage: (page: number) => void
  nextPage: () => void
  previousPage: () => void
  setPageSize: (size: number) => void
  
  // Sorting methods
  setSorting: (column: string, direction?: 'asc' | 'desc') => void
  toggleSort: (column: string) => void
  
  // Selection methods
  selectItem: (id: string | number) => void
  unselectItem: (id: string | number) => void
  toggleSelectItem: (id: string | number) => void
  selectAll: () => void
  unselectAll: () => void
  toggleSelectAll: () => void
  getSelectedItems: () => T[]
  clearSelection: () => void
  
  // Search methods
  setSearchQuery: (query: string) => void
  clearSearch: () => void
  
  // Utility methods
  refresh: () => void
  reset: () => void
}

export function useTable<T = any>(
  fetchFunction: (params: {
    page: number
    pageSize: number
    search?: string
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
  }) => Promise<{ data: T[], total: number }>,
  options: UseTableOptions = {}
): UseTableReturn<T> {
  
  const {
    initialPageSize = 10,
    initialSortColumn = '',
    initialSortDirection = 'asc',
    searchDebounceMs = 300
  } = options

  // Data state
  const data = ref<T[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalItems = ref(0)

  // Search state
  const searchQuery = ref('')
  const debouncedSearchQuery = ref('')
  let searchTimeout: NodeJS.Timeout | null = null

  // Pagination state
  const currentPage = ref(1)
  const pageSize = ref(initialPageSize)

  // Sorting state
  const sortColumn = ref(initialSortColumn)
  const sortDirection = ref<'asc' | 'desc'>(initialSortDirection)

  // Selection state
  const selectedItems = ref<(string | number)[]>([])

  // Computed properties
  const pagination = computed<TablePagination>(() => ({
    currentPage: currentPage.value,
    pageSize: pageSize.value,
    total: totalItems.value,
    totalPages: Math.ceil(totalItems.value / pageSize.value),
    from: Math.min((currentPage.value - 1) * pageSize.value + 1, totalItems.value),
    to: Math.min(currentPage.value * pageSize.value, totalItems.value),
    hasPrevious: currentPage.value > 1,
    hasNext: currentPage.value * pageSize.value < totalItems.value
  }))

  const sort = computed<TableSort>(() => ({
    column: sortColumn.value,
    direction: sortDirection.value
  }))

  const isAllSelected = computed(() => {
    return data.value.length > 0 && selectedItems.value.length === data.value.length
  })

  const isPartiallySelected = computed(() => {
    return selectedItems.value.length > 0 && selectedItems.value.length < data.value.length
  })

  // Watch for search changes with debounce
  watch(searchQuery, (newQuery) => {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    
    searchTimeout = setTimeout(() => {
      debouncedSearchQuery.value = newQuery
      currentPage.value = 1 // Reset to first page on search
      fetchData()
    }, searchDebounceMs)
  })

  // Watch for pagination and sorting changes
  watch([currentPage, pageSize, sortColumn, sortDirection], () => {
    fetchData()
  })

  // Watch for debounced search changes
  watch(debouncedSearchQuery, () => {
    fetchData()
  })

  // Methods
  const fetchData = async () => {
    loading.value = true
    error.value = null

    try {
      const params = {
        page: currentPage.value,
        pageSize: pageSize.value,
        search: debouncedSearchQuery.value || undefined,
        sortBy: sortColumn.value || undefined,
        sortOrder: sortDirection.value
      }

      const result = await fetchFunction(params)
      data.value = result.data
      totalItems.value = result.total
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch data'
      console.error('Table fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  const setData = (newData: T[]) => {
    data.value = newData
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setTotal = (total: number) => {
    totalItems.value = total
  }

  // Pagination methods
  const goToPage = (page: number) => {
    if (page >= 1 && page <= pagination.value.totalPages) {
      currentPage.value = page
    }
  }

  const nextPage = () => {
    if (pagination.value.hasNext) {
      currentPage.value++
    }
  }

  const previousPage = () => {
    if (pagination.value.hasPrevious) {
      currentPage.value--
    }
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1 // Reset to first page when changing page size
  }

  // Sorting methods
  const setSorting = (column: string, direction: 'asc' | 'desc' = 'asc') => {
    sortColumn.value = column
    sortDirection.value = direction
  }

  const toggleSort = (column: string) => {
    if (sortColumn.value === column) {
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortColumn.value = column
      sortDirection.value = 'asc'
    }
  }

  // Selection methods
  const selectItem = (id: string | number) => {
    if (!selectedItems.value.includes(id)) {
      selectedItems.value.push(id)
    }
  }

  const unselectItem = (id: string | number) => {
    const index = selectedItems.value.indexOf(id)
    if (index > -1) {
      selectedItems.value.splice(index, 1)
    }
  }

  const toggleSelectItem = (id: string | number) => {
    if (selectedItems.value.includes(id)) {
      unselectItem(id)
    } else {
      selectItem(id)
    }
  }

  const selectAll = () => {
    selectedItems.value = data.value.map((item: any) => item.id)
  }

  const unselectAll = () => {
    selectedItems.value = []
  }

  const toggleSelectAll = () => {
    if (isAllSelected.value) {
      unselectAll()
    } else {
      selectAll()
    }
  }

  const getSelectedItems = (): T[] => {
    return data.value.filter((item: any) => selectedItems.value.includes(item.id)) as T[]
  }

  const clearSelection = () => {
    selectedItems.value = []
  }

  // Search methods
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const clearSearch = () => {
    searchQuery.value = ''
    debouncedSearchQuery.value = ''
  }

  // Utility methods
  const refresh = () => {
    fetchData()
  }

  const reset = () => {
    currentPage.value = 1
    pageSize.value = initialPageSize
    sortColumn.value = initialSortColumn
    sortDirection.value = initialSortDirection
    searchQuery.value = ''
    debouncedSearchQuery.value = ''
    selectedItems.value = []
    error.value = null
    fetchData()
  }

  return {
    // Data
    data: data as Ref<T[]>,
    loading,
    error,
    
    // Search
    searchQuery,
    debouncedSearchQuery,
    
    // Pagination
    currentPage,
    pageSize,
    totalItems,
    pagination,
    
    // Sorting
    sortColumn,
    sortDirection,
    sort,
    
    // Selection
    selectedItems,
    isAllSelected,
    isPartiallySelected,
    
    // Methods
    setData,
    setLoading,
    setError,
    setTotal,
    
    // Pagination methods
    goToPage,
    nextPage,
    previousPage,
    setPageSize,
    
    // Sorting methods
    setSorting,
    toggleSort,
    
    // Selection methods
    selectItem,
    unselectItem,
    toggleSelectItem,
    selectAll,
    unselectAll,
    toggleSelectAll,
    getSelectedItems,
    clearSelection,
    
    // Search methods
    setSearchQuery,
    clearSearch,
    
    // Utility methods
    refresh,
    reset
  }
}
