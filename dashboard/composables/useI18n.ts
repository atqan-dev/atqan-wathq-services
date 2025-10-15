import en from '~/locales/en.json'
import ar from '~/locales/ar.json'

interface LocaleData {
  code: string
  name: string
  dir: 'ltr' | 'rtl'
  flag: string
}

const translations = {
  en,
  ar
}

const locales: LocaleData[] = [
  {
    code: 'en',
    name: 'English',
    dir: 'ltr',
    flag: '🇺🇸'
  },
  {
    code: 'ar',
    name: 'العربية',
    dir: 'rtl',
    flag: '🇸🇦'
  }
]

export const useI18n = () => {
  const currentLocale = useCookie('locale', {
    default: () => 'en'
  })

  const locale = computed({
    get: () => currentLocale.value,
    set: (value: string) => {
      currentLocale.value = value
    }
  })

  const availableLocales = computed(() => locales)

  const currentLocaleData = computed(() => {
    return locales.find(l => l.code === locale.value) || locales[0]
  })

  const t = (key: string, params?: Record<string, any>): string => {
    const keys = key.split('.')
    let value: any = translations[locale.value as keyof typeof translations]
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return key // Return key if translation not found
      }
    }
    
    if (typeof value === 'string' && params) {
      // Replace parameters in the format {paramName}
      return value.replace(/{([^}]+)}/g, (_, paramName) => {
        return params[paramName] !== undefined ? String(params[paramName]) : `{${paramName}}`
      })
    }
    
    return typeof value === 'string' ? value : key
  }

  const setLocale = (newLocale: string) => {
    if (locales.some(l => l.code === newLocale)) {
      locale.value = newLocale
    }
  }

  return {
    locale: readonly(locale),
    locales: availableLocales,
    currentLocale: currentLocaleData,
    t,
    setLocale
  }
}
