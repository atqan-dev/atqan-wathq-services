<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ t('settings.title') }}</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">{{ t('settings.subtitle') }}</p>
      </div>

      <!-- Settings Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Settings Navigation -->
        <div class="lg:col-span-1">
          <nav class="space-y-1">
            <button v-for="section in settingSections" :key="section.id" @click="activeSection = section.id" :class="[
              'w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors',
              activeSection === section.id
                ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-l-4 border-blue-500'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            ]">
              <span class="w-5 h-5 mr-3">{{ section.icon }}</span>
              <span class="font-medium">{{ t(section.title) }}</span>
            </button>
          </nav>
        </div>

        <!-- Settings Content -->
        <div class="lg:col-span-2">
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <!-- Appearance Settings -->
            <div v-if="activeSection === 'appearance'" class="p-6">
              <div class="flex items-center mb-6">
                <span class="w-6 h-6 mr-3">🎨</span>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('settings.appearance.title') }}
                </h2>
              </div>

              <div class="space-y-6">
                <!-- Theme Selection -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.appearance.theme') }}
                  </label>
                  <div class="grid grid-cols-3 gap-3">
                    <button v-for="theme in themes" :key="theme.value" @click="setTheme(theme.value)" :class="[
                      'p-4 rounded-lg border-2 transition-all',
                      currentTheme === theme.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    ]">
                      <span class="block text-2xl mb-2">{{ theme.icon }}</span>
                      <div class="text-sm font-medium text-gray-900 dark:text-white">{{ t(theme.label) }}</div>
                    </button>
                  </div>
                </div>

                <!-- Font Selection -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.appearance.font') }}
                  </label>
                  <select :value="currentFont" @change="setFont(($event.target as HTMLSelectElement).value)"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option v-for="font in fonts" :key="font.value" :value="font.value">
                      {{ font.label }}
                    </option>
                  </select>
                  <div class="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p :style="{ fontFamily: currentFont }" class="text-gray-900 dark:text-white">
                      {{ t('settings.appearance.fontPreview') }}
                    </p>
                  </div>
                </div>

                <!-- Font Size -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.appearance.fontSize') }}
                  </label>
                  <div class="flex items-center space-x-4">
                    <input :value="currentFontSize"
                      @input="setFontSize(Number(($event.target as HTMLInputElement).value))" type="range" min="12"
                      max="20" step="1"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
                    <span class="text-sm font-medium text-gray-900 dark:text-white w-12">{{ currentFontSize }}px</span>
                  </div>
                </div>

                <!-- Color Accent -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.appearance.accentColor') }}
                  </label>
                  <div class="grid grid-cols-6 gap-2">
                    <button v-for="color in accentColors" :key="color.value" @click="setAccentColor(color.value)"
                      :class="[
                        'w-10 h-10 rounded-lg border-2 transition-all',
                        currentAccentColor === color.value
                          ? 'border-gray-400 scale-110'
                          : 'border-gray-200 hover:scale-105'
                      ]" :style="{ backgroundColor: color.color }" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Language Settings -->
            <div v-if="activeSection === 'language'" class="p-6">
              <div class="flex items-center mb-6">
                <span class="w-6 h-6 mr-3">🌍</span>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('settings.language.title') }}</h2>
              </div>

              <div class="space-y-6">
                <!-- Language Selection -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.language.select') }}
                  </label>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button v-for="lang in languages" :key="lang.code" @click="setLanguage(lang.code)" :class="[
                      'p-4 rounded-lg border-2 transition-all text-left',
                      currentLanguage === lang.code
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    ]">
                      <div class="flex items-center">
                        <span class="text-2xl mr-3">{{ lang.flag }}</span>
                        <div>
                          <div class="font-medium text-gray-900 dark:text-white">{{ lang.name }}</div>
                          <div class="text-sm text-gray-500 dark:text-gray-400">{{ lang.nativeName }}</div>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>

                <!-- Date Format -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.language.dateFormat') }}
                  </label>
                  <select :value="currentDateFormat" @change="setDateFormat(($event.target as HTMLSelectElement).value)"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option v-for="format in dateFormats" :key="format.value" :value="format.value">
                      {{ format.label }} ({{ format.example }})
                    </option>
                  </select>
                </div>

                <!-- Time Format -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    {{ t('settings.language.timeFormat') }}
                  </label>
                  <div class="flex space-x-4">
                    <label class="flex items-center">
                      <input :checked="currentTimeFormat === '12'" @change="setTimeFormat('12')" type="radio"
                        name="timeFormat" class="mr-2 text-blue-600 focus:ring-blue-500">
                      <span class="text-gray-900 dark:text-white">12-hour (2:30 PM)</span>
                    </label>
                    <label class="flex items-center">
                      <input :checked="currentTimeFormat === '24'" @change="setTimeFormat('24')" type="radio"
                        name="timeFormat" class="mr-2 text-blue-600 focus:ring-blue-500">
                      <span class="text-gray-900 dark:text-white">24-hour (14:30)</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Notifications Settings -->
            <div v-if="activeSection === 'notifications'" class="p-6">
              <div class="flex items-center mb-6">
                <span class="w-6 h-6 mr-3">🔔</span>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('settings.notifications.title') }}
                </h2>
              </div>

              <div class="space-y-6">
                <!-- Browser Notifications -->
                <BrowserNotificationSettings />

                <!-- Email Notifications -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.notifications.email.title') }}
                  </h3>
                  <div class="space-y-3">
                    <label v-for="option in emailNotificationOptions" :key="option.key" class="flex items-center">
                      <input :checked="emailNotifications[option.key as keyof typeof emailNotifications]"
                        @change="handleEmailNotificationChange(option.key, $event)" type="checkbox"
                        class="mr-3 text-blue-600 focus:ring-blue-500 rounded">
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">{{ t(option.title) }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">{{ t(option.description) }}</div>
                      </div>
                    </label>
                  </div>
                </div>

                <!-- Sound Settings -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.notifications.sound.title') }}
                  </h3>
                  <div class="space-y-4">
                    <label class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-900 dark:text-white">
                        {{ t('settings.notifications.sound.enable') }}
                      </span>
                      <input :checked="soundEnabled"
                        @change="setSoundEnabled(($event.target as HTMLInputElement).checked)" type="checkbox"
                        class="text-blue-600 focus:ring-blue-500 rounded">
                    </label>
                    <div v-if="soundEnabled">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {{ t('settings.notifications.sound.volume') }}
                      </label>
                      <div class="flex items-center space-x-4">
                        <input :value="soundVolume"
                          @input="setSoundVolume(Number(($event.target as HTMLInputElement).value))" type="range"
                          min="0" max="100" step="5"
                          class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                        <span class="text-sm font-medium text-gray-900 dark:text-white w-12">{{ soundVolume }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Privacy Settings -->
            <div v-if="activeSection === 'privacy'" class="p-6">
              <div class="flex items-center mb-6">
                <span class="w-6 h-6 mr-3">🛡️</span>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('settings.privacy.title') }}</h2>
              </div>

              <div class="space-y-6">
                <!-- Data Collection -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.privacy.dataCollection.title') }}
                  </h3>
                  <div class="space-y-3">
                    <label class="flex items-center justify-between">
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ t('settings.privacy.dataCollection.analytics') }}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {{ t('settings.privacy.dataCollection.analyticsDesc') }}
                        </div>
                      </div>
                      <input :checked="analyticsEnabled"
                        @change="setAnalyticsEnabled(($event.target as HTMLInputElement).checked)" type="checkbox"
                        class="text-blue-600 focus:ring-blue-500 rounded">
                    </label>
                  </div>
                </div>

                <!-- Session Management -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.privacy.session.title') }}
                  </h3>
                  <div class="space-y-3">
                    <label class="flex items-center justify-between">
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ t('settings.privacy.session.rememberMe') }}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {{ t('settings.privacy.session.rememberMeDesc') }}
                        </div>
                      </div>
                      <input :checked="rememberMeEnabled"
                        @change="setRememberMeEnabled(($event.target as HTMLInputElement).checked)" type="checkbox"
                        class="text-blue-600 focus:ring-blue-500 rounded">
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Advanced Settings -->
            <div v-if="activeSection === 'advanced'" class="p-6">
              <div class="flex items-center mb-6">
                <span class="w-6 h-6 mr-3">⚙️</span>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t('settings.advanced.title') }}</h2>
              </div>

              <div class="space-y-6">
                <!-- Performance -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.advanced.performance.title') }}
                  </h3>
                  <div class="space-y-3">
                    <label class="flex items-center justify-between">
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ t('settings.advanced.performance.animations') }}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {{ t('settings.advanced.performance.animationsDesc') }}
                        </div>
                      </div>
                      <input :checked="animationsEnabled"
                        @change="setAnimationsEnabled(($event.target as HTMLInputElement).checked)" type="checkbox"
                        class="text-blue-600 focus:ring-blue-500 rounded">
                    </label>
                  </div>
                </div>

                <!-- Dashboard Auto-Refresh -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    {{ t('settings.advanced.dashboard.title') }}
                  </h3>
                  <div class="space-y-4">
                    <label class="flex items-center justify-between">
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ t('settings.advanced.dashboard.autoRefresh') }}
                        </div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">
                          {{ t('settings.advanced.dashboard.autoRefreshDesc') }}
                        </div>
                      </div>
                      <input :checked="dashboardAutoRefresh"
                        @change="setDashboardAutoRefresh(($event.target as HTMLInputElement).checked)" type="checkbox"
                        class="text-blue-600 focus:ring-blue-500 rounded">
                    </label>
                    
                    <div v-if="dashboardAutoRefresh">
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {{ t('settings.advanced.dashboard.refreshInterval') }}
                      </label>
                      <div class="flex items-center space-x-4">
                        <input :value="dashboardRefreshInterval"
                          @input="setDashboardRefreshInterval(Number(($event.target as HTMLInputElement).value))"
                          type="range" min="10" max="300" step="10"
                          class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                        <span class="text-sm font-medium text-gray-900 dark:text-white w-16">{{ dashboardRefreshInterval }}s</span>
                      </div>
                      <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        {{ t('settings.advanced.dashboard.refreshIntervalNote') }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Reset Settings -->
                <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
                  <h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-4">
                    {{ t('settings.advanced.reset.title') }}
                  </h3>
                  <p class="text-sm text-red-600 dark:text-red-300 mb-4">
                    {{ t('settings.advanced.reset.description') }}
                  </p>
                  <button @click="resetAllSettings"
                    class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors">
                    {{ t('settings.advanced.reset.button') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useSettings } from '@/composables/useSettings'
import BrowserNotificationSettings from '@/components/BrowserNotificationSettings.vue'

// Apply auth middleware
definePageMeta({
  middleware: ['auth']
})

const { t, locale } = useI18n()
const {
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
  initializeSettings
} = useSettings()

// Active section
const activeSection = ref('appearance')

// Settings sections
const settingSections = [
  { id: 'appearance', title: 'settings.sections.appearance', icon: '🎨' },
  { id: 'language', title: 'settings.sections.language', icon: '🌍' },
  { id: 'notifications', title: 'settings.sections.notifications', icon: '🔔' },
  { id: 'privacy', title: 'settings.sections.privacy', icon: '🛡️' },
  { id: 'advanced', title: 'settings.sections.advanced', icon: '⚙️' }
]

// Theme settings
const themes = [
  { value: 'light', label: 'settings.appearance.themes.light', icon: '☀️' },
  { value: 'dark', label: 'settings.appearance.themes.dark', icon: '🌙' },
  { value: 'system', label: 'settings.appearance.themes.system', icon: '💻' }
]

// Font settings
const fonts = [
  { value: 'Inter', label: 'Inter' },
  { value: 'Roboto', label: 'Roboto' },
  { value: 'Open Sans', label: 'Open Sans' },
  { value: 'Lato', label: 'Lato' },
  { value: 'Poppins', label: 'Poppins' },
  { value: 'Montserrat', label: 'Montserrat' }
]

// Accent colors
const accentColors = [
  { value: 'blue', color: '#3B82F6' },
  { value: 'purple', color: '#8B5CF6' },
  { value: 'green', color: '#10B981' },
  { value: 'red', color: '#EF4444' },
  { value: 'yellow', color: '#F59E0B' },
  { value: 'pink', color: '#EC4899' }
]

// Language settings
const languages = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' }
]

const dateFormats = [
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY', example: '12/31/2023' },
  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY', example: '31/12/2023' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD', example: '2023-12-31' }
]

