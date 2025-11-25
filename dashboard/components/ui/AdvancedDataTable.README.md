# Advanced DataTable Component

A comprehensive, reusable DataTable component system built with Vue 3, TypeScript, and best practices. This component provides enterprise-grade features including filtering, sorting, pagination, column management, bulk actions, and more.

## 🚀 Features

### Core Features
- ✅ **Pagination** - Client-side and server-side pagination
- ✅ **Sorting** - Multi-column sorting with custom sort functions
- ✅ **Filtering** - Global search and column-specific filters
- ✅ **Selection** - Single and multi-row selection with bulk actions
- ✅ **Column Management** - Show/hide columns, reorder, resize
- ✅ **Export** - CSV, JSON, Excel, PDF export capabilities
- ✅ **Responsive** - Mobile-friendly design
- ✅ **Accessibility** - ARIA labels and keyboard navigation
- ✅ **State Persistence** - Save table state to localStorage

### Advanced Features
- ✅ **Custom Cell Rendering** - Custom components and formatters
- ✅ **Row Actions** - Context-specific actions per row
- ✅ **Bulk Actions** - Operations on multiple selected rows
- ✅ **Loading States** - Loading indicators and skeleton screens
- ✅ **Error Handling** - Graceful error states and retry mechanisms
- ✅ **Empty States** - Customizable empty state messages
- ✅ **Sticky Columns** - Pin columns to left or right
- ✅ **Virtual Scrolling** - Handle large datasets efficiently

## 📦 Installation

The component is already included in your project. Import it like this:

```vue
<script setup>
import AdvancedDataTable from '~/components/ui/AdvancedDataTable.vue'
import { useAdvancedDataTable } from '~/composables/useAdvancedDataTable'
</script>
```

## 🎯 Basic Usage

### Simple Static Data Table

```vue
<template>
  <AdvancedDataTable
    :config="tableConfig"
    title="Users"
    description="Manage your application users"
  />
</template>

<script setup lang="ts">
import type { DataTableConfig } from '~/types/datatable'

interface User {
  id: number
  name: string
  email: string
  role: string
  status: 'active' | 'inactive'
  createdAt: string
}

const users: User[] = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    status: 'active',
    createdAt: '2024-01-15'
  },
  // ... more users
]

const tableConfig: DataTableConfig<User> = {
  data: users,
  columns: [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      searchable: true
    },
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      searchable: true
    },
    {
      key: 'role',
      label: 'Role',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: 'Status',
      type: 'badge',
      sortable: true,
      filterable: true
    },
    {
      key: 'createdAt',
      label: 'Created',
      type: 'date',
      sortable: true,
      format: (value) => new Date(value).toLocaleDateString()
    }
  ],
  pagination: true,
  selectable: true,
  exportable: true
}
</script>
```

### Server-Side Data Table

