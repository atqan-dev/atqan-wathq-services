import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'

export interface WathqCallLog {
  id: string
  tenant_id: number | null
  user_id: number | null
  management_user_id: number | null
  service_slug: string
  endpoint: string
  method: string
  status_code: number
  request_data: Record<string, any> | null
  response_body: Record<string, any> | any[]
  fetched_at: string
  duration_ms: number | null
  // Joined fields
  tenant?: {
    id: number
    name: string
    slug: string
  }
  user?: {
    id: number
    email: string
    first_name: string
    last_name: string
  }
  management_user?: {
    id: number
    email: string
    first_name: string
    last_name: string
  }
}

export interface WathqCallLogStats {
  total_calls: number
  success_calls: number
  error_calls: number
  avg_duration_ms: number
  calls_by_service: Record<string, number>
  calls_by_status: Record<string, number>
}

export interface FetchLogsParams {
  page?: number
  limit?: number
  tenant_id?: number
  service_slug?: string
  status_code?: number
  method?: string
  start_date?: string
  end_date?: string
  search?: string
}

export function useWathqCallLogs() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const logs = ref<WathqCallLog[]>([])
  const currentLog = ref<WathqCallLog | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const stats = ref<WathqCallLogStats | null>(null)

  /**
   * Fetch all call logs with optional filters
   */
  async function fetchLogs(params: FetchLogsParams = {}): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const queryParams = new URLSearchParams()
      if (params.page) queryParams.append('skip', String((params.page - 1) * (params.limit || 20)))
      if (params.limit) queryParams.append('limit', String(params.limit))
      if (params.tenant_id) queryParams.append('tenant_id', String(params.tenant_id))
      if (params.service_slug) queryParams.append('service_slug', params.service_slug)
      if (params.method) queryParams.append('method', params.method)

      const url = `/api/v1/management/tenants/history${queryParams.toString() ? '?' + queryParams.toString() : ''}`
      const data = await authenticatedFetch<WathqCallLog[]>(url)
      logs.value = data
      total.value = data.length

      console.log('[WathqCallLogs] Fetched successfully:', data.length, 'logs')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch call logs'
      error.value = errorMessage
      console.error('[WathqCallLogs] Error fetching logs:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single call log by ID
   */
  async function fetchLog(logId: string): Promise<WathqCallLog | null> {
    try {
      isLoading.value = true
      error.value = null

      // Fetch all logs and find the one with matching ID
      // In a real implementation, you'd have a dedicated endpoint
      const data = await authenticatedFetch<WathqCallLog[]>('/api/v1/management/tenants/history?limit=1000')
      const log = data.find(l => l.id === logId)
      
      if (log) {
        currentLog.value = log
        return log
      }
      
      throw new Error('Log not found')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch call log'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[WathqCallLogs] Error fetching log:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch logs for a specific tenant
   */
  async function fetchTenantLogs(tenantId: number, params: FetchLogsParams = {}): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const queryParams = new URLSearchParams()
      if (params.page) queryParams.append('skip', String((params.page - 1) * (params.limit || 20)))
      if (params.limit) queryParams.append('limit', String(params.limit))

      const url = `/api/v1/management/tenants/${tenantId}/history${queryParams.toString() ? '?' + queryParams.toString() : ''}`
      const data = await authenticatedFetch<WathqCallLog[]>(url)
      logs.value = data
      total.value = data.length

      console.log('[WathqCallLogs] Fetched tenant logs:', data.length)
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch tenant call logs'
      error.value = errorMessage
      console.error('[WathqCallLogs] Error fetching tenant logs:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Calculate stats from logs
   */
  function calculateStats(): WathqCallLogStats {
    const successCalls = logs.value.filter(l => l.status_code >= 200 && l.status_code < 300).length
    const errorCalls = logs.value.filter(l => l.status_code >= 400).length
    const durations = logs.value.filter(l => l.duration_ms).map(l => l.duration_ms!)
    const avgDuration = durations.length > 0 ? durations.reduce((a, b) => a + b, 0) / durations.length : 0

    const callsByService: Record<string, number> = {}
    const callsByStatus: Record<string, number> = {}

    logs.value.forEach(log => {
      callsByService[log.service_slug] = (callsByService[log.service_slug] || 0) + 1
      const statusGroup = `${Math.floor(log.status_code / 100)}xx`
      callsByStatus[statusGroup] = (callsByStatus[statusGroup] || 0) + 1
    })

    const result: WathqCallLogStats = {
      total_calls: logs.value.length,
      success_calls: successCalls,
      error_calls: errorCalls,
      avg_duration_ms: Math.round(avgDuration),
      calls_by_service: callsByService,
      calls_by_status: callsByStatus
    }

    stats.value = result
    return result
  }

  /**
   * Get service display name
   */
  function getServiceDisplayName(slug: string): string {
    const serviceNames: Record<string, string> = {
      'commercial-registration': 'Commercial Registration',
      'real-estate': 'Real Estate',
      'employee-verification': 'Employee Verification',
      'company-contract': 'Company Contract',
      'attorney-services': 'Attorney Services',
      'national-address': 'National Address'
    }
    return serviceNames[slug] || slug
  }

  /**
   * Get status badge color
   */
  function getStatusColor(statusCode: number): string {
    if (statusCode >= 200 && statusCode < 300) return 'green'
    if (statusCode >= 300 && statusCode < 400) return 'blue'
    if (statusCode >= 400 && statusCode < 500) return 'yellow'
    if (statusCode >= 500) return 'red'
    return 'gray'
  }

  /**
   * Get method badge color
   */
  function getMethodColor(method: string): string {
    const colors: Record<string, string> = {
      'GET': 'blue',
      'POST': 'green',
      'PUT': 'yellow',
      'PATCH': 'orange',
      'DELETE': 'red'
    }
    return colors[method] || 'gray'
  }

  /**
   * Format duration
   */
  function formatDuration(ms: number | null): string {
    if (!ms) return '-'
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  /**
   * Format date
   */
  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString()
  }

  /**
   * Reset state
   */
  function reset(): void {
    logs.value = []
    currentLog.value = null
    error.value = null
    total.value = 0
    stats.value = null
  }

  return {
    // State
    logs,
    currentLog,
    isLoading,
    error,
    total,
    stats,

    // Methods
    fetchLogs,
    fetchLog,
    fetchTenantLogs,
    calculateStats,
    reset,

    // Helpers
    getServiceDisplayName,
    getStatusColor,
    getMethodColor,
    formatDuration,
    formatDate
  }
}