// Notification settings
const emailNotificationOptions = [
  {
    key: 'deployments',
    title: 'settings.notifications.email.deployments',
    description: 'settings.notifications.email.deploymentsDesc'
  },
  {
    key: 'security',
    title: 'settings.notifications.email.security',
    description: 'settings.notifications.email.securityDesc'
  },
  {
    key: 'updates',
    title: 'settings.notifications.email.updates',
    description: 'settings.notifications.email.updatesDesc'
  },
  {
    key: 'marketing',
    title: 'settings.notifications.email.marketing',
    description: 'settings.notifications.email.marketingDesc'
  }
]

// Methods using the composable
function setTheme(theme: string) {
  updateTheme(theme as 'light' | 'dark' | 'system')
}

function setFont(font: string) {
  updateFont(font)
}

function setFontSize(size: number) {
  updateFontSize(size)
}

function setAccentColor(color: string) {
  updateAccentColor(color)
}

function setLanguage(lang: string) {
  updateLanguage(lang)
}

function setDateFormat(format: string) {
  updateDateFormat(format)
}

function setTimeFormat(format: string) {
  updateTimeFormat(format as '12' | '24')
}

function handleEmailNotificationChange(key: string, event: Event) {
  const target = event.target as HTMLInputElement
  const newNotifications = { ...emailNotifications.value }
  newNotifications[key as keyof typeof newNotifications] = target.checked
  updateEmailNotifications(newNotifications)
}

function setSoundEnabled(enabled: boolean) {
  updateSoundSettings(enabled, soundVolume.value)
}

function setSoundVolume(volume: number) {
  updateSoundSettings(soundEnabled.value, volume)
}

function setAnalyticsEnabled(enabled: boolean) {
  updatePrivacySettings(enabled, rememberMeEnabled.value)
}

function setRememberMeEnabled(enabled: boolean) {
  updatePrivacySettings(analyticsEnabled.value, enabled)
}

function setAnimationsEnabled(enabled: boolean) {
  updateAnimations(enabled)
}

function setDashboardAutoRefresh(enabled: boolean) {
  updateDashboardRefresh(enabled)
}

function setDashboardRefreshInterval(interval: number) {
  updateDashboardRefresh(dashboardAutoRefresh.value, interval)
}

function resetAllSettings() {
  if (confirm(t('settings.advanced.reset.confirm'))) {
    resetSettings()
  }
}

// Initialize settings on mount
onMounted(() => {
  initializeSettings()
})
</script>

<style scoped>
/* Custom styles for better appearance */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
}
</style>