```vue
<template>
  <AdvancedDataTable
    :config="tableConfig"
    title="Products"
    @row-click="handleRowClick"
    @action-click="handleAction"
  />
</template>

<script setup lang="ts">
import type { DataTableConfig, DataTableFetchParams } from '~/types/datatable'

interface Product {
  id: number
  name: string
  price: number
  category: string
  stock: number
  status: string
}

// Server-side fetch function
const fetchProducts = async (params: DataTableFetchParams) => {
  const { data } = await $fetch('/api/products', {
    query: {
      page: params.page,
      limit: params.pageSize,
      search: params.search,
      sortBy: params.sortBy,
      sortOrder: params.sortOrder,
      ...params.filters
    }
  })
  
  return {
    data: data.items,
    total: data.total,
    page: data.page,
    pageSize: data.pageSize
  }
}

const tableConfig: DataTableConfig<Product> = {
  fetchFunction: fetchProducts,
  columns: [
    {
      key: 'name',
      label: 'Product Name',
      sortable: true,
      searchable: true,
      width: '200px'
    },
    {
      key: 'price',
      label: 'Price',
      type: 'number',
      sortable: true,
      align: 'right',
      format: (value) => `$${value.toFixed(2)}`
    },
    {
      key: 'category',
      label: 'Category',
      sortable: true,
      filterable: true
    },
    {
      key: 'stock',
      label: 'Stock',
      type: 'number',
      sortable: true,
      align: 'right',
      cellClass: (value) => value < 10 ? 'text-red-600' : 'text-green-600'
    },
    {
      key: 'status',
      label: 'Status',
      type: 'badge',
      sortable: true
    }
  ],
  filters: [
    {
      key: 'category',
      label: 'Category',
      type: 'select',
      options: [
        { label: 'Electronics', value: 'electronics' },
        { label: 'Clothing', value: 'clothing' },
        { label: 'Books', value: 'books' }
      ]
    },
    {
      key: 'price_range',
      label: 'Price Range',
      type: 'numberrange',
      placeholder: 'Min - Max'
    },
    {
      key: 'in_stock',
      label: 'In Stock',
      type: 'boolean'
    }
  ],
  actions: [
    {
      key: 'edit',
      label: 'Edit',
      icon: 'i-heroicons-pencil',
      color: 'primary',
      handler: (row) => navigateTo(`/products/${row.id}/edit`)
    },
    {
      key: 'delete',
      label: 'Delete',
      icon: 'i-heroicons-trash',
      color: 'red',
      confirm: {
        title: 'Delete Product',
        message: 'Are you sure you want to delete this product?'
      },
      handler: async (row) => {
        await $fetch(`/api/products/${row.id}`, { method: 'DELETE' })
        // Refresh table
      }
    }
  ],
  bulkActions: [
    {
      key: 'delete_selected',
      label: 'Delete Selected',
      icon: 'i-heroicons-trash',
      color: 'red',
      confirm: {
        title: 'Delete Products',
        message: 'Are you sure you want to delete the selected products?'
      },
      handler: async (selectedRows) => {
        const ids = selectedRows.map(row => row.id)
        await $fetch('/api/products/bulk-delete', {
          method: 'POST',
          body: { ids }
        })
      }
    }
  ],
  initialPageSize: 25,
  persistState: true,
  stateKey: 'products-table'
}

// Event handlers
const handleRowClick = (row: Product) => {
  navigateTo(`/products/${row.id}`)
}

const handleAction = (action: string, row: Product) => {
  console.log(`Action ${action} clicked for product:`, row)
}
</script>
```

## 🔧 Configuration Options

### DataTableConfig Interface

```typescript
interface DataTableConfig<T = any> {
  // Data source
  fetchFunction?: DataTableFetchFunction<T>  // Server-side data fetching
  data?: T[]                                 // Static data

  // Display
  columns: DataTableColumn<T>[]              // Column definitions
  keyField?: string                          // Unique identifier field (default: 'id')

  // Pagination
  pagination?: boolean                       // Enable pagination (default: true)
  initialPage?: number                       // Starting page (default: 1)
  initialPageSize?: number                   // Items per page (default: 10)
  pageSizeOptions?: number[]                 // Page size options

  // Sorting
  sortable?: boolean                         // Enable sorting (default: true)
  initialSortColumn?: string                 // Default sort column
  initialSortDirection?: 'asc' | 'desc'      // Default sort direction
  multiSort?: boolean                        // Multiple column sorting

  // Filtering
  filterable?: boolean                       // Enable filtering (default: true)
  filters?: DataTableFilter[]                // Column filters
  globalSearch?: boolean                     // Global search (default: true)
  searchPlaceholder?: string                 // Search input placeholder
  searchDebounce?: number                    // Search debounce delay (default: 300ms)

  // Selection
  selectable?: boolean                       // Enable row selection
  multiSelect?: boolean                      // Multiple selection (default: true)
  selectOnRowClick?: boolean                 // Select on row click

  // Actions
  actions?: DataTableAction<T>[]             // Row actions
  bulkActions?: DataTableBulkAction<T>[]     // Bulk actions

  // Export
  exportable?: boolean                       // Enable export
  exportFormats?: ('csv' | 'excel' | 'pdf' | 'json')[]

  // UI
  loading?: boolean                          // Loading state
  height?: string                            // Table height
  maxHeight?: string                         // Max table height
  striped?: boolean                          // Striped rows
  bordered?: boolean                         // Table borders
  hoverable?: boolean                        // Row hover effects (default: true)
  dense?: boolean                            // Compact layout

  // Empty state
  emptyStateTitle?: string                   // Empty state title
  emptyStateDescription?: string             // Empty state description
  emptyStateIcon?: string                    // Empty state icon

  // State persistence
  persistState?: boolean                     // Save state to localStorage
  stateKey?: string                          // localStorage key

  // Responsive
  responsive?: boolean                       // Responsive design (default: true)
  mobileBreakpoint?: number                  // Mobile breakpoint (default: 768px)
}
```

### Column Configuration

