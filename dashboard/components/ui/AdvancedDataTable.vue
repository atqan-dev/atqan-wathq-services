<template>
  <div class="advanced-datatable" :class="tableClasses">
    <!-- Header Section -->
    <div v-if="showHeader" class="datatable-header">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
        <!-- Left side: Title and bulk actions -->
        <div class="flex items-center gap-4">
          <div v-if="title" class="datatable-title">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ title }}
            </h3>
            <p v-if="description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ description }}
            </p>
          </div>
          
          <!-- Bulk Actions -->
          <div v-if="hasBulkActions && selectedCount > 0" class="flex items-center gap-2">
            <span class="text-sm text-gray-600 dark:text-gray-400">
              {{ selectedCount }} selected
            </span>
            <UButton
              v-for="action in config.bulkActions"
              :key="action.key"
              :color="action.color || 'primary'"
              :variant="action.variant || 'outline'"
              :size="action.size || 'sm'"
              :loading="action.loading"
              :disabled="typeof action.disabled === 'function' ? action.disabled(dataTable.state.selection.selectedRows) : action.disabled"
              @click="handleBulkAction(action)"
            >
              <UIcon v-if="action.icon" :name="action.icon" class="w-4 h-4" />
              {{ action.label }}
            </UButton>
          </div>
        </div>

        <!-- Right side: Search, filters, and actions -->
        <div class="flex items-center gap-3">
          <!-- Global Search -->
          <div v-if="config.globalSearch !== false" class="datatable-search">
            <UInput
              :model-value="dataTable.state.globalSearch"
              :placeholder="config.searchPlaceholder || 'Search...'"
              icon="i-heroicons-magnifying-glass"
              :loading="dataTable.state.loading"
              clearable
              @update:model-value="dataTable.setGlobalSearch"
            />
          </div>

          <!-- Column Visibility Toggle -->
          <UDropdown v-if="showColumnToggle" :items="columnToggleItems">
            <UButton
              color="gray"
              variant="outline"
              icon="i-heroicons-view-columns"
              size="sm"
            >
              Columns
            </UButton>
          </UDropdown>

          <!-- Export Button -->
          <UDropdown v-if="config.exportable" :items="exportItems">
            <UButton
              color="gray"
              variant="outline"
              icon="i-heroicons-arrow-down-tray"
              size="sm"
            >
              Export
            </UButton>
          </UDropdown>

          <!-- Refresh Button -->
          <UButton
            color="gray"
            variant="outline"
            icon="i-heroicons-arrow-path"
            size="sm"
            :loading="dataTable.state.refreshing"
            @click="dataTable.refresh"
          >
            Refresh
          </UButton>
        </div>
      </div>

      <!-- Filters Row -->
      <div v-if="hasFilters && showFilters" class="datatable-filters mb-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="filter in config.filters"
            :key="filter.key"
            class="datatable-filter"
          >
            <!-- Text Filter -->
            <UInput
              v-if="filter.type === 'text'"
              :model-value="dataTable.state.filters[filter.key] || ''"
              :label="filter.label"
              :placeholder="filter.placeholder"
              clearable
              @update:model-value="(value) => dataTable.setFilter(filter.key, value)"
            />

            <!-- Select Filter -->
            <USelect
              v-else-if="filter.type === 'select'"
              :model-value="dataTable.state.filters[filter.key]"
              :options="filter.options || []"
              :label="filter.label"
              :placeholder="filter.placeholder"
              :multiple="filter.multiple"
              :searchable="filter.searchable"
              :clearable="filter.clearable !== false"
              @update:model-value="(value) => dataTable.setFilter(filter.key, value)"
            />

            <!-- Boolean Filter -->
            <USelectMenu
              v-else-if="filter.type === 'boolean'"
              :model-value="dataTable.state.filters[filter.key]"
              :options="[
                { label: 'All', value: null },
                { label: 'Yes', value: true },
                { label: 'No', value: false }
              ]"
              :label="filter.label"
              @update:model-value="(value) => dataTable.setFilter(filter.key, value)"
            />

            <!-- Date Filter -->
            <UInput
              v-else-if="filter.type === 'date'"
              :model-value="dataTable.state.filters[filter.key] || ''"
              :label="filter.label"
              type="date"
              @update:model-value="(value) => dataTable.setFilter(filter.key, value)"
            />

            <!-- Number Filter -->
            <UInput
              v-else-if="filter.type === 'number'"
              :model-value="dataTable.state.filters[filter.key] || ''"
              :label="filter.label"
              :placeholder="filter.placeholder"
              type="number"
              @update:model-value="(value) => dataTable.setFilter(filter.key, value)"
            />
          </div>
        </div>

        <!-- Clear Filters -->
        <div v-if="hasActiveFilters" class="mt-4">
          <UButton
            color="gray"
            variant="ghost"
            size="sm"
            icon="i-heroicons-x-mark"
            @click="dataTable.clearAllFilters"
          >
            Clear All Filters
          </UButton>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="dataTable.state.loading && !dataTable.state.refreshing" class="datatable-loading">
      <div class="flex items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary-500" />
        <span class="ml-3 text-gray-600 dark:text-gray-400">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="dataTable.state.error" class="datatable-error">
      <div class="text-center py-12">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Error Loading Data
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ dataTable.state.error }}
        </p>
        <UButton
          color="primary"
          variant="outline"
          @click="dataTable.refresh"
        >
          Try Again
        </UButton>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="dataTable.state.paginatedData.length === 0" class="datatable-empty">
      <div class="text-center py-12">
        <UIcon 
          :name="config.emptyStateIcon || 'i-heroicons-document-text'" 
          class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" 
        />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          {{ config.emptyStateTitle || 'No data found' }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ config.emptyStateDescription || 'There are no items to display.' }}
        </p>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="datatable-container" :style="containerStyle">
      <div class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <!-- Table Header -->
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <!-- Selection Column -->
              <th v-if="hasSelection" class="datatable-header-cell selection-cell">
                <UCheckbox
                  :model-value="dataTable.isAllSelected.value"
                  :indeterminate="dataTable.isIndeterminate.value"
                  @update:model-value="dataTable.toggleAllSelection"
                />
              </th>

              <!-- Data Columns -->
              <th
                v-for="column in dataTable.visibleColumns.value"
                :key="column.key"
                class="datatable-header-cell"
                :class="[
                  column.headerClass,
                  {
                    'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700': column.sortable !== false,
                    'text-left': column.align === 'left' || !column.align,
                    'text-center': column.align === 'center',
                    'text-right': column.align === 'right'
                  }
                ]"
                :style="getColumnStyle(column)"
                @click="column.sortable !== false && dataTable.sortBy(column.key)"
              >
                <div class="flex items-center gap-2">
                  <span>{{ column.label }}</span>
                  <div v-if="column.sortable !== false" class="flex flex-col">
                    <UIcon
                      name="i-heroicons-chevron-up"
                      class="w-3 h-3"
                      :class="{
                        'text-primary-500': dataTable.state.sort.column === column.key && dataTable.state.sort.direction === 'asc',
                        'text-gray-400': dataTable.state.sort.column !== column.key || dataTable.state.sort.direction !== 'asc'
                      }"
                    />
                    <UIcon
                      name="i-heroicons-chevron-down"
                      class="w-3 h-3 -mt-1"
                      :class="{
                        'text-primary-500': dataTable.state.sort.column === column.key && dataTable.state.sort.direction === 'desc',
                        'text-gray-400': dataTable.state.sort.column !== column.key || dataTable.state.sort.direction !== 'desc'
                      }"
                    />
                  </div>
                </div>
              </th>

              <!-- Actions Column -->
              <th v-if="hasActions" class="datatable-header-cell actions-cell">
                Actions
              </th>
            </tr>
          </thead>

          <!-- Table Body -->
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="(row, index) in dataTable.state.paginatedData"
              :key="getRowKey(row)"
              class="datatable-row"
              :class="{
                'hover:bg-gray-50 dark:hover:bg-gray-800': config.hoverable !== false,
                'bg-gray-50 dark:bg-gray-800': config.striped && index % 2 === 1,
                'cursor-pointer': config.selectOnRowClick
              }"
              @click="handleRowClick(row, index, $event)"
              @dblclick="handleRowDoubleClick(row, index, $event)"
            >
              <!-- Selection Cell -->
              <td v-if="hasSelection" class="datatable-cell selection-cell">
                <UCheckbox
                  :model-value="isRowSelected(row)"
                  @update:model-value="(selected) => dataTable.toggleRowSelection(row, selected)"
                  @click.stop
                />
              </td>

              <!-- Data Cells -->
              <td
                v-for="column in dataTable.visibleColumns.value"
                :key="column.key"
                class="datatable-cell"
                :class="[
                  typeof column.cellClass === 'function' 
                    ? column.cellClass(getCellValue(row, column), row)
                    : column.cellClass,
                  {
                    'text-left': column.align === 'left' || !column.align,
                    'text-center': column.align === 'center',
                    'text-right': column.align === 'right'
                  }
                ]"
                :style="getColumnStyle(column)"
                @click="handleCellClick(getCellValue(row, column), row, column, $event)"
              >
                <!-- Custom Render -->
                <div v-if="column.render" v-html="column.render(getCellValue(row, column), row)"></div>
                
                <!-- Badge Type -->
                <UBadge
                  v-else-if="column.type === 'badge'"
                  :color="getBadgeColor(getCellValue(row, column), row)"
                  variant="subtle"
                >
                  {{ formatCellValue(getCellValue(row, column), column, row) }}
                </UBadge>

                <!-- Boolean Type -->
                <UIcon
                  v-else-if="column.type === 'boolean'"
                  :name="getCellValue(row, column) ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                  :class="getCellValue(row, column) ? 'text-green-500' : 'text-red-500'"
                  class="w-5 h-5"
                />

                <!-- Default Text -->
                <span v-else>
                  {{ formatCellValue(getCellValue(row, column), column, row) }}
                </span>
              </td>

              <!-- Actions Cell -->
              <td v-if="hasActions" class="datatable-cell actions-cell">
                <div class="flex items-center gap-2">
                  <UButton
                    v-for="action in getRowActions(row)"
                    :key="action.key"
                    :color="action.color || 'gray'"
                    :variant="action.variant || 'ghost'"
                    :size="action.size || 'sm'"
                    :loading="typeof action.loading === 'function' ? action.loading(row) : action.loading"
                    :disabled="typeof action.disabled === 'function' ? action.disabled(row) : action.disabled"
                    @click.stop="handleRowAction(action, row, index)"
                  >
                    <UIcon v-if="action.icon" :name="action.icon" class="w-4 h-4" />
                    <span v-if="action.label">{{ action.label }}</span>
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="config.pagination !== false && dataTable.state.pagination.totalPages > 1" class="datatable-pagination">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
        <!-- Page Size Selector -->
        <div v-if="dataTable.state.pagination.showSizeChanger" class="flex items-center gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">Show</span>
          <USelect
            :model-value="dataTable.state.pagination.pageSize"
            :options="pageSizeOptions"
            size="sm"
            @update:model-value="dataTable.changePageSize"
          />
          <span class="text-sm text-gray-600 dark:text-gray-400">per page</span>
        </div>

        <!-- Pagination Info -->
        <div v-if="dataTable.state.pagination.showTotal" class="text-sm text-gray-600 dark:text-gray-400">
          Showing {{ paginationStart }} to {{ paginationEnd }} of {{ dataTable.state.pagination.total }} results
        </div>

        <!-- Pagination Controls -->
        <UPagination
          :model-value="dataTable.state.pagination.page"
          :page-count="dataTable.state.pagination.totalPages"
          :total="dataTable.state.pagination.total"
          :max="5"
          @update:model-value="dataTable.goToPage"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends DataTableItem">
