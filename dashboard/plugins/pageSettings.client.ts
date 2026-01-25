import { usePageSettingsStore } from '~/stores/pageSettings'

export default defineNuxtPlugin((nuxtApp) => {
  const settingsStore = usePageSettingsStore()

  // Load settings from localStorage on app initialization
  settingsStore.loadSettings()

  // Apply settings to ensure theme and language are synced
  if (process.client) {
    // Wait for next tick to ensure composables are available
    nuxtApp.hook('app:mounted', () => {
      const colorMode = useColorMode()
      const { setLocale } = useI18n()

      // Sync theme with stored settings
      if (settingsStore.app.theme) {
        colorMode.preference = settingsStore.app.theme
      }

      // Sync language with stored settings
      if (settingsStore.app.language) {
        setLocale(settingsStore.app.language)
      }

      // Apply appearance settings
      settingsStore.applyAppearanceSettings()
    })
  }
})
