/**
 * Comprehensive DataTable Types and Interfaces
 * Provides type safety for the reusable DataTable system
 */

// Base data item interface - extend this for your specific data types
export interface DataTableItem {
  id: string | number
  [key: string]: any
}

// Column definition interface
export interface DataTableColumn<T = any> {
  key: string
  label: string
  sortable?: boolean
  searchable?: boolean
  filterable?: boolean
  visible?: boolean
  width?: string
  minWidth?: string
  maxWidth?: string
  align?: 'left' | 'center' | 'right'
  type?: 'text' | 'number' | 'date' | 'boolean' | 'badge' | 'actions' | 'custom'
  format?: (value: any, row: T) => string | number
  render?: (value: any, row: T) => any
  headerClass?: string
  cellClass?: string | ((value: any, row: T) => string)
  sticky?: 'left' | 'right'
}

// Filter types
export type FilterType = 'text' | 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'numberrange' | 'boolean'

export interface FilterOption {
  label: string
  value: any
  disabled?: boolean
}

export interface DataTableFilter {
  key: string
  label: string
  type: FilterType
  placeholder?: string
  options?: FilterOption[]
  multiple?: boolean
  clearable?: boolean
  searchable?: boolean
  defaultValue?: any
  validation?: (value: any) => boolean | string
}

// Action interfaces
export interface DataTableAction<T = any> {
  key: string
  label: string
  icon?: string
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  variant?: 'solid' | 'outline' | 'ghost' | 'soft'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  disabled?: boolean | ((row: T) => boolean)
  visible?: boolean | ((row: T) => boolean)
  loading?: boolean | ((row: T) => boolean)
  handler: (row: T, index: number) => void | Promise<void>
  confirm?: {
    title: string
    message: string
    confirmText?: string
    cancelText?: string
  }
}

export interface DataTableBulkAction<T = any> {
  key: string
  label: string
  icon?: string
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  variant?: 'solid' | 'outline' | 'ghost' | 'soft'
  disabled?: boolean | ((selectedRows: T[]) => boolean)
  visible?: boolean | ((selectedRows: T[]) => boolean)
  loading?: boolean
  handler: (selectedRows: T[], selectedIds: (string | number)[]) => void | Promise<void>
  confirm?: {
    title: string
    message: string
    confirmText?: string
    cancelText?: string
  }
}

// Pagination interface
export interface DataTablePagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
  showSizeChanger?: boolean
  showQuickJumper?: boolean
  showTotal?: boolean
  pageSizeOptions?: number[]
}

// Sorting interface
export interface DataTableSort {
  column: string | null
  direction: 'asc' | 'desc' | null
}

// Selection interface
export interface DataTableSelection<T = any> {
  enabled: boolean
  multiple: boolean
  selectedRows: T[]
  selectedIds: (string | number)[]
  selectAll: boolean
  indeterminate: boolean
}

// Export interface
export interface DataTableExport {
  enabled: boolean
  formats: ('csv' | 'excel' | 'pdf' | 'json')[]
  filename?: string
  includeFilters?: boolean
  customData?: (data: any[]) => any[]
}

// Fetch function interface
export interface DataTableFetchParams {
  page: number
  pageSize: number
  search?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, any>
}

export interface DataTableFetchResult<T = any> {
  data: T[]
  total: number
  page?: number
  pageSize?: number
  totalPages?: number
}

export type DataTableFetchFunction<T = any> = (
  params: DataTableFetchParams
) => Promise<DataTableFetchResult<T>>

// Configuration interface
export interface DataTableConfig<T = any> {
  // Data fetching
  fetchFunction?: DataTableFetchFunction<T>
  data?: T[]
  
  // Columns and display
  columns: DataTableColumn<T>[]
  keyField?: string
  
  // Pagination
  pagination?: boolean
  initialPage?: number
  initialPageSize?: number
  pageSizeOptions?: number[]
  
  // Sorting
  sortable?: boolean
  initialSortColumn?: string
  initialSortDirection?: 'asc' | 'desc'
  multiSort?: boolean
  
  // Filtering
  filterable?: boolean
  filters?: DataTableFilter[]
  globalSearch?: boolean
  searchPlaceholder?: string
  searchDebounce?: number
  
  // Selection
  selectable?: boolean
  multiSelect?: boolean
  selectOnRowClick?: boolean
  
  // Actions
  actions?: DataTableAction<T>[]
  bulkActions?: DataTableBulkAction<T>[]
  
  // Export
  exportable?: boolean
  exportFormats?: ('csv' | 'excel' | 'pdf' | 'json')[]
  
  // UI customization
  loading?: boolean
  height?: string
  maxHeight?: string
  striped?: boolean
  bordered?: boolean
  hoverable?: boolean
  dense?: boolean
  
  // Empty state
  emptyStateTitle?: string
  emptyStateDescription?: string
  emptyStateIcon?: string
  
  // State persistence
  persistState?: boolean
  stateKey?: string
  
  // Responsive
  responsive?: boolean
  mobileBreakpoint?: number
  
  // Accessibility
  ariaLabel?: string
  ariaDescription?: string
}

// State interface for the composable
export interface DataTableState<T = any> {
  // Data
  data: T[]
  filteredData: T[]
  paginatedData: T[]
  
  // Loading states
  loading: boolean
  refreshing: boolean
  
  // Pagination
  pagination: DataTablePagination
  
  // Sorting
  sort: DataTableSort
  
  // Filtering
  filters: Record<string, any>
  globalSearch: string
  
  // Selection
  selection: DataTableSelection<T>
  
  // Column visibility
  visibleColumns: string[]
  columnOrder: string[]
  
  // UI state
  expandedRows: (string | number)[]
  
  // Error handling
  error: string | null
}

// Events interface
export interface DataTableEvents<T = any> {
  'row-click': (row: T, index: number, event: Event) => void
  'row-double-click': (row: T, index: number, event: Event) => void
  'cell-click': (value: any, row: T, column: DataTableColumn<T>, event: Event) => void
  'selection-change': (selectedRows: T[], selectedIds: (string | number)[]) => void
  'sort-change': (sort: DataTableSort) => void
  'filter-change': (filters: Record<string, any>) => void
  'page-change': (page: number) => void
  'page-size-change': (pageSize: number) => void
  'refresh': () => void
  'export': (format: string, data: T[]) => void
}

// Utility types
export type DataTableColumnKey<T> = keyof T | string
export type DataTableFilterValue = string | number | boolean | Date | null | undefined | any[]
export type DataTableSortDirection = 'asc' | 'desc' | null