```typescript
interface DataTableColumn<T = any> {
  key: string                                // Data property key
  label: string                              // Column header text
  
  // Behavior
  sortable?: boolean                         // Enable sorting (default: true)
  searchable?: boolean                       // Include in global search
  filterable?: boolean                       // Enable column filter
  visible?: boolean                          // Column visibility (default: true)
  
  // Styling
  width?: string                             // Column width
  minWidth?: string                          // Minimum width
  maxWidth?: string                          // Maximum width
  align?: 'left' | 'center' | 'right'       // Text alignment
  headerClass?: string                       // Header CSS classes
  cellClass?: string | ((value: any, row: T) => string)  // Cell CSS classes
  sticky?: 'left' | 'right'                 // Sticky positioning
  
  // Data handling
  type?: 'text' | 'number' | 'date' | 'boolean' | 'badge' | 'actions' | 'custom'
  format?: (value: any, row: T) => string | number  // Value formatter
  render?: (value: any, row: T) => any       // Custom renderer (HTML)
}
```

### Filter Configuration

```typescript
interface DataTableFilter {
  key: string                                // Filter property key
  label: string                              // Filter label
  type: FilterType                           // Filter type
  placeholder?: string                       // Input placeholder
  options?: FilterOption[]                   // Select options
  multiple?: boolean                         // Multiple selection
  clearable?: boolean                        // Show clear button (default: true)
  searchable?: boolean                       // Searchable select
  defaultValue?: any                         // Default filter value
  validation?: (value: any) => boolean | string  // Value validation
}

type FilterType = 'text' | 'select' | 'multiselect' | 'date' | 'daterange' | 'number' | 'numberrange' | 'boolean'
```

### Action Configuration

```typescript
interface DataTableAction<T = any> {
  key: string                                // Unique action key
  label: string                              // Action label
  icon?: string                              // Action icon
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  variant?: 'solid' | 'outline' | 'ghost' | 'soft'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  disabled?: boolean | ((row: T) => boolean) // Disable condition
  visible?: boolean | ((row: T) => boolean)  // Visibility condition
  loading?: boolean | ((row: T) => boolean)  // Loading state
  handler: (row: T, index: number) => void | Promise<void>  // Click handler
  confirm?: {                                // Confirmation dialog
    title: string
    message: string
    confirmText?: string
    cancelText?: string
  }
}
```

## 🎨 Styling and Theming

The component uses Tailwind CSS classes and can be customized through:

### CSS Classes

```css
/* Custom table styles */
.datatable-header-cell {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider;
}

.datatable-cell {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white;
}

/* Responsive styles */
@media (max-width: 768px) {
  .datatable-container {
    @apply overflow-x-auto;
  }
}
```

### Theme Customization

```vue
<template>
  <AdvancedDataTable
    :config="config"
    class="custom-datatable"
  />
</template>

<style scoped>
.custom-datatable {
  --datatable-header-bg: theme('colors.blue.50');
  --datatable-border-color: theme('colors.blue.200');
  --datatable-hover-bg: theme('colors.blue.25');
}

.custom-datatable :deep(.datatable-header-cell) {
  background-color: var(--datatable-header-bg);
  border-color: var(--datatable-border-color);
}

.custom-datatable :deep(.datatable-row:hover) {
  background-color: var(--datatable-hover-bg);
}
</style>
```

## 🔌 Events

The component emits several events for interaction:

```vue
<template>
  <AdvancedDataTable
    :config="config"
    @row-click="onRowClick"
    @row-double-click="onRowDoubleClick"
    @cell-click="onCellClick"
    @action-click="onActionClick"
    @bulk-action-click="onBulkActionClick"
  />
</template>

<script setup>
const onRowClick = (row, index, event) => {
  console.log('Row clicked:', row)
}

const onRowDoubleClick = (row, index, event) => {
  console.log('Row double-clicked:', row)
}

const onCellClick = (value, row, column, event) => {
  console.log('Cell clicked:', { value, row, column })
}

const onActionClick = (action, row, index) => {
  console.log('Action clicked:', action.key, row)
}

const onBulkActionClick = (action, selectedRows) => {
  console.log('Bulk action clicked:', action.key, selectedRows)
}
</script>
```

## 🚀 Advanced Examples

### Custom Cell Rendering

