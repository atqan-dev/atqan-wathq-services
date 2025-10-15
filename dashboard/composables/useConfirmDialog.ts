import { ref } from 'vue'
import type { ConfirmDialogOptions, ConfirmDialogState } from '~/types/confirm-dialog'

/**
 * Global state for confirm dialog
 */
const dialogState = ref<ConfirmDialogState>({
  isOpen: false,
  options: {
    message: '',
    type: 'info'
  },
  resolve: null
})

/**
 * Composable for confirm dialog functionality
 */
export function useConfirmDialog() {
  /**
   * Show confirm dialog
   */
  function confirm(options: ConfirmDialogOptions | string): Promise<boolean> {
    return new Promise((resolve) => {
      // Handle string shorthand
      const dialogOptions: ConfirmDialogOptions = typeof options === 'string'
        ? { message: options }
        : options

      // Set default values based on type
      const type = dialogOptions.type || 'info'
      const defaults = getDefaultsByType(type)

      dialogState.value = {
        isOpen: true,
        options: {
          ...defaults,
          ...dialogOptions
        },
        resolve
      }
    })
  }

  /**
   * Quick confirm dialogs with presets
   */
  function confirmDelete(message: string, title?: string): Promise<boolean> {
    return confirm({
      message,
      title: title || 'Delete Confirmation',
      type: 'danger',
      confirmText: 'Delete',
      icon: 'i-heroicons-trash'
    })
  }

  function confirmAction(message: string, title?: string): Promise<boolean> {
    return confirm({
      message,
      title: title || 'Confirm Action',
      type: 'warning',
      confirmText: 'Confirm',
      icon: 'i-heroicons-exclamation-triangle'
    })
  }

  function confirmSuccess(message: string, title?: string): Promise<boolean> {
    return confirm({
      message,
      title: title || 'Success',
      type: 'success',
      confirmText: 'Continue',
      icon: 'i-heroicons-check-circle',
      hideCancel: true
    })
  }

  function confirmInfo(message: string, title?: string): Promise<boolean> {
    return confirm({
      message,
      title: title || 'Information',
      type: 'info',
      confirmText: 'OK',
      icon: 'i-heroicons-information-circle',
      hideCancel: true
    })
  }

  /**
   * Handle user response
   */
  function handleConfirm() {
    if (dialogState.value.resolve) {
      dialogState.value.resolve(true)
    }
    closeDialog()
  }

  function handleCancel() {
    if (dialogState.value.resolve) {
      dialogState.value.resolve(false)
    }
    closeDialog()
  }

  /**
   * Close dialog
   */
  function closeDialog() {
    dialogState.value.isOpen = false
    dialogState.value.resolve = null
  }

  /**
   * Get default options by type
   */
  function getDefaultsByType(type: string) {
    switch (type) {
      case 'danger':
        return {
          title: 'Confirm Delete',
          confirmText: 'Delete',
          cancelText: 'Cancel',
          confirmColor: 'red' as const,
          cancelColor: 'gray' as const,
          icon: 'i-heroicons-exclamation-circle',
          confirmIcon: 'i-heroicons-trash'
        }
      case 'warning':
        return {
          title: 'Confirm Action',
          confirmText: 'Confirm',
          cancelText: 'Cancel',
          confirmColor: 'yellow' as const,
          cancelColor: 'gray' as const,
          icon: 'i-heroicons-exclamation-triangle',
          confirmIcon: 'i-heroicons-check'
        }
      case 'success':
        return {
          title: 'Success',
          confirmText: 'OK',
          cancelText: 'Cancel',
          confirmColor: 'green' as const,
          cancelColor: 'gray' as const,
          icon: 'i-heroicons-check-circle',
          confirmIcon: 'i-heroicons-check'
        }
      default: // info
        return {
          title: 'Confirm',
          confirmText: 'OK',
          cancelText: 'Cancel',
          confirmColor: 'blue' as const,
          cancelColor: 'gray' as const,
          icon: 'i-heroicons-information-circle',
          confirmIcon: 'i-heroicons-check'
        }
    }
  }

  return {
    // State
    dialogState,
    
    // Methods
    confirm,
    confirmDelete,
    confirmAction,
    confirmSuccess,
    confirmInfo,
    handleConfirm,
    handleCancel,
    closeDialog
  }
}
