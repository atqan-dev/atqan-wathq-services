import { computed } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useNotifications } from '@/composables/useNotifications'
import { usePageSettingsStore } from '@/stores/pageSettings'

export interface UserSettings {
  // Appearance
  theme: 'light' | 'dark' | 'system'
  font: string
  fontSize: number
  accentColor: string
  
  // Language & Region
  language: string
  dateFormat: string
  timeFormat: '12' | '24'
  
  // Notifications
  emailNotifications: {
    deployments: boolean
    security: boolean
    updates: boolean
    marketing: boolean
  }
  soundEnabled: boolean
  soundVolume: number
  
  // Privacy
  analyticsEnabled: boolean
  rememberMeEnabled: boolean
  
  // Advanced
  animationsEnabled: boolean
  
  // Dashboard
  dashboardAutoRefresh: boolean
  dashboardRefreshInterval: number // in seconds
}

const defaultSettings: UserSettings = {
  theme: 'system',
  font: 'Inter',
  fontSize: 14,
  accentColor: 'blue',
  language: 'en',
  dateFormat: 'MM/DD/YYYY',
  timeFormat: '12',
  emailNotifications: {
    deployments: true,
    security: true,
    updates: false,
    marketing: false
  },
  soundEnabled: true,
  soundVolume: 50,
  analyticsEnabled: true,
  rememberMeEnabled: true,
  animationsEnabled: true,
  dashboardAutoRefresh: false,
  dashboardRefreshInterval: 30 // 30 seconds default
}

