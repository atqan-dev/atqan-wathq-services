<template>
  <UDropdown :items="themeItems" :popper="{ placement: isRTL ? 'bottom-start' : 'bottom-end' }">
    <UButton
      :icon="currentThemeInfo.icon"
      variant="ghost"
      color="gray"
      size="sm"
      :aria-label="t('theme.switchTheme')"
      class="transition-colors duration-200"
    />
    
    <template #item="{ item }">
      <div class="flex items-center gap-2 w-full" :class="isRTL ? 'dropdown-item-rtl' : ''">
        <UIcon :name="item.icon" class="w-4 h-4" />
        <span>{{ item.label }}</span>
        <UIcon 
          v-if="item.value === currentTheme" 
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
const { themes, currentTheme, setTheme, currentThemeInfo } = useTheme()

// Dropdown items - UDropdown expects array of arrays for grouping
const themeItems = computed(() => [[
  ...themes.map(theme => ({
    value: theme.value,
    label: t(`theme.${theme.value}`),
    icon: theme.icon,
    click: () => setTheme(theme.value)
  }))
]])
</script>
