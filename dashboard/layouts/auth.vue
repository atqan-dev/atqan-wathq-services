<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800">
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
    </div>
    
    <!-- Content -->
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>

<script setup>

// Auth layout for login/register pages
useHead({
  title: 'Authentication'
})
</script>

<style scoped>
.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}
</style> 