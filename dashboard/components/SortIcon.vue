<template>
  <div class="flex flex-col">
    <svg 
      :class="[
        'w-3 h-3 transition-colors',
        column === currentSort.column && currentSort.direction === 'asc' ? 'text-indigo-600' : 'text-gray-400'
      ]"
      fill="currentColor" 
      viewBox="0 0 20 20"
    >
      <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" />
    </svg>
    <svg 
      :class="[
        'w-3 h-3 -mt-1 transition-colors',
        column === currentSort.column && currentSort.direction === 'desc' ? 'text-indigo-600' : 'text-gray-400'
      ]"
      fill="currentColor" 
      viewBox="0 0 20 20"
    >
      <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
    </svg>
  </div>
</template>

<script setup lang="ts">
interface Props {
  column: string
  currentSort: {
    column: string
    direction: 'asc' | 'desc'
  }
}

defineProps<Props>()
</script>
