import { reactive } from 'vue'

/**
 * Confirm Dialog Options
 */
export interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'info' | 'warning' | 'danger' | 'success'
  icon?: string
  confirmIcon?: string
  cancelIcon?: string
  confirmColor?: 'primary' | 'red' | 'green' | 'yellow' | 'blue' | 'gray'
  cancelColor?: 'gray' | 'red'
  reverseButtons?: boolean
  hideCancel?: boolean
  html?: boolean
  size?: 'sm' | 'md' | 'lg'
  closeOnConfirm?: boolean
  closeOnCancel?: boolean
}

/**
 * Confirm Dialog State
 */
interface ConfirmState {
  isOpen: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  type: 'info' | 'warning' | 'danger' | 'success'
  icon?: string
  confirmIcon?: string
  cancelIcon?: string
  confirmColor: string
  cancelColor: string
  reverseButtons: boolean
  hideCancel: boolean
  html: boolean
  size: 'sm' | 'md' | 'lg'
  closeOnConfirm: boolean
  closeOnCancel: boolean
}

/**
 * Global confirm state
 */
const confirmState = reactive<ConfirmState>({
  isOpen: false,
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  type: 'info',
  confirmColor: 'blue',
  cancelColor: 'gray',
  reverseButtons: false,
  hideCancel: false,
  html: false,
  size: 'md',
  closeOnConfirm: true,
  closeOnCancel: true
})

/**
 * Resolve function stored outside reactive state to avoid XrayWrapper errors
 */
let resolveFunction: ((value: boolean) => void) | undefined

/**
 * Composable for confirm dialog
 */
export const useConfirm = () => {
  /**
   * Show confirm dialog
   */
  const confirm = (options: ConfirmOptions | string): Promise<boolean> => {
    return new Promise((resolve) => {
      // Handle string shorthand
      const opts = typeof options === 'string' ? { message: options } : options
      
      // Get defaults based on type
      const type = opts.type || 'info'
      const defaults = getDefaults(type)
      
      // Merge options
      confirmState.isOpen = true
      confirmState.title = opts.title || defaults.title
      confirmState.message = opts.message
      confirmState.confirmText = opts.confirmText || defaults.confirmText
      confirmState.cancelText = opts.cancelText || defaults.cancelText
      confirmState.type = type
      confirmState.icon = opts.icon || defaults.icon
      confirmState.confirmIcon = opts.confirmIcon
      confirmState.cancelIcon = opts.cancelIcon
      confirmState.confirmColor = opts.confirmColor || defaults.confirmColor
      confirmState.cancelColor = opts.cancelColor || 'gray'
      confirmState.reverseButtons = opts.reverseButtons || false
      confirmState.hideCancel = opts.hideCancel || false
      confirmState.html = opts.html || false
      confirmState.size = opts.size || 'md'
      confirmState.closeOnConfirm = opts.closeOnConfirm !== false
      confirmState.closeOnCancel = opts.closeOnCancel !== false
      resolveFunction = resolve
    })
  }

  /**
   * Preset confirm dialogs
   */
  const confirmDelete = (message: string, title?: string): Promise<boolean> => {
    return confirm({
      title: title || 'Confirm Delete',
      message,
      type: 'danger',
      confirmText: 'Delete',
      confirmIcon: 'i-heroicons-trash'
    })
  }

  const confirmWarning = (message: string, title?: string): Promise<boolean> => {
    return confirm({
      title: title || 'Warning',
      message,
      type: 'warning',
      confirmText: 'Continue'
    })
  }

  const confirmInfo = (message: string, title?: string): Promise<boolean> => {
    return confirm({
      title: title || 'Information',
      message,
      type: 'info',
      confirmText: 'OK',
      hideCancel: true
    })
  }

  const confirmSuccess = (message: string, title?: string): Promise<boolean> => {
    return confirm({
      title: title || 'Success',
      message,
      type: 'success',
      confirmText: 'OK',
      hideCancel: true
    })
  }

  /**
   * Handle user response
   */
  const handleConfirm = () => {
    resolveFunction?.(true)
    if (confirmState.closeOnConfirm) {
      closeDialog()
    }
  }

  const handleCancel = () => {
    resolveFunction?.(false)
    if (confirmState.closeOnCancel) {
      closeDialog()
    }
  }

  /**
   * Close dialog
   */
  const closeDialog = () => {
    confirmState.isOpen = false
    resolveFunction = undefined
  }

  /**
   * Get default options by type
   */
  function getDefaults(type: string) {
    switch (type) {
      case 'danger':
        return {
          title: 'Confirm Delete',
          confirmText: 'Delete',
          cancelText: 'Cancel',
          confirmColor: 'red',
          icon: 'i-heroicons-exclamation-circle'
        }
      case 'warning':
        return {
          title: 'Warning',
          confirmText: 'Continue',
          cancelText: 'Cancel',
          confirmColor: 'yellow',
          icon: 'i-heroicons-exclamation-triangle'
        }
      case 'success':
        return {
          title: 'Success',
          confirmText: 'OK',
          cancelText: 'Cancel',
          confirmColor: 'green',
          icon: 'i-heroicons-check-circle'
        }
      default: // info
        return {
          title: 'Confirm',
          confirmText: 'OK',
          cancelText: 'Cancel',
          confirmColor: 'blue',
          icon: 'i-heroicons-information-circle'
        }
    }
  }

  return {
    confirmState,
    confirm,
    confirmDelete,
    confirmWarning,
    confirmInfo,
    confirmSuccess,
    handleConfirm,
    handleCancel,
    closeDialog
  }
}
