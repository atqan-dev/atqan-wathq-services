/**
 * Language and RTL/LTR management composable
 * Handles internationalization with proper RTL/LTR support
 */
export const useLanguage = () => {
  const { locale, locales, setLocale } = useI18n()

  // Available languages
  const languages = computed(() => locales.value)

  // Current language
  const currentLanguage = computed(() => {
    return locales.value.find(l => l.code === locale.value) || locales.value[0]
  })

  // Is RTL active
  const isRTL = computed(() => currentLanguage.value?.dir === 'rtl')

  // Switch language
  const switchLanguage = (langCode: string) => {
    if (langCode && (langCode === 'en' || langCode === 'ar')) {
      setLocale(langCode)
      updateDirection()
    }
  }

  // Update document direction
  const updateDirection = () => {
    if (process.client) {
      const html = document.documentElement
      const body = document.body
      const currentLang = currentLanguage.value
      
      if (currentLang) {
        html.setAttribute('dir', currentLang.dir)
        html.setAttribute('lang', currentLang.code || 'en')
        // Update body classes for RTL/LTR styling
        body.classList.toggle('rtl', currentLang.dir === 'rtl')
        body.classList.toggle('ltr', currentLang.dir === 'ltr')
      }
    }
  }

  // Toggle between English and Arabic
  const toggleLanguage = () => {
    const newLang = locale.value === 'en' ? 'ar' : 'en'
    switchLanguage(newLang)
  }

  // Initialize direction on mount
  const initializeDirection = () => {
    updateDirection()
  }

  return {
    locale,
    languages,
    currentLanguage,
    isRTL,
    switchLanguage,
    toggleLanguage,
    updateDirection,
    initializeDirection
  }
}