export function useSettings() {
  const { setLocale } = useI18n()
  const notify = useNotifications()
  const settingsStore = usePageSettingsStore()
  
  // Get settings from store
  const settings = computed(() => settingsStore.app)
  
  // Save settings (handled by store automatically)
  function saveSettings() {
    notify.success('Settings saved successfully')
  }
  
  // Load settings
  function loadSettings() {
    settingsStore.loadSettings()
  }
  
  // Apply theme
  function applyTheme(theme: string) {
    const html = document.documentElement
    const body = document.body
    
    // Remove existing theme classes
    html.classList.remove('dark', 'light')
    body.classList.remove('dark', 'light')
    
    if (theme === 'dark') {
      html.classList.add('dark')
      body.classList.add('dark')
    } else if (theme === 'light') {
      html.classList.add('light')
      body.classList.add('light')
    } else {
      // System theme
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        html.classList.add('dark')
        body.classList.add('dark')
      } else {
        html.classList.add('light')
        body.classList.add('light')
      }
    }
    
    // Force a repaint to ensure theme changes are applied immediately
    html.style.display = 'none'
    html.offsetHeight // Trigger reflow
    html.style.display = ''
  }
  
  // Apply font settings
  function applyFont(font: string, fontSize: number) {
    document.documentElement.style.setProperty('--font-family', `'${font}', system-ui, -apple-system, sans-serif`)
    document.documentElement.style.setProperty('--font-size', `${fontSize}px`)
    
    // Also apply directly to body for immediate effect
    document.body.style.fontFamily = `'${font}', system-ui, -apple-system, sans-serif`
    document.body.style.fontSize = `${fontSize}px`
  }
  
  // Apply accent color
  function applyAccentColor(color: string) {
    const colorMap: Record<string, string> = {
      blue: '#3B82F6',
      purple: '#8B5CF6',
      green: '#10B981',
      red: '#EF4444',
      yellow: '#F59E0B',
      pink: '#EC4899'
    }
    
    const colorValue = colorMap[color] || colorMap.blue
    document.documentElement.style.setProperty('--accent-color', colorValue)
    
    // Apply to common Tailwind classes immediately
    const style = document.createElement('style')
    style.id = 'dynamic-accent-colors'
    
    // Remove existing dynamic styles
    const existing = document.getElementById('dynamic-accent-colors')
    if (existing) {
      existing.remove()
    }
    
    style.textContent = `
      .bg-blue-600, .bg-blue-500, .hover\\:bg-blue-700 { background-color: ${colorValue} !important; }
      .text-blue-600, .text-blue-500 { color: ${colorValue} !important; }
      .border-blue-500, .border-blue-600 { border-color: ${colorValue} !important; }
      .ring-blue-500 { --tw-ring-color: ${colorValue} !important; }
      input[type="checkbox"]:checked, input[type="radio"]:checked { background-color: ${colorValue} !important; }
      .btn-primary { background-color: ${colorValue} !important; border-color: ${colorValue} !important; }
    `
    
    document.head.appendChild(style)
  }
  
  // Apply animations setting
  function applyAnimations(enabled: boolean) {
    if (enabled) {
      document.documentElement.classList.remove('reduce-motion')
    } else {
      document.documentElement.classList.add('reduce-motion')
    }
  }
  
  // Setting update functions
  function updateTheme(theme: 'light' | 'dark' | 'system') {
    settingsStore.updateAppearance({ theme })
    applyTheme(theme)
    saveSettings()
  }
  
  function updateFont(font: string) {
    settingsStore.updateAppearance({ font })
    applyFont(font, settings.value.fontSize)
    saveSettings()
  }
  
  function updateFontSize(size: number) {
    settingsStore.updateAppearance({ fontSize: size })
    applyFont(settings.value.font, size)
    saveSettings()
  }
  
  function updateAccentColor(color: string) {
    settingsStore.updateAppearance({ accentColor: color })
    applyAccentColor(color)
    saveSettings()
  }
  
  function updateLanguage(language: string) {
    settingsStore.updateLanguage({ language })
    setLocale(language)
    saveSettings()
  }
  
  function updateDateFormat(format: string) {
    settingsStore.updateLanguage({ dateFormat: format })
    saveSettings()
  }
  
  function updateTimeFormat(format: '12' | '24') {
    settingsStore.updateLanguage({ timeFormat: format })
    saveSettings()
  }
  
  function updateEmailNotifications(notifications: Partial<UserSettings['emailNotifications']>) {
    const merged = { ...settings.value.emailNotifications, ...notifications }
    settingsStore.updateNotifications({ emailNotifications: merged })
    saveSettings()
  }
  
  function updateSoundSettings(enabled: boolean, volume?: number) {
    settingsStore.updateNotifications({ 
      soundEnabled: enabled,
      ...(volume !== undefined && { soundVolume: volume })
    })
    saveSettings()
  }
  
  function updatePrivacySettings(analytics: boolean, rememberMe: boolean) {
    settingsStore.updatePrivacy({ 
      analyticsEnabled: analytics,
      rememberMeEnabled: rememberMe
    })
    saveSettings()
  }
  
  function updateAnimations(enabled: boolean) {
    settingsStore.updateAdvanced({ animationsEnabled: enabled })
    applyAnimations(enabled)
    saveSettings()
  }
  
  function updateDashboardRefresh(enabled: boolean, interval?: number) {
    settingsStore.updateAdvanced({
      dashboardAutoRefresh: enabled,
      ...(interval !== undefined && { dashboardRefreshInterval: interval })
    })
    console.log(`[Settings] Dashboard auto-refresh updated - Enabled: ${enabled}, Interval: ${interval || settings.value.dashboardRefreshInterval}s`)
    saveSettings()
  }
  
  // Reset all settings
  function resetSettings() {
    settingsStore.resetAppSettings()
    
    // Apply all settings
    applyTheme(settings.value.theme)
    applyFont(settings.value.font, settings.value.fontSize)
    applyAccentColor(settings.value.accentColor)
    applyAnimations(settings.value.animationsEnabled)
    setLocale(settings.value.language)
    
    notify.success('Settings reset to defaults')
  }
  
  // Initialize settings
  function initializeSettings() {
    loadSettings()
    
    // Ensure DOM is ready before applying settings
    if (typeof window !== 'undefined') {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          applyAllSettings()
        })
      } else {
        applyAllSettings()
      }
    }
  }
  
  // Apply all settings
  function applyAllSettings() {
    applyTheme(settings.value.theme)
    applyFont(settings.value.font, settings.value.fontSize)
    applyAccentColor(settings.value.accentColor)
    applyAnimations(settings.value.animationsEnabled)
    setLocale(settings.value.language)
  }
  
  // Watch for system theme changes
  if (typeof window !== 'undefined') {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', () => {
      if (settings.value.theme === 'system') {
        applyTheme('system')
      }
    })
    
    // Listen for storage changes from other tabs/windows
    window.addEventListener('storage', (e) => {
      if (e.key === 'page-settings' && e.newValue) {
        settingsStore.loadSettings()
      }
    })
  }
  
  // Computed properties for easy access
  const currentTheme = computed(() => settings.value.theme)
  const currentFont = computed(() => settings.value.font)
  const currentFontSize = computed(() => settings.value.fontSize)
  const currentAccentColor = computed(() => settings.value.accentColor)
  const currentLanguage = computed(() => settings.value.language)
  const currentDateFormat = computed(() => settings.value.dateFormat)
  const currentTimeFormat = computed(() => settings.value.timeFormat)
  const emailNotifications = computed(() => settings.value.emailNotifications)
  const soundEnabled = computed(() => settings.value.soundEnabled)
  const soundVolume = computed(() => settings.value.soundVolume)
  const analyticsEnabled = computed(() => settings.value.analyticsEnabled)
  const rememberMeEnabled = computed(() => settings.value.rememberMeEnabled)
  const animationsEnabled = computed(() => settings.value.animationsEnabled)
  const dashboardAutoRefresh = computed(() => settings.value.dashboardAutoRefresh)
  const dashboardRefreshInterval = computed(() => settings.value.dashboardRefreshInterval)
  
  return {
    // State
    settings: computed(() => settings.value),
    
    // Computed properties
    currentTheme,
    currentFont,
    currentFontSize,
    currentAccentColor,
    currentLanguage,
    currentDateFormat,
    currentTimeFormat,
    emailNotifications,
    soundEnabled,
    soundVolume,
    analyticsEnabled,
    rememberMeEnabled,
    animationsEnabled,
    dashboardAutoRefresh,
    dashboardRefreshInterval,
    
    // Methods
    initializeSettings,
    updateTheme,
    updateFont,
    updateFontSize,
    updateAccentColor,
    updateLanguage,
    updateDateFormat,
    updateTimeFormat,
    updateEmailNotifications,
    updateSoundSettings,
    updatePrivacySettings,
    updateAnimations,
    updateDashboardRefresh,
    resetSettings,
    
    // Utilities
    loadSettings,
    saveSettings
  }
}
