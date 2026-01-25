import { ref, computed } from 'vue'

/**
 * Browser Notifications Composable
 * 
 * Handles native browser notifications using the Notification API
 * Integrates with the existing notification system
 */

// Reactive state
const permission = ref<NotificationPermission>('default')
const isSupported = ref(false)
const isEnabled = ref(false)

// Check if browser supports notifications
if (typeof window !== 'undefined') {
  isSupported.value = 'Notification' in window
  if (isSupported.value) {
    permission.value = Notification.permission
    // Load user preference from localStorage
    isEnabled.value = localStorage.getItem('browserNotificationsEnabled') === 'true'
  }
}

// Computed properties
const canRequestPermission = computed(() => 
  isSupported.value && permission.value === 'default'
)

const hasPermission = computed(() => 
  isSupported.value && permission.value === 'granted'
)

const shouldShowNotifications = computed(() => 
  hasPermission.value && isEnabled.value
)

/**
 * Request permission for browser notifications
 */
async function requestPermission(): Promise<boolean> {
  if (!isSupported.value) {
    console.warn('Browser notifications are not supported')
    return false
  }

  if (permission.value === 'granted') {
    return true
  }

  try {
    const result = await Notification.requestPermission()
    permission.value = result
    return result === 'granted'
  } catch (error) {
    console.error('Failed to request notification permission:', error)
    return false
  }
}

/**
 * Show a native browser notification
 */
function showBrowserNotification(options: {
  title: string
  message: string
  type?: 'info' | 'success' | 'warning' | 'error'
  icon?: string
  tag?: string
  requireInteraction?: boolean
  onClick?: () => void
}) {
  if (!shouldShowNotifications.value) {
    return null
  }

  const {
    title,
    message,
    type = 'info',
    icon,
    tag,
    requireInteraction = false,
    onClick
  } = options

  // Validate and sanitize inputs
  const validTitle = title && title.trim() ? title.trim() : 'SaaS App Notification'
  const validMessage = message && message.trim() ? message.trim() : 'You have a new notification'
  const validType = ['info', 'success', 'warning', 'error'].includes(type) ? type : 'info'

  // Default icons based on notification type - all use favicon for consistency
  const defaultIcons = {
    info: '/favicon.ico',
    success: '/favicon.ico',
    warning: '/favicon.ico',
    error: '/favicon.ico'
  }

  try {
    const notification = new Notification(validTitle, {
      body: validMessage,
      icon: icon || defaultIcons[validType] || '/favicon.ico',
      tag: tag || `notification-${Date.now()}`,
      requireInteraction,
      badge: '/favicon.ico'
    })

    // Handle click events
    if (onClick) {
      notification.onclick = () => {
        onClick()
        notification.close()
        window.focus() // Bring the app to focus
      }
    } else {
      // Default behavior: focus the app
      notification.onclick = () => {
        window.focus()
        notification.close()
      }
    }

    // Auto-close after 5 seconds unless requireInteraction is true
    if (!requireInteraction) {
      setTimeout(() => {
        notification.close()
      }, 5000)
    }

    return notification
  } catch (error) {
    console.error('Failed to show browser notification:', error)
    return null
  }
}

/**
 * Enable/disable browser notifications
 */
function setEnabled(enabled: boolean) {
  isEnabled.value = enabled
  localStorage.setItem('browserNotificationsEnabled', enabled.toString())
}

/**
 * Show notification for app-specific events
 */
function notifyAppEvent(options: {
  appName: string
  message: string
  type?: 'info' | 'success' | 'warning' | 'error'
  onClick?: () => void
}) {
  const { appName, message, type = 'info', onClick } = options
  
  // Validate and sanitize inputs
  const validAppName = appName && appName.trim() ? appName.trim() : 'SaaS App'
  const validType = ['info', 'success', 'warning', 'error'].includes(type) ? type : 'info'
  
  const titles = {
    info: `📢 ${validAppName}`,
    success: `✅ ${validAppName}`,
    warning: `⚠️ ${validAppName}`,
    error: `❌ ${validAppName}`
  }

  return showBrowserNotification({
    title: titles[validType],
    message,
    type: validType,
    tag: `app-${validAppName}-${validType}`,
    onClick
  })
}

/**
 * Show notification for system events
 */
function notifySystemEvent(options: {
  message: string
  type?: 'info' | 'success' | 'warning' | 'error'
  onClick?: () => void
}) {
  const { message, type = 'info', onClick } = options
  
  // Validate and sanitize type
  const validType = ['info', 'success', 'warning', 'error'].includes(type) ? type : 'info'
  
  const titles = {
    info: '📢 SaaS App',
    success: '✅ SaaS App',
    warning: '⚠️ SaaS App',
    error: '❌ SaaS App'
  }

  return showBrowserNotification({
    title: titles[validType],
    message,
    type: validType,
    tag: `system-${validType}`,
    onClick
  })
}

/**
 * Test browser notifications
 */
function testNotification() {
  return showBrowserNotification({
    title: '🧪 Test Notification',
    message: 'Browser notifications are working correctly!',
    type: 'success',
    icon: '/favicon.ico',
    requireInteraction: false
  })
}

export function useBrowserNotifications() {
  return {
    // State
    permission: computed(() => permission.value),
    isSupported: computed(() => isSupported.value),
    isEnabled: computed(() => isEnabled.value),
    canRequestPermission,
    hasPermission,
    shouldShowNotifications,
    
    // Actions
    requestPermission,
    setEnabled,
    showBrowserNotification,
    notifyAppEvent,
    notifySystemEvent,
    testNotification
  }
}
