/**
 * Confirm Dialog type definitions
 */

export type ConfirmDialogType = 'info' | 'warning' | 'danger' | 'success'

export interface ConfirmDialogOptions {
  title?: string
  message: string
  type?: ConfirmDialogType
  confirmText?: string
  cancelText?: string
  icon?: string
  confirmColor?: 'primary' | 'red' | 'green' | 'yellow' | 'blue' | 'gray'
  cancelColor?: 'gray' | 'red'
  confirmIcon?: string
  cancelIcon?: string
  reverseButtons?: boolean
  hideCancel?: boolean
  html?: boolean
}

export interface ConfirmDialogState {
  isOpen: boolean
  options: ConfirmDialogOptions
  resolve: ((value: boolean) => void) | null
}
