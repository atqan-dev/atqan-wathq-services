/**
 * Confirm Dialog - Practical Examples
 * 
 * This file contains real-world examples of using the confirm dialog
 * in your application.
 */

import { useConfirm } from '@/composables/useConfirm'

// ============================================================================
// EXAMPLE 1: Basic Delete Confirmation
// ============================================================================

export async function exampleBasicDelete() {
  const { confirmDelete } = useConfirm()
  
  const confirmed = await confirmDelete(
    'Are you sure you want to delete this item?'
  )
  
  if (confirmed) {
    console.log('Item deleted')
  }
}

// ============================================================================
// EXAMPLE 2: Custom Delete with Details
// ============================================================================

export async function exampleCustomDelete(itemName: string) {
  const { confirmDelete } = useConfirm()
  
  const confirmed = await confirmDelete(
    `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
    'Delete Item'
  )
  
  if (confirmed) {
    // await deleteItem(itemId)
    console.log('Delete confirmed')
  }
}

// ============================================================================
// EXAMPLE 3: Warning Before Action
// ============================================================================

export async function exampleWarningAction() {
  const { confirmWarning } = useConfirm()
  
  const confirmed = await confirmWarning(
    'This action will affect all users in the system. Do you want to continue?',
    'System-wide Change'
  )
  
  if (confirmed) {
    console.log('Action confirmed')
  }
}

// ============================================================================
// EXAMPLE 4: Info Dialog (No Cancel)
// ============================================================================

export async function exampleInfoDialog() {
  const { confirmInfo } = useConfirm()
  
  await confirmInfo(
    'Your export has been queued and will be sent to your email when ready.',
    'Export Started'
  )
  
  console.log('User acknowledged')
}

// ============================================================================
// EXAMPLE 5: Success Dialog
// ============================================================================

export async function exampleSuccessDialog() {
  const { confirmSuccess } = useConfirm()
  
  await confirmSuccess(
    'Your profile has been updated successfully!',
    'Success'
  )
}

// ============================================================================
// EXAMPLE 6: Custom Configuration
// ============================================================================

export async function exampleCustomConfig() {
  const { confirm } = useConfirm()
  
  const confirmed = await confirm({
    title: 'Enable Feature',
    message: 'Would you like to enable this beta feature?',
    type: 'info',
    confirmText: 'Enable',
    cancelText: 'Not Now',
    confirmColor: 'blue',
    icon: 'i-heroicons-sparkles'
  })
  
  if (confirmed) {
    console.log('Feature enabled')
  }
}

// ============================================================================
// EXAMPLE 7: Reverse Button Order
// ============================================================================

export async function exampleReverseButtons() {
  const { confirm } = useConfirm()
  
  const confirmed = await confirm({
    message: 'Save changes before closing?',
    confirmText: 'Save',
    cancelText: 'Discard',
    reverseButtons: true, // Cancel on left, Save on right
    type: 'warning'
  })
  
  if (confirmed) {
    console.log('Changes saved')
  } else {
    console.log('Changes discarded')
  }
}

// ============================================================================
// EXAMPLE 8: HTML Content
// ============================================================================

export async function exampleHTMLContent() {
  const { confirm } = useConfirm()
  
  const confirmed = await confirm({
    title: 'Delete Multiple Items',
    message: `
      <p class="mb-3 font-semibold">You are about to delete:</p>
      <ul class="list-disc ml-5 space-y-1">
        <li>3 Projects</li>
        <li>15 Tasks</li>
        <li>42 Files</li>
      </ul>
      <p class="mt-3 text-red-600 dark:text-red-400">This action cannot be undone!</p>
    `,
    html: true,
    type: 'danger',
    size: 'lg'
  })
  
  if (confirmed) {
    console.log('Bulk delete confirmed')
  }
}

// ============================================================================
// EXAMPLE 9: Form Unsaved Changes
// ============================================================================

export async function exampleUnsavedChanges(isDirty: boolean) {
  if (!isDirty) return true
  
  const { confirmWarning } = useConfirm()
  
  return await confirmWarning(
    'You have unsaved changes. Are you sure you want to leave?',
    'Unsaved Changes'
  )
}

// ============================================================================
// EXAMPLE 10: Status Toggle
// ============================================================================

export async function exampleToggleStatus(isActive: boolean, itemName: string) {
  const { confirm } = useConfirm()
  
  const action = isActive ? 'deactivate' : 'activate'
  
  const confirmed = await confirm({
    title: `${action.charAt(0).toUpperCase() + action.slice(1)} Item`,
    message: `Are you sure you want to ${action} "${itemName}"?`,
    type: isActive ? 'warning' : 'success',
    confirmText: action.charAt(0).toUpperCase() + action.slice(1),
    confirmIcon: isActive ? 'i-heroicons-pause' : 'i-heroicons-play'
  })
  
  return confirmed
}

// ============================================================================
// EXAMPLE 11: Multi-Step Confirmation
// ============================================================================

export async function exampleMultiStepConfirm() {
  const { confirmWarning, confirm, confirmDelete } = useConfirm()
  
  // Step 1
  const step1 = await confirmWarning(
    'This is a critical operation. Are you sure you want to continue?',
    'Warning'
  )
  if (!step1) return false
  
  // Step 2
  const step2 = await confirm({
    message: 'Have you backed up your data?',
    confirmText: 'Yes, I have a backup',
    type: 'info'
  })
  if (!step2) return false
  
  // Step 3 - Final confirmation
  const step3 = await confirmDelete(
    'Final confirmation: This will permanently delete all data. Type DELETE to confirm.',
    'Final Warning'
  )
  
  return step3
}

// ============================================================================
// EXAMPLE 12: Custom Icons
// ============================================================================

export async function exampleCustomIcons() {
  const { confirm } = useConfirm()
  
  const confirmed = await confirm({
    title: 'Send Notification',
    message: 'Send notification to all 1,000 users?',
    type: 'info',
    icon: 'i-heroicons-bell',
    confirmText: 'Send',
    confirmIcon: 'i-heroicons-paper-airplane',
    cancelIcon: 'i-heroicons-x-mark'
  })
  
  return confirmed
}

// ============================================================================
// EXAMPLE 13: Different Sizes
// ============================================================================

export async function exampleDifferentSizes() {
  const { confirm } = useConfirm()
  
  // Small dialog
  await confirm({
    message: 'Continue?',
    size: 'sm'
  })
  
  // Medium dialog (default)
  await confirm({
    message: 'Are you sure you want to proceed with this action?',
    size: 'md'
  })
  
  // Large dialog
  await confirm({
    message: 'This is a detailed message with lots of information...',
    size: 'lg'
  })
}

// ============================================================================
// EXAMPLE 14: With Async Operations
// ============================================================================

export async function exampleAsyncOperation() {
  const { confirmDelete, confirmSuccess, confirmWarning } = useConfirm()
  
  const confirmed = await confirmDelete(
    'Delete this tenant? All associated data will be removed.',
    'Delete Tenant'
  )
  
  if (confirmed) {
    try {
      // Simulate API call
      // await api.deleteTenant(id)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      await confirmSuccess(
        'Tenant deleted successfully!',
        'Success'
      )
    } catch (error: any) {
      await confirmWarning(
        `Failed to delete tenant: ${error.message}`,
        'Error'
      )
    }
  }
}

// ============================================================================
// EXAMPLE 15: Usage in Vue Component
// ============================================================================

/*
<template>
  <div>
    <UButton @click="handleDelete" color="red">
      Delete
    </UButton>
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm'

const { confirmDelete } = useConfirm()

async function handleDelete() {
  const confirmed = await confirmDelete(
    'Are you sure you want to delete this item?'
  )
  
  if (confirmed) {
    // Perform deletion
    await deleteItem()
  }
}
</script>
*/

// ============================================================================
// EXAMPLE 16: Table Row Actions
// ============================================================================

export async function exampleTableRowDelete(item: { id: number; name: string }) {
  const { confirmDelete } = useConfirm()
  
  const confirmed = await confirmDelete(
    `Delete "${item.name}"? This action cannot be undone.`,
    'Confirm Delete'
  )
  
  if (confirmed) {
    // await api.delete(`/items/${item.id}`)
    console.log(`Deleted item ${item.id}`)
  }
}

// ============================================================================
// EXAMPLE 17: Bulk Actions
// ============================================================================

export async function exampleBulkDelete(selectedItems: any[]) {
  const { confirm } = useConfirm()
  
  const confirmed = await confirm({
    title: 'Delete Multiple Items',
    message: `You are about to delete ${selectedItems.length} items. This action cannot be undone.`,
    html: false,
    type: 'danger',
    confirmText: `Delete ${selectedItems.length} Items`,
    confirmIcon: 'i-heroicons-trash'
  })
  
  if (confirmed) {
    // await api.bulkDelete(selectedItems.map(i => i.id))
    console.log(`Deleted ${selectedItems.length} items`)
  }
}

// ============================================================================
// EXAMPLE 18: Conditional Cancel Hide
// ============================================================================

export async function exampleMandatoryAction() {
  const { confirm } = useConfirm()
  
  await confirm({
    title: 'Terms and Conditions',
    message: 'Please read and accept the terms and conditions to continue.',
    confirmText: 'I Accept',
    hideCancel: true, // No way to cancel
    type: 'info',
    size: 'lg'
  })
  
  console.log('Terms accepted')
}

// ============================================================================
// EXAMPLE 19: String Shorthand
// ============================================================================

export async function exampleStringShorthand() {
  const { confirm } = useConfirm()
  
  // Simple string message
  const result = await confirm('Are you sure?')
  
  return result
}

// ============================================================================
// EXAMPLE 20: Logout Confirmation
// ============================================================================

export async function exampleLogoutConfirm() {
  const { confirmWarning } = useConfirm()
  
  const confirmed = await confirmWarning(
    'Are you sure you want to log out?',
    'Confirm Logout'
  )
  
  if (confirmed) {
    // await authStore.logout()
    // router.push('/login')
    console.log('Logged out')
  }
}

// ============================================================================
// Export all examples for easy access
// ============================================================================

export default {
  exampleBasicDelete,
  exampleCustomDelete,
  exampleWarningAction,
  exampleInfoDialog,
  exampleSuccessDialog,
  exampleCustomConfig,
  exampleReverseButtons,
  exampleHTMLContent,
  exampleUnsavedChanges,
  exampleToggleStatus,
  exampleMultiStepConfirm,
  exampleCustomIcons,
  exampleDifferentSizes,
  exampleAsyncOperation,
  exampleTableRowDelete,
  exampleBulkDelete,
  exampleMandatoryAction,
  exampleStringShorthand,
  exampleLogoutConfirm
}
