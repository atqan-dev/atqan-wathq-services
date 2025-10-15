<template>
  <NuxtLayout>
    <NuxtPage />
    
    <!-- Global Components -->
    <NotificationContainer />
    <NotificationPermissionPrompt />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from 'vue'

// Initialize settings after the app is fully mounted
onMounted(async () => {
  // Wait for next tick to ensure all plugins are loaded
  await nextTick()
  
  // Dynamically import the settings composable to avoid early initialization issues
  try {
    const { useSettings } = await import('@/composables/useSettings')
    const { initializeSettings } = useSettings()
    initializeSettings()
  } catch (error) {
    console.warn('Failed to initialize settings:', error)
  }
})
</script>

<style>
/* Global CSS Custom Properties for Theme Support */
:root {
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --font-size: 14px;
  --accent-color: #3B82F6;
}

/* Apply font settings globally */
* {
  font-family: var(--font-family);
  font-size: var(--font-size);
}

/* Reduce motion for users who prefer it */
.reduce-motion * {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}

/* Theme transition for smooth changes */
html {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Accent color application */
.btn-primary, 
.bg-blue-600, 
.text-blue-600,
input[type="checkbox"]:checked,
input[type="radio"]:checked {
  background-color: var(--accent-color) !important;
  border-color: var(--accent-color) !important;
  color: white !important;
}

.border-blue-500,
.ring-blue-500 {
  border-color: var(--accent-color) !important;
  --tw-ring-color: var(--accent-color) !important;
}
</style>