```typescript
const columns: DataTableColumn[] = [
  {
    key: 'avatar',
    label: 'Avatar',
    render: (value, row) => `
      <div class="flex items-center">
        <img src="${row.avatar}" alt="${row.name}" class="w-8 h-8 rounded-full mr-2">
        <span>${row.name}</span>
      </div>
    `
  },
  {
    key: 'progress',
    label: 'Progress',
    render: (value) => `
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-blue-600 h-2 rounded-full" style="width: ${value}%"></div>
      </div>
      <span class="text-xs text-gray-500">${value}%</span>
    `
  }
]
```

### Complex Filtering

```typescript
const filters: DataTableFilter[] = [
  {
    key: 'name',
    label: 'Name',
    type: 'text',
    placeholder: 'Search by name...'
  },
  {
    key: 'department',
    label: 'Department',
    type: 'multiselect',
    options: [
      { label: 'Engineering', value: 'engineering' },
      { label: 'Marketing', value: 'marketing' },
      { label: 'Sales', value: 'sales' }
    ],
    multiple: true,
    searchable: true
  },
  {
    key: 'salary_range',
    label: 'Salary Range',
    type: 'numberrange',
    validation: (value) => {
      if (Array.isArray(value) && value[0] > value[1]) {
        return 'Min value cannot be greater than max value'
      }
      return true
    }
  },
  {
    key: 'hire_date',
    label: 'Hire Date',
    type: 'daterange'
  }
]
```

### State Persistence

```typescript
const config: DataTableConfig = {
  // ... other config
  persistState: true,
  stateKey: 'my-unique-table',
  
  // The following will be automatically saved/restored:
  // - Current page and page size
  // - Sort column and direction
  // - Filter values
  // - Column visibility and order
}
```

## 🧪 Testing

### Unit Testing Example

```typescript
import { mount } from '@vue/test-utils'
import AdvancedDataTable from '~/components/ui/AdvancedDataTable.vue'

describe('AdvancedDataTable', () => {
  const mockData = [
    { id: 1, name: 'John', email: 'john@example.com' },
    { id: 2, name: 'Jane', email: 'jane@example.com' }
  ]

  const mockConfig = {
    data: mockData,
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'email', label: 'Email' }
    ]
  }

  it('renders table with data', () => {
    const wrapper = mount(AdvancedDataTable, {
      props: { config: mockConfig }
    })

    expect(wrapper.find('table').exists()).toBe(true)
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
  })

  it('handles row selection', async () => {
    const wrapper = mount(AdvancedDataTable, {
      props: {
        config: { ...mockConfig, selectable: true }
      }
    })

    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setChecked(true)

    expect(wrapper.emitted('selection-change')).toBeTruthy()
  })
})
```

## 🔧 Troubleshooting

### Common Issues

1. **TypeScript Errors**: Ensure your data interface extends `DataTableItem`
2. **Performance Issues**: Use server-side pagination for large datasets
3. **Styling Issues**: Check Tailwind CSS classes and dark mode support
4. **State Persistence**: Ensure `stateKey` is unique across different tables

### Performance Tips

- Use `fetchFunction` for server-side operations with large datasets
- Implement virtual scrolling for very large client-side datasets
- Debounce search and filter operations
- Use `v-memo` for complex cell renderers

## 📚 API Reference

### Composable Methods

```typescript
const dataTable = useAdvancedDataTable(config)

// Data operations
dataTable.refresh()                        // Refresh data
dataTable.fetchData(params)                // Fetch with custom params

// Pagination
dataTable.goToPage(page)                   // Go to specific page
dataTable.nextPage()                       // Next page
dataTable.prevPage()                       // Previous page
dataTable.changePageSize(size)             // Change page size

// Sorting
dataTable.sortBy(column, direction)        // Sort by column
dataTable.clearSort()                      // Clear sorting

// Filtering
dataTable.setFilter(key, value)            // Set filter value
dataTable.clearFilter(key)                 // Clear specific filter
dataTable.clearAllFilters()                // Clear all filters
dataTable.setGlobalSearch(search)          // Set global search

// Selection
dataTable.toggleRowSelection(row, selected) // Toggle row selection
dataTable.toggleAllSelection(selected)     // Toggle all selection
dataTable.clearSelection()                 // Clear selection

// Column management
dataTable.toggleColumnVisibility(key)      // Toggle column visibility
dataTable.showColumn(key)                  // Show column
dataTable.hideColumn(key)                  // Hide column
dataTable.resetColumnVisibility()          // Reset to defaults

// Export
dataTable.exportData(format, filename)     // Export data
```

This comprehensive DataTable system provides everything you need for building professional data tables in your Vue 3 application! 🚀
