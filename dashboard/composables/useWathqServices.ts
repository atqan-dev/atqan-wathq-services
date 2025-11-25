import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type {
  WathqService,
  WathqServiceType,
  WathqApiRequest,
  WathqTestRequest,
  WathqTestResponse,
  WathqRequestFilters,
  WathqStats
} from '~/types/wathq'

/**
 * Composable for Wathq API services
 */
export function useWathqServices() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const services = ref<WathqService[]>([])
  const requests = ref<WathqApiRequest[]>([])
  const stats = ref<WathqStats>({
    total_requests: 0,
    successful_requests: 0,
    failed_requests: 0,
    average_duration_ms: 0,
    requests_today: 0,
    requests_this_week: 0,
    requests_this_month: 0
  })
  const isLoading = ref(false)
  const isTesting = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeServices = computed(() => 
    services.value.filter(s => s.is_active)
  )

  const successfulRequests = computed(() =>
    requests.value.filter(r => r.is_success)
  )

  const failedRequests = computed(() =>
    requests.value.filter(r => !r.is_success)
  )

  /**
   * Get available Wathq services
   */
  const wathqServicesList: WathqService[] = [
    {
      id: 'wathq-cr',
      name: 'Commercial Registration',
      name_ar: 'السجل التجاري',
      slug: 'commercial-registration',
      description: 'Query commercial registration information',
      description_ar: 'الاستعلام عن معلومات السجل التجاري',
      icon: 'i-heroicons-building-office-2',
      is_active: true,
      requires_authentication: true
    },
    {
      id: 'wathq-contract',
      name: 'Company Contract',
      name_ar: 'عقد الشركة',
      slug: 'company-contract',
      description: 'Retrieve company contract details',
      description_ar: 'استرجاع تفاصيل عقد الشركة',
      icon: 'i-heroicons-document-text',
      is_active: true,
      requires_authentication: true
    },
    {
      id: 'wathq-attorney',
      name: 'Attorney Authorization',
      name_ar: 'التوكيل',
      slug: 'attorney',
      description: 'Verify attorney authorization',
      description_ar: 'التحقق من التوكيل',
      icon: 'i-heroicons-scale',
      is_active: true,
      requires_authentication: true
    },
    {
      id: 'wathq-real-estate',
      name: 'Real Estate',
      name_ar: 'العقارات',
      slug: 'real-estate',
      description: 'Query real estate information',
      description_ar: 'الاستعلام عن معلومات العقارات',
      icon: 'i-heroicons-home',
      is_active: true,
      requires_authentication: true
    },
    {
      id: 'wathq-address',
      name: 'National Address',
      name_ar: 'العنوان الوطني',
      slug: 'spl-national-address',
      description: 'Retrieve national address details',
      description_ar: 'استرجاع تفاصيل العنوان الوطني',
      icon: 'i-heroicons-map-pin',
      is_active: true,
      requires_authentication: true
    },
    {
      id: 'wathq-employee',
      name: 'Employee Verification',
      name_ar: 'التحقق من الموظف',
      slug: 'employee',
      description: 'Verify employee information',
      description_ar: 'التحقق من معلومات الموظف',
      icon: 'i-heroicons-user-circle',
      is_active: true,
      requires_authentication: true
    }
  ]

  /**
   * Get base URL for Wathq API
   */
  function getBaseUrl(): string {
    return '/api/v1/wathq'
  }

  /**
   * Fetch all services
   */
  async function fetchServices(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      services.value = wathqServicesList
      console.log('[WathqServices] Loaded services:', services.value.length)
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load Wathq services'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[WathqServices] Error loading services:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch request logs
   */
  async function fetchRequests(filters?: WathqRequestFilters): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const params = new URLSearchParams()
      params.append('limit', '100') // Default limit
      if (filters?.tenant_id) params.append('tenant_id', filters.tenant_id.toString())
      if (filters?.status === 'error') params.append('only_failed', 'true')

      const url = `/api/v1/management/analytics/requests?${params.toString()}`
      const apiData = await authenticatedFetch<any[]>(url)
      
      // Transform API response to match frontend interface
      requests.value = apiData.map(item => ({
        id: item.id,
        service_type: item.service_name?.toLowerCase().replace(/\s+/g, '-') || 'unknown',
        endpoint: item.endpoint,
        method: item.method,
        request_data: item.request_params || {},
        response_data: {},
        status_code: item.response_status,
        duration_ms: item.response_time_ms,
        is_success: item.is_successful,
        error_message: item.error_message,
        created_at: item.created_at,
        tenant_id: item.tenant_name ? 1 : undefined, // Approximate mapping
        user_id: item.user_email ? 1 : undefined // Approximate mapping
      }))

      calculateStats()
      console.log('[WathqServices] Fetched requests:', requests.value.length)
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch Wathq requests'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[WathqServices] Error fetching requests:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Test API call
   */
  async function testApiCall(testRequest: WathqTestRequest): Promise<WathqTestResponse> {
    try {
      isTesting.value = true
      error.value = null

      const startTime = Date.now()
      const url = `${getBaseUrl()}/test`
      
      const response = await authenticatedFetch<any>(url, {
        method: 'POST',
        body: JSON.stringify(testRequest)
      })

      const duration = Date.now() - startTime

      const result: WathqTestResponse = {
        success: true,
        data: response,
        duration_ms: duration,
        timestamp: new Date().toISOString()
      }

      success('API test completed successfully')
      console.log('[WathqServices] Test successful:', result)
      return result
    } catch (err: any) {
      const duration = Date.now() - Date.now()
      const errorMessage = err.message || 'API test failed'
      error.value = errorMessage
      notifyError(errorMessage)
      
      const result: WathqTestResponse = {
        success: false,
        error: errorMessage,
        duration_ms: duration,
        timestamp: new Date().toISOString()
      }
      
      console.error('[WathqServices] Test failed:', err)
      return result
    } finally {
      isTesting.value = false
    }
  }

  /**
   * Make live API request
   */
  async function makeLiveRequest(
    serviceType: WathqServiceType,
    endpoint: string,
    parameters: Record<string, any>
  ): Promise<WathqApiRequest> {
    try {
      isLoading.value = true
      error.value = null

      const url = `${getBaseUrl()}/live/${serviceType}/${endpoint}`
      const data = await authenticatedFetch<WathqApiRequest>(url, {
        method: 'POST',
        body: JSON.stringify(parameters)
      })

      requests.value.unshift(data)
      calculateStats()
      success('Live request completed')
      console.log('[WathqServices] Live request successful:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Live request failed'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[WathqServices] Live request error:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get offline requests (cached/saved)
   */
  async function fetchOfflineRequests(serviceType?: WathqServiceType): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const url = serviceType 
        ? `${getBaseUrl()}/offline/${serviceType}`
        : `${getBaseUrl()}/offline`
      
      const data = await authenticatedFetch<WathqApiRequest[]>(url)
      requests.value = data

      console.log('[WathqServices] Fetched offline requests:', requests.value.length)
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch offline requests'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[WathqServices] Error fetching offline:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Calculate statistics
   */
  function calculateStats(): void {
    const total = requests.value.length
    const successful = successfulRequests.value.length
    const failed = failedRequests.value.length
    const avgDuration = total > 0
      ? requests.value.reduce((sum, r) => sum + r.duration_ms, 0) / total
      : 0

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

    const requestsToday = requests.value.filter(r => 
      new Date(r.created_at) >= today
    ).length

    const requestsThisWeek = requests.value.filter(r =>
      new Date(r.created_at) >= weekAgo
    ).length

    const requestsThisMonth = requests.value.filter(r =>
      new Date(r.created_at) >= monthAgo
    ).length

    stats.value = {
      total_requests: total,
      successful_requests: successful,
      failed_requests: failed,
      average_duration_ms: Math.round(avgDuration),
      requests_today: requestsToday,
      requests_this_week: requestsThisWeek,
      requests_this_month: requestsThisMonth
    }
  }

  /**
   * Reset state
   */
  function reset(): void {
    services.value = []
    requests.value = []
    error.value = null
  }

  return {
    // State
    services,
    requests,
    stats,
    isLoading,
    isTesting,
    error,

    // Computed
    activeServices,
    successfulRequests,
    failedRequests,

    // Methods
    fetchServices,
    fetchRequests,
    testApiCall,
    makeLiveRequest,
    fetchOfflineRequests,
    reset
  }
}
