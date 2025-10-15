import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { Service, AssignServiceRequest } from '~/types/service'

/**
 * Composable for services management
 */
export function useServices() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const services = ref<Service[]>([])
  const isLoading = ref(false)
  const isAssigning = ref(false)
  const error = ref<string | null>(null)

  /**
   * Fetch all available services
   */
  async function fetchServices(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<Service[]>('/api/v1/management/services')
      services.value = data
      
      console.log('[Services] Fetched successfully:', data.length, 'services')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch services'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Services] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Assign a service to a tenant
   */
  async function assignServiceToTenant(
    tenantId: number,
    payload: AssignServiceRequest
  ): Promise<boolean> {
    try {
      isAssigning.value = true
      error.value = null
      
      await authenticatedFetch(
        `/api/v1/management/tenants/${tenantId}/services`,
        {
          method: 'POST',
          body: JSON.stringify(payload)
        }
      )
      
      success('Service assigned to tenant successfully')
      console.log('[Services] Assigned service to tenant:', tenantId, payload)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to assign service to tenant'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Services] Error assigning:', err)
      return false
    } finally {
      isAssigning.value = false
    }
  }

  /**
   * Get active services only
   */
  const activeServices = computed(() => {
    return services.value.filter(s => s.is_active)
  })

  /**
   * Reset state
   */
  function reset(): void {
    services.value = []
    error.value = null
  }

  return {
    // State
    services,
    isLoading,
    isAssigning,
    error,
    
    // Computed
    activeServices,
    
    // Methods
    fetchServices,
    assignServiceToTenant,
    reset
  }
}
