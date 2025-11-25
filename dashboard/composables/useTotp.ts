/**
 * TOTP (Two-Factor Authentication) composable for the dashboard.
 * 
 * Provides methods for:
 * - Setting up TOTP
 * - Enabling/disabling TOTP
 * - Verifying TOTP codes
 * - Managing backup codes
 */

import { ref, computed } from 'vue'

export interface TOTPStatus {
  enabled: boolean
  verified_at: string | null
  last_used_at: string | null
  backup_codes_remaining: number
}

export interface TOTPSetupResponse {
  secret: string
  qr_code: string
  provisioning_uri: string
  backup_codes: string[]
}

// Define locally to avoid circular dependency with auth store
interface TOTPRequiredResponse {
  requires_totp: boolean
  temp_token: string
  message: string
}

export function useTotp() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  
  // State
  const status = ref<TOTPStatus | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const setupData = ref<TOTPSetupResponse | null>(null)
  
  // Computed
  const isEnabled = computed(() => status.value?.enabled ?? false)
  const backupCodesRemaining = computed(() => status.value?.backup_codes_remaining ?? 0)
  
  /**
   * Fetch current TOTP status
   */
  const fetchStatus = async (): Promise<TOTPStatus> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authenticatedFetch<TOTPStatus>(
        '/api/v1/management/totp/status'
      )
      status.value = response
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to fetch TOTP status'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Initialize TOTP setup - generates secret and QR code
   */
  const initSetup = async (): Promise<TOTPSetupResponse> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authenticatedFetch<TOTPSetupResponse>(
        '/api/v1/management/totp/setup',
        { method: 'POST' }
      )
      setupData.value = response
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to initialize TOTP setup'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Enable TOTP after verifying setup code
   */
  const enable = async (code: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    
    try {
      await authenticatedFetch(
        '/api/v1/management/totp/enable',
        {
          method: 'POST',
          body: { code }
        }
      )
      // Refresh status
      await fetchStatus()
      setupData.value = null
      return true
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to enable TOTP'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Disable TOTP
   */
  const disable = async (password: string, code?: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    
    try {
      await authenticatedFetch(
        '/api/v1/management/totp/disable',
        {
          method: 'POST',
          body: { password, code }
        }
      )
      // Refresh status
      await fetchStatus()
      return true
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to disable TOTP'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Verify a TOTP code (for testing)
   */
  const verify = async (code: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authenticatedFetch<{ success: boolean; message: string }>(
        '/api/v1/management/totp/verify',
        {
          method: 'POST',
          body: { code }
        }
      )
      return response.success
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to verify TOTP code'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Regenerate backup codes
   */
  const regenerateBackupCodes = async (
    password: string,
    code: string
  ): Promise<string[]> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authenticatedFetch<{
        backup_codes: string[]
        message: string
      }>(
        '/api/v1/management/totp/backup-codes/regenerate',
        {
          method: 'POST',
          body: { password, code }
        }
      )
      // Refresh status to update backup codes count
      await fetchStatus()
      return response.backup_codes
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to regenerate backup codes'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Verify a backup code
   */
  const verifyBackupCode = async (code: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authenticatedFetch<{ success: boolean; message: string }>(
        '/api/v1/management/totp/backup-codes/verify',
        {
          method: 'POST',
          body: { code }
        }
      )
      if (response.success) {
        // Refresh status to update backup codes count
        await fetchStatus()
      }
      return response.success
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to verify backup code'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Complete login with TOTP code
   */
  const completeLogin = async (
    tempToken: string,
    code: string
  ): Promise<{ access_token: string; refresh_token: string }> => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await $fetch<{
        access_token: string
        refresh_token: string
        token_type: string
      }>('/api/v1/management/auth/login/totp', {
        method: 'POST',
        body: {
          temp_token: tempToken,
          code
        }
      })
      return response
    } catch (err: any) {
      error.value = err?.data?.detail || 'Failed to verify TOTP code'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * Check if login response requires TOTP
   */
  const isTotpRequired = (response: any): response is TOTPRequiredResponse => {
    return response && response.requires_totp === true && response.temp_token
  }
  
  /**
   * Clear setup data
   */
  const clearSetup = () => {
    setupData.value = null
  }
  
  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }
  
  return {
    // State
    status,
    isLoading,
    error,
    setupData,
    
    // Computed
    isEnabled,
    backupCodesRemaining,
    
    // Methods
    fetchStatus,
    initSetup,
    enable,
    disable,
    verify,
    regenerateBackupCodes,
    verifyBackupCode,
    completeLogin,
    isTotpRequired,
    clearSetup,
    clearError
  }
}
