export default defineNuxtPlugin(() => {
  const colorMode = useColorMode()

  // Watch for color mode changes and update the HTML element
  watch(
    () => colorMode.value,
    (newMode) => {
      const html = document.documentElement
      
      // Remove all dark mode classes first
      html.classList.remove('dark')
      
      // Add dark class if in dark mode
      if (newMode === 'dark') {
        html.classList.add('dark')
      }
    },
    { immediate: true }
  )

  // Initialize on mount
  const html = document.documentElement
  
  // Apply initial theme
  if (colorMode.value === 'dark') {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
})