import { computed, ref } from 'vue'
import { useAdvancedDataTable } from '~/composables/useAdvancedDataTable'
import type {
  DataTableItem,
  DataTableColumn,
  DataTableConfig,
  DataTableAction,
  DataTableBulkAction
} from '~/types/datatable'

// Props
interface Props {
  config: DataTableConfig<T>
  title?: string
  description?: string
  showHeader?: boolean
  showFilters?: boolean
  showColumnToggle?: boolean
  height?: string
  maxHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  showHeader: true,
  showFilters: true,
  showColumnToggle: true
})

// Emits
const emit = defineEmits<{
  'row-click': [row: T, index: number, event: Event]
  'row-double-click': [row: T, index: number, event: Event]
  'cell-click': [value: any, row: T, column: DataTableColumn<T>, event: Event]
  'action-click': [action: DataTableAction<T>, row: T, index: number]
  'bulk-action-click': [action: DataTableBulkAction<T>, selectedRows: T[]]
}>()

// Initialize the data table composable
const dataTable = useAdvancedDataTable<T>(props.config)

// Computed properties
const tableClasses = computed(() => ({
  'datatable-striped': props.config.striped,
  'datatable-bordered': props.config.bordered,
  'datatable-dense': props.config.dense,
  'datatable-hoverable': props.config.hoverable !== false
}))

