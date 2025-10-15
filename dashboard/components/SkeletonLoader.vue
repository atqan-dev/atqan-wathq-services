<template>
  <div class="animate-pulse">
    <!-- Card Skeleton -->
    <div v-if="type === 'card'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center space-x-4 mb-4">
        <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
        <div class="flex-1">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
        </div>
        <div class="w-16 h-6 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
      </div>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/3 mb-1"></div>
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-2/3"></div>
        </div>
        <div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/3 mb-1"></div>
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
        </div>
      </div>
      <div class="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex space-x-2">
          <div class="w-16 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
          <div class="w-20 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
        <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
      </div>
    </div>

    <!-- Table Row Skeleton -->
    <div v-else-if="type === 'table-row'" class="flex items-center space-x-4 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
      <div class="flex-1">
        <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-1"></div>
        <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
      </div>
      <div class="w-20 h-6 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
      <div class="w-24 h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
      <div class="flex space-x-2">
        <div class="w-16 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
        <div class="w-16 h-8 bg-gray-300 dark:bg-gray-600 rounded"></div>
      </div>
    </div>

    <!-- Stats Card Skeleton -->
    <div v-else-if="type === 'stats'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
        <div class="flex-1">
          <div class="h-8 bg-gray-300 dark:bg-gray-600 rounded w-16 mb-2"></div>
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-24"></div>
        </div>
      </div>
    </div>

    <!-- Generic Rectangle Skeleton -->
    <div v-else class="bg-gray-300 dark:bg-gray-600 rounded" :class="skeletonClass"></div>
  </div>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'rectangle',
    validator: (value) => ['card', 'table-row', 'stats', 'rectangle'].includes(value)
  },
  width: {
    type: String,
    default: 'w-full'
  },
  height: {
    type: String,
    default: 'h-4'
  }
})

const skeletonClass = computed(() => {
  if (props.type === 'rectangle') {
    return `${props.width} ${props.height}`
  }
  return ''
})
</script>
