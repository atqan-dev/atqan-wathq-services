<template>
  <div class="folder-browser">
    <!-- Header with current path -->
    <div class="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center space-x-2">
        <UIcon name="i-heroicons-folder" class="w-5 h-5 text-gray-500" />
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ currentPath || '/var/www' }}
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <UButton
          v-if="parentPath"
          size="xs"
          variant="ghost"
          icon="i-heroicons-arrow-up"
          @click="navigateToParent"
        >
          Up
        </UButton>
        <UButton
          size="xs"
          variant="ghost"
          icon="i-heroicons-arrow-path"
          @click="refreshDirectory"
          :loading="loading"
        >
          Refresh
        </UButton>
      </div>
    </div>

    <!-- Directory contents -->
    <div class="max-h-64 overflow-y-auto">
      <div v-if="loading" class="p-4 text-center">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin mx-auto" />
        <p class="text-sm text-gray-500 mt-2">Loading...</p>
      </div>

      <div v-else-if="error" class="p-4 text-center">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-500 mx-auto" />
        <p class="text-sm text-red-500 mt-2">{{ error }}</p>
        <UButton size="xs" variant="ghost" @click="refreshDirectory" class="mt-2">
          Try Again
        </UButton>
      </div>

      <div v-else-if="items && items.length === 0" class="p-4 text-center">
        <UIcon name="i-heroicons-folder-open" class="w-6 h-6 text-gray-400 mx-auto" />
        <p class="text-sm text-gray-500 mt-2">This directory is empty</p>
      </div>

      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="item in items"
          :key="item.path"
          class="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
          @click="handleItemClick(item)"
          @dblclick="handleItemDoubleClick(item)"
        >
          <div class="flex items-center space-x-3 flex-1 min-w-0">
            <UIcon
              :name="item.is_directory ? 'i-heroicons-folder' : 'i-heroicons-document'"
              :class="item.is_directory ? 'text-blue-500' : 'text-gray-400'"
              class="w-5 h-5 flex-shrink-0"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ item.name }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ item.is_directory ? 'Directory' : formatFileSize(item.size) }}
              </p>
            </div>
          </div>
          
          <div class="flex items-center space-x-2">
            <UBadge
              v-if="selectedPath === item.path"
              color="primary"
              variant="soft"
              size="xs"
            >
              Selected
            </UBadge>
            <UButton
              v-if="item.is_directory"
              size="xs"
              variant="ghost"
              icon="i-heroicons-chevron-right"
              @click.stop="navigateToDirectory(item.path)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Footer with actions -->
    <div class="flex items-center justify-between p-3 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center space-x-2">
        <UInput
          v-model="newFolderName"
          placeholder="New folder name"
          size="xs"
          class="w-32"
        />
        <UButton
          size="xs"
          variant="outline"
          icon="i-heroicons-plus"
          @click="createNewFolder"
          :disabled="!newFolderName.trim()"
        >
          Create
        </UButton>
      </div>
      
      <div class="flex items-center space-x-2">
        <UButton
          size="xs"
          variant="ghost"
          @click="$emit('cancel')"
        >
          Cancel
        </UButton>
        <UButton
          size="xs"
          color="primary"
          @click="selectCurrentPath"
          :disabled="!selectedPath"
        >
          Select
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthenticatedFetch } from '~/composables/useAuthenticatedFetch'
interface DirectoryItem {
  name: string
  path: string
  is_directory: boolean
  size: number
  permissions: string
}

interface DirectoryListing {
  current_path: string
  parent_path: string | null
  items: DirectoryItem[]
}

interface Props {
  initialPath?: string
  allowFileSelection?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialPath: '/var/www',
  allowFileSelection: false
})

const emit = defineEmits<{
  select: [path: string]
  cancel: []
}>()

// Reactive state
const currentPath = ref(props.initialPath)
const parentPath = ref<string | null>(null)
const items = ref<DirectoryItem[]>([])
const selectedPath = ref<string>('')
const loading = ref(false)
const error = ref<string>('')
const newFolderName = ref('')

// Toast for notifications
const toast = useToast()

// Get authenticated fetch function
const { authenticatedFetch } = useAuthenticatedFetch()

// Load directory contents
const loadDirectory = async (path: string) => {
  loading.value = true
  error.value = ''
  
  try {
    console.log('Loading directory:', path);
    // Use authenticated fetch to include auth headers
    const response = await authenticatedFetch<DirectoryListing>(`/api/v1/filesystem/browse?path=${encodeURIComponent(path)}`, {
      onRequest({ request, options }: { request: any; options: any }) {
        console.log('Request:', request, options);
      },
      onResponse({ response }: { response: any }) {
        console.log('Response:', response.status, response._data);
      },
      onResponseError({ response }: { response: any }) {
        console.error('Response error:', response.status, response._data);
      },
      onRequestError({ error }: { error: any }) {
        console.error('Request error:', error);
      },
    })
    
    currentPath.value = response.current_path
    parentPath.value = response.parent_path
    items.value = response.items
    selectedPath.value = ''
  } catch (err: any) {
    console.error('Directory loading error:', err)
    console.error('Error details:', JSON.stringify(err, null, 2))
    error.value = err.data?.detail || err.message || 'Failed to load directory'
  } finally {
    loading.value = false
  }
}

// Navigation methods
const navigateToDirectory = (path: string) => {
  loadDirectory(path)
}

const navigateToParent = () => {
  if (parentPath.value) {
    loadDirectory(parentPath.value)
  }
}

const refreshDirectory = () => {
  loadDirectory(currentPath.value)
}

// Item interaction handlers
const handleItemClick = (item: DirectoryItem) => {
  if (item.is_directory || props.allowFileSelection) {
    selectedPath.value = item.path
  }
}

const handleItemDoubleClick = (item: DirectoryItem) => {
  if (item.is_directory) {
    navigateToDirectory(item.path)
  } else if (props.allowFileSelection) {
    emit('select', item.path)
  }
}

// Folder creation
const createNewFolder = async () => {
  if (!newFolderName.value.trim()) return
  
  const newPath = `${currentPath.value}/${newFolderName.value.trim()}`
  
  try {
    await authenticatedFetch(`/api/v1/filesystem/create-directory?path=${encodeURIComponent(newPath)}`, {
      method: 'POST'
    })
    
    toast.add({
      title: 'Success',
      description: 'Folder created successfully',
      color: 'green'
    })
    
    newFolderName.value = ''
    refreshDirectory()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.data?.detail || 'Failed to create folder',
      color: 'red'
    })
  }
}

// Path selection
const selectCurrentPath = () => {
  if (selectedPath.value) {
    emit('select', selectedPath.value)
  }
}

// Utility functions
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Initialize
onMounted(() => {
  loadDirectory(currentPath.value)
})
</script>

<style scoped>
.folder-browser {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  min-width: 400px;
  max-width: 600px;
}

.dark .folder-browser {
  background-color: #111827;
  border-color: #374151;
}
</style>
