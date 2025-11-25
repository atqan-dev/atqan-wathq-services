import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'

/**
 * Notifications composable with WebSocket support
 * 
 * Current implementation:
 * - WebSocket endpoint: ws://localhost:5500/api/v1/ws/notifications
 * - Real-time notification delivery
 * - Automatic reconnection with exponential backoff
 * - Ping/pong keep-alive mechanism
 * - Fallback to polling if WebSocket fails
 * 
 * Connection states:
 * - 'connected': WebSocket is connected (real-time updates)
 * - 'polling': Using polling fallback (updates every 30 seconds)
 * - 'connecting': Attempting to connect WebSocket
 * - 'disconnected': WebSocket failed/disconnected
 */

const notifications = ref<any[]>([])
const unreadCount = computed(() => notifications.value.filter(n => n.status === 'unread').length)
const connectionStatus = ref<'connecting' | 'connected' | 'disconnected' | 'polling'>('disconnected')

let ws: WebSocket | null = null
let reconnectAttempts = 0
const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_DELAY = 5000
let pollingInterval: ReturnType<typeof setInterval> | null = null
let pingInterval: ReturnType<typeof setInterval> | null = null
const POLLING_INTERVAL = 30000 // 30 seconds
const PING_INTERVAL = 30000 // 30 seconds

// Configuration - WebSocket is now enabled!
const ENABLE_WEBSOCKET = true

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

export function useNotifications() {
  const { authenticatedFetch } = useAuthenticatedFetch()

  async function fetchNotifications() {
    try {
      const res = await authenticatedFetch<any[]>('/api/v1/notifications/management/', { method: 'GET' })
      notifications.value = res
    } catch (error) {
      console.error('Error fetching notifications:', error)
    }
  }

  async function markAsRead(notification: any) {
    if (notification.status === 'read') return
    try {
      await authenticatedFetch(`/api/v1/notifications/management/mark-as-read`, { method: 'POST', body: JSON.stringify({ notification_ids: [notification.id] }) })
      notification.status = 'read'
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  function startPolling() {
    // Clear any existing polling interval
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }
    
    // Start polling for notifications
    pollingInterval = setInterval(() => {
      fetchNotifications()
    }, POLLING_INTERVAL)
    
    connectionStatus.value = 'polling'
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  function getAuthToken(): string | null {
    // Get token from localStorage (adjust based on your auth implementation)
    const token = localStorage.getItem('auth_token')
    return token
  }

  function getUserType(): string {
    // Get user type from localStorage or auth store
    const userStr = localStorage.getItem('auth-user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        return user.is_super_admin ? 'management' : 'user'
      } catch {
        return 'user'
      }
    }
    return 'user'
  }

  function connectWebSocket() {
    if (!ENABLE_WEBSOCKET) {
      console.log('[WebSocket] Disabled, using polling fallback')
      startPolling()
      return
    }

    const token = getAuthToken()
    if (!token) {
      console.warn('[WebSocket] No auth token found, using polling')
      startPolling()
      return
    }

    connectionStatus.value = 'connecting'
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = 'localhost:5500'
    const userType = getUserType()
    
    // Build WebSocket URL with authentication
    const wsUrl = `${protocol}//${wsHost}/api/v1/ws/notifications?token=${token}&user_type=${userType}`
    
    console.log(`[WebSocket] Connecting to ${wsUrl.replace(token, 'TOKEN')}`)
    
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('[WebSocket] Connected successfully')
      connectionStatus.value = 'connected'
      reconnectAttempts = 0
      
      // Stop polling when WebSocket is connected
      stopPolling()
      
      // Start ping interval to keep connection alive
      if (pingInterval) {
        clearInterval(pingInterval)
      }
      pingInterval = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          console.log('[WebSocket] Sending ping')
          ws.send('ping')
        }
      }, PING_INTERVAL)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('[WebSocket] Message received:', data.type)
        
        if (data.type === 'connected') {
          console.log('[WebSocket]', data.message)
        } else if (data.type === 'notification') {
          // New notification received
          console.log('[WebSocket] New notification:', data.data)
          
          // Add to notifications list
          notifications.value.unshift(data.data)
          
          // Show browser notification if enabled
          showBrowserNotification(data.data)
        } else if (data.type === 'pong') {
          console.log('[WebSocket] Pong received')
        }
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error)
      connectionStatus.value = 'disconnected'
      
      // Clear ping interval
      if (pingInterval) {
        clearInterval(pingInterval)
        pingInterval = null
      }
      
      // Start polling as fallback when WebSocket fails
      if (!pollingInterval) {
        console.log('[WebSocket] Starting polling fallback')
        startPolling()
      }
      
      // Attempt reconnection with exponential backoff
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts)
        reconnectAttempts++
        console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`)
        setTimeout(connectWebSocket, delay)
      }
    }

    ws.onclose = (event) => {
      console.log('[WebSocket] Closed:', event.code, event.reason)
      connectionStatus.value = 'disconnected'
      
      // Clear ping interval
      if (pingInterval) {
        clearInterval(pingInterval)
        pingInterval = null
      }
      
      // Start polling as fallback when WebSocket disconnects
      if (!pollingInterval) {
        console.log('[WebSocket] Starting polling fallback')
        startPolling()
      }
      
      // Attempt reconnection with exponential backoff
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts)
        reconnectAttempts++
        console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`)
        setTimeout(connectWebSocket, delay)
      }
    }
  }

  function showBrowserNotification(notification: any) {
    // Check if browser notifications are enabled
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
      try {
        new Notification(notification.title || 'New Notification', {
          body: notification.message,
          icon: '/favicon-96x96.png',
          badge: '/favicon-96x96.png'
        })
      } catch (error) {
        console.warn('[WebSocket] Failed to show browser notification:', error)
      }
    }
  }

  function disconnect() {
    console.log('[WebSocket] Disconnecting...')
    
    // Clear intervals
    if (pingInterval) {
      clearInterval(pingInterval)
      pingInterval = null
    }
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
    
    // Close WebSocket
    if (ws) {
      ws.onclose = null // Prevent reconnection
      ws.onerror = null
      ws.close()
      ws = null
    }
    
    connectionStatus.value = 'disconnected'
    reconnectAttempts = 0
  }

  onMounted(() => {
    fetchNotifications()
    
    // Try WebSocket first, fallback to polling if it fails
    try {
      connectWebSocket()
    } catch (error) {
      console.error('[WebSocket] Failed to initialize:', error)
      startPolling()
    }
  })

  onUnmounted(() => {
    disconnect()
  })

  function add(notification: any) {
    notifications.value.push(notification)
  }

  function success(msg: string) {
    add({ title: 'Success', description: msg, color: 'green' })
  }

  function error(msg: string) {
    add({ title: 'Error', description: msg, color: 'red' })
  }

  return {
    notifications,
    unreadCount,
    connectionStatus,
    markAsRead,
    formatDate,
    add,
    success,
    error,
    disconnect,
    connectWebSocket,
    fetchNotifications
  }
}
