<template>
  <div class="bg-white dark:bg-gray-900 rounded-lg shadow-md overflow-hidden">
    <!-- Table Header with Title and Actions -->
    <div v-if="title || $slots.header" class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-center">
        <h2 v-if="title" class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {{ title }}
        </h2>
        <slot name="header" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <LoadingSpinner />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="px-6 py-8 text-center">
      <div class="text-red-500 mb-2">
        <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-red-600 dark:text-red-400 font-medium">{{ error }}</p>
      <button v-if="onRetry" @click="onRetry" 
              class="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
        {{ retryText || 'Retry' }}
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="!data.length" class="px-6 py-12 text-center">
      <div class="text-gray-400 mb-4">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8l-4 4-4-4m0 0L9 7v4" />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400">{{ emptyMessage || 'No data available' }}</p>
      <slot name="empty-actions" />
    </div>

    <!-- Table Content -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Table Header -->
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <!-- Selection Column -->
            <th v-if="selectable" class="table-header w-12">
              <input 
                type="checkbox" 
                :checked="isAllSelected"
                :indeterminate="isPartiallySelected"
                @change="toggleSelectAll"
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </th>
            
            <!-- Data Columns -->
            <th 
              v-for="column in columns" 
              :key="column.key"
              :class="[
                'table-header',
                column.align === 'center' ? 'text-center' : 
                column.align === 'right' ? 'text-right' : 'text-left',
                column.sortable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700' : '',
                column.width ? `w-${column.width}` : ''
              ]"
              @click="column.sortable ? handleSort(column.key) : null"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <div v-if="column.sortable" class="flex flex-col">
                  <svg 
                    :class="[
                      'w-3 h-3 transition-colors',
                      sortBy === column.key && sortOrder === 'asc' ? 'text-indigo-600' : 'text-gray-400'
                    ]"
                    fill="currentColor" viewBox="0 0 20 20"
                  >
                    <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" />
                  </svg>
                  <svg 
                    :class="[
                      'w-3 h-3 -mt-1 transition-colors',
                      sortBy === column.key && sortOrder === 'desc' ? 'text-indigo-600' : 'text-gray-400'
                    ]"
                    fill="currentColor" viewBox="0 0 20 20"
                  >
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                  </svg>
                </div>
              </div>
            </th>

            <!-- Actions Column -->
            <th v-if="actions.length || $slots.actions" class="table-header text-right">
              Actions
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr 
            v-for="(item, index) in sortedData" 
            :key="getRowKey(item, index)"
            :class="[
              'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors',
              selectedItems.includes(getRowKey(item, index)) ? 'bg-indigo-50 dark:bg-indigo-900/20' : '',
              rowClass ? rowClass(item, index) : ''
            ]"
            @click="onRowClick ? onRowClick(item, index) : null"
          >
            <!-- Selection Column -->
            <td v-if="selectable" class="table-cell">
              <input 
                type="checkbox" 
                :checked="selectedItems.includes(getRowKey(item, index))"
                @change="toggleSelectItem(item, index)"
                @click.stop
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
            </td>

            <!-- Data Columns -->
            <td 
              v-for="column in columns" 
              :key="column.key"
              :class="[
                'table-cell',
                column.align === 'center' ? 'text-center' : 
                column.align === 'right' ? 'text-right' : 'text-left',
                column.cellClass ? column.cellClass(item[column.key], item, index) : ''
              ]"
            >
              <!-- Custom Column Slot -->
              <slot 
                v-if="$slots[`column-${column.key}`]" 
                :name="`column-${column.key}`" 
                :value="item[column.key]" 
                :item="item" 
                :index="index"
              />
              
              <!-- Custom Formatter -->
              <span v-else-if="column.formatter">
                {{ column.formatter(item[column.key], item, index) }}
              </span>
              
              <!-- Default Value Display -->
              <span v-else>
                {{ item[column.key] ?? (column.defaultValue || '-') }}
              </span>
            </td>

            <!-- Actions Column -->
            <td v-if="actions.length || $slots.actions" class="table-cell text-right">
              <div class="flex justify-end space-x-2">
                <!-- Predefined Actions -->
                <button
                  v-for="action in getVisibleActions(item)"
                  :key="action.key"
                  @click.stop="action.handler(item, index)"
                  :disabled="action.disabled && action.disabled(item)"
                  :class="[
                    'btn-icon',
                    action.class || '',
                    action.disabled && action.disabled(item) ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                  :title="action.tooltip ? action.tooltip(item) : action.label"
                >
                  <component v-if="action.icon" :is="action.icon" class="w-4 h-4" />
                  <span v-else class="text-sm">{{ action.label }}</span>
                </button>

                <!-- Custom Actions Slot -->
                <slot name="actions" :item="item" :index="index" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && data.length" class="px-6 py-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <!-- Results Info -->
        <div class="text-sm text-gray-700 dark:text-gray-300">
          <span v-if="pagination.total">
            Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} results
          </span>
          <span v-else>
            Showing {{ data.length }} results
          </span>
        </div>

        <!-- Pagination Controls -->
        <div class="flex items-center space-x-2">
          <button
            :disabled="!pagination.hasPrevious"
            @click="$emit('page-change', pagination.currentPage - 1)"
            class="btn btn-secondary"
          >
            Previous
          </button>
          
          <span class="text-sm text-gray-700 dark:text-gray-300">
            Page {{ pagination.currentPage }} of {{ pagination.totalPages }}
          </span>
          
          <button
            :disabled="!pagination.hasNext"
            @click="$emit('page-change', pagination.currentPage + 1)"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectable && selectedItems.length && bulkActions.length" 
         class="px-6 py-3 bg-indigo-50 dark:bg-indigo-900/20 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <span class="text-sm text-indigo-700 dark:text-indigo-300">
          {{ selectedItems.length }} item(s) selected
        </span>
        <div class="flex space-x-2">
          <button
            v-for="action in bulkActions"
            :key="action.key"
            @click="action.handler(getSelectedItems())"
            :class="['btn', action.class || 'btn-secondary']"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

