<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading && !profile" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-gray-400" />
    </div>

    <!-- Error State -->
    <div v-else-if="error && !profile" class="text-center py-12">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
      <p class="text-sm text-gray-600 dark:text-gray-400">{{ error }}</p>
    </div>

    <!-- Create Profile Form (when profile doesn't exist) -->
    <div v-else-if="!profile && !loading">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Create Your Profile</h3>
        </template>

        <form @submit.prevent="createNewProfile" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Fullname -->
            <UFormGroup label="Full Name" required>
              <UInput 
                v-model="newProfileData.fullname" 
                placeholder="Enter your full name"
                required
              />
            </UFormGroup>

            <!-- Email -->
            <UFormGroup label="Email" required>
              <UInput 
                v-model="newProfileData.email" 
                type="email"
                placeholder="email@example.com"
                required
              />
            </UFormGroup>

            <!-- Mobile -->
            <UFormGroup label="Mobile">
              <UInput 
                v-model="newProfileData.mobile" 
                placeholder="01234567890"
              />
            </UFormGroup>

            <!-- WhatsApp -->
            <UFormGroup label="WhatsApp Number">
              <UInput 
                v-model="newProfileData.whatsapp_number" 
                placeholder="01234567890"
              />
            </UFormGroup>

            <!-- City -->
            <UFormGroup label="City">
              <UInput 
                v-model="newProfileData.city" 
                placeholder="Enter your city"
              />
            </UFormGroup>

            <!-- Company Name -->
            <UFormGroup label="Company Name">
              <UInput 
                v-model="newProfileData.company_name" 
                placeholder="Enter company name"
              />
            </UFormGroup>

            <!-- Commercial Registration -->
            <UFormGroup label="Commercial Registration Number">
              <UInput 
                v-model="newProfileData.commercial_registration_number" 
                placeholder="Enter registration number"
              />
            </UFormGroup>

            <!-- Entity Number -->
            <UFormGroup label="Entity Number">
              <UInput 
                v-model="newProfileData.entity_number" 
                placeholder="Enter entity number"
              />
            </UFormGroup>

            <!-- Address (Full Width) -->
            <UFormGroup label="Address" class="md:col-span-2">
              <UTextarea 
                v-model="newProfileData.address" 
                placeholder="Enter your full address"
                :rows="3"
              />
            </UFormGroup>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-3">
            <UButton
              type="submit"
              :loading="updating"
              :disabled="updating"
            >
              Create Profile
            </UButton>
          </div>

          <div v-if="updateError" class="text-red-600 dark:text-red-400 text-sm">
            {{ updateError }}
          </div>
        </form>
      </UCard>
    </div>

    <!-- Profile Content -->
    <div v-else-if="profile">
      <!-- Avatar and Header Section -->
      <UCard>
        <div class="flex flex-col sm:flex-row items-center gap-6">
          <!-- Avatar -->
          <div class="relative">
            <div class="w-32 h-32 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <img 
                v-if="profile.avatar_image_url" 
                :src="avatarUrlWithCacheBust" 
                alt="Profile Avatar"
                class="w-full h-full object-cover"
                :key="avatarKey"
              />
              <UIcon 
                v-else 
                name="i-heroicons-user" 
                class="w-16 h-16 text-gray-400"
              />
            </div>
            
            <!-- Avatar Upload Button -->
            <label 
              class="absolute bottom-0 right-0 p-2 bg-primary-600 hover:bg-primary-700 rounded-full cursor-pointer shadow-lg transition-colors"
              :class="{ 'opacity-50 cursor-not-allowed': uploadingAvatar }"
            >
              <UIcon name="i-heroicons-camera" class="w-5 h-5 text-white" />
              <input 
                type="file" 
                accept="image/*" 
                class="hidden" 
                @change="handleAvatarUpload"
                :disabled="uploadingAvatar"
              />
            </label>
          </div>

          <!-- Profile Info -->
          <div class="flex-1 text-center sm:text-left">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ profile.fullname }}
            </h2>
            <p class="text-gray-600 dark:text-gray-400 mt-1">
              {{ profile.email }}
            </p>
            <div class="flex items-center justify-center sm:justify-start gap-2 mt-2">
              <UBadge :color="profile.is_active ? 'green' : 'red'" variant="subtle">
                {{ profile.is_active ? 'Active' : 'Inactive' }}
              </UBadge>
              <span class="text-xs text-gray-500">ID: {{ profile.id }}</span>
            </div>
          </div>

          <!-- Edit Button -->
          <UButton
            v-if="!isEditing"
            @click="startEdit"
            icon="i-heroicons-pencil"
            size="lg"
          >
            Edit Profile
          </UButton>
        </div>
      </UCard>

      <!-- View Mode -->
      <UCard v-if="!isEditing">
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Profile Details</h3>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Mobile</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.mobile || '-' }}</p>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">WhatsApp</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.whatsapp_number || '-' }}</p>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">City</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.city || '-' }}</p>
          </div>

          <div class="md:col-span-2 lg:col-span-3">
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Address</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.address || '-' }}</p>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Company Name</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.company_name || '-' }}</p>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Commercial Registration</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.commercial_registration_number || '-' }}</p>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Entity Number</label>
            <p class="mt-1 text-gray-900 dark:text-white">{{ profile.entity_number || '-' }}</p>
          </div>

          <div class="md:col-span-2 lg:col-span-3">
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Created At</label>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {{ formatDate(profile.created_at) }}
            </p>
          </div>
        </div>
      </UCard>

      <!-- Edit Mode -->
      <UCard v-else>
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Edit Profile</h3>
        </template>

        <form @submit.prevent="saveChanges" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Fullname -->
            <UFormGroup label="Full Name" required>
              <UInput 
                v-model="editData.fullname" 
                placeholder="Enter your full name"
                required
              />
            </UFormGroup>

            <!-- Email -->
            <UFormGroup label="Email" required>
              <UInput 
                v-model="editData.email" 
                type="email"
                placeholder="email@example.com"
                required
              />
            </UFormGroup>

            <!-- Mobile -->
            <UFormGroup label="Mobile">
              <UInput 
                v-model="editData.mobile" 
                placeholder="01234567890"
              />
            </UFormGroup>

            <!-- WhatsApp -->
            <UFormGroup label="WhatsApp Number">
              <UInput 
                v-model="editData.whatsapp_number" 
                placeholder="01234567890"
              />
            </UFormGroup>

            <!-- City -->
            <UFormGroup label="City">
              <UInput 
                v-model="editData.city" 
                placeholder="Enter your city"
              />
            </UFormGroup>

            <!-- Company Name -->
            <UFormGroup label="Company Name">
              <UInput 
                v-model="editData.company_name" 
                placeholder="Enter company name"
              />
            </UFormGroup>

            <!-- Commercial Registration -->
            <UFormGroup label="Commercial Registration Number">
              <UInput 
                v-model="editData.commercial_registration_number" 
                placeholder="Enter registration number"
              />
            </UFormGroup>

            <!-- Entity Number -->
            <UFormGroup label="Entity Number">
              <UInput 
                v-model="editData.entity_number" 
                placeholder="Enter entity number"
              />
            </UFormGroup>

            <!-- Address (Full Width) -->
            <UFormGroup label="Address" class="md:col-span-2">
              <UTextarea 
                v-model="editData.address" 
                placeholder="Enter your full address"
                :rows="3"
              />
            </UFormGroup>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-3">
            <UButton
              type="button"
              color="gray"
              variant="ghost"
              @click="cancelEdit"
              :disabled="updating"
            >
              Cancel
            </UButton>
            <UButton
              type="submit"
              :loading="updating"
              :disabled="updating"
            >
              Save Changes
            </UButton>
          </div>

          <div v-if="updateError" class="text-red-600 dark:text-red-400 text-sm">
            {{ updateError }}
          </div>
        </form>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { UserProfile, UserProfileCreate } from '@/composables/useUserProfile'

