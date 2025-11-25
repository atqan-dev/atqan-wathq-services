# Enhanced DataTable Components

This document describes the new reusable DataTable components and composables that provide advanced features like filtering, sorting, column visibility, pagination, and export functionality.

## Components

### 1. DataTable.vue
A generic, reusable data table component with advanced features.

### 2. EnhancedRequestLogsTable.vue
A specialized component for WATHQ request logs with predefined columns and actions.

## Composables

### 1. useDataTable.ts
Enhanced version of the base `useTable` composable with additional features:
- Column visibility management
- Advanced filtering
- Export functionality
- State persistence

### 2. useWathqDataTable.ts
Specialized composables for WATHQ data:
- `useWathqLiveRequestsTable()` - For live requests
- `useWathqRequestLogsTable()` - For request logs
- `useWathqOfflineRequestsTable()` - For offline data

## Features

### ✅ Implemented Features

1. **Filtering & Search**
   - Global search across all searchable columns
   - Column-specific filters (text, select, date, number, boolean)
   - Active filter indicators
   - Clear individual or all filters

2. **Sorting**
   - Click column headers to sort
   - Visual indicators for sort direction
   - Multi-column sorting support

3. **Column Management**
   - Show/hide columns
   - Column visibility dropdown
   - Persistent column preferences

4. **Pagination**
   - Configurable page sizes (10, 25, 50, 100)
   - Page navigation controls
   - Total count display

5. **Selection**
   - Row selection with checkboxes
   - Select all/none functionality
   - Bulk actions on selected rows

6. **Export**
   - Export to CSV
   - Export to JSON
   - Export filtered/sorted data

7. **State Persistence**
   - Save table state to localStorage
   - Restore filters, sorting, pagination on reload
   - Per-table state keys

8. **Responsive Design**
   - Mobile-friendly layout
   - Horizontal scroll for wide tables
   - Collapsible filter panel

## Usage Examples

### Basic DataTable Usage

```vue
<template>
  <DataTable
    :table="table"
    :selectable="true"
    :exportable="true"
    search-placeholder="Search requests..."
    empty-state-title="No requests found"
    empty-state-description="Try adjusting your filters"
  />
</template>

<script setup>
import { useDataTable } from '~/composables/useDataTable'
import DataTable from '~/components/ui/DataTable.vue'

// Define columns
const columns = [
  {
    key: 'name',
    label: 'Name',
    sortable: true,
    searchable: true,
    type: 'text'
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    type: 'badge',
    width: '100px'
  },
  {
    key: 'created_at',
    label: 'Created',
    sortable: true,
    type: 'date',
    format: (value) => new Date(value).toLocaleDateString()
  },
  {
    key: 'actions',
    label: 'Actions',
    type: 'actions',
    width: '120px',
    align: 'right'
  }
]

// Define filters
const filters = [
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Active', value: 'active' },
      { label: 'Inactive', value: 'inactive' }
    ]
  },
  {
    key: 'name',
    label: 'Name',
    type: 'text',
    placeholder: 'Search by name...'
  }
]

// Define actions
const actions = [
  {
    key: 'view',
    label: 'View',
    icon: 'i-heroicons-eye',
    color: 'gray',
    variant: 'ghost',
    size: 'xs',
    handler: (row) => console.log('View:', row)
  },
  {
    key: 'edit',
    label: 'Edit',
    icon: 'i-heroicons-pencil',
    color: 'blue',
    variant: 'ghost',
    size: 'xs',
    handler: (row) => console.log('Edit:', row)
  }
]

// Fetch function
const fetchData = async (params) => {
  const response = await $fetch('/api/data', { query: params })
  return {
    data: response.items,
    total: response.total
  }
}

// Initialize table
const table = useDataTable(fetchData, {
  columns,
  filters,
  actions,
  initialPageSize: 25,
  persistState: true,
  stateKey: 'my-table-state'
})
</script>
```

### WATHQ Request Logs Usage

```vue
<template>
  <EnhancedRequestLogsTable 
    type="logs" 
    service-type="commercial-registration" 
  />
</template>

<script setup>
import EnhancedRequestLogsTable from '~/components/wathq/EnhancedRequestLogsTable.vue'
</script>
```

