export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  email?: boolean
  url?: boolean
  custom?: (value: any) => string | null
  message?: string
}

export interface ValidationResult {
  isValid: boolean
  errors: string[]
}

export const useValidation = () => {
  const validateField = (value: any, rules: ValidationRule[]): ValidationResult => {
    const errors: string[] = []

    for (const rule of rules) {
      // Required validation
      if (rule.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
        errors.push(rule.message || 'This field is required')
        continue
      }

      // Skip other validations if value is empty and not required
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        continue
      }

      // String validations
      if (typeof value === 'string') {
        // Min length
        if (rule.minLength && value.length < rule.minLength) {
          errors.push(rule.message || `Minimum length is ${rule.minLength} characters`)
        }

        // Max length
        if (rule.maxLength && value.length > rule.maxLength) {
          errors.push(rule.message || `Maximum length is ${rule.maxLength} characters`)
        }

        // Pattern validation
        if (rule.pattern && !rule.pattern.test(value)) {
          errors.push(rule.message || 'Invalid format')
        }

        // Email validation
        if (rule.email) {
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          if (!emailPattern.test(value)) {
            errors.push(rule.message || 'Invalid email address')
          }
        }

        // URL validation
        if (rule.url) {
          try {
            new URL(value)
          } catch {
            errors.push(rule.message || 'Invalid URL')
          }
        }
      }

      // Custom validation
      if (rule.custom) {
        const customError = rule.custom(value)
        if (customError) {
          errors.push(customError)
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  const validateForm = (formData: Record<string, any>, validationSchema: Record<string, ValidationRule[]>): Record<string, ValidationResult> => {
    const results: Record<string, ValidationResult> = {}

    for (const [field, rules] of Object.entries(validationSchema)) {
      results[field] = validateField(formData[field], rules)
    }

    return results
  }

  const isFormValid = (validationResults: Record<string, ValidationResult>): boolean => {
    return Object.values(validationResults).every(result => result.isValid)
  }

  // Common validation rules
  const commonRules = {
    required: (message?: string): ValidationRule => ({
      required: true,
      message: message || 'This field is required'
    }),

    email: (message?: string): ValidationRule => ({
      email: true,
      message: message || 'Please enter a valid email address'
    }),

    url: (message?: string): ValidationRule => ({
      url: true,
      message: message || 'Please enter a valid URL'
    }),

    minLength: (length: number, message?: string): ValidationRule => ({
      minLength: length,
      message: message || `Minimum length is ${length} characters`
    }),

    maxLength: (length: number, message?: string): ValidationRule => ({
      maxLength: length,
      message: message || `Maximum length is ${length} characters`
    }),

    pattern: (regex: RegExp, message?: string): ValidationRule => ({
      pattern: regex,
      message: message || 'Invalid format'
    }),

    githubRepo: (message?: string): ValidationRule => ({
      pattern: /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/,
      message: message || 'Please enter a valid GitHub repository (owner/repo)'
    }),

    port: (message?: string): ValidationRule => ({
      custom: (value) => {
        const num = parseInt(value)
        if (isNaN(num) || num < 1 || num > 65535) {
          return message || 'Port must be between 1 and 65535'
        }
        return null
      }
    }),

    domain: (message?: string): ValidationRule => ({
      pattern: /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/,
      message: message || 'Please enter a valid domain name'
    })
  }

  // Sanitization functions
  const sanitize = {
    string: (value: string): string => {
      return value.trim().replace(/[<>]/g, '')
    },

    email: (value: string): string => {
      return value.trim().toLowerCase()
    },

    url: (value: string): string => {
      let url = value.trim()
      if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url
      }
      return url
    },

    githubRepo: (value: string): string => {
      return value.trim().replace(/^https?:\/\/github\.com\//, '')
    },

    port: (value: string): number | null => {
      const num = parseInt(value.trim())
      return isNaN(num) ? null : num
    }
  }

  return {
    validateField,
    validateForm,
    isFormValid,
    commonRules,
    sanitize
  }
}
