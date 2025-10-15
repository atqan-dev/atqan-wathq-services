import { useAuthStore } from '~/stores/auth'
import { watch } from 'vue'

// Function to decode JWT and get expiration time
function getTokenExpirationTime(token: string): number | null {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    const payload = JSON.parse(jsonPayload)
    return payload.exp * 1000 // Convert to milliseconds
  } catch (error) {
    console.error('Error decoding token:', error)
    return null
  }
}

// Check if token is about to expire (within the next 5 minutes)
function isTokenExpiringSoon(token: string): boolean {
  const expirationTime = getTokenExpirationTime(token)
  if (!expirationTime) return false
  
  // Token is considered "expiring soon" if it expires in less than 5 minutes
  const fiveMinutesInMs = 5 * 60 * 1000
  return Date.now() + fiveMinutesInMs > expirationTime
}

// Global variable to store interval ID
let tokenRefreshIntervalId: number | null = null

// Function to start token refresh monitoring
function startTokenRefreshMonitoring(authStore: ReturnType<typeof useAuthStore>) {
  // Clear any existing interval first to prevent duplicates
  if (tokenRefreshIntervalId !== null) {
    clearInterval(tokenRefreshIntervalId)
    tokenRefreshIntervalId = null
  }
  
  // Set up new interval
  tokenRefreshIntervalId = window.setInterval(async () => {
    // Only check if user is authenticated
    if (authStore.isAuthenticated && authStore.token) {
      // Check if token is about to expire
      if (isTokenExpiringSoon(authStore.token)) {
        console.log('Access token is expiring soon, refreshing...')
        await authStore.refreshAuthToken()
      }
    } else {
      // If not authenticated, stop checking
      if (tokenRefreshIntervalId !== null) {
        clearInterval(tokenRefreshIntervalId)
        tokenRefreshIntervalId = null
      }
    }
  }, 60000) // Check every minute
}

export default defineNuxtPlugin(() => {
  // Only run in client-side
  if (process.client) {
    const authStore = useAuthStore()
    
    // Start monitoring when plugin is loaded
    startTokenRefreshMonitoring(authStore)
    
    // Watch for authentication state changes
    watch(() => authStore.isAuthenticated, (isAuthenticated) => {
      if (isAuthenticated) {
        // Start monitoring when user becomes authenticated
        startTokenRefreshMonitoring(authStore)
      } else {
        // Stop monitoring when user logs out
        if (tokenRefreshIntervalId !== null) {
          clearInterval(tokenRefreshIntervalId)
          tokenRefreshIntervalId = null
        }
      }
    })
  }
})
