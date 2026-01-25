/**
 * Theme management composable
 * Handles light/dark theme switching with system preference detection
 */
export const useTheme = () => {
  const colorMode = useColorMode()
  const settingsStore = usePageSettingsStore()

  // Available theme options
  const themes = [
    { value: 'light', label: 'Light', icon: 'i-heroicons-sun' },
    { value: 'dark', label: 'Dark', icon: 'i-heroicons-moon' },
    { value: 'system', label: 'System', icon: 'i-heroicons-computer-desktop' }
  ]

  // Current theme (user's preference, not computed value)
  const currentTheme = computed(() => colorMode.preference)

  // Is dark mode active
  const isDark = computed(() => colorMode.value === 'dark')

  // Set theme and persist to store
  const setTheme = (theme: string) => {
    colorMode.preference = theme
    // Persist to pageSettings store
    settingsStore.updateAppearance({ theme: theme as 'light' | 'dark' | 'system' })
  }

  // Toggle between light and dark (skip system)
  const toggleTheme = () => {
    if (colorMode.value === 'light') {
      setTheme('dark')
    } else {
      setTheme('light')
    }
  }

  // Get current theme info
  const currentThemeInfo = computed(() => {
    return themes.find(theme => theme.value === colorMode.preference) || themes[0]
  })

  return {
    themes,
    currentTheme,
    isDark,
    setTheme,
    toggleTheme,
    currentThemeInfo
  }
}