const containerStyle = computed(() => ({
  height: props.height,
  maxHeight: props.maxHeight || props.config.maxHeight
}))

const hasSelection = computed(() => dataTable.hasSelection.value)
const hasActions = computed(() => dataTable.hasActions.value)
const hasBulkActions = computed(() => dataTable.hasBulkActions.value)
const hasFilters = computed(() => dataTable.hasFilters.value)
const selectedCount = computed(() => dataTable.selectedCount.value)

const hasActiveFilters = computed(() => 
  Object.values(dataTable.state.filters).some(value => 
    value !== null && value !== undefined && value !== ''
  )
)

const pageSizeOptions = computed(() => 
  dataTable.state.pagination.pageSizeOptions?.map(size => ({
    label: size.toString(),
    value: size
  })) || []
)

const paginationStart = computed(() => 
  (dataTable.state.pagination.page - 1) * dataTable.state.pagination.pageSize + 1
)

const paginationEnd = computed(() => 
  Math.min(
    dataTable.state.pagination.page * dataTable.state.pagination.pageSize,
    dataTable.state.pagination.total
  )
)

// Column toggle items
const columnToggleItems = computed(() => 
  props.config.columns.map(column => ([{
    label: column.label,
    icon: dataTable.state.visibleColumns.includes(column.key) 
      ? 'i-heroicons-check' 
      : undefined,
    click: () => dataTable.toggleColumnVisibility(column.key)
  }]))
)

