<template>
  <div class="space-y-4">
    <!-- Header with Search, Filters, and Actions -->
    <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <!-- Search -->
      <div class="flex-1 max-w-md">
        <UInput
          v-model="searchQuery"
          :placeholder="searchPlaceholder || t('common.search')"
          icon="i-heroicons-magnifying-glass"
          :loading="loading"
          clearable
        />
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <!-- Filters Toggle -->
        <UButton
          v-if="filters.length > 0"
          variant="outline"
          color="gray"
          icon="i-heroicons-funnel"
          @click="showFilters = !showFilters"
          :class="{ 'bg-primary-50 border-primary-200': hasActiveFilters }"
        >
          {{ t('common.filters') }}
          <UBadge v-if="hasActiveFilters" color="primary" size="xs" class="ml-1">
            {{ Object.keys(activeFilters).length }}
          </UBadge>
        </UButton>

        <!-- Column Visibility -->
        <UDropdown :items="columnVisibilityItems">
          <UButton variant="outline" color="gray" icon="i-heroicons-view-columns">
            {{ t('common.columns') }}
          </UButton>
        </UDropdown>

        <!-- Export -->
        <UDropdown v-if="exportable" :items="exportItems">
          <UButton variant="outline" color="gray" icon="i-heroicons-arrow-down-tray">
            {{ t('common.export') }}
          </UButton>
        </UDropdown>

        <!-- Bulk Actions -->
        <UDropdown v-if="bulkActions.length > 0 && selectedItems.length > 0" :items="bulkActionItems">
          <UButton color="primary" icon="i-heroicons-ellipsis-horizontal">
            {{ t('common.actions') }} ({{ selectedItems.length }})
          </UButton>
        </UDropdown>

        <!-- Refresh -->
        <UButton
          variant="outline"
          color="gray"
          icon="i-heroicons-arrow-path"
          :loading="loading"
          @click="refresh"
        >
          {{ t('common.refresh') }}
        </UButton>
      </div>
    </div>

    <!-- Filters Panel -->
    <UCard v-if="showFilters && filters.length > 0" class="border-l-4 border-l-primary-500">
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium">{{ t('common.filters') }}</h3>
          <UButton
            v-if="hasActiveFilters"
            size="xs"
            variant="ghost"
            color="gray"
            @click="clearAllFilters"
          >
            {{ t('common.clearAll') }}
          </UButton>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="filter in filters" :key="filter.key" class="space-y-1">
          <label class="text-xs font-medium text-gray-700 dark:text-gray-300">
            {{ filter.label }}
          </label>

          <!-- Text Filter -->
          <UInput
            v-if="filter.type === 'text'"
            :model-value="activeFilters[filter.key] || ''"
            :placeholder="filter.placeholder"
            @update:model-value="setFilter(filter.key, $event)"
            clearable
          />

          <!-- Select Filter -->
          <USelect
            v-else-if="filter.type === 'select'"
            :model-value="activeFilters[filter.key]"
            :options="filter.options || []"
            :placeholder="filter.placeholder"
            :multiple="filter.multiple"
            @update:model-value="setFilter(filter.key, $event)"
            clearable
          />

          <!-- Date Filter -->
          <UInput
            v-else-if="filter.type === 'date'"
            :model-value="activeFilters[filter.key] || ''"
            type="date"
            :placeholder="filter.placeholder"
            @update:model-value="setFilter(filter.key, $event)"
            clearable
          />

          <!-- Number Filter -->
          <UInput
            v-else-if="filter.type === 'number'"
            :model-value="activeFilters[filter.key] || ''"
            type="number"
            :placeholder="filter.placeholder"
            @update:model-value="setFilter(filter.key, $event)"
            clearable
          />

          <!-- Boolean Filter -->
          <USelect
            v-else-if="filter.type === 'boolean'"
            :model-value="activeFilters[filter.key]"
            :options="[
              { label: t('common.yes'), value: true },
              { label: t('common.no'), value: false }
            ]"
            :placeholder="filter.placeholder"
            @update:model-value="setFilter(filter.key, $event)"
            clearable
          />
        </div>
      </div>
    </UCard>

    <!-- Active Filters -->
    <div v-if="hasActiveFilters && !showFilters" class="flex flex-wrap gap-2">
      <UBadge
        v-for="(value, key) in activeFilters"
        :key="key"
        color="primary"
        variant="subtle"
        class="cursor-pointer"
        @click="clearFilter(key)"
      >
        {{ getFilterLabel(key) }}: {{ formatFilterValue(key, value) }}
        <UIcon name="i-heroicons-x-mark" class="w-3 h-3 ml-1" />
      </UBadge>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <!-- Error State -->
    <UAlert v-else-if="error" color="red" variant="subtle" :title="t('common.error')" :description="error" />

    <!-- Empty State -->
    <div v-else-if="data.length === 0" class="text-center py-12">
      <UIcon name="i-heroicons-document-text" class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
        {{ emptyStateTitle || t('common.noData') }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ emptyStateDescription || t('common.noDataDescription') }}
      </p>
    </div>

    <!-- Data Table -->
    <div v-else class="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Header -->
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <!-- Selection Column -->
            <th v-if="selectable" class="w-12 px-4 py-3">
              <UCheckbox
                :model-value="isAllSelected"
                :indeterminate="isPartiallySelected"
                @update:model-value="toggleSelectAll"
              />
            </th>

            <!-- Data Columns -->
            <th
              v-for="column in visibleColumns"
              :key="column.key"
              :class="[
                'px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider',
                column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
              ]"
              :style="column.width ? { width: column.width } : undefined"
            >
              <div
                v-if="column.sortable"
                class="flex items-center gap-1 cursor-pointer hover:text-gray-700 dark:hover:text-gray-200"
                @click="toggleSort(column.key)"
              >
                {{ column.label }}
                <UIcon
                  v-if="sortColumn === column.key"
                  :name="sortDirection === 'asc' ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                  class="w-4 h-4"
                />
                <UIcon
                  v-else
                  name="i-heroicons-chevron-up-down"
                  class="w-4 h-4 opacity-50"
                />
              </div>
              <span v-else>{{ column.label }}</span>
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="(row, index) in data"
            :key="getRowKey(row, index)"
            class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            :class="{ 'bg-primary-50 dark:bg-primary-900/20': selectedItems.includes(getRowKey(row, index)) }"
          >
            <!-- Selection Column -->
            <td v-if="selectable" class="w-12 px-4 py-4">
              <UCheckbox
                :model-value="selectedItems.includes(getRowKey(row, index))"
                @update:model-value="toggleSelectItem(getRowKey(row, index))"
              />
            </td>

            <!-- Data Columns -->
            <td
              v-for="column in visibleColumns"
              :key="column.key"
              :class="[
                'px-6 py-4',
                column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
              ]"
            >
              <!-- Custom Component -->
              <component
                v-if="column.component"
                :is="column.component"
                :value="getCellValue(row, column)"
                :row="row"
                :column="column"
                v-bind="column.props"
              />

              <!-- Badge Type -->
              <UBadge
                v-else-if="column.type === 'badge'"
                :color="getBadgeColor(getCellValue(row, column))"
                variant="subtle"
              >
                {{ formatCellValue(row, column) }}
              </UBadge>

              <!-- Actions Type -->
              <div v-else-if="column.type === 'actions'" class="flex items-center gap-1">
                <UButton
                  v-for="action in getRowActions(row)"
                  :key="action.key"
                  :size="action.size || 'xs'"
                  :color="action.color || 'gray'"
                  :variant="action.variant || 'ghost'"
                  :icon="action.icon"
                  @click="action.handler(row)"
                >
                  {{ action.label }}
                </UButton>
              </div>

              <!-- Default Text -->
              <span v-else class="text-sm text-gray-900 dark:text-white">
                {{ formatCellValue(row, column) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="data.length > 0" class="flex flex-col sm:flex-row gap-4 items-center justify-between">
      <!-- Page Size Selector -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('common.show') }}</span>
        <USelect
          :model-value="pageSize"
          :options="[
            { label: '10', value: 10 },
            { label: '25', value: 25 },
            { label: '50', value: 50 },
            { label: '100', value: 100 }
          ]"
          @update:model-value="setPageSize"
          class="w-20"
        />
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('common.entries') }}</span>
      </div>

      <!-- Pagination Info -->
      <div class="text-sm text-gray-600 dark:text-gray-400">
        {{ t('common.showing') }} {{ pagination.from }} {{ t('common.to') }} {{ pagination.to }} 
        {{ t('common.of') }} {{ pagination.total }} {{ t('common.entries') }}
      </div>

      <!-- Pagination Controls -->
      <UPagination
        :model-value="currentPage"
        :page-count="pagination.totalPages"
        :total="pagination.total"
        :max="5"
        @update:model-value="goToPage"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from '~/composables/useI18n'
