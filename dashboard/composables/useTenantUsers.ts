import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { User, CreateUserData, UpdateUserData } from '~/types/user'

/**
 * Composable for tenant users CRUD operations
 * Provides reactive state management and API calls for user management within a tenant
 */
export function useTenantUsers(tenantId?: number) {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isDeleting = ref(false)
  const error = ref<string | null>(null)
  const selectedTenantId = ref<number | undefined>(tenantId)

  // Computed
  const activeUsers = computed(() => 
    users.value.filter(u => u.is_active)
  )

  const inactiveUsers = computed(() => 
    users.value.filter(u => !u.is_active)
  )

  const superAdmins = computed(() => 
    users.value.filter(u => u.is_super_admin)
  )

  const regularUsers = computed(() => 
    users.value.filter(u => !u.is_super_admin)
  )

  /**
   * Set the tenant ID for subsequent operations
   */
  function setTenantId(id: number) {
    selectedTenantId.value = id
  }

  /**
   * Get the base URL for tenant users API
   */
  function getBaseUrl(): string {
    if (!selectedTenantId.value) {
      throw new Error('Tenant ID is required')
    }
    return `/api/v1/management/tenants/${selectedTenantId.value}/users`
  }

  /**
   * Fetch all users for the current tenant
   */
  async function fetchUsers(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<User[]>(getBaseUrl())
      users.value = data
      
      console.log('[TenantUsers] Fetched successfully:', data.length, 'users')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch users'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single user by ID
   */
  async function fetchUser(userId: number): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await authenticatedFetch<User>(`${getBaseUrl()}/${userId}`)
      currentUser.value = data
      
      console.log('[TenantUsers] Fetched user:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error fetching user:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new user for the current tenant
   */
  async function createUser(data: CreateUserData & { password: string }): Promise<User | null> {
    try {
      isSaving.value = true
      error.value = null
      
      const newUser = await authenticatedFetch<User>(getBaseUrl(), {
        method: 'POST',
        body: JSON.stringify(data)
      })
      
      // Add to local state
      users.value.push(newUser)
      
      success('User created successfully')
      console.log('[TenantUsers] Created:', newUser)
      
      return newUser
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error creating:', err)
      return null
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Update an existing user
   */
  async function updateUser(userId: number, data: UpdateUserData): Promise<User | null> {
    try {
      isSaving.value = true
      error.value = null
      
      const updatedUser = await authenticatedFetch<User>(`${getBaseUrl()}/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      })
      
      // Update in local state
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      
      // Update current user if it's the one being edited
      if (currentUser.value?.id === userId) {
        currentUser.value = updatedUser
      }
      
      success('User updated successfully')
      console.log('[TenantUsers] Updated:', updatedUser)
      
      return updatedUser
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error updating:', err)
      return null
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Delete a user
   */
  async function deleteUser(userId: number): Promise<boolean> {
    try {
      isDeleting.value = true
      error.value = null
      
      await authenticatedFetch(`${getBaseUrl()}/${userId}`, {
        method: 'DELETE'
      })
      
      // Remove from local state
      users.value = users.value.filter(u => u.id !== userId)
      
      // Clear current user if it's the one being deleted
      if (currentUser.value?.id === userId) {
        currentUser.value = null
      }
      
      success('User deleted successfully')
      console.log('[TenantUsers] Deleted:', userId)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error deleting:', err)
      return false
    } finally {
      isDeleting.value = false
    }
  }

  /**
   * Toggle user active status
   */
  async function toggleActive(userId: number): Promise<boolean> {
    const user = users.value.find(u => u.id === userId)
    if (!user) {
      notifyError('User not found')
      return false
    }

    return await updateUser(userId, { is_active: !user.is_active }) !== null
  }

  /**
   * Update user password
   */
  async function updatePassword(userId: number, newPassword: string): Promise<boolean> {
    try {
      isSaving.value = true
      error.value = null
      
      await authenticatedFetch(`${getBaseUrl()}/${userId}/password`, {
        method: 'PUT',
        body: JSON.stringify({ password: newPassword })
      })
      
      success('Password updated successfully')
      console.log('[TenantUsers] Password updated for user:', userId)
      
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update password'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[TenantUsers] Error updating password:', err)
      return false
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Validate user data before submission
   */
  function validateUserData(data: CreateUserData | UpdateUserData): string[] {
    const errors: string[] = []

    if ('email' in data && data.email !== undefined) {
      if (!data.email || data.email.trim().length === 0) {
        errors.push('Email is required')
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
        errors.push('Email must be valid')
      }
    }

    if ('first_name' in data && data.first_name !== undefined) {
      if (!data.first_name || data.first_name.trim().length === 0) {
        errors.push('First name is required')
      } else if (data.first_name.length < 2) {
        errors.push('First name must be at least 2 characters')
      } else if (data.first_name.length > 50) {
        errors.push('First name must not exceed 50 characters')
      }
    }

    if ('last_name' in data && data.last_name !== undefined) {
      if (!data.last_name || data.last_name.trim().length === 0) {
        errors.push('Last name is required')
      } else if (data.last_name.length < 2) {
        errors.push('Last name must be at least 2 characters')
      } else if (data.last_name.length > 50) {
        errors.push('Last name must not exceed 50 characters')
      }
    }

    return errors
  }

  /**
   * Validate password
   */
  function validatePassword(password: string): string[] {
    const errors: string[] = []

    if (!password || password.length === 0) {
      errors.push('Password is required')
    } else if (password.length < 8) {
      errors.push('Password must be at least 8 characters')
    } else if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter')
    } else if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter')
    } else if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number')
    }

    return errors
  }

  /**
   * Reset state
   */
  function reset(): void {
    users.value = []
    currentUser.value = null
    error.value = null
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    isSaving,
    isDeleting,
    error,
    selectedTenantId,
    
    // Computed
    activeUsers,
    inactiveUsers,
    superAdmins,
    regularUsers,
    
    // Methods
    setTenantId,
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    toggleActive,
    updatePassword,
    validateUserData,
    validatePassword,
    reset
  }
}
