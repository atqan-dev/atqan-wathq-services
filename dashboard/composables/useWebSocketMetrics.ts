import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'

export interface WebSocketMetrics {
  active_connections: number
  connected_users: number
  connected_management_users: number
  connected_tenants: number
  total_connections: number
  total_disconnections: number
  total_messages_sent: number
  total_errors: number
  uptime_seconds: number
}

export function useWebSocketMetrics() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  
  const metrics = ref<WebSocketMetrics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  let metricsInterval: ReturnType<typeof setInterval> | null = null

  async function fetchMetrics() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<WebSocketMetrics>('/api/v1/ws/metrics')
      metrics.value = data
      
      console.log('[Metrics] Fetched successfully:', data)
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch metrics'
      console.error('[Metrics] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  function startPolling(intervalMs: number = 10000) {
    if (metricsInterval) {
      clearInterval(metricsInterval)
    }
    
    // Fetch immediately
    fetchMetrics()
    
    // Then poll at specified interval
    metricsInterval = setInterval(fetchMetrics, intervalMs)
    console.log(`[Metrics] Polling started (every ${intervalMs}ms)`)
  }

  function stopPolling() {
    if (metricsInterval) {
      clearInterval(metricsInterval)
      metricsInterval = null
      console.log('[Metrics] Polling stopped')
    }
  }

  function formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    const parts: string[] = []
    if (days > 0) parts.push(`${days}d`)
    if (hours > 0) parts.push(`${hours}h`)
    if (minutes > 0) parts.push(`${minutes}m`)
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`)
    
    return parts.join(' ')
  }

  function getErrorRate(): number {
    if (!metrics.value || metrics.value.total_messages_sent === 0) {
      return 0
    }
    return (metrics.value.total_errors / metrics.value.total_messages_sent) * 100
  }

  onUnmounted(() => {
    stopPolling()
  })

  return {
    metrics,
    isLoading,
    error,
    fetchMetrics,
    startPolling,
    stopPolling,
    formatUptime,
    getErrorRate
  }
}
