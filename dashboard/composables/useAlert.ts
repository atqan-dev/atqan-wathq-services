import { useToast } from '#imports'
import { useI18n } from '~/composables/useI18n'
import type { NotificationColor } from '#ui/types'

export type AlertType = 'success' | 'error' | 'info' | 'warning' | 'loading'

export interface AlertOptions {
  timeout?: number
  closeButton?: boolean | { icon: string }
  icon?: string
  actions?: Array<{ label: string; click: () => void }>
  callback?: () => void
  ui?: Record<string, any>
}

export interface AlertPayload {
  title: string
  description?: string
  type: AlertType
  options?: AlertOptions
}

/**
 * A composable that provides a centralized alert system
 * Wraps Nuxt UI's toast system to provide a more consistent API
 */
export function useAlert() {
  const toast = useToast()
  const { t } = useI18n()

  /**
   * Show an alert with the given parameters
   */
  const show = (payload: AlertPayload) => {
    const { title, description, type, options } = payload
    
    // Map alert types to toast colors and icons
    const colorMap: Record<AlertType, NotificationColor> = {
      success: 'green',
      error: 'red',
      info: 'blue',
      warning: 'yellow',
      loading: 'gray'
    }

    const iconMap: Record<AlertType, string> = {
      success: 'i-heroicons-check-circle',
      error: 'i-heroicons-exclamation-circle',
      info: 'i-heroicons-information-circle',
      warning: 'i-heroicons-exclamation-triangle',
      loading: 'i-heroicons-arrow-path'
    }

    // Default options
    const defaultOptions = {
      timeout: 5000,
      closeButton: { icon: 'i-heroicons-x-mark-20-solid' }
    }

    // Merge options
    const mergedOptions = { ...defaultOptions, ...options }

    // Prepare closeButton option
    let closeButtonOption;
    if (typeof mergedOptions.closeButton === 'boolean') {
      closeButtonOption = mergedOptions.closeButton ? { icon: 'i-heroicons-x-mark-20-solid' } : undefined;
    } else {
      closeButtonOption = mergedOptions.closeButton;
    }

    // Show toast
    return toast.add({
      title,
      description,
      color: colorMap[type],
      timeout: mergedOptions.timeout,
      closeButton: closeButtonOption,
      icon: mergedOptions.icon || iconMap[type],
      actions: mergedOptions.actions,
      callback: mergedOptions.callback,
      ui: mergedOptions.ui
    })
  }

  /**
   * Show a success alert
   */
  const success = (title: string, description?: string, options?: AlertOptions) => {
    return show({ title, description, type: 'success', options })
  }

  /**
   * Show an error alert
   */
  const error = (title: string, description?: string, options?: AlertOptions) => {
    return show({ title, description, type: 'error', options })
  }

  /**
   * Show an info alert
   */
  const info = (title: string, description?: string, options?: AlertOptions) => {
    return show({ title, description, type: 'info', options })
  }

  /**
   * Show a warning alert
   */
  const warning = (title: string, description?: string, options?: AlertOptions) => {
    return show({ title, description, type: 'warning', options })
  }

  /**
   * Show a loading alert
   */
  const loading = (title: string, description?: string, options?: AlertOptions) => {
    return show({ title, description, type: 'loading', options })
  }

  /**
   * Show an alert for an API operation (with loading, success, and error states)
   * @param operation The async operation to perform
   * @param messages Object containing loading, success, and error messages
   * @param options Toast options
   */
  const withAsync = async <T>(
    operation: () => Promise<T>,
    messages: {
      loading: { title: string; description?: string }
      success: { title: string; description?: string }
      error: { title: string; description?: string }
    },
    options?: AlertOptions
  ): Promise<T> => {
    // Store the toast ID as string
    const loadingToast = loading(messages.loading.title, messages.loading.description, options)
    const toastId = typeof loadingToast === 'string' ? loadingToast : undefined
    
    try {
      const result = await operation()
      
      // Remove loading toast and show success
      if (toastId) toast.remove(toastId)
      success(messages.success.title, messages.success.description, options)
      
      return result
    } catch (err: any) {
      // Remove loading toast and show error
      if (toastId) toast.remove(toastId)
      
      const errorDescription = err?.message || messages.error.description
      error(messages.error.title, errorDescription, options)
      
      throw err
    }
  }

  /**
   * Translate and show an alert
   * @param keys Object containing translation keys for title and description
   * @param params Parameters to pass to the translation function
   * @param type Alert type
   * @param options Toast options
   */
  const showTranslated = (
    keys: { title: string; description?: string },
    params: Record<string, any> = {},
    type: AlertType = 'info',
    options?: AlertOptions
  ) => {
    return show({
      title: t(keys.title, params),
      description: keys.description ? t(keys.description, params) : undefined,
      type,
      options
    })
  }

  return {
    show,
    success,
    error,
    info,
    warning,
    loading,
    withAsync,
    showTranslated
  }
}