// Types
interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  formatter?: (value: any, item: any, index: number) => string
  cellClass?: (value: any, item: any, index: number) => string
  align?: 'left' | 'center' | 'right'
  width?: string
  defaultValue?: string
}

interface TableAction {
  key: string
  label: string
  handler: (item: any, index: number) => void
  icon?: any
  class?: string
  tooltip?: (item: any) => string
  disabled?: (item: any) => boolean
  visible?: (item: any) => boolean
}

interface BulkAction {
  key: string
  label: string
  handler: (items: any[]) => void
  class?: string
}

interface TablePagination {
  currentPage: number
  totalPages: number
  total?: number
  from: number
  to: number
  hasPrevious: boolean
  hasNext: boolean
}

// Props
const props = withDefaults(defineProps<{
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  error?: string
  title?: string
  emptyMessage?: string
  retryText?: string
  onRetry?: () => void
  onRowClick?: (item: any, index: number) => void
  rowClass?: (item: any, index: number) => string
  rowKey?: string | ((item: any, index: number) => string | number)
  actions?: TableAction[]
  bulkActions?: BulkAction[]
  selectable?: boolean
  pagination?: TablePagination
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}>(), {
  data: () => [],
  columns: () => [],
  loading: false,
  error: '',
  actions: () => [],
  bulkActions: () => [],
  selectable: false,
  sortBy: '',
  sortOrder: 'asc'
})

// Emits
const emit = defineEmits<{
  'sort-change': [{ sortBy: string, sortOrder: 'asc' | 'desc' }]
  'page-change': [page: number]
  'selection-change': [selectedItems: any[]]
}>()

// State
const selectedItems = ref<(string | number)[]>([])
const currentSortBy = ref(props.sortBy)
const currentSortOrder = ref<'asc' | 'desc'>(props.sortOrder)

// Computed
const sortedData = computed(() => {
  if (!currentSortBy.value) return props.data
  
  const column = props.columns.find(col => col.key === currentSortBy.value)
  if (!column?.sortable) return props.data
  
  return [...props.data].sort((a, b) => {
    const aVal = a[currentSortBy.value]
    const bVal = b[currentSortBy.value]
    
    if (aVal === bVal) return 0
    
    const comparison = aVal < bVal ? -1 : 1
    return currentSortOrder.value === 'asc' ? comparison : -comparison
  })
})

const isAllSelected = computed(() => {
  return props.data.length > 0 && selectedItems.value.length === props.data.length
})

const isPartiallySelected = computed(() => {
  return selectedItems.value.length > 0 && selectedItems.value.length < props.data.length
})

// Methods
const getRowKey = (item: any, index: number): string | number => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item, index)
  }
  return props.rowKey ? item[props.rowKey] : item.id ?? index
}

const handleSort = (columnKey: string) => {
  if (currentSortBy.value === columnKey) {
    currentSortOrder.value = currentSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    currentSortBy.value = columnKey
    currentSortOrder.value = 'asc'
  }
  
  emit('sort-change', { 
    sortBy: currentSortBy.value, 
    sortOrder: currentSortOrder.value 
  })
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = props.data.map((item, index) => getRowKey(item, index))
  }
  emitSelectionChange()
}

const toggleSelectItem = (item: any, index: number) => {
  const key = getRowKey(item, index)
  const selectedIndex = selectedItems.value.indexOf(key)
  
  if (selectedIndex > -1) {
    selectedItems.value.splice(selectedIndex, 1)
  } else {
    selectedItems.value.push(key)
  }
  emitSelectionChange()
}

const getSelectedItems = () => {
  return props.data.filter((item, index) => 
    selectedItems.value.includes(getRowKey(item, index))
  )
}

const getVisibleActions = (item: any) => {
  return props.actions.filter(action => 
    !action.visible || action.visible(item)
  )
}

const emitSelectionChange = () => {
  emit('selection-change', getSelectedItems())
}

// Watch for prop changes
watch(() => props.sortBy, (newVal) => {
  currentSortBy.value = newVal
})

watch(() => props.sortOrder, (newVal) => {
  currentSortOrder.value = newVal
})
</script>

<style lang="postcss" scoped>
.table-header {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider;
}

.table-cell {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100;
}

.btn {
  @apply px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors;
}

.btn-secondary {
  @apply bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-icon {
  @apply p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 transition-colors;
}
</style>
