<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Advanced DataTable Examples
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Comprehensive examples of the reusable DataTable component
      </p>
    </div>

    <!-- Example 1: Basic Static Data Table -->
    <div class="mb-12">
      <h2 class="text-2xl font-semibold mb-4">Basic Static Data Table</h2>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <AdvancedDataTable
          :config="basicTableConfig"
          title="Sample Users"
          description="A simple example with static data"
        />
      </div>
    </div>

    <!-- Example 2: Advanced Features -->
    <div class="mb-12">
      <h2 class="text-2xl font-semibold mb-4">Advanced Features</h2>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <AdvancedDataTable
          :config="advancedTableConfig"
          title="Products Management"
          description="Full-featured table with filtering, actions, and bulk operations"
          @row-click="handleRowClick"
          @action-click="handleActionClick"
          @bulk-action-click="handleBulkActionClick"
        />
      </div>
    </div>

    <!-- Example 3: Server-Side Data -->
    <div class="mb-12">
      <h2 class="text-2xl font-semibold mb-4">Server-Side Data (Simulated)</h2>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <AdvancedDataTable
          :config="serverTableConfig"
          title="Server-Side Data"
          description="Demonstrates server-side pagination, sorting, and filtering"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { DataTableConfig, DataTableFetchParams } from '~/types/datatable'

// Define page meta
definePageMeta({
  title: 'DataTable Examples',
  description: 'Advanced DataTable component examples'
})

// Sample data interfaces
interface User {
  id: number
  name: string
  email: string
  role: string
  status: 'active' | 'inactive'
  createdAt: string
}

interface Product {
  id: number
  name: string
  price: number
  category: string
  stock: number
  status: 'active' | 'inactive' | 'discontinued'
  rating: number
  createdAt: string
}

// Sample static data
const sampleUsers: User[] = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    status: 'active',
    createdAt: '2024-01-15'
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'User',
    status: 'active',
    createdAt: '2024-01-20'
  },
  {
    id: 3,
    name: 'Bob Johnson',
    email: 'bob@example.com',
    role: 'Moderator',
    status: 'inactive',
    createdAt: '2024-01-10'
  },
  {
    id: 4,
    name: 'Alice Brown',
    email: 'alice@example.com',
    role: 'User',
    status: 'active',
    createdAt: '2024-01-25'
  },
  {
    id: 5,
    name: 'Charlie Wilson',
    email: 'charlie@example.com',
    role: 'Admin',
    status: 'active',
    createdAt: '2024-01-12'
  }
]

const sampleProducts: Product[] = [
  {
    id: 1,
    name: 'Wireless Headphones',
    price: 99.99,
    category: 'Electronics',
    stock: 25,
    status: 'active',
    rating: 4.5,
    createdAt: '2024-01-15'
  },
  {
    id: 2,
    name: 'Coffee Mug',
    price: 12.99,
    category: 'Home',
    stock: 100,
    status: 'active',
    rating: 4.2,
    createdAt: '2024-01-20'
  },
  {
    id: 3,
    name: 'Laptop Stand',
    price: 45.00,
    category: 'Office',
    stock: 5,
    status: 'active',
    rating: 4.8,
    createdAt: '2024-01-10'
  },
  {
    id: 4,
    name: 'Bluetooth Speaker',
    price: 79.99,
    category: 'Electronics',
    stock: 0,
    status: 'inactive',
    rating: 4.1,
    createdAt: '2024-01-25'
  },
  {
    id: 5,
    name: 'Desk Lamp',
    price: 34.99,
    category: 'Office',
    stock: 15,
    status: 'active',
    rating: 4.6,
    createdAt: '2024-01-12'
  }
]

// Basic table configuration
const basicTableConfig: DataTableConfig<User> = {
  data: sampleUsers,
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
      type: 'badge'
    },
    {
      key: 'status',
      label: 'Status',
      type: 'badge',
      sortable: true
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
  initialPageSize: 3,
  selectable: true,
  exportable: true
}

