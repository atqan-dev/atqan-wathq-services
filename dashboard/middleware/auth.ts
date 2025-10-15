export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  
  // If user is not authenticated and trying to access a protected route
  if (!authStore.isAuthenticated) {
    // Redirect to login with the intended destination
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }
  
  // If user is authenticated, allow access
  return
})