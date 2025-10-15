import { defineStore } from 'pinia'

// Tenant Services Page Settings
export interface TenantServicesSettings {
  filters: {
    search: string
    category: string
    is_active: string
    is_approved: string
  }
  groupBy: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
  currentPage: number
}

// Tenants Page Settings
export interface TenantsSettings {
  searchQuery: string
  filters: {
    status: string
  }
  sortBy: string
  sortOrder: 'asc' | 'desc'
  viewMode: 'table' | 'grid'
}

// Users Page Settings
export interface UsersSettings {
  searchQuery: string
  filters: {
    status: string
    role: string
  }
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

// Wathq Page Settings
export interface WathqSettings {
  filters: {
    serviceType: string
    status: string
    dateFrom: string
    dateTo: string
  }
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

// Main Settings (from settings page)
export interface AppSettings {
  // Appearance
  theme: 'light' | 'dark' | 'system'
  font: string
  fontSize: number
  accentColor: string
  
  // Language
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
  dashboardAutoRefresh: boolean
  dashboardRefreshInterval: number
}

export interface PageSettingsState {
  tenantServices: TenantServicesSettings
  tenants: TenantsSettings
  users: UsersSettings
  wathq: WathqSettings
  app: AppSettings
}

// Default values
const defaultTenantServicesSettings: TenantServicesSettings = {
  filters: {
    search: '',
    category: 'all',
    is_active: 'all',
    is_approved: 'all'
  },
  groupBy: 'none',
  sortBy: 'registered_at',
  sortOrder: 'desc',
  currentPage: 1
}

const defaultTenantsSettings: TenantsSettings = {
  searchQuery: '',
  filters: {
    status: 'all'
  },
  sortBy: 'created_at',
  sortOrder: 'desc',
  viewMode: 'table'
}

const defaultUsersSettings: UsersSettings = {
  searchQuery: '',
  filters: {
    status: 'all',
    role: 'all'
  },
  sortBy: 'created_at',
  sortOrder: 'desc'
}

const defaultWathqSettings: WathqSettings = {
  filters: {
    serviceType: 'all',
    status: 'all',
    dateFrom: '',
    dateTo: ''
  },
  sortBy: 'created_at',
  sortOrder: 'desc'
}

const defaultAppSettings: AppSettings = {
  theme: 'system',
  font: 'Inter',
  fontSize: 16,
  accentColor: 'blue',
  language: 'en',
  dateFormat: 'MM/DD/YYYY',
  timeFormat: '12',
  emailNotifications: {
    deployments: true,
    security: true,
    updates: true,
    marketing: false
  },
  soundEnabled: true,
  soundVolume: 50,
  analyticsEnabled: true,
  rememberMeEnabled: true,
  animationsEnabled: true,
  dashboardAutoRefresh: false,
  dashboardRefreshInterval: 60
}

export const usePageSettingsStore = defineStore('pageSettings', {
  state: (): PageSettingsState => ({
    tenantServices: { ...defaultTenantServicesSettings },
    tenants: { ...defaultTenantsSettings },
    users: { ...defaultUsersSettings },
    wathq: { ...defaultWathqSettings },
    app: { ...defaultAppSettings }
  }),

  getters: {
    getTenantServicesSettings: (state) => state.tenantServices,
    getTenantsSettings: (state) => state.tenants,
    getUsersSettings: (state) => state.users,
    getWathqSettings: (state) => state.wathq,
    getAppSettings: (state) => state.app
  },

  actions: {
    // Tenant Services Actions
    updateTenantServicesFilters(filters: Partial<TenantServicesSettings['filters']>) {
      this.tenantServices.filters = { ...this.tenantServices.filters, ...filters }
      this.persistSettings()
    },

    updateTenantServicesGroupBy(groupBy: string) {
      this.tenantServices.groupBy = groupBy
      this.persistSettings()
    },

    updateTenantServicesSorting(sortBy: string, sortOrder?: 'asc' | 'desc') {
      this.tenantServices.sortBy = sortBy
      if (sortOrder) {
        this.tenantServices.sortOrder = sortOrder
      }
      this.persistSettings()
    },

    updateTenantServicesPage(page: number) {
      this.tenantServices.currentPage = page
      this.persistSettings()
    },

    resetTenantServicesSettings() {
      this.tenantServices = { ...defaultTenantServicesSettings }
      this.persistSettings()
    },

    // Tenants Actions
    updateTenantsSearch(search: string) {
      this.tenants.searchQuery = search
      this.persistSettings()
    },

    updateTenantsFilters(filters: Partial<TenantsSettings['filters']>) {
      this.tenants.filters = { ...this.tenants.filters, ...filters }
      this.persistSettings()
    },

    updateTenantsSorting(sortBy: string, sortOrder?: 'asc' | 'desc') {
      this.tenants.sortBy = sortBy
      if (sortOrder) {
        this.tenants.sortOrder = sortOrder
      }
      this.persistSettings()
    },

    updateTenantsViewMode(viewMode: 'table' | 'grid') {
      this.tenants.viewMode = viewMode
      this.persistSettings()
    },

    resetTenantsSettings() {
      this.tenants = { ...defaultTenantsSettings }
      this.persistSettings()
    },

    // Users Actions
    updateUsersSearch(search: string) {
      this.users.searchQuery = search
      this.persistSettings()
    },

    updateUsersFilters(filters: Partial<UsersSettings['filters']>) {
      this.users.filters = { ...this.users.filters, ...filters }
      this.persistSettings()
    },

    updateUsersSorting(sortBy: string, sortOrder?: 'asc' | 'desc') {
      this.users.sortBy = sortBy
      if (sortOrder) {
        this.users.sortOrder = sortOrder
      }
      this.persistSettings()
    },

    resetUsersSettings() {
      this.users = { ...defaultUsersSettings }
      this.persistSettings()
    },

    // Wathq Actions
    updateWathqFilters(filters: Partial<WathqSettings['filters']>) {
      this.wathq.filters = { ...this.wathq.filters, ...filters }
      this.persistSettings()
    },

    updateWathqSorting(sortBy: string, sortOrder?: 'asc' | 'desc') {
      this.wathq.sortBy = sortBy
      if (sortOrder) {
        this.wathq.sortOrder = sortOrder
      }
      this.persistSettings()
    },

    resetWathqSettings() {
      this.wathq = { ...defaultWathqSettings }
      this.persistSettings()
    },

    // App Settings Actions
    updateAppearance(settings: Partial<Pick<AppSettings, 'theme' | 'font' | 'fontSize' | 'accentColor'>>) {
      this.app = { ...this.app, ...settings }
      this.persistSettings()
      this.applyAppearanceSettings()
    },

    updateLanguage(settings: Partial<Pick<AppSettings, 'language' | 'dateFormat' | 'timeFormat'>>) {
      this.app = { ...this.app, ...settings }
      this.persistSettings()
    },

    updateNotifications(settings: Partial<Pick<AppSettings, 'emailNotifications' | 'soundEnabled' | 'soundVolume'>>) {
      this.app = { ...this.app, ...settings }
      this.persistSettings()
    },

    updatePrivacy(settings: Partial<Pick<AppSettings, 'analyticsEnabled' | 'rememberMeEnabled'>>) {
      this.app = { ...this.app, ...settings }
      this.persistSettings()
    },

    updateAdvanced(settings: Partial<Pick<AppSettings, 'animationsEnabled' | 'dashboardAutoRefresh' | 'dashboardRefreshInterval'>>) {
      this.app = { ...this.app, ...settings }
      this.persistSettings()
    },

    resetAppSettings() {
      this.app = { ...defaultAppSettings }
      this.persistSettings()
      this.applyAppearanceSettings()
    },

    // Global Actions
    resetAllSettings() {
      this.tenantServices = { ...defaultTenantServicesSettings }
      this.tenants = { ...defaultTenantsSettings }
      this.users = { ...defaultUsersSettings }
      this.wathq = { ...defaultWathqSettings }
      this.app = { ...defaultAppSettings }
      this.persistSettings()
      this.applyAppearanceSettings()
    },

    // Persistence
    persistSettings() {
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('page-settings', JSON.stringify(this.$state))
        } catch (error) {
          console.error('Failed to persist settings:', error)
        }
      }
    },

    loadSettings() {
      if (typeof window !== 'undefined') {
        try {
          const stored = localStorage.getItem('page-settings')
          if (stored) {
            const parsed = JSON.parse(stored)
            // Merge with defaults to ensure all properties exist
            this.tenantServices = { ...defaultTenantServicesSettings, ...parsed.tenantServices }
            this.tenants = { ...defaultTenantsSettings, ...parsed.tenants }
            this.users = { ...defaultUsersSettings, ...parsed.users }
            this.wathq = { ...defaultWathqSettings, ...parsed.wathq }
            this.app = { ...defaultAppSettings, ...parsed.app }
            
            // Apply appearance settings
            this.applyAppearanceSettings()
          }
        } catch (error) {
          console.error('Failed to load settings:', error)
        }
      }
    },

    // Apply appearance settings to DOM
    applyAppearanceSettings() {
      if (typeof window !== 'undefined') {
        const root = document.documentElement

        // Apply theme
        if (this.app.theme === 'dark') {
          root.classList.add('dark')
        } else if (this.app.theme === 'light') {
          root.classList.remove('dark')
        } else {
          // System preference
          if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            root.classList.add('dark')
          } else {
            root.classList.remove('dark')
          }
        }

        // Apply font
        root.style.fontFamily = this.app.font

        // Apply font size
        root.style.fontSize = `${this.app.fontSize}px`

        // Apply animations
        if (!this.app.animationsEnabled) {
          root.style.setProperty('--animation-duration', '0s')
        } else {
          root.style.removeProperty('--animation-duration')
        }
      }
    }
  }
})