import type { 
  UseDataTableReturn, 
  DataTableColumn, 
  DataTableFilter, 
  DataTableAction 
} from '~/composables/useDataTable'

interface Props {
  // Data table instance
  table: UseDataTableReturn<any>
  
  // Configuration
  selectable?: boolean
  exportable?: boolean
  searchPlaceholder?: string
  emptyStateTitle?: string
  emptyStateDescription?: string
}

const props = withDefaults(defineProps<Props>(), {
  selectable: false,
  exportable: false
})

const { t } = useI18n()

// Destructure table functionality
const {
  // Data
  data,
  loading,
  error,
  
  // Search
  searchQuery,
  
  // Pagination
  currentPage,
  pageSize,
  pagination,
  goToPage,
  setPageSize,
  
  // Sorting
  sortColumn,
  sortDirection,
  toggleSort,
  
  // Selection
  selectedItems,
  isAllSelected,
  isPartiallySelected,
  toggleSelectItem,
  toggleSelectAll,
  
  // Columns
  columns,
  visibleColumns,
  toggleColumnVisibility,
  showAllColumns,
  hideAllColumns,
  resetColumnVisibility,
  
  // Filters
  filters,
  activeFilters,
  hasActiveFilters,
  setFilter,
  clearFilter,
  clearAllFilters,
  
  // Actions
  actions,
  bulkActions,
  
  // Methods
  refresh,
  exportData
} = props.table

