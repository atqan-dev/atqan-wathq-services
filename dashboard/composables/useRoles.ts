import { ref, computed } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { Role } from '~/types/user'

export interface RoleCreate {
    name: string
    description?: string
    permission_ids?: number[]
}

export interface RoleUpdate {
    name?: string
    description?: string
    permission_ids?: number[]
}

/**
 * Composable for managing roles
 */
export function useRoles() {
    const { authenticatedFetch } = useAuthenticatedFetch()
    const { success, error: notifyError } = useAlert()

    // State
    const roles = ref<Role[]>([])
    const currentRole = ref<Role | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    /**
     * Get the base URL for roles API
     */
    function getBaseUrl(): string {
        // Roles endpoint is the same for both management and tenant users
        return '/api/v1/roles'
    }

    /**
     * Fetch all roles
     */
    async function fetchRoles(): Promise<void> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Role[]>(getBaseUrl())
            roles.value = data

            console.log('[Roles] Fetched successfully:', data.length, 'roles')
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to fetch roles'
            error.value = errorMessage
            // Don't notify error - roles may not be available for management users
            console.warn('[Roles] Could not fetch roles:', err)
            throw err // Re-throw so caller can handle
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Fetch a single role by ID
     */
    async function fetchRole(roleId: number): Promise<Role | null> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Role>(`${getBaseUrl()}/${roleId}`)
            currentRole.value = data

            console.log('[Roles] Fetched role:', data)
            return data
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to fetch role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error fetching role:', err)
            return null
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Create a new role
     */
    async function createRole(roleData: RoleCreate): Promise<Role | null> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Role>(getBaseUrl(), {
                method: 'POST',
                body: JSON.stringify(roleData)
            })

            roles.value.push(data)
            success('Role created successfully')
            console.log('[Roles] Created role:', data)
            return data
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to create role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error creating role:', err)
            return null
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Update a role
     */
    async function updateRole(roleId: number, roleData: RoleUpdate): Promise<Role | null> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Role>(`${getBaseUrl()}/${roleId}`, {
                method: 'PUT',
                body: JSON.stringify(roleData)
            })

            const index = roles.value.findIndex(r => r.id === roleId)
            if (index !== -1) {
                roles.value[index] = data
            }

            success('Role updated successfully')
            console.log('[Roles] Updated role:', data)
            return data
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to update role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error updating role:', err)
            return null
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Delete a role
     */
    async function deleteRole(roleId: number): Promise<boolean> {
        try {
            isLoading.value = true
            error.value = null

            await authenticatedFetch(`${getBaseUrl()}/${roleId}`, {
                method: 'DELETE'
            })

            roles.value = roles.value.filter(r => r.id !== roleId)
            success('Role deleted successfully')
            console.log('[Roles] Deleted role:', roleId)
            return true
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to delete role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error deleting role:', err)
            return false
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Assign role to user
     */
    async function assignRoleToUser(roleId: number, userId: number): Promise<boolean> {
        try {
            isLoading.value = true
            error.value = null

            await authenticatedFetch(`${getBaseUrl()}/${roleId}/assign/${userId}`, {
                method: 'POST'
            })

            success('Role assigned successfully')
            return true
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to assign role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error assigning role:', err)
            return false
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Remove role from user
     */
    async function removeRoleFromUser(roleId: number, userId: number): Promise<boolean> {
        try {
            isLoading.value = true
            error.value = null

            await authenticatedFetch(`${getBaseUrl()}/${roleId}/assign/${userId}`, {
                method: 'DELETE'
            })

            success('Role removed successfully')
            return true
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to remove role'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Roles] Error removing role:', err)
            return false
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Reset state
     */
    function reset(): void {
        roles.value = []
        currentRole.value = null
        error.value = null
    }

    return {
        // State
        roles,
        currentRole,
        isLoading,
        error,

        // Methods
        fetchRoles,
        fetchRole,
        createRole,
        updateRole,
        deleteRole,
        assignRoleToUser,
        removeRoleFromUser,
        reset
    }
}
