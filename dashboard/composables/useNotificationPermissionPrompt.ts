import { ref, computed, watch } from 'vue'
import { useBrowserNotifications } from './useBrowserNotifications'
import { useAuthStore } from '~/stores/auth'

/**
 * Composable for managing notification permission prompts
 * Handles when and how to show permission requests to users
 */

const showPrompt = ref(false)
const hasShownThisSession = ref(false)

export function useNotificationPermissionPrompt() {
  const {
    permission,
    isSupported,
    canRequestPermission,
    requestPermission,
    setEnabled,
    showBrowserNotification
  } = useBrowserNotifications()

  const authStore = useAuthStore()

  // Check if we should show the prompt
  const shouldShowPrompt = computed(() => {
    // Don't show if browser doesn't support notifications
    if (!isSupported.value) return false
    
    // Don't show if user is not authenticated
    if (!authStore.isAuthenticated) return false
    
    // Don't show if already shown this session
    if (hasShownThisSession.value) return false
    
    // Don't show if permission already granted or denied
    if (permission.value !== 'default') return false
    
    // Don't show if user has dismissed it permanently
    if (localStorage.getItem('notificationPromptDismissed') === 'never') return false
    
    // Don't show if dismissed recently (within 7 days)
    const lastDismissed = localStorage.getItem('notificationPromptLastDismissed')
    if (lastDismissed) {
      const daysSinceLastDismiss = (Date.now() - parseInt(lastDismissed)) / (1000 * 60 * 60 * 24)
      if (daysSinceLastDismiss < 7) return false
    }
    
    return true
  })

  // Watch for authentication changes to trigger prompt
  watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
      if (isAuthenticated && shouldShowPrompt.value) {
        // Show prompt after a delay to let the user settle in
        setTimeout(() => {
          showPrompt.value = true
          hasShownThisSession.value = true
        }, 3000) // 3 second delay after login
      }
    },
    { immediate: true }
  )

  // Methods
  async function handleAllow() {
    try {
      const granted = await requestPermission()
      if (granted) {
        // Auto-enable notifications when permission is granted
        setEnabled(true)
        showPrompt.value = false
        
        // Show a success notification after a short delay
        setTimeout(() => {
          showBrowserNotification({
            title: '🎉 Notifications Enabled!',
            message: 'You\'ll now receive important updates from your SaaS app.',
            type: 'success',
            icon: '/favicon-96x96.png',
            requireInteraction: false
          })
        }, 500)
        
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to request notification permission:', error)
      return false
    }
  }

  function handleDismiss() {
    showPrompt.value = false
    // Remember that user dismissed it
    localStorage.setItem('notificationPromptLastDismissed', Date.now().toString())
  }

  function handleNeverShow() {
    showPrompt.value = false
    // Remember that user never wants to see this
    localStorage.setItem('notificationPromptDismissed', 'never')
  }

  function resetPrompt() {
    // Reset all stored preferences (useful for testing or user settings)
    localStorage.removeItem('notificationPromptDismissed')
    localStorage.removeItem('notificationPromptLastDismissed')
    hasShownThisSession.value = false
    showPrompt.value = false
  }

  function showPromptManually() {
    // Allow manual triggering of the prompt (e.g., from settings)
    if (shouldShowPrompt.value) {
      showPrompt.value = true
      hasShownThisSession.value = true
    }
  }

  return {
    showPrompt: computed(() => showPrompt.value),
    shouldShowPrompt,
    handleAllow,
    handleDismiss,
    handleNeverShow,
    resetPrompt,
    showPromptManually
  }
}