// Advanced table configuration
const advancedTableConfig: DataTableConfig<Product> = {
  data: sampleProducts,
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
      type: 'badge'
    },
    {
      key: 'stock',
      label: 'Stock',
      type: 'number',
      sortable: true,
      align: 'right',
      cellClass: (value) => value < 10 ? 'text-red-600 font-semibold' : 'text-green-600'
    },
    {
      key: 'rating',
      label: 'Rating',
      type: 'number',
      sortable: true,
      align: 'center',
      format: (value) => `⭐ ${value}`
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
        { label: 'Electronics', value: 'Electronics' },
        { label: 'Home', value: 'Home' },
        { label: 'Office', value: 'Office' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
        { label: 'Discontinued', value: 'discontinued' }
      ]
    },
    {
      key: 'stock',
      label: 'Low Stock',
      type: 'boolean'
    }
  ],
  actions: [
    {
      key: 'edit',
      label: 'Edit',
      icon: 'i-heroicons-pencil',
      color: 'primary',
      handler: (row) => {
        console.log('Edit product:', row)
      }
    },
    {
      key: 'duplicate',
      label: 'Duplicate',
      icon: 'i-heroicons-document-duplicate',
      color: 'gray',
      handler: (row) => {
        console.log('Duplicate product:', row)
      }
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
      handler: (row) => {
        console.log('Delete product:', row)
      }
    }
  ],
  bulkActions: [
    {
      key: 'activate',
      label: 'Activate Selected',
      icon: 'i-heroicons-check-circle',
      color: 'green',
      handler: (selectedRows) => {
        console.log('Activate products:', selectedRows)
      }
    },
    {
      key: 'deactivate',
      label: 'Deactivate Selected',
      icon: 'i-heroicons-x-circle',
      color: 'yellow',
      handler: (selectedRows) => {
        console.log('Deactivate products:', selectedRows)
      }
    },
    {
      key: 'delete_bulk',
      label: 'Delete Selected',
      icon: 'i-heroicons-trash',
      color: 'red',
      confirm: {
        title: 'Delete Products',
        message: 'Are you sure you want to delete the selected products?'
      },
      handler: (selectedRows) => {
        console.log('Delete products:', selectedRows)
      }
    }
  ],
  initialPageSize: 5,
  selectable: true,
  multiSelect: true,
  exportable: true,
  exportFormats: ['csv', 'json'],
  persistState: true,
  stateKey: 'products-example-table'
}

// Server-side fetch simulation
const serverSideData = ref([...sampleProducts])

const fetchServerData = async (params: DataTableFetchParams) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  
  let filteredData = [...serverSideData.value]
  
  // Apply global search
  if (params.search) {
    const searchTerm = params.search.toLowerCase()
    filteredData = filteredData.filter(item => 
      item.name.toLowerCase().includes(searchTerm) ||
      item.category.toLowerCase().includes(searchTerm)
    )
  }
  
  // Apply filters
  if (params.filters) {
    Object.entries(params.filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (key === 'category' || key === 'status') {
          filteredData = filteredData.filter(item => item[key as keyof Product] === value)
        }
      }
    })
  }
  
  // Apply sorting
  if (params.sortBy && params.sortOrder) {
    filteredData.sort((a, b) => {
      const aValue = a[params.sortBy as keyof Product]
      const bValue = b[params.sortBy as keyof Product]
      
      let comparison = 0
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        comparison = aValue - bValue
      } else {
        comparison = String(aValue).localeCompare(String(bValue))
      }
      
      return params.sortOrder === 'desc' ? -comparison : comparison
    })
  }
  
  // Apply pagination
  const total = filteredData.length
  const start = (params.page - 1) * params.pageSize
  const end = start + params.pageSize
  const paginatedData = filteredData.slice(start, end)
  
  return {
    data: paginatedData,
    total,
    page: params.page,
    pageSize: params.pageSize,
    totalPages: Math.ceil(total / params.pageSize)
  }
}

// Server-side table configuration
const serverTableConfig: DataTableConfig<Product> = {
  fetchFunction: fetchServerData,
  columns: [
    {
      key: 'name',
      label: 'Product Name',
      sortable: true,
      searchable: true
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
      type: 'badge'
    },
    {
      key: 'stock',
      label: 'Stock',
      type: 'number',
      sortable: true,
      align: 'right'
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
        { label: 'Electronics', value: 'Electronics' },
        { label: 'Home', value: 'Home' },
        { label: 'Office', value: 'Office' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { label: 'Active', value: 'active' },
        { label: 'Inactive', value: 'inactive' },
        { label: 'Discontinued', value: 'discontinued' }
      ]
    }
  ],
  initialPageSize: 3,
  selectable: true,
  exportable: true,
  persistState: true,
  stateKey: 'server-example-table'
}

// Event handlers
const handleRowClick = (row: Product) => {
  console.log('Row clicked:', row)
  // You could navigate to a detail page here
  // navigateTo(`/products/${row.id}`)
}

const handleActionClick = (action: any, row: Product) => {
  console.log(`Action ${action.key} clicked for:`, row)
  
  // Show a toast notification
  // $toast.success(`${action.label} action performed on ${row.name}`)
}

const handleBulkActionClick = (action: any, selectedRows: Product[]) => {
  console.log(`Bulk action ${action.key} performed on:`, selectedRows)
  
  // Show a toast notification
  // $toast.success(`${action.label} performed on ${selectedRows.length} items`)
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style>
