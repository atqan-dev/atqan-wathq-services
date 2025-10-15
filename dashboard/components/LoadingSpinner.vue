<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div class="relative">
      <!-- Spinner -->
      <div 
        class="animate-spin rounded-full border-2 border-gray-300 border-t-primary-600"
        :class="spinnerClass"
      ></div>
      
      <!-- Optional text -->
      <div v-if="text" class="mt-3 text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">{{ text }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  fullHeight: {
    type: Boolean,
    default: false
  }
})

const spinnerClass = computed(() => {
  const sizes = {
    xs: 'w-4 h-4',
    sm: 'w-6 h-6', 
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }
  return sizes[props.size]
})

const containerClass = computed(() => {
  return props.fullHeight ? 'min-h-64 py-12' : 'py-8'
})
</script>
