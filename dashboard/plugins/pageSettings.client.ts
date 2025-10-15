import { usePageSettingsStore } from '~/stores/pageSettings'

export default defineNuxtPlugin(() => {
  const settingsStore = usePageSettingsStore()
  
  // Load settings from localStorage on app initialization
  settingsStore.loadSettings()
})
