<template>
  <nav :class="['flex', isRTL ? 'rtl-space-x-2' : '']" aria-label="Breadcrumb">
    <ol :class="['inline-flex items-center space-x-1 md:space-x-3', isRTL ? 'flex-row-reverse' : '']">
      <li class="inline-flex items-center">
        <NuxtLink 
          to="/"
          :class="[
            'inline-flex items-center text-sm font-medium',
            'text-gray-700 hover:text-primary-600 dark:text-gray-400 dark:hover:text-white',
            'transition-colors duration-200',
            isRTL ? 'flex-row-reverse space-x-reverse' : ''
          ]"
        >
          <UIcon 
            name="i-heroicons-home" 
            :class="['w-4 h-4', isRTL ? 'ml-2' : 'mr-2']"
          />
          {{ t('breadcrumb.home') }}
        </NuxtLink>
      </li>
      
      <li 
        v-for="(crumb, index) in breadcrumbs" 
        :key="index"
        class="inline-flex items-center"
      >
        <UIcon 
          name="i-heroicons-chevron-right" 
          :class="[
            'w-5 h-5 text-gray-400',
            isRTL ? 'ml-1 rotate-180' : 'mx-1'
          ]"
        />
        
        <NuxtLink 
          v-if="crumb.path && index < breadcrumbs.length - 1"
          :to="crumb.path"
          :class="[
            'text-sm font-medium',
            'text-gray-700 hover:text-primary-600 dark:text-gray-400 dark:hover:text-white',
            'transition-colors duration-200'
          ]"
        >
          {{ crumb.label }}
        </NuxtLink>
        
        <span 
          v-else
          class="text-sm font-medium text-gray-500 dark:text-gray-500"
        >
          {{ crumb.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
interface Breadcrumb {
  label: string
  path?: string
}

const route = useRoute()
const { t } = useI18n()
const { isRTL } = useLanguage()

// Generate breadcrumbs based on route
const breadcrumbs = computed<Breadcrumb[]>(() => {
  const pathArray = route.path.split('/').filter(p => p)
  const crumbs: Breadcrumb[] = []
  
  // Skip if we're on home page
  if (pathArray.length === 0) {
    return []
  }
  
  // Build breadcrumbs from path
  let currentPath = ''
  pathArray.forEach((segment, index) => {
    currentPath += `/${segment}`
    
    // Try to get translation key for the segment
    const translationKey = `breadcrumb.${segment}`
    const label = t(translationKey)
    
    // If translation not found, use the segment with capitalization
    const displayLabel = label !== translationKey 
      ? label 
      : segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ')
    
    crumbs.push({
      label: displayLabel,
      path: index < pathArray.length - 1 ? currentPath : undefined
    })
  })
  
  return crumbs
})
</script>

<style scoped>
/* RTL specific spacing adjustments */
.rtl-space-x-2 > :not([hidden]) ~ :not([hidden]) {
  margin-right: 0.5rem;
  margin-left: 0;
}
</style>
