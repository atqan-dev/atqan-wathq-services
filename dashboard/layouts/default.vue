<template>
  <div :class="[
      'min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 relative',
      isRTL ? 'rtl' : 'ltr'
    ]">
    <!-- Watermark -->
    <div class="fixed inset-0 flex items-center justify-center pointer-events-none z-0 opacity-30">
      <img 
        src="/assets/images/tawthiq-logo.png" 
        alt="Tawthiq Watermark" 
        class="w-96 h-96 transform rotate-[-30deg] opacity-50" 
      />
    </div>

    <!-- Main Layout with Sidebar -->
    <div class="relative z-10 flex flex-col min-h-screen">
      <!-- Header -->
      <AppHeader />

      <!-- Content Wrapper -->
      <div class="flex flex-1 pt-16">
        <!-- Sidebar -->
        <AppSidebar />

        <!-- Main Content Area -->
        <main 
          :class="[
            'flex-1 transition-all duration-300 ease-in-out',
            'min-h-[calc(100vh-4rem)]',
            'px-4 sm:px-6 lg:px-8 py-6 sm:py-8',
            // Desktop: adjust for sidebar
            isRTL 
              ? (isCollapsed ? 'lg:pr-16' : 'lg:pr-64')
              : (isCollapsed ? 'lg:pl-16' : 'lg:pl-64'),
            // Mobile: full width when sidebar is hidden
            'w-full'
          ]"
          :style="{
            '--sidebar-width': `${sidebarWidth}px`
          }"
        >
          <!-- Content Container with max-width for better readability -->
          <div class="max-w-[1920px] mx-auto w-full">
            <slot />
          </div>
        </main>
      </div>

      <!-- Notifications -->
      <UNotifications />
      
      <!-- Confirm Dialog -->
      <ConfirmDialog />
    </div>
  </div>
</template>

<script setup lang="ts">
const { initializeDirection, isRTL } = useLanguage()
const { isCollapsed, sidebarWidth, initializeSidebar } = useSidebar()



// Initialize on mount
onMounted(() => {
  initializeDirection()
  initializeSidebar()
})
</script>
