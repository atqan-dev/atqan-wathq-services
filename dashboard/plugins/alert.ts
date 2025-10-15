import { defineNuxtPlugin } from '#app'
import { useAlert } from '~/composables/useAlert'

export default defineNuxtPlugin((nuxtApp) => {
  const alert = useAlert()
  
  // Make the alert system available globally
  nuxtApp.provide('alert', alert)
})

// Type declarations for better TypeScript support
declare module '#app' {
  interface NuxtApp {
    $alert: ReturnType<typeof useAlert>
  }
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $alert: ReturnType<typeof useAlert>
  }
}