### Custom WATHQ Table

```vue
<template>
  <DataTable :table="table" :selectable="true" :exportable="true" />
</template>

<script setup>
import { useWathqRequestLogsTable } from '~/composables/useWathqDataTable'
import DataTable from '~/components/ui/DataTable.vue'

const table = useWathqRequestLogsTable({
  serviceType: 'commercial-registration',
  persistState: true
})
</script>
```

## Column Configuration

### Column Types
- `text` - Plain text display
- `number` - Numeric values with formatting
- `date` - Date values with formatting
- `badge` - Status badges with colors
- `actions` - Action buttons
- `custom` - Custom component

### Column Properties
```typescript
interface DataTableColumn {
  key: string              // Data property key
  label: string            // Display label
  sortable?: boolean       // Enable sorting
  searchable?: boolean     // Include in global search
  visible?: boolean        // Initial visibility
  width?: string           // CSS width
  align?: 'left' | 'center' | 'right'
  type?: 'text' | 'number' | 'date' | 'badge' | 'actions' | 'custom'
  format?: (value: any, row: any) => string  // Custom formatter
  component?: string       // Custom component name
  props?: Record<string, any>  // Props for custom component
}
```

## Filter Configuration

### Filter Types
- `text` - Text input
- `select` - Dropdown selection
- `date` - Date picker
- `daterange` - Date range picker
- `number` - Number input
- `boolean` - Yes/No selection

### Filter Properties
```typescript
interface DataTableFilter {
  key: string              // Filter key
  label: string            // Display label
  type: 'text' | 'select' | 'date' | 'daterange' | 'number' | 'boolean'
  options?: { label: string; value: any }[]  // For select filters
  multiple?: boolean       // Multiple selection
  placeholder?: string     // Input placeholder
}
```

## Action Configuration

```typescript
interface DataTableAction {
  key: string              // Unique action key
  label: string            // Button label
  icon?: string            // Icon name
  color?: string           // Button color
  variant?: string         // Button variant
  size?: string            // Button size
  condition?: (row: any) => boolean  // Show condition
  handler: (row: any, rows?: any[]) => void | Promise<void>
}
```

## Best Practices

### 1. Performance
- Use pagination for large datasets
- Implement server-side filtering and sorting
- Limit the number of visible columns initially
- Use `format` functions for expensive computations

### 2. User Experience
- Provide meaningful empty states
- Use loading indicators
- Implement proper error handling
- Save user preferences with `persistState`

### 3. Accessibility
- Use semantic HTML
- Provide proper ARIA labels
- Ensure keyboard navigation works
- Use sufficient color contrast

### 4. Responsive Design
- Test on mobile devices
- Use appropriate column widths
- Consider hiding less important columns on small screens
- Implement horizontal scrolling for wide tables

## Migration Guide

### From RequestLogsTable to EnhancedRequestLogsTable

**Before:**
```vue
<RequestLogsTable :requests="requests" :is-loading="loading" />
```

**After:**
```vue
<EnhancedRequestLogsTable 
  type="logs" 
  service-type="commercial-registration" 
/>
```

### Benefits of Migration
1. **Advanced Filtering** - Multiple filter types and combinations
2. **Column Management** - Show/hide columns as needed
3. **Export Functionality** - Export data in multiple formats
4. **Better Performance** - Server-side pagination and filtering
5. **State Persistence** - Remember user preferences
6. **Responsive Design** - Better mobile experience
7. **Accessibility** - Improved screen reader support

## Troubleshooting

### Common Issues

1. **Data not loading**
   - Check fetch function implementation
   - Verify API endpoint returns correct format
   - Check network requests in browser dev tools

2. **Filters not working**
   - Ensure filter keys match data properties
   - Verify server-side filter implementation
   - Check filter value types

3. **Sorting not working**
   - Verify `sortable: true` on columns
   - Check server-side sorting implementation
   - Ensure sort parameters are passed correctly

4. **State not persisting**
   - Check `persistState: true` option
   - Verify unique `stateKey` for each table
   - Check localStorage permissions

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('datatable-debug', 'true')
```

This will log table operations to the browser console.
