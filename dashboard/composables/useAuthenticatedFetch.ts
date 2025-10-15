export const useAuthenticatedFetch = () => {
  const authStore = useAuthStore();
  const router = useRouter();

  const authenticatedFetch = async <T>(
    url: string,
    options: any = {}
  ): Promise<T> => {
    // Check if body is FormData - if so, don't set Content-Type (browser will set it with boundary)
    const isFormData = options.body instanceof FormData;
    
    const headers: Record<string, string> = {
      ...options.headers,
    };

    // Only set Content-Type for non-FormData requests
    if (!isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    if (authStore.token) {
      headers.Authorization = `Bearer ${authStore.token}`;
    }

    try {
      const response = await $fetch<T>(url, {
        ...options,
        headers,
      });
      return response;
    } catch (err: any) {
      if (err?.response?.status === 401) {
        // Clear auth data
        authStore.$reset?.() // If using Pinia, or manually clear token/user
        // Optionally clear other stores/data here
        // Redirect to login
        router.push('/login');
      }
      throw err;
    }
  };

  return {
    authenticatedFetch,
  };
};
