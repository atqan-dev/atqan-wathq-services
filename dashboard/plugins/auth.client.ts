export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  
  // Initialize authentication state and wait for completion
  await authStore.initAuth()
  
  // Debug log to verify auth state
  
})