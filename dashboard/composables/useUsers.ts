import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { User } from '~/types/user'

/**
 * Composable for managing all users across all tenants
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
    return '/api/v1/management/tenants/users'
  }

  /**
   * Fetch all users with pagination
   */
  async function fetchUsers(skip?: number, limit?: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null
      
      const params = new URLSearchParams()
      params.append('skip', String(skip ?? pagination.value.skip))
      params.append('limit', String(limit ?? pagination.value.limit))
      
      const url = `${getBaseUrl()}?${params.toString()}`
      const data = await authenticatedFetch<User[]>(url)
      
      users.value = data
      pagination.value.total = data.length
      
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
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    error,
    pagination,
    
    // Computed
    activeUsers,
    inactiveUsers,
    superAdmins,
    regularUsers,
    stats,
    
    // Methods
    fetchUsers,
    fetchUser,
    setPagination,
    reset
  }
}