// Local state
const showFilters = ref(false)

// Computed properties
const columnVisibilityItems = computed(() => [
  [
    ...columns.value.map(col => ({
      label: col.label,
      icon: col.visible ? 'i-heroicons-eye' : 'i-heroicons-eye-slash',
      click: () => toggleColumnVisibility(col.key)
    }))
  ],
  [
    {
      label: t('common.showAll'),
      icon: 'i-heroicons-eye',
      click: showAllColumns
    },
    {
      label: t('common.hideAll'),
      icon: 'i-heroicons-eye-slash',
      click: hideAllColumns
    },
    {
      label: t('common.reset'),
      icon: 'i-heroicons-arrow-path',
      click: resetColumnVisibility
    }
  ]
])

const exportItems = computed(() => [
  {
    label: 'CSV',
    icon: 'i-heroicons-document-text',
    click: () => exportData('csv')
  },
  {
    label: 'JSON',
    icon: 'i-heroicons-code-bracket',
    click: () => exportData('json')
  }
])

const bulkActionItems = computed(() => [
  bulkActions.value.map(action => ({
    label: action.label,
    icon: action.icon,
    click: () => action.handler(null, props.table.getSelectedItems())
  }))
])

// Helper methods
const getRowKey = (row: any, index: number): string | number => {
  return row.id || row.key || index
}

const getCellValue = (row: any, column: DataTableColumn): any => {
  return row[column.key]
}

const formatCellValue = (row: any, column: DataTableColumn): string => {
  const value = getCellValue(row, column)
  
  if (column.format) {
    return column.format(value, row)
  }
  
  if (column.type === 'date' && value) {
    return new Date(value).toLocaleDateString()
  }
  
  if (column.type === 'number' && typeof value === 'number') {
    return value.toLocaleString()
  }
  
  return value?.toString() || ''
}

const getBadgeColor = (value: any): string => {
  // Default badge color logic - can be customized
  if (typeof value === 'boolean') {
    return value ? 'green' : 'red'
  }
  
  if (typeof value === 'string') {
    const lowerValue = value.toLowerCase()
    if (lowerValue.includes('success') || lowerValue.includes('active')) return 'green'
    if (lowerValue.includes('error') || lowerValue.includes('failed')) return 'red'
    if (lowerValue.includes('warning') || lowerValue.includes('pending')) return 'yellow'
  }
  
  return 'gray'
}

const getRowActions = (row: any): DataTableAction[] => {
  return actions.value.filter(action => 
    !action.condition || action.condition(row)
  )
}

const getFilterLabel = (key: string): string => {
  const filter = filters.value.find(f => f.key === key)
  return filter?.label || key
}

const formatFilterValue = (key: string, value: any): string => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  
  if (typeof value === 'boolean') {
    return value ? t('common.yes') : t('common.no')
  }
  
  return value?.toString() || ''
}
</script>