// Export items
const exportItems = computed(() => {
  const formats = props.config.exportFormats || ['csv', 'json']
  return formats.map(format => ([{
    label: format.toUpperCase(),
    icon: 'i-heroicons-arrow-down-tray',
    click: () => dataTable.exportData(format)
  }]))
})

// Helper functions
const getRowKey = (row: T): string | number => {
  return dataTable.getNestedValue(row, props.config.keyField || 'id')
}

const isRowSelected = (row: T): boolean => {
  const id = getRowKey(row)
  return dataTable.state.selection.selectedIds.includes(id)
}

const getCellValue = (row: T, column: DataTableColumn<T>): any => {
  return dataTable.getNestedValue(row, column.key)
}

const formatCellValue = (value: any, column: DataTableColumn<T>, row: T): string => {
  if (column.format) {
    return column.format(value, row)
  }
  
  if (value === null || value === undefined) {
    return ''
  }
  
  if (column.type === 'date' && value) {
    return new Date(value).toLocaleDateString()
  }
  
  if (column.type === 'number' && typeof value === 'number') {
    return value.toLocaleString()
  }
  
  return String(value)
}

const getBadgeColor = (value: any, row: T): string => {
  // This could be customized based on your needs
  if (typeof value === 'boolean') {
    return value ? 'green' : 'red'
  }
  
  if (typeof value === 'string') {
    const lower = value.toLowerCase()
    if (lower.includes('success') || lower.includes('active') || lower.includes('completed')) {
      return 'green'
    }
    if (lower.includes('warning') || lower.includes('pending')) {
      return 'yellow'
    }
    if (lower.includes('error') || lower.includes('failed') || lower.includes('inactive')) {
      return 'red'
    }
  }
  
  return 'gray'
}

