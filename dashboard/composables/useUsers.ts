import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import { useAuthStore } from '~/stores/auth'
import type { User, UserCreate, UserUpdate } from '~/types/user'

/**
 * Composable for managing users with full CRUD operations
 * Provides reactive state management and API calls for user management
 */
export function useUsers() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const { success, error: notifyError } = useAlert()

  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    skip: 0,
    limit: 100,
    total: 0
  })
  const filters = ref({
    search: '',
    is_active: null as boolean | null,
    role_id: null as number | null
  })

  // Computed
  const activeUsers = computed(() =>
    users.value.filter(u => u.is_active)
  )

  const inactiveUsers = computed(() =>
    users.value.filter(u => !u.is_active)
  )

  const superAdmins = computed(() =>
    users.value.filter(u => u.is_superuser)
  )

  const regularUsers = computed(() =>
    users.value.filter(u => !u.is_superuser)
  )

  const stats = computed(() => ({
    total: users.value.length,
    active: activeUsers.value.length,
    inactive: inactiveUsers.value.length,
    superAdmins: superAdmins.value.length,
    regularUsers: regularUsers.value.length
  }))

  /**
   * Get the base URL for users API
   */
  function getBaseUrl(): string {
    // Check if we should use management endpoints
    // Management users access /api/v1/management/tenants/users
    // Regular tenant users access /api/v1/users
    const authStore = useAuthStore()
    if (authStore.user?.is_super_admin) {
      return '/api/v1/management/tenants/users'
    }
    return '/api/v1/users'
  }

  /**
   * Fetch all users with pagination and filters
   */
  async function fetchUsers(options?: {
    skip?: number
    limit?: number
    search?: string
    is_active?: boolean | null
    role_id?: number | null
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const params = new URLSearchParams()
      params.append('skip', String(options?.skip ?? pagination.value.skip))
      params.append('limit', String(options?.limit ?? pagination.value.limit))

      if (options?.search || filters.value.search) {
        params.append('search', options?.search ?? filters.value.search)
      }

      if (options?.is_active !== undefined || filters.value.is_active !== null) {
        params.append('is_active', String(options?.is_active ?? filters.value.is_active))
      }

      if (options?.role_id || filters.value.role_id) {
        params.append('role_id', String(options?.role_id ?? filters.value.role_id))
      }

      const url = `${getBaseUrl()}?${params.toString()}`
      const data = await authenticatedFetch<User[]>(url)

      console.log('[Users] Fetched data sample:', data[0])

      users.value = data

      // For management endpoints, set total to data length since there's no count endpoint
      // For tenant endpoints, fetch the count
      const authStore = useAuthStore()
      if (authStore.user?.is_super_admin) {
        // Management API doesn't have a count endpoint, use data length
        pagination.value.total = data.length
      } else {
        // Tenant API has count endpoint
        await fetchUserCount()
      }

      console.log('[Users] Fetched successfully:', data.length, 'users')
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch users'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Users] Error fetching:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch total user count
   */
  async function fetchUserCount(): Promise<void> {
    try {
      const params = new URLSearchParams()

      if (filters.value.search) {
        params.append('search', filters.value.search)
      }

      if (filters.value.is_active !== null) {
        params.append('is_active', String(filters.value.is_active))
      }

      const url = `${getBaseUrl()}/count?${params.toString()}`
      const count = await authenticatedFetch<number>(url)
      pagination.value.total = count
    } catch (err: any) {
      console.error('[Users] Error fetching count:', err)
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

      console.log('[Users] Fetched user:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Users] Error fetching user:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get user-specific endpoint URL (with tenant_id for management users)
   */
  function getUserEndpoint(userId: number, tenantId: number): string {
    const authStore = useAuthStore()
    if (authStore.user?.is_super_admin) {
      // Management users need tenant_id in the path
      console.log('[Users] Building endpoint for user:', userId, 'tenant_id:', tenantId)
      return `/api/v1/management/tenants/${tenantId}/users/${userId}`
    }
    return `${getBaseUrl()}/${userId}`
  }

  /**
   * Get create endpoint URL (with tenant_id for management users)
   */
  function getCreateEndpoint(tenantId?: number): string {
    const authStore = useAuthStore()
    if (authStore.user?.is_super_admin && tenantId) {
      return `/api/v1/management/tenants/${tenantId}/users`
    }
    return getBaseUrl()
  }

  /**
   * Create a new user
   */
  async function createUser(userData: UserCreate & { tenant_id?: number }): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null

      const endpoint = getCreateEndpoint(userData.tenant_id)
      const data = await authenticatedFetch<User>(endpoint, {
        method: 'POST',
        body: JSON.stringify(userData)
      })

      users.value.unshift(data)
      success('User created successfully')
      console.log('[Users] Created user:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Users] Error creating user:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update a user
   */
  async function updateUser(userId: number, userData: UserUpdate): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null

      // Get the user from the list to find tenant_id
      const user = users.value.find(u => u.id === userId)

      if (!user) {
        throw new Error(`User with ID ${userId} not found in the list`)
      }

      if (!user.tenant_id) {
        console.error('[Users] User object missing tenant_id:', user)
        throw new Error('User data is missing tenant_id. Please refresh the page.')
      }

      const endpoint = getUserEndpoint(userId, user.tenant_id)
      console.log('[Users] Update endpoint:', endpoint)

      const data = await authenticatedFetch<User>(endpoint, {
        method: 'PUT',
        body: JSON.stringify(userData)
      })

      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = data
      }

      success('User updated successfully')
      console.log('[Users] Updated user:', data)
      return data
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Users] Error updating user:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete a user
   */
  async function deleteUser(userId: number): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      // Get the user to find tenant_id
      const user = users.value.find(u => u.id === userId)

      if (!user) {
        throw new Error(`User with ID ${userId} not found in the list`)
      }

      if (!user.tenant_id) {
        console.error('[Users] User object missing tenant_id:', user)
        throw new Error('User data is missing tenant_id. Please refresh the page.')
      }

      const endpoint = getUserEndpoint(userId, user.tenant_id)

      await authenticatedFetch(endpoint, {
        method: 'DELETE'
      })

      users.value = users.value.filter(u => u.id !== userId)
      success('User deleted successfully')
      console.log('[Users] Deleted user:', userId)
      return true
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete user'
      error.value = errorMessage
      notifyError(errorMessage)
      console.error('[Users] Error deleting user:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Set filters
   */
  function setFilters(newFilters: Partial<typeof filters.value>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  /**
   * Set pagination parameters
   */
  function setPagination(skip: number, limit: number) {
    pagination.value.skip = skip
    pagination.value.limit = limit
  }

  /**
   * Reset state
   */
  function reset(): void {
    users.value = []
    currentUser.value = null
    error.value = null
    pagination.value = { skip: 0, limit: 100, total: 0 }
    filters.value = { search: '', is_active: null, role_id: null }
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    error,
    pagination,
    filters,

    // Computed
    activeUsers,
    inactiveUsers,
    superAdmins,
    regularUsers,
    stats,

    // Methods
    fetchUsers,
    fetchUser,
    fetchUserCount,
    createUser,
    updateUser,
    deleteUser,
    setFilters,
    setPagination,
    reset
  }
}
