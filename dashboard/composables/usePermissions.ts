import { ref } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'
import { useAlert } from './useAlert'
import type { Permission } from '~/types/user'

/**
 * Composable for managing permissions
 */
export function usePermissions() {
    const { authenticatedFetch } = useAuthenticatedFetch()
    const { error: notifyError } = useAlert()

    // State
    const permissions = ref<Permission[]>([])
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    /**
     * Get the base URL for permissions API
     */
    function getBaseUrl(): string {
        return '/api/v1/permissions'
    }

    /**
     * Fetch all permissions
     */
    async function fetchPermissions(): Promise<void> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Permission[]>(getBaseUrl())
            permissions.value = data

            console.log('[Permissions] Fetched successfully:', data.length, 'permissions')
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to fetch permissions'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Permissions] Error fetching:', err)
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Fetch permissions by scope
     */
    async function fetchPermissionsByScope(scope: 'tenant' | 'system'): Promise<void> {
        try {
            isLoading.value = true
            error.value = null

            const data = await authenticatedFetch<Permission[]>(`${getBaseUrl()}/scope/${scope}`)
            permissions.value = data

            console.log('[Permissions] Fetched by scope:', scope, data.length, 'permissions')
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to fetch permissions'
            error.value = errorMessage
            notifyError(errorMessage)
            console.error('[Permissions] Error fetching by scope:', err)
        } finally {
            isLoading.value = false
        }
    }

    /**
     * Reset state
     */
    function reset(): void {
        permissions.value = []
        error.value = null
    }

    return {
        // State
        permissions,
        isLoading,
        error,

        // Methods
        fetchPermissions,
        fetchPermissionsByScope,
        reset
    }
}
