// API composable for handling backend communication
export const useApi = () => {
  const config = useRuntimeConfig();

  // Base API URL - will be configured in nuxt.config.ts
  const baseURL = config.public.apiBase || "http://localhost:5500/api/v1";

  // Generic API call function
  const apiCall = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    // Get auth token from auth store
    const authStore = useAuthStore()
    const authToken = authStore.token
    
    // Prevent double /api in URL if baseURL already ends with /api
    const url =
      baseURL.endsWith("/api") && endpoint.startsWith("/api")
        ? `${baseURL}${endpoint.substring(4)}` // Remove /api from endpoint
        : `${baseURL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...(authToken && { Authorization: `Bearer ${authToken}` }),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      
      throw error;
    }
  };

  // Specific API methods
  const api = {
    // Generic GET method
    get: <T>(endpoint: string) => apiCall<T>(endpoint),
    // Generic PATCH method
    patch: <T>(endpoint: string, data: any) => apiCall<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

    // Dashboard stats
    getStats: () => apiCall<DashboardStats>("/stats"),
  };

  return api;
};


export interface DashboardStats {
  total_apps: number;
  running_apps: number;
  down_apps: number;
  total_deployments: number;
}
