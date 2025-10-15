import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { TenantService, TenantServiceFilters, TenantServiceStats } from '~/types/tenant-service'

/**
 * Composable for tenant services CRUD operations
 */
export function useTenantServices() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const services = ref<TenantService[]>([])
  const currentService = ref<TenantService | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isDeleting = ref(false)
  const error = ref<string | null>(null)
  const stats = ref<TenantServiceStats>({
    total_services: 0,
    active_services: 0,
    inactive_services: 0,
    approved_services: 0,
    pending_approval: 0,
    total_usage: 0
  })

  // Computed
  const activeServices = computed(() => 
    services.value.filter(s => s.is_active)
  )

  const inactiveServices = computed(() => 
    services.value.filter(s => !s.is_active)
  )

  const approvedServices = computed(() => 
    services.value.filter(s => s.is_approved)
  )

  const pendingApproval = computed(() => 
    services.value.filter(s => !s.is_approved && s.service.requires_approval)
  )

  /**
   * Get the base URL for tenant services API
   */
  function getBaseUrl(): string {
    return '/api/v1/management/tenants/services'
  }
  
  function getApproveURL(tenantId: number, serviceId: number): string {
    return `/api/v1/management/tenants/${tenantId}/services/${serviceId}/approve`
  }
  /**
   * Fetch all tenant services with optional filters
   */
  async function fetchServices(filters?: TenantServiceFilters, skip = 0, limit = 100): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      
      // Build query params
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString()
      })

      if (filters?.tenant_id) params.append('tenant_id', filters.tenant_id.toString())
      if (filters?.service_id) params.append('service_id', filters.service_id)
      if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString())
      if (filters?.is_approved !== undefined) params.append('is_approved', filters.is_approved.toString())
      if (filters?.category && filters.category !== 'all') params.append('category', filters.category)
      if (filters?.search) params.append('search', filters.search)

      const url = `${getBaseUrl()}?${params.toString()}`
      const data = await authenticatedFetch<TenantService[]>(url)
      services.value = data
      
      // Calculate stats
      calculateStats()
      
      console.log('[TenantServices] Fetched successfully:', data.length, 'services')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch tenant services'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantServices] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single tenant service by ID
   */
  async function fetchService(serviceId: number): Promise<TenantService | null> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<TenantService>(`${getBaseUrl()}/${serviceId}`)
      currentService.value = data
      
      console.log('[TenantServices] Fetched service:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch tenant service'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantServices] Error fetching service:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Approve a tenant service
   */
  async function approveService(serviceId: number, tenantId: number): Promise<boolean> {
    try {
      isSaving.value = true
      error.value = null
      
      await authenticatedFetch(getApproveURL(tenantId, serviceId), {
        method: 'PATCH'
      })
      
      // Update in local state
      const index = services.value.findIndex(s => s.id === serviceId)
      if (index !== -1) {
        services.value[index].is_approved = true
        services.value[index].approved_at = new Date().toISOString()
      }
      
      calculateStats()
      success('Service approved successfully')
      console.log('[TenantServices] Approved:', serviceId)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to approve service'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantServices] Error approving:', err)
      return false
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Toggle service active status
   */
  async function toggleActive(serviceId: number): Promise<boolean> {
    const service = services.value.find(s => s.id === serviceId)
    if (!service) {
      notifyError('Service not found')
      return false
    }

    try {
      isSaving.value = true
      error.value = null
      
      const updatedService = await authenticatedFetch<TenantService>(`${getBaseUrl()}/${serviceId}`, {
        method: 'PUT',
        body: JSON.stringify({ is_active: !service.is_active })
      })
      
      // Update in local state
      const index = services.value.findIndex(s => s.id === serviceId)
      if (index !== -1) {
        services.value[index] = updatedService
      }
      
      calculateStats()
      success(`Service ${updatedService.is_active ? 'activated' : 'deactivated'} successfully`)
      console.log('[TenantServices] Toggled active:', updatedService)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to toggle service status'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantServices] Error toggling:', err)
      return false
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Delete a tenant service
   */
  async function deleteService(serviceId: number): Promise<boolean> {
    try {
      isDeleting.value = true
      error.value = null
      
      await authenticatedFetch(`${getBaseUrl()}/${serviceId}`, {
        method: 'DELETE'
      })
      
      // Remove from local state
      services.value = services.value.filter(s => s.id !== serviceId)
      
      if (currentService.value?.id === serviceId) {
        currentService.value = null
      }
      
      calculateStats()
      success('Service deleted successfully')
      console.log('[TenantServices] Deleted:', serviceId)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete service'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantServices] Error deleting:', err)
      return false
    } finally {
      isDeleting.value = false
    }
  }

  /**
   * Calculate statistics
   */
  function calculateStats() {
    stats.value = {
      total_services: services.value.length,
      active_services: activeServices.value.length,
      inactive_services: inactiveServices.value.length,
      approved_services: approvedServices.value.length,
      pending_approval: pendingApproval.value.length,
      total_usage: services.value.reduce((sum, s) => sum + s.usage_count, 0)
    }
  }

  /**
   * Reset state
   */
  function reset(): void {
    services.value = []
    currentService.value = null
    error.value = null
  }

  return {
    // State
    services,
    currentService,
    isLoading,
    isSaving,
    isDeleting,
    error,
    stats,
    
    // Computed
    activeServices,
    inactiveServices,
    approvedServices,
    pendingApproval,
    
    // Methods
    fetchServices,
    fetchService,
    approveService,
    toggleActive,
    deleteService,
    reset
  }
}
