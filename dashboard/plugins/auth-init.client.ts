export default defineNuxtPlugin(async (nuxtApp) => {
  // Initialize auth store on app start
  nuxtApp.hook('app:created', async () => {
    const authStore = useAuthStore()
    
    await authStore.initAuth()
    
    // If token is missing but refresh token exists, try to refresh
    if (!authStore.token && authStore.refreshToken) {
      console.log('Access token missing but refresh token exists, attempting refresh')
      await authStore.refreshAuthToken()
    }
  })
}) 