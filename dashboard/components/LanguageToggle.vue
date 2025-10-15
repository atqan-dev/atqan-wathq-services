<template>
  <UDropdown :items="languageItems" :popper="{ placement: isRTL ? 'bottom-start' : 'bottom-end' }">
    <UButton
      variant="ghost"
      color="gray"
      size="sm"
      :aria-label="t('language.switchLanguage')"
      class="transition-colors duration-200"
    >
      <span class="text-lg">{{ currentLanguage.flag }}</span>
    </UButton>
    
    <template #item="{ item }">
      <div class="flex items-center gap-3 w-full" :class="isRTL ? 'dropdown-item-rtl' : ''">
        <span class="text-lg">{{ item.flag }}</span>
        <div class="flex flex-col" :class="isRTL ? 'rtl-text-right' : ''">
          <span class="font-medium">{{ item.name }}</span>
          <span class="text-xs text-gray-500 dark:text-gray-400">{{ item.code.toUpperCase() }}</span>
        </div>
        <UIcon 
          v-if="item.code === currentLanguage.code" 
          name="i-heroicons-check" 
          :class="isRTL ? 'w-4 h-4 mr-auto text-primary-500' : 'w-4 h-4 ml-auto text-primary-500'"
        />
      </div>
    </template>
  </UDropdown>
</template>

<script setup>
const { t } = useI18n()
const { isRTL } = useLanguage()
const { languages, currentLanguage, switchLanguage } = useLanguage()

// Dropdown items
const languageItems = computed(() => [
  languages.value.map(lang => ({
    ...lang,
    click: () => switchLanguage(lang.code)
  }))
])
</script>
