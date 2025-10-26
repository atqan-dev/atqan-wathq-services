<template>
  <div class="container mx-auto py-8 px-4 max-w-7xl">
    <UserProfile 
      :profile="profile" 
      :loading="loading" 
      :error="error" 
      :updating="updating" 
      :updateError="updateError"
      :uploadingAvatar="uploadingAvatar"
      @update="handleUpdate"
      @upload-avatar="handleAvatarUpload"
      @create="handleCreate"
    />
  </div>
</template>

<script setup lang="ts">
// Apply auth middleware to protect this page
definePageMeta({
  middleware: ['auth']
})

import { onMounted } from 'vue'
import { useUserProfile } from '@/composables/useUserProfile'
import type { UserProfileCreate } from '@/composables/useUserProfile'
import UserProfile from '@/components/UserProfile.vue'

const { 
  profile, 
  loading, 
  error, 
  fetchProfile, 
  createProfile,
  updateProfile, 
  updating, 
  updateError,
  uploadAvatar,
  uploadingAvatar
} = useUserProfile()

// Fetch profile on mount
onMounted(() => {
  fetchProfile()
})

// Handle profile update
async function handleUpdate(updates: Partial<NonNullable<typeof profile.value>>) {
  try {
    await updateProfile(updates)
    // Success notification is handled in the composable
  } catch (err: any) {
    // Error notification is handled in the composable
    console.error('Failed to update profile:', err)
  }
}

// Handle avatar upload
async function handleAvatarUpload(file: File) {
  try {
    await uploadAvatar(file)
    // Success notification is handled in the composable
  } catch (err: any) {
    // Error notification is handled in the composable
    console.error('Failed to upload avatar:', err)
  }
}

// Handle profile creation
async function handleCreate(profileData: UserProfileCreate) {
  try {
    await createProfile(profileData)
    // Success notification is handled in the composable
    // Refetch profile after creation
    await fetchProfile()
  } catch (err: any) {
    // Error notification is handled in the composable
    console.error('Failed to create profile:', err)
  }
}
</script>