const props = defineProps<{
  profile: UserProfile | null
  loading: boolean
  error: string | null
  updating?: boolean
  updateError?: string | null
  uploadingAvatar?: boolean
}>()

const emit = defineEmits<{
  'update': [updates: Partial<UserProfile>]
  'upload-avatar': [file: File]
  'create': [profileData: UserProfileCreate]
}>()

const isEditing = ref(false)
const editData = ref<Partial<UserProfile>>({})
const newProfileData = ref<UserProfileCreate>({
  fullname: '',
  email: '',
  address: '',
  mobile: '',
  city: '',
  company_name: '',
  commercial_registration_number: '',
  entity_number: '',
  whatsapp_number: ''
})
const avatarKey = ref(Date.now())

// Computed property to add cache-busting timestamp to avatar URL
const avatarUrlWithCacheBust = computed(() => {
  if (!props.profile?.avatar_image_url) return ''
  
  const url = props.profile.avatar_image_url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}t=${avatarKey.value}`
})

// Watch for avatar URL changes and update cache-busting key
watch(
  () => props.profile?.avatar_image_url,
  (newUrl, oldUrl) => {
    if (newUrl !== oldUrl && newUrl) {
      avatarKey.value = Date.now()
    }
  }
)

// Format date for display
function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch (e) {
    return dateString
  }
}

// Start editing
function startEdit() {
  if (props.profile) {
    editData.value = {
      fullname: props.profile.fullname,
      email: props.profile.email,
      mobile: props.profile.mobile,
      whatsapp_number: props.profile.whatsapp_number,
      city: props.profile.city,
      address: props.profile.address,
      company_name: props.profile.company_name,
      commercial_registration_number: props.profile.commercial_registration_number,
      entity_number: props.profile.entity_number
    }
  }
  isEditing.value = true
}

// Cancel editing
function cancelEdit() {
  isEditing.value = false
  editData.value = {}
}

// Save changes
function saveChanges() {
  emit('update', editData.value)
  isEditing.value = false
}

// Handle avatar upload
function handleAvatarUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file')
      return
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size should be less than 5MB')
      return
    }
    
    emit('upload-avatar', file)
    
    // Update cache-busting key to force image refresh
    avatarKey.value = Date.now()
    
    // Reset input
    target.value = ''
  }
}

// Create new profile
function createNewProfile() {
  emit('create', newProfileData.value)
}
</script>