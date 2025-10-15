import { ref, reactive } from 'vue'

export interface NotificationOptions {
  title?: string
  message: string
  type?: 'info' | 'success' | 'warning' | 'error'
  duration?: number
  persistent?: boolean
}

interface Notification extends NotificationOptions {
  id: string
  timestamp: number
}

const notifications = ref<Notification[]>([])

export const useNotification = () => {
  const show = (options: NotificationOptions) => {
    const notification: Notification = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: Date.now(),
      title: options.title,
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 5000,
      persistent: options.persistent || false
    }

    notifications.value.push(notification)

    // Auto remove after duration (unless persistent)
    if (!notification.persistent) {
      setTimeout(() => {
        remove(notification.id)
      }, notification.duration)
    }

    return notification.id
  }

  const remove = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clear = () => {
    notifications.value = []
  }

  // Convenience methods
  const success = (message: string, title?: string, duration?: number) => {
    return show({ message, title, type: 'success', duration })
  }

  const error = (message: string, title?: string, persistent = false) => {
    return show({ message, title, type: 'error', persistent })
  }

  const warning = (message: string, title?: string, duration?: number) => {
    return show({ message, title, type: 'warning', duration })
  }

  const info = (message: string, title?: string, duration?: number) => {
    return show({ message, title, type: 'info', duration })
  }

  return {
    notifications,
    show,
    remove,
    clear,
    success,
    error,
    warning,
    info
  }
}
