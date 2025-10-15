import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useNotifications } from './useNotifications'
import type { Tenant, CreateTenantData, UpdateTenantData } from '~/types/tenant'

/**
 * Composable for tenant CRUD operations
 * Provides reactive state management and API calls for tenant management
 */
export function useTenants() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useNotifications()

  // State
  const tenants = ref<Tenant[]>([])
  const currentTenant = ref<Tenant | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isDeleting = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeTenants = computed(() => 
    tenants.value.filter(t => t.is_active)
  )

  const inactiveTenants = computed(() => 
    tenants.value.filter(t => !t.is_active)
  )

  const totalUsers = computed(() => 
    tenants.value.reduce((sum, t) => sum + (t.users_count || 0), 0)
  )

  /**
   * Fetch all tenants from the API
   */
  async function fetchTenants(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<Tenant[]>('/api/v1/management/tenants')
      tenants.value = data
      
      console.log('[Tenants] Fetched successfully:', data.length, 'tenants')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch tenants'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Tenants] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single tenant by ID
   */
  async function fetchTenant(id: number): Promise<Tenant | null> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<Tenant>(`/api/v1/management/tenants/${id}`)
      currentTenant.value = data
      
      console.log('[Tenants] Fetched tenant:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch tenant'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Tenants] Error fetching tenant:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new tenant
   */
  async function createTenant(data: CreateTenantData): Promise<Tenant | null> {
    try {
      isSaving.value = true
      error.value = null
      
      const newTenant = await authenticatedFetch<Tenant>('/api/v1/management/tenants', {
        method: 'POST',
        body: JSON.stringify(data)
      })
      
      // Add to local state
      tenants.value.push(newTenant)
      
      success('Tenant created successfully')
      console.log('[Tenants] Created:', newTenant)
      
      return newTenant
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create tenant'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Tenants] Error creating:', err)
      return null
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Update an existing tenant
   */
  async function updateTenant(id: number, data: UpdateTenantData): Promise<Tenant | null> {
    try {
      isSaving.value = true
      error.value = null
      
      const updatedTenant = await authenticatedFetch<Tenant>(`/api/v1/management/tenants/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      })
      
      // Update in local state
      const index = tenants.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tenants.value[index] = updatedTenant
      }
      
      // Update current tenant if it's the one being edited
      if (currentTenant.value?.id === id) {
        currentTenant.value = updatedTenant
      }
      
      success('Tenant updated successfully')
      console.log('[Tenants] Updated:', updatedTenant)
      
      return updatedTenant
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update tenant'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Tenants] Error updating:', err)
      return null
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Delete a tenant
   */
  async function deleteTenant(id: number): Promise<boolean> {
    try {
      isDeleting.value = true
      error.value = null
      
      await authenticatedFetch(`/api/v1/management/tenants/${id}`, {
        method: 'DELETE'
      })
      
      // Remove from local state
      tenants.value = tenants.value.filter(t => t.id !== id)
      
      // Clear current tenant if it's the one being deleted
      if (currentTenant.value?.id === id) {
        currentTenant.value = null
      }
      
      success('Tenant deleted successfully')
      console.log('[Tenants] Deleted:', id)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete tenant'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Tenants] Error deleting:', err)
      return false
    } finally {
      isDeleting.value = false
    }
  }

  /**
   * Toggle tenant active status
   */
  async function toggleActive(id: number): Promise<boolean> {
    const tenant = tenants.value.find(t => t.id === id)
    if (!tenant) {
      notifyError('Tenant not found')
      return false
    }

    return await updateTenant(id, { is_active: !tenant.is_active }) !== null
  }

  /**
   * Validate tenant data before submission
   */
  function validateTenantData(data: CreateTenantData | UpdateTenantData): string[] {
    const errors: string[] = []

    if ('name' in data && data.name !== undefined) {
      if (!data.name || data.name.trim().length === 0) {
        errors.push('Name is required')
      } else if (data.name.length < 2) {
        errors.push('Name must be at least 2 characters')
      } else if (data.name.length > 100) {
        errors.push('Name must not exceed 100 characters')
      } else if (!/^[a-zA-Z0-9\s\-_&]+$/.test(data.name)) {
        errors.push('Name must contain only English letters, numbers, spaces, and basic symbols (-, _, &)')
      }
    }

    if ('slug' in data && data.slug !== undefined) {
      if (!data.slug || data.slug.trim().length === 0) {
        errors.push('Slug is required')
      } else if (!/^[a-z0-9-]+$/.test(data.slug)) {
        errors.push('Slug must contain only lowercase letters, numbers, and hyphens')
      } else if (data.slug.length < 2) {
        errors.push('Slug must be at least 2 characters')
      } else if (data.slug.length > 50) {
        errors.push('Slug must not exceed 50 characters')
      }
    }

    if ('max_users' in data && data.max_users !== undefined) {
      if (data.max_users < 1) {
        errors.push('Max users must be at least 1')
      } else if (data.max_users > 10000) {
        errors.push('Max users must not exceed 10000')
      }
    }

    return errors
  }

  /**
   * Reset state
   */
  function reset(): void {
    tenants.value = []
    currentTenant.value = null
    error.value = null
  }

  return {
    // State
    tenants,
    currentTenant,
    isLoading,
    isSaving,
    isDeleting,
    error,
    
    // Computed
    activeTenants,
    inactiveTenants,
    totalUsers,
    
    // Methods
    fetchTenants,
    fetchTenant,
    createTenant,
    updateTenant,
    deleteTenant,
    toggleActive,
    validateTenantData,
    reset
  }
}
