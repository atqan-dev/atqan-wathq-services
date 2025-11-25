import { ref } from 'vue'
import type { Ref } from 'vue'
import { useAuthenticatedFetch } from './useAuthenticatedFetch'

export interface UserProfile {
  id: number
  management_user_id: number
  fullname: string
  address: string
  mobile: string
  city: string
  company_name: string
  commercial_registration_number: string
  entity_number: string
  full_info: Record<string, any>
  email: string
  whatsapp_number: string
  avatar_image_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface UserProfileCreate {
  fullname: string
  address?: string
  mobile?: string
  city?: string
  company_name?: string
  commercial_registration_number?: string
  entity_number?: string
  full_info?: Record<string, any>
  email: string
  whatsapp_number?: string
}

export function useUserProfile() {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const toast = useToast()

  const profile: Ref<UserProfile | null> = ref(null)
  const profileExists = ref(true)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const updating = ref(false)
  const updateError = ref<string | null>(null)
  const uploadingAvatar = ref(false)

  /**
   * Fetch current user's profile
   * @param silent - If true, don't show error toast (used for internal refetches)
   */
  const fetchProfile = async (silent = false): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const data = await authenticatedFetch<UserProfile>('/api/v1/management/users/me/profile')
      profile.value = data
      profileExists.value = true
    } catch (err: any) {
      // Check if it's a 404 error (profile not found)
      if (err.status === 404 || err.message?.includes('404')) {
        profileExists.value = false
        profile.value = null
        error.value = null
        if (!silent) {
          toast.add({
            title: 'Profile Not Found',
            description: 'Please create your profile to get started.',
            color: 'blue',
            icon: 'i-heroicons-information-circle',
            timeout: 3000
          })
        }
      } else {
        profileExists.value = true
        const errorMsg = err.message || 'Failed to fetch user profile.'
        error.value = errorMsg
        if (!silent) {
          toast.add({
            title: 'Error',
            description: errorMsg,
            color: 'red',
            icon: 'i-heroicons-exclamation-circle'
          })
        }
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Create user profile (self-service)
   */
  const createProfile = async (profileData: UserProfileCreate): Promise<void> => {
    updating.value = true
    updateError.value = null
    try {
      const data = await authenticatedFetch<UserProfile>(
        '/api/v1/management/users/me/profile',
        {
          method: 'POST',
          body: profileData
        }
      )
      profile.value = data
      toast.add({
        title: 'Success',
        description: 'Profile created successfully!',
        color: 'green',
        icon: 'i-heroicons-check-circle'
      })
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to create user profile.'
      updateError.value = errorMsg
      toast.add({
        title: 'Error',
        description: errorMsg,
        color: 'red',
        icon: 'i-heroicons-exclamation-circle'
      })
      throw err
    } finally {
      updating.value = false
    }
  }

  /**
   * Update user profile
   */
  const updateProfile = async (updates: Partial<UserProfile>): Promise<void> => {
    updating.value = true
    updateError.value = null
    try {
      const data = await authenticatedFetch<UserProfile>(
        '/api/v1/management/users/me/profile',
        {
          method: 'PUT',
          body: updates
        }
      )
      profile.value = data
      toast.add({
        title: '✅ Profile Updated',
        description: 'Your profile has been updated successfully!',
        color: 'green',
        icon: 'i-heroicons-check-circle',
        timeout: 3000
      })
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to update user profile.'
      updateError.value = errorMsg
      toast.add({
        title: 'Error',
        description: errorMsg,
        color: 'red',
        icon: 'i-heroicons-exclamation-circle'
      })
      throw err
    } finally {
      updating.value = false
    }
  }

  /**
   * Upload or update avatar image
   */
  const uploadAvatar = async (file: File): Promise<void> => {
    uploadingAvatar.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await authenticatedFetch<any>(
        '/api/v1/management/avatar',
        {
          method: 'PUT',
          body: formData
        }
      )

      // Log response to see what API returns
      console.log('Avatar upload response:', response)

      // Handle various response formats
      const avatarUrl = response.avatar_url || response.avatar_image_url || response.url || response.file_url
      
      if (avatarUrl && profile.value) {
        profile.value.avatar_image_url = avatarUrl
      }
      
      // Refetch profile to ensure we have the latest data (silent to avoid duplicate errors)
      await fetchProfile(true)
      
      toast.add({
        title: '🎉 Avatar Updated',
        description: 'Your profile picture has been updated successfully!',
        color: 'green',
        icon: 'i-heroicons-photo',
        timeout: 3000
      })
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to upload avatar.'
      toast.add({
        title: 'Upload Failed',
        description: errorMsg,
        color: 'red',
        icon: 'i-heroicons-exclamation-circle'
      })
      throw err
    } finally {
      uploadingAvatar.value = false
    }
  }

  return {
    profile,
    profileExists,
    loading,
    error,
    fetchProfile,
    createProfile,
    updateProfile,
    updating,
    updateError,
    uploadAvatar,
    uploadingAvatar
  }
} 