const getColumnStyle = (column: DataTableColumn<T>) => ({
  width: column.width,
  minWidth: column.minWidth,
  maxWidth: column.maxWidth
})

const getRowActions = (row: T) => {
  return props.config.actions?.filter(action => 
    typeof action.visible === 'function' ? action.visible(row) : action.visible !== false
  ) || []
}

// Event handlers
const handleRowClick = (row: T, index: number, event: Event) => {
  if (props.config.selectOnRowClick && hasSelection.value) {
    dataTable.toggleRowSelection(row)
  }
  emit('row-click', row, index, event)
}

const handleRowDoubleClick = (row: T, index: number, event: Event) => {
  emit('row-double-click', row, index, event)
}

const handleCellClick = (value: any, row: T, column: DataTableColumn<T>, event: Event) => {
  emit('cell-click', value, row, column, event)
}

const handleRowAction = async (action: DataTableAction<T>, row: T, index: number) => {
  if (action.confirm) {
    // You would implement a confirmation dialog here
    const confirmed = confirm(`${action.confirm.title}\n${action.confirm.message}`)
    if (!confirmed) return
  }
  
  try {
    await action.handler(row, index)
    emit('action-click', action, row, index)
  } catch (error) {
    console.error('Action failed:', error)
  }
}

const handleBulkAction = async (action: DataTableBulkAction<T>) => {
  if (action.confirm) {
    const confirmed = confirm(`${action.confirm.title}\n${action.confirm.message}`)
    if (!confirmed) return
  }
  
  try {
    await action.handler(
      dataTable.state.selection.selectedRows,
      dataTable.state.selection.selectedIds
    )
    emit('bulk-action-click', action, dataTable.state.selection.selectedRows)
  } catch (error) {
    console.error('Bulk action failed:', error)
  }
}

// Expose the data table instance for parent components
defineExpose({
  dataTable,
  refresh: dataTable.refresh,
  exportData: dataTable.exportData,
  clearSelection: dataTable.clearSelection
})
</script>

<style scoped>
.datatable-header-cell {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider;
}

.datatable-cell {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white;
}

.selection-cell {
  @apply w-12 px-4;
}

.actions-cell {
  @apply text-right;
}

.datatable-row:hover {
  @apply transition-colors duration-150;
}

.datatable-loading,
.datatable-error,
.datatable-empty {
  @apply border border-gray-200 dark:border-gray-700 rounded-lg;
}

.datatable-dense .datatable-header-cell {
  @apply py-2;
}

.datatable-dense .datatable-cell {
  @apply py-2;
}

.datatable-bordered {
  @apply border border-gray-200 dark:border-gray-700 rounded-lg;
}

.datatable-bordered .datatable-cell {
  @apply border-r border-gray-200 dark:border-gray-700;
}

.datatable-bordered .datatable-cell:last-child {
  @apply border-r-0;
}
</style>
